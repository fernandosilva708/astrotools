# SPDX-License-Identifier: GPL-2.0-only
import pytest
from unittest.mock import patch, MagicMock
from app.utils import LocationService, safe_get
from app.models import User
import requests

def test_location_service_unauthenticated(app):
    with app.test_request_context():
        # current_user will be anonymous since we didn't log in
        loc = LocationService.get_current_location()
        assert loc.name == "Lisboa (Default)"
        assert loc.latitude == 38.7223
        assert loc.longitude == -9.1393
        assert loc.elevation == 45.0

@patch('app.utils.http.get')
def test_safe_get_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    resp = safe_get('http://example.com')
    assert resp.status_code == 200
    mock_get.assert_called_once_with('http://example.com', params=None, timeout=10)

@patch('app.utils.http.get')
def test_safe_get_timeout(mock_get):
    mock_get.side_effect = requests.exceptions.Timeout("Timeout")
    with pytest.raises(Exception, match="O servidor remoto demorou demasiado tempo a responder."):
        safe_get('http://example.com')

@patch('app.utils.http.get')
def test_safe_get_http_error(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_error = requests.exceptions.HTTPError("Not found")
    mock_error.response = mock_response
    
    # raise_for_status called directly when mocking side_effect on mock_get or we mock the raise
    # Wait, safe_get calls get, then raise_for_status on the response.
    mock_response.raise_for_status.side_effect = mock_error
    mock_get.return_value = mock_response

    with pytest.raises(Exception, match="Erro do serviço remoto"):
        safe_get('http://example.com')
