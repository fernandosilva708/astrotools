import pytest
from app.gallery.ingest import extract_fits_metadata
from pathlib import Path
import os

# Criar um ficheiro FITS simulado muito simples para teste
def test_extract_fits_metadata_mock(tmp_path):
    from astropy.io import fits
    import numpy as np
    
    # Criar um objeto de cabeçalho simples
    hdu = fits.PrimaryHDU()
    hdu.header['OBJECT'] = 'M31'
    hdu.header['EXPTIME'] = 300.0
    hdu.header['GAIN'] = 100
    
    fits_file = tmp_path / "test.fits"
    hdu.writeto(fits_file)
    
    metadata = extract_fits_metadata(str(fits_file))
    
    assert metadata['target_name'] == 'M31'
    assert metadata['exposure_time'] == 300.0
    assert metadata['gain'] == 100
