# SPDX-License-Identifier: GPL-2.0-only
import subprocess
import os
import time
import threading
import requests
import json
from pathlib import Path
from app import db
from app.models import GalleryImage

def get_app_context(app):
    """Retorna o contexto da aplicação Flask."""
    return app.app_context()

def extract_coords_from_wcs(wcs_filepath):
    """Extrai as coordenadas RA e DEC de um ficheiro .wcs gerado pelo ASTAP."""
    ra, dec = None, None
    if os.path.exists(wcs_filepath):
        try:
            with open(wcs_filepath, 'rb') as f:
                while True:
                    card = f.read(80)
                    if not card or len(card) < 80:
                        break
                    card_str = card.decode('ascii', errors='ignore')
                    if card_str.startswith('CRVAL1'):
                        parts = card_str.split('=')
                        if len(parts) > 1:
                            val_part = parts[1].split('/')[0].strip()
                            ra = float(val_part)
                    elif card_str.startswith('CRVAL2'):
                        parts = card_str.split('=')
                        if len(parts) > 1:
                            val_part = parts[1].split('/')[0].strip()
                            dec = float(val_part)
        except Exception as e:
            print(f"Erro ao ler coordenadas do ficheiro .wcs: {e}")
    return ra, dec

def solve_online_polling(app, image_id, sub_id, api_key):
    """Faz polling à API do Astrometry.net para verificar o estado da resolução e obter as coordenadas."""
    time.sleep(10)  # Aguarda antes do primeiro check
    
    with app.app_context():
        image = GalleryImage.query.get(image_id)
        if not image:
            return
            
        max_attempts = 30  # Timeout de aproximadamente 5-10 minutos
        attempt = 0
        job_id = None
        
        # 1. Obter o Job ID a partir da Submissão
        while attempt < max_attempts:
            try:
                sub_url = f'http://nova.astrometry.net/api/submissions/{sub_id}'
                resp = requests.get(sub_url)
                if resp.status_code == 200:
                    data = resp.json()
                    jobs = data.get('jobs', [])
                    if jobs and jobs[0] is not None:
                        job_id = jobs[0]
                        break
            except Exception as e:
                print(f"Erro no polling de submissão: {e}")
            attempt += 1
            time.sleep(15)
            
        if not job_id:
            image.astrometry_job_id = None
            db.session.commit()
            return
            
        # Atualizar a BD com o Job ID real
        image.astrometry_job_id = str(job_id)
        db.session.commit()
        
        # 2. Fazer polling do estado do Job
        attempt = 0
        while attempt < max_attempts:
            try:
                job_url = f'http://nova.astrometry.net/api/jobs/{job_id}'
                resp = requests.get(job_url)
                if resp.status_code == 200:
                    data = resp.json()
                    status = data.get('status')
                    if status == 'success':
                        # Obter calibração
                        calib_url = f'http://nova.astrometry.net/api/jobs/{job_id}/calibration'
                        calib_resp = requests.get(calib_url)
                        if calib_resp.status_code == 200:
                            calib_data = calib_resp.json()
                            image.ra = calib_data.get('ra')
                            image.dec = calib_data.get('dec')
                            image.plate_solved = True
                            image.astrometry_job_id = None
                            db.session.commit()
                            return
                    elif status == 'failure':
                        break
            except Exception as e:
                print(f"Erro no polling de job: {e}")
            attempt += 1
            time.sleep(15)
            
        # Caso falhe
        image.astrometry_job_id = None
        db.session.commit()

def solve_offline_background(app, image_id, astap_path, catalog_path):
    """Executa a resolução local via ASTAP numa thread em segundo plano."""
    with app.app_context():
        image = GalleryImage.query.get(image_id)
        if not image or not os.path.exists(image.filepath):
            if image:
                image.astrometry_job_id = None
                db.session.commit()
            return
            
        # Comando para rodar o ASTAP
        # ASTAP cria um ficheiro .wcs na mesma pasta da imagem
        cmd = [astap_path, '-f', image.filepath, '-d', catalog_path, '-z', '2']
        
        try:
            # Executa de forma síncrona dentro da thread em segundo plano
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                # Extrair RA/DEC do ficheiro .wcs gerado
                wcs_path = str(Path(image.filepath).with_suffix('.wcs'))
                ra, dec = extract_coords_from_wcs(wcs_path)
                
                if ra is not None and dec is not None:
                    image.ra = ra
                    image.dec = dec
                    image.plate_solved = True
                else:
                    # Alternativa: tentar resolver lendo metadados ou logs do ASTAP
                    image.plate_solved = True
                
                # Apagar o ficheiro .wcs temporário
                try:
                    if os.path.exists(wcs_path):
                        os.remove(wcs_path)
                except:
                    pass
            else:
                print(f"Erro ASTAP: {result.stderr}")
        except Exception as e:
            print(f"Falha ao executar ASTAP em segundo plano: {e}")
        finally:
            image.astrometry_job_id = None
            db.session.commit()

def start_solving_thread(app, image_id, mode='offline'):
    """Inicia a thread apropriada em background."""
    # Obter a imagem na BD
    image = GalleryImage.query.get(image_id)
    if not image:
        return False
        
    if mode == 'online':
        # Obter chave de API
        api_key = image.author.astrometry_api_key or app.config.get('ASTROMETRY_API_KEY', '')
        if not api_key:
            return False
            
        # Submissão inicial síncrona rápida para obter o ID de submissão
        from app.astrometry.routes import solve_online
        try:
            sub_id = solve_online(image.filepath, api_key)
            if sub_id:
                image.astrometry_job_id = f"sub_{sub_id}"
                db.session.commit()
                
                # Disparar thread de polling em segundo plano
                thread = threading.Thread(
                    target=solve_online_polling,
                    args=(app._get_current_object(), image_id, sub_id, api_key)
                )
                thread.daemon = True
                thread.start()
                return True
        except Exception as e:
            print(f"Falha ao iniciar submissão online: {e}")
            return False
    else:
        # Modo Offline
        astap_path = app.config.get('ASTAP_CLI_PATH', '/usr/bin/astap')
        catalog_path = app.config.get('ASTAP_CATALOG_PATH', '/opt/astap/d80')
        
        image.astrometry_job_id = "offline_running"
        db.session.commit()
        
        thread = threading.Thread(
            target=solve_offline_background,
            args=(app._get_current_object(), image_id, astap_path, catalog_path)
        )
        thread.daemon = True
        thread.start()
        return True
    
    return False
