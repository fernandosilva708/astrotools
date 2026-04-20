from pathlib import Path
from datetime import datetime
from app import db
from app.models import GalleryImage

SEESTAR_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.fits', '.fit'}


def ingest_seestar_folder(folder_path: str, user_id: int) -> int:
    """Scan a Seestar output folder and import new images into the gallery.

    TODO: Parse Seestar FITS headers (TARGET, EXPTIME, GAIN, DATE-OBS) via astropy.io.fits.
    TODO: Generate JPEG thumbnails using Pillow and store in thumb_path.
    """
    folder = Path(folder_path)
    if not folder.is_dir():
        return 0

    existing_filenames = {
        row[0] for row in db.session.query(GalleryImage.filename).all()
    }
    count = 0

    for filepath in sorted(folder.rglob('*')):
        if filepath.suffix.lower() not in SEESTAR_EXTENSIONS:
            continue
        if filepath.name in existing_filenames:
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

    if count:
        db.session.commit()
    return count
