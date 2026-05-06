# SPDX-License-Identifier: GPL-2.0-only
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import AppConfig, Location, User

config_bp = Blueprint('config', __name__)

def update_app_config(key, value):
    config = AppConfig.query.filter_by(key=key).first()
    if not config:
        config = AppConfig(key=key, value=value)
        db.session.add(config)
    else:
        config.value = value

@config_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        # Atualizar Perfil
        current_user.username = request.form.get('username', current_user.username)
        
        # Atualizar Password se fornecida
        new_password = request.form.get('new_password')
        if new_password:
            current_user.set_password(new_password)
            
        # Atualizar APIs (Algumas no user, outras nas configs globais)
        current_user.astrometry_api_key = request.form.get('astrometry_key', current_user.astrometry_api_key)
        
        update_app_config('SEESTAR_IMPORT_PATH', request.form.get('seestar_path'))
        update_app_config('RCLONE_REMOTE', request.form.get('rclone_remote'))
        update_app_config('RCLONE_PATH', request.form.get('rclone_path'))

        # Location
        loc_name = request.form.get('loc_name')
        if loc_name:
            new_loc = Location(name=loc_name, 
                               latitude=float(request.form.get('lat', 0)), 
                               longitude=float(request.form.get('lon', 0)),
                               elevation=float(request.form.get('elev', 0)),
                               user_id=current_user.id)
            db.session.add(new_loc)
            db.session.commit()
            current_user.default_location_id = new_loc.id
        
        db.session.commit()
        flash('Configurações atualizadas com sucesso.', 'success')
        return redirect(url_for('config.index'))
    
    locations = Location.query.filter_by(user_id=current_user.id).all()
    configs = {c.key: c.value for c in AppConfig.query.all()}
    return render_template('config/index.html', locations=locations, configs=configs)
