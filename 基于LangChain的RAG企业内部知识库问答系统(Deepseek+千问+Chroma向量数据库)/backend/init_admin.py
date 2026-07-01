"""初始化管理员账号"""
from app import create_app, db
from app.models import User
from app.utils.auth import generate_password

def init_admin():
    app = create_app()
    with app.app_context():
        existing = User.query.filter_by(username='admin').first()
        if existing:
            if existing.role != 'admin':
                existing.role = 'admin'
                db.session.commit()
            print(f'Admin user already exists (role: {existing.role})')
            return

        admin = User(
            username='admin',
            password=generate_password('123456'),
            email='admin@example.com',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print('Admin user created: admin / 123456')

if __name__ == '__main__':
    init_admin()
