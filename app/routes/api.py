from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.event import Event, BreakingNews
from app import db, limiter, cache
from app.utils.decorators import admin_required
from datetime import datetime

api = Blueprint('api', __name__)

@api.route('/events', methods=['POST'])
@login_required
@limiter.limit("10/minute")
def create_event():
    """Create new event."""
    data = request.get_json()
    
    event = Event(
        title=data.get('title'),
        description=data.get('description'),
        event_type=data.get('event_type'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        location_name=data.get('location_name'),
        source_url=data.get('source_url'),
        image_url=data.get('image_url'),
        user_id=current_user.id
    )
    
    db.session.add(event)
    db.session.commit()
    cache.delete('events')
    
    return jsonify(event.to_dict()), 201

@api.route('/events/<int:event_id>', methods=['PUT'])
@login_required
@limiter.limit("10/minute")
def update_event(event_id):
    """Update event."""
    event = Event.query.get_or_404(event_id)
    
    if event.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    for key, value in data.items():
        if hasattr(event, key):
            setattr(event, key, value)
    
    event.updated_at = datetime.utcnow()
    db.session.commit()
    cache.delete('events')
    
    return jsonify(event.to_dict())

@api.route('/events/<int:event_id>', methods=['DELETE'])
@login_required
def delete_event(event_id):
    """Delete event."""
    event = Event.query.get_or_404(event_id)
    
    if event.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(event)
    db.session.commit()
    cache.delete('events')
    
    return '', 204

@api.route('/breaking-news', methods=['POST'])
@login_required
@admin_required
@limiter.limit("5/minute")
def create_breaking_news():
    """Create breaking news."""
    data = request.get_json()
    
    news = BreakingNews(
        title=data.get('title'),
        content=data.get('content'),
        source=data.get('source'),
        source_url=data.get('source_url'),
        priority=data.get('priority', 0)
    )
    
    db.session.add(news)
    db.session.commit()
    cache.delete('breaking_news')
    
    return jsonify(news.to_dict()), 201

@api.route('/events/verify/<int:event_id>', methods=['POST'])
@login_required
@admin_required
def verify_event(event_id):
    """Verify event."""
    event = Event.query.get_or_404(event_id)
    event.verified = True
    db.session.commit()
    cache.delete('events')
    
    return jsonify(event.to_dict())
