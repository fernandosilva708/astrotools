# SPDX-License-Identifier: GPL-2.0-only
import pytest
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

def test_ephemeris_calculate_solar_system(auth_client):
    """Testa o cálculo para um corpo do sistema solar."""
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
    assert data['target'] == 'Mars'
    assert 'ra' in data
    assert 'dec' in data
    assert 'alt' in data
    assert 'az' in data
    assert 'AU' in data['distance']

def test_ephemeris_calculate_catalog(auth_client):
    """Testa o cálculo para um objeto do catálogo estelar."""
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
    assert 'M31' in data['target']
    assert 'ra' in data
    assert 'dec' in data

def test_ephemeris_calculate_invalid_target(auth_client):
    """Testa o erro ao fornecer um alvo inexistente."""
    response = auth_client.post('/ephemeris/calculate', json={
        'target': 'ObjetoInexistente123',
        'lat': 38.7169,
        'lon': -9.1395
    })
    assert response.status_code == 404
    data = response.get_json()
    assert data['status'] == 'error'

def test_ephemeris_calculate_iss(auth_client):
    """Testa o cálculo de distância relativo à ISS."""
    response = auth_client.post('/ephemeris/calculate_iss', json={
        'target': 'mars'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert 'distance_au' in data

def test_ephemeris_calculate_iss_invalid_target(auth_client):
    """Testa o cálculo com alvo inválido para a ISS."""
    response = auth_client.post('/ephemeris/calculate_iss', json={
        'target': 'objeto_invalido'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['status'] == 'error'

def test_update_ephemeris_local(auth_client):
    """Testa o endpoint de atualização de efemérides local."""
    response = auth_client.post('/ephemeris/update_ephemeris')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
