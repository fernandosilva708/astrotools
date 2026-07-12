# SPDX-License-Identifier: GPL-2.0-only
from flask import Blueprint, render_template, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
import subprocess
import threading
from datetime import datetime
from pathlib import Path
import shutil
from app import db
from app.models import GalleryImage
from app.gallery.ingest import SEESTAR_EXTENSIONS, extract_fits_metadata

backup_bp = Blueprint('backup', __name__)

# Estado global para monitorizar o backup
backup_status = {
    "running": False, 
    "last_result": "Nenhuma cópia efetuada.", 
    "last_run": None
}

# Estado global para monitorizar a importação do Seestar via USB
seestar_usb_status = {
    "running": False,
    "last_result": "Nenhuma transferência efetuada.",
    "last_run": None
}


def run_rclone_task(app_context, remote, path):
    """Tarefa em segundo plano para executar o rclone de forma eficiente."""
    global backup_status
    with app_context:
        try:
            # Uso de --timeout para evitar bloqueios longos no RPi 2
            result = subprocess.run(
                ['rclone', 'sync', path, remote, '--progress', '--timeout', '10m'],
                capture_output=True, text=True
            )
            
            backup_status["last_run"] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            if result.returncode == 0:
                backup_status["last_result"] = "Sucesso: Cópia concluída com êxito."
            else:
                backup_status["last_result"] = f"Erro: {result.stderr[:150]}"
        except Exception as e:
            backup_status["last_result"] = f"Falha crítica: {str(e)[:150]}"
        finally:
            backup_status["running"] = False


def detect_seestar_usb():
    """Deteta automaticamente o ponto de montagem do telescópio Seestar S50 por USB.
    
    Verifica caminhos de automontagem comuns no Linux/Raspberry Pi. Se o dispositivo
    estiver presente mas não montado, tenta efetuar a montagem.
    """
    # 1. Verificar caminhos de automontagem comuns (/media/pi/<Label> ou /media/<user>/<Label>)
    media_dir = Path("/media")
    if media_dir.is_dir():
        for user_dir in media_dir.iterdir():
            if user_dir.is_dir():
                for mount_dir in user_dir.iterdir():
                    if "seestar" in mount_dir.name.lower() and mount_dir.is_dir():
                        # Verifica se contém a estrutura esperada
                        if (mount_dir / "MyPhotos").is_dir() or (mount_dir / "EMMC").is_dir():
                            return str(mount_dir), False
                        return str(mount_dir), False

    # 2. Verificar se o dispositivo está listado em /dev/disk/by-label/
    by_label_dir = Path("/dev/disk/by-label")
    seestar_device = None
    if by_label_dir.is_dir():
        for label_path in by_label_dir.iterdir():
            if "seestar" in label_path.name.lower():
                seestar_device = str(label_path.resolve())
                break

    if seestar_device:
        # Verificar se já se encontra montado algures (lendo /proc/mounts)
        try:
            with open("/proc/mounts", "r") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2 and (parts[0] == seestar_device or parts[0].startswith("/dev/sd")):
                        mnt_pt = parts[1]
                        if "seestar" in mnt_pt.lower() or mnt_pt.startswith("/media/"):
                            return mnt_pt, False
        except Exception:
            pass

        # Se não estiver montado, tenta montar numa diretoria local na workspace
        mount_point = Path(current_app.root_path).parent / "instance" / "seestar_usb"
        mount_point.mkdir(parents=True, exist_ok=True)
        try:
            # Tentar montagem direta
            res = subprocess.run(["mount", seestar_device, str(mount_point)], capture_output=True)
            if res.returncode != 0:
                # Tentar com privilégios de superutilizador (sudo)
                res = subprocess.run(["sudo", "mount", seestar_device, str(mount_point)], capture_output=True)
            if res.returncode == 0:
                return str(mount_point), True
        except Exception:
            pass

    return None, False


