# SPDX-License-Identifier: GPL-2.0-only
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import GalleryImage, Observation
from app.backup.routes import backup_status
from app.planner.routes import CATALOG, load_sky, ts, earth
from skyfield.api import Topos, Star
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    # Contagens e dados básicos
    image_count = GalleryImage.query.filter_by(user_id=current_user.id).count()
    images_no_backup = GalleryImage.query.filter_by(user_id=current_user.id, backup_status=False).all()
    obs_count = Observation.query.filter_by(user_id=current_user.id).count()
    
    # Itens recentes
    recent_images = GalleryImage.query.filter_by(user_id=current_user.id).order_by(GalleryImage.created_at.desc()).limit(4).all()
    recent_observations = Observation.query.filter_by(user_id=current_user.id).order_by(Observation.observed_at.desc()).limit(4).all()
    
    # Objetos visíveis agora (top 3 do planeador)
    lat = 38.7169 # Lisboa por defeito
    lon = -9.1395
    observer = earth + Topos(latitude_degrees=lat, longitude_degrees=lon)
    now_ts = ts.now()
    
    visible_now = []
    for obj in CATALOG[:5]: # Verificar apenas os primeiros 5 para performance no dashboard
        star = Star(ra_hours=obj['ra'], dec_degrees=obj['dec'])
        alt, az, dist = observer.at(now_ts).observe(star).apparent().altaz()
        if alt.degrees > 10:
            visible_now.append({"name": obj['name'], "alt": f"{alt.degrees:.1f}°"})
    
    return render_template('dashboard/index.html',
                           image_count=image_count,
                           images_no_backup=images_no_backup,
                           obs_count=obs_count,
                           recent_images=recent_images,
                           recent_observations=recent_observations,
                           visible_now=visible_now,
                           backup_status=backup_status)
