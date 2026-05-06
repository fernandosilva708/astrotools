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
    from app.models import Observation, GalleryImage
    from datetime import datetime

    # ... (rest of routes)

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
            image_ids = request.form.getlist('image_ids') # IDs das imagens selecionadas

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

                # Associar imagens
                if image_ids:
                    images = GalleryImage.query.filter(GalleryImage.id.in_(image_ids), GalleryImage.user_id == current_user.id).all()
                    for img in images:
                        img.observation_id = obs.id
                    db.session.commit()

                flash('Observação registada com sucesso.', 'success')
                return redirect(url_for('observations.index'))
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao guardar observação: {str(e)}', 'danger')

        # Obter imagens sem observação para o utilizador
        available_images = GalleryImage.query.filter_by(user_id=current_user.id, observation_id=None).all()
        return render_template('observations/add.html', now=datetime.utcnow().strftime('%Y-%m-%dT%H:%M'), available_images=available_images)

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
