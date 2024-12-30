from flask import Blueprint, render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from app.models.event import Event, BreakingNews
from app import cache, limiter

main = Blueprint('main', __name__)

@main.route('/')
@cache.cached(timeout=60)
def index():
    """Render main page."""
    return render_template('index.html')

@main.route('/events')
@limiter.limit("60/minute")
@cache.cached(timeout=30)
def get_events():
    """Get all events."""
    events = Event.query.filter_by(archived=False).order_by(Event.created_at.desc()).all()
    return jsonify([event.to_dict() for event in events])

@main.route('/breaking-news')
@limiter.limit("60/minute")
@cache.cached(timeout=30)
def breaking_news():
    """Get breaking news."""
    news = BreakingNews.query.filter_by(active=True).order_by(
        BreakingNews.priority.desc(),
        BreakingNews.created_at.desc()
    ).limit(5).all()
    return jsonify([news_item.to_dict() for news_item in news])

@main.route('/statistics')
@cache.cached(timeout=300)
def get_statistics():
    """Get event statistics."""
    total_events = Event.query.count()
    verified_events = Event.query.filter_by(verified=True).count()
    event_types = db.session.query(
        Event.event_type,
        db.func.count(Event.id)
    ).group_by(Event.event_type).all()
    
    return jsonify({
        'total_events': total_events,
        'verified_events': verified_events,
        'event_types': dict(event_types)
    })
