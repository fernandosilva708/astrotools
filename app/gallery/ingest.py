# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
from datetime import datetime
from app import db
from app.models import GalleryImage
import os

SEESTAR_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.fits', '.fit'}


def ingest_seestar_folder(folder_path: str, user_id: int, limit: int = 50) -> int:
    """Analisa uma pasta do Seestar e importa imagens de forma eficiente.
    
    Otimizado para Raspberry Pi 2:
    - Verifica duplicados um a um para poupar RAM.
    - Commits parciais a cada 10 imagens.
    - Limite de processamento por execução.
    """
    folder = Path(folder_path)
    if not folder.is_dir():
        return 0

    count = 0
    new_images_in_batch = 0

    try:
        # Usamos os.scandir via rglob para ser mais eficiente em termos de memória
        for filepath in folder.rglob('*'):
            if count >= limit:
                break
                
            if filepath.suffix.lower() not in SEESTAR_EXTENSIONS:
                continue

            # Verificação eficiente: pergunta à DB apenas por este ficheiro
            exists = db.session.query(GalleryImage.id).filter_by(
                filename=filepath.name, 
                user_id=user_id
            ).first() is not None

            if exists:
                continue

            image = GalleryImage(
                filename=filepath.name,
                title=filepath.stem,
                filepath=str(filepath),
                user_id=user_id,
                captured_at=datetime.fromtimestamp(filepath.stat().st_mtime),
            )
            db.session.add(image)
            count += 1
            new_images_in_batch += 1

            # Commit parcial a cada 10 imagens para libertar memória
            if new_images_in_batch >= 10:
                db.session.commit()
                new_images_in_batch = 0

        # Commit final dos restantes
        if new_images_in_batch > 0:
            db.session.commit()

    except Exception:
        db.session.rollback()
        raise
        
    return count
