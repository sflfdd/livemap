from app import app, db
from models import User

def check_users():
    with app.app_context():
        users = User.query.all()
        print("\nقائمة المستخدمين في قاعدة البيانات:")
        print("===================================")
        for user in users:
            print(f"الاسم: {user.name}")
            print(f"البريد الإلكتروني: {user.email}")
            print(f"صحفي: {user.is_journalist}")
            print("-----------------------------------")
