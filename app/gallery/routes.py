from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory
from flask_login import login_required, current_user
from pathlib import Path
from werkzeug.utils import secure_filename
from app import db
from app.models import GalleryImage
from app.gallery.ingest import ingest_seestar_folder
import threading
import os

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.fits', '.fit', '.gif', '.webp'}

gallery_bp = Blueprint('gallery', __name__)

# Estado global simples para monitorizar a ingestão
ingest_status = {"running": False, "last_count": 0}


def run_ingest_task(app_context, path, user_id):
    """Tarefa em segundo plano para importar imagens do Seestar."""
    global ingest_status
    with app_context:
        try:
            count = ingest_seestar_folder(path, user_id, limit=50)
            ingest_status["last_count"] = count
        except Exception:
            ingest_status["last_count"] = -1
        finally:
            ingest_status["running"] = False


@gallery_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('q', '').strip()
    per_page = 12
    
    base_query = GalleryImage.query.filter_by(user_id=current_user.id)
    
    if query:
        # Filtrar por título, nome do ficheiro ou alvo
        search = f"%{query}%"
        base_query = base_query.filter(
            (GalleryImage.title.ilike(search)) | 
            (GalleryImage.filename.ilike(search)) |
            (GalleryImage.target_name.ilike(search))
        )
    
    pagination = base_query.order_by(GalleryImage.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    images = pagination.items
    
    return render_template('gallery/index.html', 
                           images=images, 
                           pagination=pagination,
                           search_query=query,
                           ingest_status=ingest_status)


@gallery_bp.route('/image/<path:filename>')
@login_required
def serve_image(filename):
    """Serve ficheiros da galeria."""
    upload_dir = Path(current_app.root_path).parent / current_app.config['GALLERY_UPLOAD_FOLDER']
    return send_from_directory(upload_dir, filename)


@gallery_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files.get('image')
        if not file or file.filename == '':
            flash('Nenhum ficheiro selecionado.', 'warning')
            return redirect(request.url)
        safe_name = secure_filename(file.filename)
        if Path(safe_name).suffix.lower() not in ALLOWED_EXTENSIONS:
            flash('Tipo de ficheiro não permitido.', 'danger')
            return redirect(request.url)
        upload_dir = Path(current_app.root_path).parent / current_app.config['GALLERY_UPLOAD_FOLDER']
        upload_dir.mkdir(parents=True, exist_ok=True)
        filepath = upload_dir / safe_name
        file.save(filepath)
        image = GalleryImage(
            filename=safe_name,
            title=request.form.get('title') or safe_name,
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
    global ingest_status
    if ingest_status["running"]:
        flash('Já existe uma importação em curso.', 'warning')
        return redirect(url_for('gallery.index'))

    seestar_path = current_app.config.get('SEESTAR_IMPORT_PATH', '')
    if not seestar_path:
        flash('SEESTAR_IMPORT_PATH não está configurado no ficheiro .env.', 'danger')
        return redirect(url_for('gallery.index'))
    
    ingest_status["running"] = True
    ingest_status["last_count"] = 0
    
    # Iniciar tarefa em segundo plano
    thread = threading.Thread(
        target=run_ingest_task,
        args=(current_app.app_context(), seestar_path, current_user.id)
    )
    thread.start()
    
    flash('Importação de imagens iniciada em segundo plano (limite: 50 imagens).', 'info')
    return redirect(url_for('gallery.index'))


@gallery_bp.route('/details/<int:image_id>', methods=['GET', 'POST'])
@login_required
def details(image_id):
    """Exibe e edita os detalhes de uma imagem."""
    image = GalleryImage.query.get_or_404(image_id)
    if request.method == 'POST':
        image.title = request.form.get('title', image.title)
        image.description = request.form.get('description', image.description)
        image.target_name = request.form.get('target_name', image.target_name)
        db.session.commit()
        flash('Detalhes atualizados com sucesso.', 'success')
        return redirect(url_for('gallery.details', image_id=image.id))
    return render_template('gallery/details.html', image=image)


@gallery_bp.route('/delete/<int:image_id>', methods=['POST'])
@login_required
def delete(image_id):
    """Elimina uma imagem da base de dados e do sistema de ficheiros."""
    image = GalleryImage.query.get_or_404(image_id)
    # Tentar apagar o ficheiro físico
    try:
        if os.path.exists(image.filepath):
            os.remove(image.filepath)
    except Exception:
        pass
    
    db.session.delete(image)
    db.session.commit()
    flash('Imagem eliminada com sucesso.', 'success')
    return redirect(url_for('gallery.index'))
