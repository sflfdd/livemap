from datetime import datetime
from app import db

class Event(db.Model):
    """Event model for storing map events."""
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_type = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    location_name = db.Column(db.String(200))
    source_url = db.Column(db.String(500))
    image_url = db.Column(db.String(500))
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    archived = db.Column(db.Boolean, default=False)

    def to_dict(self):
        """Convert event to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'event_type': self.event_type,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'location_name': self.location_name,
            'source_url': self.source_url,
            'image_url': self.image_url,
            'verified': self.verified,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'author': self.author.username if self.author else None,
            'archived': self.archived
        }

    def __repr__(self):
        return f'<Event {self.title}>'

class BreakingNews(db.Model):
    """Breaking news model."""
    __tablename__ = 'breaking_news'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    source = db.Column(db.String(100))
    source_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    priority = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        """Convert breaking news to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'source': self.source,
            'source_url': self.source_url,
            'created_at': self.created_at.isoformat(),
            'priority': self.priority,
            'active': self.active
        }

    def __repr__(self):
        return f'<BreakingNews {self.title}>'
