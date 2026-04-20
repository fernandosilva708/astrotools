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
    """Submit image to astrometry.net for plate-solving.

    TODO: Implement full astrometry.net API flow:
      1. POST /api/login with api_key -> session key
      2. POST /api/upload with image file -> submission id
      3. Poll GET /api/submissions/{sub_id} until jobs list is non-empty
      4. Poll GET /api/jobs/{job_id} until status == 'success'
      5. GET /api/jobs/{job_id}/calibration -> ra, dec, orientation, pixscale
      6. Update GalleryImage: ra, dec, plate_solved=True, astrometry_job_id
    """
    image = GalleryImage.query.get_or_404(image_id)
    api_key = current_app.config.get('ASTROMETRY_API_KEY', '')
    if not api_key:
        flash('ASTROMETRY_API_KEY is not configured in .env.', 'danger')
        return redirect(url_for('astrometry.index'))
    flash(f'Plate-solve for "{image.filename}" is not yet implemented.', 'info')
    return redirect(url_for('astrometry.index'))
