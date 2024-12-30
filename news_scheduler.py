from bs4 import BeautifulSoup
from datetime import datetime
from models import db, BreakingNews
import pytz
import requests
import threading
import time

# تكوين المنطقة الزمنية للقدس
TIMEZONE = pytz.timezone('UTC')

def fetch_aljazeera():
    try:
        response = requests.get('https://www.aljazeera.net/news/', headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'lxml')
        news_items = soup.select('.breaking-news-ticker .ticker-item')[:5]
        
        for item in news_items:
            title = item.text.strip()
            link = item.get('href', '')
            
            # تحقق من عدم وجود الخبر مسبقاً
            existing_news = BreakingNews.query.filter_by(title=title, source='الجزيرة').first()
            if not existing_news:
                news = BreakingNews(source='الجزيرة', title=title, link=link)
                db.session.add(news)
        
        db.session.commit()
    except Exception as e:
        print(f"Error fetching Al Jazeera news: {e}")

def fetch_almayadeen():
    try:
        response = requests.get('https://www.almayadeen.net/news/palestine', headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'lxml')
        news_items = soup.select('.news-item h3')[:5]
        
        for item in news_items:
            title = item.text.strip()
            link = item.find_parent('a')['href'] if item.find_parent('a') else ''
            
            existing_news = BreakingNews.query.filter_by(title=title, source='الميادين').first()
            if not existing_news:
                news = BreakingNews(source='الميادين', title=title, link=link)
                db.session.add(news)
        
        db.session.commit()
    except Exception as e:
        print(f"Error fetching Al Mayadeen news: {e}")

def fetch_channel12():
    try:
        response = requests.get('https://www.mako.co.il/news-channel12', headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'lxml')
        news_items = soup.select('.breaking-news-item')[:5]
        
        for item in news_items:
            title = item.text.strip()
            link = item.get('href', '')
            
            existing_news = BreakingNews.query.filter_by(title=title, source='القناة 12').first()
            if not existing_news:
                news = BreakingNews(source='القناة 12', title=title, link=link)
                db.session.add(news)
        
        db.session.commit()
    except Exception as e:
        print(f"Error fetching Channel 12 news: {e}")

def cleanup_old_news():
    """حذف الأخبار القديمة من قاعدة البيانات"""
    try:
        old_news = BreakingNews.query.filter_by(is_active=False).all()
        for news in old_news:
            db.session.delete(news)
        db.session.commit()
    except Exception as e:
        print(f"Error cleaning up old news: {e}")

def update_breaking_news():
    """تحديث الأخبار العاجلة من جميع المصادر"""
    fetch_aljazeera()
    fetch_almayadeen()
    fetch_channel12()
    cleanup_old_news()

def news_scheduler(app):
    """تشغيل مجدول الأخبار في خيط منفصل"""
    with app.app_context():
        while True:
            update_breaking_news()
            time.sleep(300)  # انتظر 5 دقائق

def init_scheduler(app):
    """تهيئة مجدول المهام"""
    scheduler_thread = threading.Thread(target=news_scheduler, args=(app,))
    scheduler_thread.daemon = True
    scheduler_thread.start()
    return scheduler_thread
