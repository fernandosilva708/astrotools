# SPDX-License-Identifier: GPL-2.0-only
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
    """Submete uma imagem ao astrometry.net para plate-solving.

    TODO: Implementar o fluxo completo da API do astrometry.net:
      1. POST /api/login com api_key -> chave de sessão
      2. POST /api/upload com o ficheiro de imagem -> id de submissão
      3. Consultar GET /api/submissions/{sub_id} até a lista de trabalhos não estar vazia
      4. Consultar GET /api/jobs/{job_id} até status == 'success'
      5. GET /api/jobs/{job_id}/calibration -> ra, dec, orientação, pixscale
      6. Atualizar GalleryImage: ra, dec, plate_solved=True, astrometry_job_id
    """
    image = GalleryImage.query.get_or_404(image_id)
    api_key = current_app.config.get('ASTROMETRY_API_KEY', '')
    if not api_key:
        flash('ASTROMETRY_API_KEY não está configurado no ficheiro .env.', 'danger')
        return redirect(url_for('astrometry.index'))
    flash(f'Plate-solve para "{image.filename}" ainda não está implementado.', 'info')
    return redirect(url_for('astrometry.index'))
