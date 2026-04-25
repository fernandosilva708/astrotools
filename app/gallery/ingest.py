# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
from datetime import datetime
from app import db
from app.models import GalleryImage
from astropy.io import fits
import os

SEESTAR_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.fits', '.fit'}


def extract_fits_metadata(filepath: str) -> dict:
    """Extrai metadados relevantes de um ficheiro FITS.

    Esta função procede à abertura do cabeçalho FITS e à extração seletiva
    de chaves pertinentes (alvo, tempo de exposição), minimizando o consumo
    de recursos de memória, crucial para a arquitetura de baixo desempenho
    do Raspberry Pi 2.
    """
    metadata = {'target_name': None, 'exposure_time': None, 'gain': None}
    try:
        with fits.open(filepath, memmap=True) as hdul:
            header = hdul[0].header
            metadata['target_name'] = header.get('OBJECT', None)
            metadata['exposure_time'] = header.get('EXPTIME', None)
            metadata['gain'] = header.get('GAIN', None)
    except Exception:
        # Em caso de falha na leitura, prosseguimos sem os metadados.
        pass
    return metadata


def ingest_seestar_folder(folder_path: str, user_id: int, limit: int = 50) -> int:
    """Analisa uma pasta do Seestar e importa imagens de forma eficiente.

    Otimizado para Raspberry Pi 2:
    - Verifica duplicados um a um para poupar RAM.
    - Commits parciais a cada 10 imagens.
    - Extração de metadados FITS.
    """
    folder = Path(folder_path)
    if not folder.is_dir():
        return 0

    count = 0
    new_images_in_batch = 0

    try:
        for filepath in folder.rglob('*'):
            if count >= limit:
                break

            if filepath.suffix.lower() not in SEESTAR_EXTENSIONS:
                continue

            exists = db.session.query(GalleryImage.id).filter_by(
                filename=filepath.name,
                user_id=user_id
            ).first() is not None

            if exists:
                continue

            # Extração de metadados se o ficheiro for FITS
            metadata = {}
            if filepath.suffix.lower() in {'.fits', '.fit'}:
                metadata = extract_fits_metadata(str(filepath))

            image = GalleryImage(
                filename=filepath.name,
                title=filepath.stem,
                filepath=str(filepath),
                user_id=user_id,
                captured_at=datetime.fromtimestamp(filepath.stat().st_mtime),
                **metadata
            )
            db.session.add(image)
            count += 1
            new_images_in_batch += 1

            if new_images_in_batch >= 10:
                db.session.commit()
                new_images_in_batch = 0

        if new_images_in_batch > 0:
            db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return count
