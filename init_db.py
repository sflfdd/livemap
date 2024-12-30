from app import app, db
import os

def init_db():
    # Remove existing database if it exists
    db_path = 'livemap.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Removed existing database")
    
    # Create new database
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    init_db()
