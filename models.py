from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import secrets
import string
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(100), nullable=False)
    organization = db.Column(db.String(100))
    api_token = db.Column(db.String(64), unique=True)
    token_created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_journalist = db.Column(db.Boolean, default=False)
    events = db.relationship('Event', backref='journalist', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_token(self):
        """Generate a new API token for the journalist"""
        # Generate a random token
        alphabet = string.ascii_letters + string.digits
        self.api_token = ''.join(secrets.choice(alphabet) for i in range(32))
        self.token_created_at = datetime.utcnow()
        return self.api_token

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'organization': self.organization,
            'email': self.email,
            'is_verified': False
        }

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    location_source = db.Column(db.String(20), nullable=False)  # 'map' or 'coordinates'
    google_maps_link = db.Column(db.String(500))
    image_url = db.Column(db.String(500))
    casualties_count = db.Column(db.Integer)
    injured_count = db.Column(db.Integer)
    source_url = db.Column(db.String(500))
    media_links = db.Column(db.Text)
    journalist_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    verified = db.Column(db.Boolean, default=False)
    is_breaking = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'event_type': self.event_type,
            'event_date': self.event_date.isoformat(),
            'latitude': self.latitude,
            'longitude': self.longitude,
            'location_source': self.location_source,
            'google_maps_link': self.google_maps_link,
            'image_url': self.image_url,
            'casualties_count': self.casualties_count,
            'injured_count': self.injured_count,
            'source_url': self.source_url,
            'media_links': self.media_links,
            'timestamp': self.timestamp.isoformat(),
            'verified': self.verified,
            'is_breaking': self.is_breaking,
            'is_active': self.is_active
        }

class BreakingNews(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(50), nullable=False)  # e.g., 'الجزيرة', 'الميادين', 'القناة 12'
    title = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(500))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'source': self.source,
            'title': self.title,
            'link': self.link,
            'date': self.date.isoformat(),
            'is_active': self.is_active
        }
