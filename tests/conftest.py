import os
import pytest
from app import create_app, db as _db


@pytest.fixture
def app():
    # Save original env
    orig_db_url = os.environ.get('DATABASE_URL')
    orig_secret = os.environ.get('SECRET_KEY')
    
    # Set testing env
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['SECRET_KEY'] = 'test-secret'
    
    app = create_app()
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
    })
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()
        
    # Restore original env
    if orig_db_url is not None:
        os.environ['DATABASE_URL'] = orig_db_url
    else:
        os.environ.pop('DATABASE_URL', None)
        
    if orig_secret is not None:
        os.environ['SECRET_KEY'] = orig_secret
    else:
        os.environ.pop('SECRET_KEY', None)


@pytest.fixture
def client(app):
    return app.test_client()
