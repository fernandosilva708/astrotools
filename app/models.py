from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    images = db.relationship('GalleryImage', backref='author', lazy='dynamic')
    observations = db.relationship('Observation', backref='observer', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
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
    # Plate-solve data
    ra = db.Column(db.Float)
    dec = db.Column(db.Float)
    plate_solved = db.Column(db.Boolean, default=False)
    astrometry_job_id = db.Column(db.String(64))
    # Seestar metadata
    target_name = db.Column(db.String(128))
    exposure_time = db.Column(db.Float)
    gain = db.Column(db.Integer)
    captured_at = db.Column(db.DateTime)

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

    def __repr__(self):
        return f'<Observation {self.target}>'
