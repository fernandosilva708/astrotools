# SPDX-License-Identifier: GPL-2.0-only
from flask import Blueprint, render_template, flash, redirect, url_for, current_app
from flask_login import login_required
import subprocess
import threading
from datetime import datetime

backup_bp = Blueprint('backup', __name__)

# Estado global para monitorizar o backup
backup_status = {
    "running": False, 
    "last_result": "Nenhuma cópia efetuada.", 
    "last_run": None
}


def run_rclone_task(app_context, remote, path):
    """Tarefa de background para executar o rclone de forma eficiente."""
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


@backup_bp.route('/')
@login_required
def index():
    return render_template('backup/index.html', status=backup_status)


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
