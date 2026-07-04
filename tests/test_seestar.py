# SPDX-License-Identifier: GPL-2.0-only
import pytest
from unittest.mock import patch, MagicMock
from app.seestar import SeestarController

@pytest.fixture
def seestar():
    return SeestarController(ip_address="192.168.1.100")

@patch('requests.get')
def test_get_connected(mock_get, seestar):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"Value": True, "ErrorNumber": 0}
    mock_get.return_value = mock_response

    assert seestar.get_connected() is True
    mock_get.assert_called_once()
    assert "telescope/0/connected" in mock_get.call_args[0][0]

@patch('requests.get')
def test_get_status_connected(mock_get, seestar):
    # Mock para 5 chamadas _get:
    # 1. connected
    # 2. slewing
    # 3. tracking
    # 4. rightascension
    # 5. declination
    responses = [
        {"Value": True, "ErrorNumber": 0},
        {"Value": False, "ErrorNumber": 0},
        {"Value": True, "ErrorNumber": 0},
        {"Value": 1.5, "ErrorNumber": 0},
        {"Value": 45.0, "ErrorNumber": 0},
    ]
    
    mock_get.side_effect = [
        MagicMock(status_code=200, json=lambda r=r: r) for r in responses
    ]

    status = seestar.get_status()
    assert status is not None
    assert status['connected'] is True
    assert status['slewing'] is False
    assert status['tracking'] is True
    assert status['ra'] == 1.5
    assert status['dec'] == 45.0
    assert mock_get.call_count == 5

@patch('app.seestar.SeestarController.get_connected', return_value=False)
def test_get_status_disconnected(mock_connected, seestar):
    status = seestar.get_status()
    assert status is None

@patch('requests.put')
def test_slew_to_coordinates(mock_put, seestar):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ErrorNumber": 0}
    mock_put.return_value = mock_response

    success = seestar.slew_to_coordinates(2.0, 50.0)
    assert success is True
    # Uma chamada para tracking, uma chamada para slewtocoordinatesasync
    assert mock_put.call_count == 2
    
@patch('requests.put')
def test_capture_image(mock_put, seestar):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ErrorNumber": 0}
    mock_put.return_value = mock_response

    success = seestar.capture_image(5.0)
    assert success is True
    assert mock_put.call_count == 1
    assert "camera/0/startexposure" in mock_put.call_args[0][0]

@patch('requests.put')
def test_abort_and_park(mock_put, seestar):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ErrorNumber": 0}
    mock_put.return_value = mock_response

    assert seestar.abort() is True
    assert seestar.park() is True
    assert mock_put.call_count == 2