def run_seestar_usb_task(app_context, user_id):
    """Tarefa em segundo plano para importar as fotos do Seestar por USB e eliminá-las de seguida."""
    global seestar_usb_status
    with app_context:
        try:
            # Detetar o telescópio
            mount_path, mounted_by_us = detect_seestar_usb()
            if not mount_path:
                seestar_usb_status["last_result"] = "Erro: Telescópio Seestar não detetado por USB."
                return
            
            seestar_usb_status["last_result"] = "Telescópio detetado. A processar ficheiros..."
            
            # Pasta de destino na Galeria do AstroTools
            dest_dir = Path(current_app.root_path).parent / current_app.config['GALLERY_UPLOAD_FOLDER']
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            mount_dir = Path(mount_path)
            
            # Procurar todos os ficheiros com extensões válidas no telescópio
            files_to_process = []
            for filepath in mount_dir.rglob('*'):
                if filepath.is_file() and filepath.suffix.lower() in SEESTAR_EXTENSIONS:
                    files_to_process.append(filepath)
            
            if not files_to_process:
                seestar_usb_status["last_result"] = "Sucesso: Nenhum ficheiro para transferir."
                # Desmontar se tiver sido montado por nós
                if mounted_by_us:
                    subprocess.run(["sudo", "umount", mount_path])
                return

            copied_count = 0
            deleted_count = 0
            new_images_in_batch = 0
            
            for src_filepath in files_to_process:
                filename = src_filepath.name
                
                # Verificar se a imagem já foi registada na BD para o utilizador
                exists = db.session.query(GalleryImage.id).filter_by(
                    filename=filename,
                    user_id=user_id
                ).first() is not None
                
                if exists:
                    # Se já existe no Pi, apaga do Seestar conforme instruído
                    try:
                        src_filepath.unlink()
                        deleted_count += 1
                    except Exception:
                        pass
                    continue
                
                # Gerar nome único na pasta de destino
                dest_filepath = dest_dir / filename
                counter = 1
                while dest_filepath.exists():
                    stem = Path(filename).stem
                    suffix = Path(filename).suffix
                    dest_filepath = dest_dir / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                # Transferir e registar na base de dados
                try:
                    shutil.copy2(src_filepath, dest_filepath)
                    
                    # Extrair metadados FITS
                    metadata = {}
                    if dest_filepath.suffix.lower() in {'.fits', '.fit'}:
                        metadata = extract_fits_metadata(str(dest_filepath))
                        
                    # Criar registo na galeria
                    image = GalleryImage(
                        filename=dest_filepath.name,
                        title=dest_filepath.stem,
                        filepath=str(dest_filepath),
                        user_id=user_id,
                        captured_at=datetime.fromtimestamp(dest_filepath.stat().st_mtime),
                        **metadata
                    )
                    db.session.add(image)
                    new_images_in_batch += 1
                    copied_count += 1
                    
                    # Commits parciais para otimização de memória
                    if new_images_in_batch >= 10:
                        db.session.commit()
                        new_images_in_batch = 0
                        
                    # Apagar ficheiro do Seestar após cópia confirmada
                    src_filepath.unlink()
                    deleted_count += 1
                except Exception as err:
                    # Reverter registo em caso de falha antes de eliminar
                    db.session.rollback()
                    print(f"Erro ao processar {src_filepath}: {err}")
                    
            if new_images_in_batch > 0:
                db.session.commit()
                
            seestar_usb_status["last_result"] = f"Sucesso: {copied_count} imagens transferidas, {deleted_count} apagadas do Seestar."
            seestar_usb_status["last_run"] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            
            # Garantir sincronização e desmontar
            if mounted_by_us:
                subprocess.run(["sync"])
                subprocess.run(["sudo", "umount", mount_path])
                
        except Exception as e:
            seestar_usb_status["last_result"] = f"Falha crítica: {str(e)[:150]}"
        finally:
            seestar_usb_status["running"] = False


@backup_bp.route('/')
@login_required
def index():
    return render_template('backup/index.html', status=backup_status, seestar_status=seestar_usb_status)


@backup_bp.route('/run', methods=['POST'])
@login_required
def run_backup():
    """Inicia a cópia de segurança em segundo plano."""
    global backup_status
    if backup_status["running"]:
        flash('Já existe uma cópia de segurança em curso.', 'warning')
        return redirect(url_for('backup.index'))

    remote = current_app.config.get('RCLONE_REMOTE', '')
    path = current_app.config.get('RCLONE_PATH', '')
    
    if not remote or not path:
        flash('RCLONE_REMOTE e RCLONE_PATH devem estar definidos no ficheiro .env.', 'danger')
        return redirect(url_for('backup.index'))

    backup_status["running"] = True
    backup_status["last_result"] = "Em curso..."
    
    thread = threading.Thread(
        target=run_rclone_task, 
        args=(current_app.app_context(), remote, path)
    )
    thread.daemon = True
    thread.start()
    
    flash('Cópia de segurança iniciada em segundo plano.', 'info')
    return redirect(url_for('backup.index'))


@backup_bp.route('/seestar-usb/run', methods=['POST'])
@login_required
def run_seestar_usb():
    """Inicia a ligação e transferência do Seestar USB em segundo plano."""
    global seestar_usb_status
    if seestar_usb_status["running"]:
        flash('Já existe uma transferência do Seestar em curso.', 'warning')
        return redirect(url_for('backup.index'))

    seestar_usb_status["running"] = True
    seestar_usb_status["last_result"] = "A detetar telescópio..."
    
    thread = threading.Thread(
        target=run_seestar_usb_task,
        args=(current_app.app_context(), current_user.id)
    )
    thread.daemon = True
    thread.start()
    
    flash('Ligação e transferência do Seestar USB iniciada em segundo plano.', 'info')
    return redirect(url_for('backup.index'))
