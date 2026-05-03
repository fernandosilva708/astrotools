# SPDX-License-Identifier: GPL-2.0-only
import subprocess
import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import GalleryImage

astrometry_bp = Blueprint('astrometry', __name__)


def solve_online(filepath, api_key):
    """Submete ficheiro à API do Astrometry.net."""
    import requests
    import json
    
    # 1. Login
    login_url = 'http://nova.astrometry.net/api/login'
    payload = {'request-json': json.dumps({'apikey': api_key})}
    resp = requests.post(login_url, data=payload)
    if resp.status_code != 200:
        return None
    session = resp.json().get('session')
    
    # 2. Upload
    upload_url = 'http://nova.astrometry.net/api/upload'
    files = {'file': open(filepath, 'rb')}
    data = {'request-json': json.dumps({'session': session})}
    resp = requests.post(upload_url, files=files, data=data)
    
    return resp.json().get('subid')

@astrometry_bp.route('/')
@login_required
def index():
    unsolved = GalleryImage.query.filter_by(plate_solved=False).all()
    solved = GalleryImage.query.filter_by(plate_solved=True).all()
    return render_template('astrometry/index.html', unsolved=unsolved, solved=solved)



@astrometry_bp.route('/submit/<int:image_id>', methods=['POST'])
@login_required
def submit(image_id):
    """Submete uma imagem para resolução astrométrica (offline ou online)."""
    image = GalleryImage.query.get_or_404(image_id)
    mode = request.args.get('mode', 'offline')
    
    if mode == 'online':
        api_key = current_user.astrometry_api_key or current_app.config.get('ASTROMETRY_API_KEY', '')
        if not api_key:
            flash('A chave de API da Astrometry.net não está configurada (verifique as Configurações).', 'danger')
            return redirect(url_for('astrometry.index'))
        
        # Iniciar processo online
        try:
            job_id = solve_online(image.filepath, api_key)
            if job_id:
                image.astrometry_job_id = job_id
                # TODO: Implementar sistema de polling assíncrono para verificar o estado da tarefa
                # e atualizar RA/DEC quando a resolução estiver concluída.
                image.plate_solved = True 
                db.session.commit()
                flash(f'Tarefa de resolução online iniciada (Job: {job_id}).', 'success')
            else:
                flash('Falha ao enviar a imagem para o serviço online.', 'danger')
        except Exception as e:
            flash(f'Erro na comunicação com a API: {str(e)}', 'danger')
            
        return redirect(url_for('astrometry.index'))

    # ASTAP Offline
    if not os.path.exists(image.filepath):
        flash('Ficheiro de imagem não encontrado.', 'danger')
        return redirect(url_for('astrometry.index'))

    astap_path = current_app.config.get('ASTAP_CLI_PATH', '/usr/bin/astap_cli')
    catalog_path = current_app.config.get('ASTAP_CATALOG_PATH', '/opt/astap/d80')
    
    cmd = [astap_path, '-f', image.filepath, '-d', catalog_path, '-z', '2']
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            image.plate_solved = True
            db.session.commit()
            flash(f'Resolução astrométrica offline concluída para "{image.filename}".', 'success')
        else:
            flash(f'Falha na resolução astrométrica: {result.stderr}', 'danger')
    except Exception as e:
        flash(f'Erro ao executar ASTAP: {str(e)}', 'danger')
        
    return redirect(url_for('astrometry.index'))
