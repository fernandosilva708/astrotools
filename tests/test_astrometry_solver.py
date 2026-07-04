# SPDX-License-Identifier: GPL-2.0-only
import pytest
import os
from unittest.mock import patch, mock_open, MagicMock
from app.astrometry.solver import extract_coords_from_wcs

def test_extract_coords_from_wcs_valid_file(tmp_path):
    wcs_content = b"""SIMPLE  =                    T / file does conform to FITS standard
BITPIX  =                  -64 / number of bits per data pixel
NAXIS   =                    2 / number of data axes
CRVAL1  =           13.5015690 / [deg] Coordinate value at reference point
CRVAL2  =            8.5020110 / [deg] Coordinate value at reference point
CTYPE1  = 'RA---TAN'           / TAN (gnomonic) projection
CTYPE2  = 'DEC--TAN'           / TAN (gnomonic) projection
END
"""
    # Pad out lines to 80 characters to simulate a real FITS header
    cards = wcs_content.split(b'\n')
    padded_content = b"".join([c.ljust(80, b' ') for c in cards])
    
    file_path = tmp_path / "dummy.wcs"
    file_path.write_bytes(padded_content)
    
    ra, dec = extract_coords_from_wcs(str(file_path))
        
    assert ra is not None
    assert dec is not None
    assert round(ra, 4) == 13.5016
    assert round(dec, 4) == 8.5020

def test_extract_coords_from_wcs_missing_keys(tmp_path):
    wcs_content = b"""SIMPLE  =                    T / file does conform to FITS standard
END
"""
    cards = wcs_content.split(b'\n')
    padded_content = b"".join([c.ljust(80, b' ') for c in cards])
    
    file_path = tmp_path / "dummy_missing.wcs"
    file_path.write_bytes(padded_content)
    
    ra, dec = extract_coords_from_wcs(str(file_path))
        
    assert ra is None
    assert dec is None

def test_extract_coords_from_wcs_file_not_found():
    with patch('builtins.open', side_effect=FileNotFoundError):
        ra, dec = extract_coords_from_wcs('non_existent.wcs')
        
    assert ra is None
    assert dec is None
