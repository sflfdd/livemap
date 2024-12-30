from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, Response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Event, BreakingNews
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from functools import wraps
import jwt
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from news_scheduler import init_scheduler
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_cors import CORS
import bleach
import re

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
# Security headers
Talisman(app, content_security_policy={
    'default-src': "'self'",
    'script-src': ["'self'", "'unsafe-inline'", 'cdnjs.cloudflare.com', 'cdn.jsdelivr.net'],
    'style-src': ["'self'", "'unsafe-inline'", 'cdnjs.cloudflare.com'],
    'img-src': ["'self'", 'data:', 'https:', 'blob:'],
    'connect-src': ["'self'", 'https://nominatim.openstreetmap.org']
})

# CORS configuration
CORS(app, resources={
    r"/api/*": {"origins": ["http://localhost:*", "https://livemap.example.com"]}
})

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise ValueError("No SECRET_KEY set in environment variables")

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///livemap.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure server-side session with security
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize Flask-Limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize Flask-Cache
cache = Cache(app, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
})

# Initialize Flask-Session
from flask_session import Session
Session(app)

db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].replace('Bearer ', '')
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        user = User.query.filter_by(api_token=token).first()
        if not user:
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(user, *args, **kwargs)
    return decorated

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # قم بتعريف الإحصائيات وأنواع الأحداث
    stats = {
        'martyrs_count': 22000,  # تحديث مع البيانات الفعلية
        'destroyed_homes': 50000  # تحديث مع البيانات الفعلية
    }
    
    event_types = [
        'قصف 💥',
        'شهداء 💔',
        'مظاهرة ✊',
        'حصار 🚫',
        'اعتقال 👮',
        'مستوطنين 👥',
        'حاجز عسكري 🚧',
        'مدرسة 🏫',
        'مستشفى 🏥',
        'مسجد 🕌'
    ]
    
    return render_template('index.html', stats=stats, event_types=event_types)

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    try:
        data = request.get_json()
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing credentials'}), 400

        email = bleach.clean(data.get('email'))
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({'error': 'Invalid email format'}), 400

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, data.get('password')):
            return jsonify({'error': 'Invalid credentials'}), 401

        login_user(user)
        return jsonify({
            'message': 'Login successful',
            'token': generate_token(user.id)
        })
    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        # التحقق من عدم وجود المستخدم مسبقاً
        user = User.query.filter_by(email=email).first()
        if user:
            flash('البريد الإلكتروني مستخدم بالفعل', 'error')
            return redirect(url_for('register'))
        
        # إنشاء مستخدم جديد
        new_user = User(
            email=email,
            name=name,
            password_hash=generate_password_hash(password),
            api_token=os.urandom(24).hex()
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('تم التسجيل بنجاح! يمكنك الآن تسجيل الدخول', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('حدث خطأ أثناء التسجيل', 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    events = Event.query.filter_by(journalist_id=current_user.id)\
                       .order_by(Event.timestamp.desc())\
                       .all()
    return render_template('dashboard.html',
                         events=events)

@app.route('/regenerate-token', methods=['POST'])
@login_required
def regenerate_token():
    current_user.generate_token()
    db.session.commit()
    flash('تم إنشاء توكن جديد بنجاح!', 'success')
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'info')
    return redirect(url_for('index'))

@app.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    if request.method == 'POST':
        try:
            data = request.form
            
            # التحقق من وجود البيانات المطلوبة
            required_fields = ['latitude', 'longitude', 'eventType', 'eventDescription']
            for field in required_fields:
                if not data.get(field):
                    flash('جميع الحقول المطلوبة يجب ملؤها', 'error')
                    return redirect(url_for('add_event'))
            
            # إنشاء حدث جديد
            event = Event(
                title=data.get('locationName', ''),
                description=data.get('eventDescription'),
                event_type=data.get('eventType'),
                latitude=float(data.get('latitude')),
                longitude=float(data.get('longitude')),
                source=data.get('eventSource', ''),
                journalist_id=current_user.id
            )
            
            db.session.add(event)
            db.session.commit()
            
            flash('تم إضافة الحدث بنجاح', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء إضافة الحدث: {str(e)}', 'error')
            return redirect(url_for('add_event'))
    
    return render_template('add_event.html')

@app.route('/delete_event/<int:event_id>', methods=['DELETE'])
@login_required
def delete_event(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        if event.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'غير مصرح لك بحذف هذا الحدث'})
        
        db.session.delete(event)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/events')
@cache.cached(timeout=300)
def get_events():
    try:
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 50)), 100)  # Cap at 100 items
        offset = (page - 1) * limit
        
        events = Event.query.order_by(Event.timestamp.desc()).offset(offset).limit(limit).all()
        return jsonify([{
            'id': event.id,
            'type': bleach.clean(event.type),
            'title': bleach.clean(event.title),
            'description': bleach.clean(event.description),
            'location': event.location,
            'timestamp': event.timestamp.isoformat(),
            'source': bleach.clean(event.source)
        } for event in events])
    except Exception as e:
        app.logger.error(f"Error fetching events: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/breaking-news')
def breaking_news():
    try:
        news = BreakingNews.query.filter_by(is_active=True)\
                                .order_by(BreakingNews.date.desc())\
                                .limit(10)\
                                .all()
        return jsonify([news_item.to_dict() for news_item in news])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics')
def get_statistics():
    try:
        # إحصائيات الشهداء
        martyrs_count = Event.query.filter_by(
            type='شهداء',
            is_active=True
        ).count()
        
        # إحصائيات المنازل المدمرة
        destroyed_homes = Event.query.filter_by(
            type='هدم منازل',
            is_active=True
        ).count()
        
        # إحصائيات حسب النوع
        events_by_type = db.session.query(
            Event.type,
            db.func.count(Event.id)
        ).group_by(Event.type).all()
        
        return jsonify({
            'martyrs_count': martyrs_count,
            'destroyed_homes': destroyed_homes,
            'events_by_type': dict(events_by_type)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search')
def search_events():
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify([])
            
        # البحث في العنوان والوصف
        events = Event.query.filter(
            db.or_(
                Event.title.ilike(f'%{query}%'),
                Event.description.ilike(f'%{query}%')
            )
        ).order_by(Event.timestamp.desc()).limit(10).all()
        
        return jsonify([event.to_dict() for event in events])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# تحسين الأداء
cache = Cache(app, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
})

# تحسين الأمان
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# تطبيق حدود الطلبات على نقاط النهاية الحساسة
@limiter.limit("5 per minute")
@app.route('/api/events/add', methods=['POST'])
@login_required
def add_event_api():
    try:
        data = request.get_json()
        event = Event(
            title=data['title'],
            description=data['description'],
            event_type=data['event_type'],
            latitude=float(data['latitude']),
            longitude=float(data['longitude']),
            journalist_id=current_user.id
        )
        db.session.add(event)
        db.session.commit()
        return jsonify({'message': 'تم إضافة الحدث بنجاح'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# API Endpoints
@app.route('/api/events', methods=['POST'])
@token_required
def create_event(user):
    data = request.json
    new_event = Event(
        title=data['title'],
        description=data['description'],
        event_type=data['event_type'],
        latitude=data['latitude'],
        longitude=data['longitude'],
        user_id=user.id
    )
    
    db.session.add(new_event)
    db.session.commit()
    
    return jsonify(new_event.to_dict()), 201

@app.route('/api/events/<int:event_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def handle_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    if event.user_id != current_user.id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    if request.method == 'GET':
        return jsonify(event.to_dict())
    
    elif request.method == 'PUT':
        data = request.json
        for key, value in data.items():
            if hasattr(event, key):
                setattr(event, key, value)
        db.session.commit()
        return jsonify(event.to_dict())
    
    elif request.method == 'DELETE':
        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': 'Event deleted'})

@app.route('/api/events/stats')
def get_events_stats():
    total_events = Event.query.count()
    events_by_type = db.session.query(
        Event.event_type, 
        db.func.count(Event.id)
    ).group_by(Event.event_type).all()
    
    return jsonify({
        'total_events': total_events,
        'events_by_type': dict(events_by_type)
    })

def auto_archive_events():
    """Archive events that are older than 25 minutes"""
    cutoff_time = datetime.utcnow() - timedelta(minutes=25)
    old_events = Event.query.filter(Event.timestamp <= cutoff_time).all()
    
    for event in old_events:
        event.is_active = False
    
    db.session.commit()

# تهيئة مجدول المهام
scheduler = BackgroundScheduler()
scheduler.add_job(func=auto_archive_events, trigger="interval", minutes=5)
scheduler.start()

# تهيئة مجدول الأخبار
scheduler = init_scheduler(app)

if __name__ == '__main__':
    # تشغيل التطبيق على المنفذ 8080 والسماح بالوصول من أي عنوان IP
    app.run(debug=True, host='0.0.0.0', port=8080)
