from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from pathlib import Path
from app import db
from app.models import GalleryImage
from app.gallery.ingest import ingest_seestar_folder

gallery_bp = Blueprint('gallery', __name__)


@gallery_bp.route('/')
@login_required
def index():
    images = GalleryImage.query.order_by(GalleryImage.created_at.desc()).all()
    return render_template('gallery/index.html', images=images)


@gallery_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files.get('image')
        if not file or file.filename == '':
            flash('Nenhum ficheiro selecionado.', 'warning')
            return redirect(request.url)
        upload_dir = Path(current_app.root_path).parent / current_app.config['GALLERY_UPLOAD_FOLDER']
        upload_dir.mkdir(parents=True, exist_ok=True)
        filepath = upload_dir / file.filename
        file.save(filepath)
        image = GalleryImage(
            filename=file.filename,
            title=request.form.get('title') or file.filename,
            description=request.form.get('description', ''),
            filepath=str(filepath),
            user_id=current_user.id,
        )
        db.session.add(image)
        db.session.commit()
        flash('Imagem carregada com sucesso.', 'success')
        return redirect(url_for('gallery.index'))
    return render_template('gallery/upload.html')


@gallery_bp.route('/ingest', methods=['POST'])
@login_required
def ingest():
    seestar_path = current_app.config.get('SEESTAR_IMPORT_PATH', '')
    if not seestar_path:
        flash('SEESTAR_IMPORT_PATH não está configurado no ficheiro .env.', 'danger')
        return redirect(url_for('gallery.index'))
    count = ingest_seestar_folder(seestar_path, current_user.id)
    flash(f'Importadas {count} nova(s) imagem(ns) da pasta do Seestar.', 'success')
    return redirect(url_for('gallery.index'))


@gallery_bp.route('/delete/<int:image_id>', methods=['POST'])
@login_required
def delete(image_id):
    image = GalleryImage.query.get_or_404(image_id)
    db.session.delete(image)
    db.session.commit()
    flash('Imagem eliminada.', 'success')
    return redirect(url_for('gallery.index'))
