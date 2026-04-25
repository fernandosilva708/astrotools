# SPDX-License-Identifier: GPL-2.0-only
from flask import Blueprint, render_template
from flask_login import login_required
from app.models import GalleryImage, Observation

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    image_count = GalleryImage.query.count()
    images_no_backup = GalleryImage.query.filter_by(backup_status=False).order_by(GalleryImage.created_at.asc()).all()
    obs_count = Observation.query.count()
    recent_images = GalleryImage.query.order_by(GalleryImage.created_at.desc()).limit(6).all()
    return render_template('dashboard/index.html',
                           image_count=image_count,
                           images_no_backup=images_no_backup,
                           obs_count=obs_count,
                           recent_images=recent_images)
