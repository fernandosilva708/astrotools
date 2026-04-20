from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor inicie sessão para aceder a esta página.'
login_manager.login_message_category = 'info'


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///astrotools.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['GALLERY_UPLOAD_FOLDER'] = os.getenv('GALLERY_UPLOAD_FOLDER', 'uploads/gallery')
    app.config['SEESTAR_IMPORT_PATH'] = os.getenv('SEESTAR_IMPORT_PATH', '')
    app.config['ASTROMETRY_API_KEY'] = os.getenv('ASTROMETRY_API_KEY', '')
    app.config['ASTROMETRY_URL'] = os.getenv('ASTROMETRY_URL', 'http://nova.astrometry.net/api/')
    app.config['TELESCOPIUS_BASE_URL'] = os.getenv('TELESCOPIUS_BASE_URL', 'https://telescopius.com')
    app.config['RCLONE_REMOTE'] = os.getenv('RCLONE_REMOTE', '')
    app.config['RCLONE_PATH'] = os.getenv('RCLONE_PATH', '')

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.auth.routes import auth_bp
    from app.gallery.routes import gallery_bp
    from app.astrometry.routes import astrometry_bp
    from app.ephemeris.routes import ephemeris_bp
    from app.telescopius.routes import telescopius_bp
    from app.backup.routes import backup_bp
    from app.dashboard.routes import dashboard_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(gallery_bp, url_prefix='/gallery')
    app.register_blueprint(astrometry_bp, url_prefix='/astrometry')
    app.register_blueprint(ephemeris_bp, url_prefix='/ephemeris')
    app.register_blueprint(telescopius_bp, url_prefix='/telescopius')
    app.register_blueprint(backup_bp, url_prefix='/backup')
    app.register_blueprint(dashboard_bp)

    return app
