from app import app, db
from models import Journalist

def show_journalists():
    print("\nRegistered Journalists")
    print("====================")
    
    with app.app_context():
        journalists = Journalist.query.all()
        
        if not journalists:
            print("No journalists found in database")
            return
            
        for j in journalists:
            print(f"\nJournalist Details:")
            print(f"Name: {j.name}")
            print(f"Email: {j.email}")
            print(f"Organization: {j.organization}")
            print(f"API Token: {j.api_token}")
            print("-" * 50)

if __name__ == '__main__':
    show_journalists()
