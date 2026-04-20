from flask import Blueprint, render_template
from flask_login import login_required
from app.models import GalleryImage, Observation

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    image_count = GalleryImage.query.count()
    obs_count = Observation.query.count()
    recent_images = GalleryImage.query.order_by(GalleryImage.created_at.desc()).limit(6).all()
    return render_template('dashboard/index.html',
                           image_count=image_count,
                           obs_count=obs_count,
                           recent_images=recent_images)
