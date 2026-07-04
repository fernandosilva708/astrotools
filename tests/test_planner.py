# SPDX-License-Identifier: GPL-2.0-only
import pytest
from unittest.mock import patch, MagicMock
from app import db
from app.models import User, CelestialObject

@pytest.fixture
def auth_client(client, app):
    with app.app_context():
        user = User(username='planneruser', email='planner@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
    
    client.post('/auth/login', data={
        'username': 'planneruser',
        'password': 'password123'
    })
    return client

@patch('app.utils.LocationService.get_current_location')
@patch('app.planner.routes.earth')
@patch('app.planner.routes.ts')
def test_planner_index(mock_ts, mock_earth, mock_location, auth_client):
    # Mock location
    mock_loc = MagicMock()
    mock_loc.latitude = 40.0
    mock_loc.longitude = -8.0
    mock_location.return_value = mock_loc
    
    # Mock observer and altaz
    mock_observer = MagicMock()
    mock_earth.__add__.return_value = mock_observer
    
    mock_altaz = MagicMock()
    mock_altaz.degrees = 45.0
    mock_observer.at().observe().apparent().altaz.return_value = (mock_altaz, mock_altaz, None)

    response = auth_client.get('/planner/')
    assert response.status_code == 200
    assert b'45.0' in response.data  # Verifica se a altitude renderizou

@patch('app.utils.LocationService.get_current_location')
@patch('app.planner.routes.earth')
@patch('app.planner.routes.ts')
def test_planner_chart_data(mock_ts, mock_earth, mock_location, auth_client):
    # Mock location
    mock_loc = MagicMock()
    mock_loc.latitude = 40.0
    mock_loc.longitude = -8.0
    mock_location.return_value = mock_loc
    
    # Mock observer and altaz
    mock_observer = MagicMock()
    mock_earth.__add__.return_value = mock_observer
    
    mock_altaz = MagicMock()
    mock_altaz.degrees = 30.0
    mock_observer.at().observe().apparent().altaz.return_value = (mock_altaz, mock_altaz, None)

    response = auth_client.get('/planner/chart/Polaris')
    assert response.status_code == 200
    data = response.get_json()
    assert data['object'] == 'Polaris'
    assert len(data['labels']) == 13
    assert len(data['altitudes']) == 13
    assert data['altitudes'][0] == 30.0
