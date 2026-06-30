# SPDX-License-Identifier: GPL-2.0-only
from cryptography.fernet import Fernet
from flask import current_app
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# A chave deve ser persistente. Usamos o SECRET_KEY da app como base ou uma variável específica.
# Nota: Fernet exige uma chave de 32 bytes em base64.
import base64
import os
from hashlib import sha256

def get_cipher_key():
    secret = os.getenv('FERNET_KEY') or os.getenv('SECRET_KEY', 'dev-secret-key')
    # Garante que temos 32 bytes para o Fernet
    key_bytes = sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(key_bytes)

cipher = Fernet(get_cipher_key())

# Gestão de sessão de utilizador
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class AppConfig(db.Model):
    __tablename__ = 'app_configs'
    key = db.Column(db.String(128), primary_key=True)
    value = db.Column(db.String(512))

class Location(db.Model):
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    elevation = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    default_location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=True)
    default_location = db.relationship('Location', foreign_keys=[default_location_id])

    # Definições personalizadas do utilizador
    _astrometry_api_key = db.Column(db.String(256))
    telescopius_base_url = db.Column(db.String(256), default='https://telescopius.com')
    avatar_filename = db.Column(db.String(256), nullable=True)



    @property
    def astrometry_api_key(self):
        if not self._astrometry_api_key: return None
        return cipher.decrypt(self._astrometry_api_key.encode()).decode()

    @astrometry_api_key.setter
    def astrometry_api_key(self, value):
        if not value: self._astrometry_api_key = None
        else: self._astrometry_api_key = cipher.encrypt(value.encode()).decode()

    # Relações: um utilizador pode ter várias imagens e observações
    images = db.relationship('GalleryImage', backref='author', lazy='dynamic')
    observations = db.relationship('Observation', backref='observer', lazy='dynamic')

    def set_password(self, password):
        """Hasheia a palavra-passe para armazenamento seguro."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica a palavra-passe fornecida contra o hash armazenado."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class GalleryImage(db.Model):
    __tablename__ = 'gallery_images'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    title = db.Column(db.String(256))
    description = db.Column(db.Text)
    filepath = db.Column(db.String(512), nullable=False)
    thumb_path = db.Column(db.String(512))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Dados de resolução astrométrica (Plate Solve)
    ra = db.Column(db.Float)  # Ascensão Reta em graus
    dec = db.Column(db.Float)  # Declinação em graus
    plate_solved = db.Column(db.Boolean, default=False)  # Indica se a imagem foi resolvida astrometricamente
    astrometry_job_id = db.Column(db.String(64))  # ID da tarefa no astrometry.net (se aplicável)
    
    # Metadados específicos do Seestar ou ficheiros FITS
    target_name = db.Column(db.String(128))  # Nome do objeto alvo (ex: M42)
    exposure_time = db.Column(db.Float)  # Tempo de exposição em segundos
    gain = db.Column(db.Integer)  # Ganho utilizado na captura
    captured_at = db.Column(db.DateTime)  # Data e hora reais da captura da imagem
    
    # Estado de sincronização/backup externa (ex: rclone)
    backup_status = db.Column(db.Boolean, default=False)
    
    # Relação com Observação: uma imagem pode pertencer a uma observação específica
    observation_id = db.Column(db.Integer, db.ForeignKey('observations.id'), nullable=True)

    def __repr__(self):
        return f'<GalleryImage {self.filename}>'


class Observation(db.Model):
    __tablename__ = 'observations'

    id = db.Column(db.Integer, primary_key=True)
    target = db.Column(db.String(128), nullable=False)
    notes = db.Column(db.Text)
    observed_at = db.Column(db.DateTime)
    ra = db.Column(db.Float)
    dec = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relação: uma observação pode ter várias imagens associadas
    images = db.relationship('GalleryImage', backref='observation', lazy='dynamic')

    def __repr__(self):
        return f'<Observation {self.target}>'


class CelestialObject(db.Model):
    __tablename__ = 'celestial_objects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    ra = db.Column(db.Float, nullable=False)  # Ascensão Reta em horas (formato float)
    dec = db.Column(db.Float, nullable=False) # Declinação em graus (formato float)
    category = db.Column(db.String(64), default='DSO') # DSO, Star, Planet, Comet, Asteroid
    description = db.Column(db.Text)

    def __repr__(self):
        return f'<CelestialObject {self.name}>'

