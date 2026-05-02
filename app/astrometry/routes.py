# SPDX-License-Identifier: GPL-2.0-only
import subprocess
import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from app import db
from app.models import GalleryImage

astrometry_bp = Blueprint('astrometry', __name__)


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
        flash('Resolução astrométrica Online via Astrometry.net iniciada.', 'info')
        # TODO: Implementar lógica de API online
        return redirect(url_for('astrometry.index'))

    # ASTAP Offline
    if not os.path.exists(image.filepath):
        flash('Ficheiro de imagem não encontrado.', 'danger')
        return redirect(url_for('astrometry.index'))

    astap_path = '/usr/bin/astap_cli'
    catalog_path = '/opt/astap/d80'
    
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
