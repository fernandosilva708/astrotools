# SPDX-License-Identifier: GPL-2.0-only
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Observation
from datetime import datetime

observations_bp = Blueprint('observations', __name__)

@observations_bp.route('/')
@login_required
def index():
    """Lista todas as observações do utilizador."""
    observations = Observation.query.filter_by(user_id=current_user.id).order_by(Observation.observed_at.desc()).all()
    return render_template('observations/index.html', observations=observations)

@observations_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Adiciona uma nova observação ao diário."""
    if request.method == 'POST':
        target = request.form.get('target', '').strip()
        notes = request.form.get('notes', '').strip()
        observed_at_str = request.form.get('observed_at', '')
        ra = request.form.get('ra')
        dec = request.form.get('dec')
        
        if not target:
            flash('O nome do alvo é obrigatório.', 'warning')
            return redirect(url_for('observations.add'))
            
        try:
            observed_at = datetime.strptime(observed_at_str, '%Y-%m-%dT%H:%M') if observed_at_str else datetime.utcnow()
            
            obs = Observation(
                target=target,
                notes=notes,
                observed_at=observed_at,
                ra=float(ra) if ra else None,
                dec=float(dec) if dec else None,
                user_id=current_user.id
            )
            db.session.add(obs)
            db.session.commit()
            flash('Observação registada com sucesso.', 'success')
            return redirect(url_for('observations.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao guardar observação: {str(e)}', 'danger')
            
    return render_template('observations/add.html', now=datetime.utcnow().strftime('%Y-%m-%dT%H:%M'))

@observations_bp.route('/delete/<int:obs_id>', methods=['POST'])
@login_required
def delete(obs_id):
    """Elimina um registo de observação."""
    obs = Observation.query.get_or_404(obs_id)
    if obs.user_id != current_user.id:
        flash('Não tem permissão para eliminar esta observação.', 'danger')
        return redirect(url_for('observations.index'))
        
    db.session.delete(obs)
    db.session.commit()
    flash('Observação eliminada.', 'success')
    return redirect(url_for('observations.index'))
