from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_journalist():
    with app.app_context():
        # حذف جميع المستخدمين الحاليين (للتجربة فقط)
        User.query.delete()
        db.session.commit()
        
        # إنشاء مستخدم جديد
        password = 'Gaza2024!'
        user = User(
            email='admin@gaza.ps',
            name='مراسل غزة',
            password_hash=generate_password_hash(password),
            is_journalist=True,
            organization='وكالة أنباء غزة',
            api_token='gaza2024'
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            print('تم إنشاء حساب الصحفي بنجاح!')
            print('===========================')
            print(f'البريد الإلكتروني: {user.email}')
            print(f'كلمة المرور: {password}')
            print(f'الاسم: {user.name}')
            print(f'المؤسسة: {user.organization}')
        except Exception as e:
            print('حدث خطأ:', str(e))
            db.session.rollback()

if __name__ == '__main__':
    create_journalist()
