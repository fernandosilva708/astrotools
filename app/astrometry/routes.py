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
    
    # Verificar se já existe alguma resolução em curso
    any_running = GalleryImage.query.filter(GalleryImage.astrometry_job_id.isnot(None)).first()
    if any_running:
        flash('Já existe uma em curso.', 'warning')
        return redirect(url_for('astrometry.index'))

    # Verificar se a imagem já está a ser processada
    if image.astrometry_job_id:
        flash('Esta imagem já se encontra em processo de resolução.', 'warning')
        return redirect(url_for('astrometry.index'))
        
    if mode == 'online':
        api_key = current_user.astrometry_api_key or current_app.config.get('ASTROMETRY_API_KEY', '')
        if not api_key:
            flash('A chave de API da Astrometry.net não está configurada (verifique as Configurações).', 'danger')
            return redirect(url_for('astrometry.index'))
    else:
        # ASTAP Offline
        if not os.path.exists(image.filepath):
            flash('Ficheiro de imagem não encontrado.', 'danger')
            return redirect(url_for('astrometry.index'))

    # Importar solver em background
    from app.astrometry.solver import start_solving_thread
    
    success = start_solving_thread(current_app, image.id, mode=mode)
    if success:
        if mode == 'online':
            flash('Tarefa de resolução online iniciada em segundo plano.', 'info')
        else:
            flash('Tarefa de resolução local (ASTAP) iniciada em segundo plano.', 'info')
    else:
        flash('Não foi possível iniciar a resolução astrométrica.', 'danger')
        
    return redirect(url_for('astrometry.index'))

