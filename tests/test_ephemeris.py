# SPDX-License-Identifier: GPL-2.0-only
import pytest
from unittest.mock import patch, MagicMock
from app import db
from app.models import User

@pytest.fixture
def auth_client(client, app):
    """Fixture para fornecer um cliente autenticado."""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
    
    # Efetuar login
    client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'password123'
    })
    return client

def test_ephemeris_requires_login(client):
    """Verifica se o acesso às páginas requer autenticação."""
    response = client.get('/ephemeris/')
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']

    response = client.get('/ephemeris/iss')
    assert response.status_code == 302

def test_ephemeris_pages_load(auth_client):
    """Verifica se as páginas principais carregam com sucesso após autenticação."""
    response = auth_client.get('/ephemeris/')
    assert response.status_code == 200
    assert b'Efem' in response.data

    response = auth_client.get('/ephemeris/iss')
    assert response.status_code == 200
    assert b'ISS' in response.data

@patch('app.ephemeris.routes.earth')
@patch('app.ephemeris.routes.ts')
@patch('app.ephemeris.routes.get_body_object')
def test_ephemeris_calculate_solar_system(mock_get_body, mock_ts, mock_earth, auth_client):
    """Testa o cálculo para um corpo do sistema solar."""
    
    mock_body = MagicMock()
    mock_get_body.return_value = (mock_body, 'planet')
    
    mock_observer = MagicMock()
    mock_earth.__add__.return_value = mock_observer
    
    mock_astrometric = MagicMock()
    mock_observer.at().observe.return_value = mock_astrometric
    
    mock_altaz = MagicMock()
    mock_altaz.degrees = 45.0
    mock_distance = MagicMock()
    mock_distance.au = 1.5
    mock_astrometric.apparent().altaz.return_value = (mock_altaz, mock_altaz, mock_distance)
    
    mock_ra = MagicMock()
    mock_ra.hours = 12.0
    mock_dec = MagicMock()
    mock_dec.degrees = 20.0
    mock_astrometric.apparent().radec.return_value = (mock_ra, mock_dec, None)
    
    response = auth_client.post('/ephemeris/calculate', json={
        'target': 'Mars',
        'lat': 38.7169,
        'lon': -9.1395,
        'elevation': 0,
        'date': '2026-06-28'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['target'] == 'mars'
    assert 'ra' in data
    assert 'dec' in data
    assert 'alt' in data
    assert 'az' in data
    assert 'AU' in data['distance']

@patch('app.ephemeris.routes.earth')
@patch('app.ephemeris.routes.ts')
@patch('app.ephemeris.routes.get_body_object')
def test_ephemeris_calculate_catalog(mock_get_body, mock_ts, mock_earth, auth_client):
    """Testa o cálculo para um objeto do catálogo estelar."""
    
    mock_body = MagicMock()
    mock_get_body.return_value = (mock_body, 'star')

    mock_observer = MagicMock()
    mock_earth.__add__.return_value = mock_observer
    
    mock_astrometric = MagicMock()
    mock_observer.at().observe.return_value = mock_astrometric
    
    mock_altaz = MagicMock()
    mock_altaz.degrees = 45.0
    mock_distance = MagicMock()
    mock_distance.au = 1.5
    mock_astrometric.apparent().altaz.return_value = (mock_altaz, mock_altaz, mock_distance)
    
    mock_ra = MagicMock()
    mock_ra.hours = 12.0
    mock_dec = MagicMock()
    mock_dec.degrees = 20.0
    mock_astrometric.apparent().radec.return_value = (mock_ra, mock_dec, None)

    response = auth_client.post('/ephemeris/calculate', json={
        'target': 'M31',
        'lat': 38.7169,
        'lon': -9.1395,
        'elevation': 0,
        'date': '2026-06-28'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert 'm31' in data['target']
    assert 'ra' in data
    assert 'dec' in data

@patch('app.ephemeris.routes.get_body_object', return_value=(None, None))
def test_ephemeris_calculate_invalid_target(mock_get_body, auth_client):
    """Testa o erro ao fornecer um alvo inexistente."""
    response = auth_client.post('/ephemeris/calculate', json={
        'target': 'ObjetoInexistente123',
        'lat': 38.7169,
        'lon': -9.1395
    })
    assert response.status_code == 404
    data = response.get_json()
    assert data['status'] == 'error'

@patch('app.ephemeris.routes.get_iss')
@patch('app.ephemeris.routes.planets')
def test_ephemeris_calculate_iss(mock_planets, mock_get_iss, auth_client):
    """Testa o cálculo de distância relativo à ISS."""
    
    mock_iss = MagicMock()
    mock_iss.at.return_value.position.au = [1.0, 1.0, 1.0]
    mock_get_iss.return_value = mock_iss
    
    mock_mars = MagicMock()
    mock_mars.at.return_value.position.au = [2.0, 2.0, 2.0]
    mock_planets.__getitem__.return_value = mock_mars
    
    response = auth_client.post('/ephemeris/calculate_iss', json={
        'target': 'mars'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert 'distance_au' in data

@patch('app.ephemeris.routes.get_iss', return_value=None)
def test_ephemeris_calculate_iss_invalid_target(mock_get_iss, auth_client):
    """Testa o cálculo com alvo inválido para a ISS."""
    response = auth_client.post('/ephemeris/calculate_iss', json={
        'target': 'objeto_invalido'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['status'] == 'error'

@patch('app.ephemeris.routes.loader')
@patch('app.ephemeris.routes.update_mpc_data', return_value=True)
def test_update_ephemeris_local(mock_mpc, mock_loader, auth_client):
    """Testa o endpoint de atualização de efemérides local."""
    response = auth_client.post('/ephemeris/update_ephemeris')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['results']['ephem'] is True
    assert data['results']['tle'] is True
    assert data['results']['mpc'] is True
