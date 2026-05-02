# SPDX-License-Identifier: GPL-2.0-only
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db

config_bp = Blueprint('config', __name__)

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
            
        # Atualizar APIs
        current_user.astrometry_api_key = request.form.get('astrometry_key', current_user.astrometry_api_key)
        current_user.telescopius_base_url = request.form.get('telescopius_url', current_user.telescopius_base_url)
        
        db.session.commit()
        flash('Configurações atualizadas com sucesso.', 'success')
        return redirect(url_for('config.index'))
    return render_template('config/index.html')
