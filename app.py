import os
import sys
import logging

# When running as main script, register ourselves as 'app' module to prevent re-import
if __name__ == '__main__':
    sys.modules['app'] = sys.modules['__main__']

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'flower-crm-super-secret-key-2024-fixed')

# Настройки сессий для HTTP (не HTTPS)
from datetime import timedelta
app.permanent_session_lifetime = timedelta(days=7)

app.config.update(
    WTF_CSRF_ENABLED=False,
    SESSION_COOKIE_SECURE=False,     # ОБЯЗАТЕЛЬНО False для HTTP!
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_NAME='flower_session'
)
print("Настройки сессий установлены для HTTP")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize Flask-Login
from flask_login import AnonymousUserMixin

class AnonymousUser(AnonymousUserMixin):
    def is_admin(self):
        return False
    
    def is_active_user(self):
        return False
    
    def can_manage_users(self):
        return False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к системе необходимо войти в систему.'
login_manager.login_message_category = 'info'
login_manager.remember_cookie_duration = 2592000  # 30 дней
login_manager.anonymous_user = AnonymousUser

# configure the database
database_uri = os.environ.get("DATABASE_URL", "sqlite:///crm.db")
app.config["SQLALCHEMY_DATABASE_URI"] = database_uri

if database_uri.startswith("sqlite"):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
else:
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_timeout": 20,
        "pool_size": 10,
        "max_overflow": 20,
        "connect_args": {
            "sslmode": "prefer",
            "connect_timeout": 10,
            "application_name": "flower_crm"
        }
    }

# initialize the app with the extension
db.init_app(app)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import User
    print(f"Загружаем пользователя с ID: {user_id} (тип: {type(user_id)})")
    try:
        # Преобразуем user_id в целое число
        user_id_int = int(user_id)
        user = User.query.get(user_id_int)
        print(f"Найден пользователь: {user.username if user else None}")
        return user
    except Exception as e:
        print(f"Ошибка при загрузке пользователя: {e}")
        return None

with app.app_context():
    # Import models and routes
    import models  # noqa: F401
    import routes  # noqa: F401
    
    # Create all tables
    db.create_all()
    
    # Initialize default settings if they don't exist
    from models import GlobalSetting, User
    
    if not GlobalSetting.query.filter_by(key='delivery_cost').first():
        delivery_setting = GlobalSetting(key='delivery_cost', value='350')
        db.session.add(delivery_setting)
    
    if not GlobalSetting.query.filter_by(key='markup_percentage').first():
        markup_setting = GlobalSetting(key='markup_percentage', value='20')
        db.session.add(markup_setting)
    
    # Create default admin user if doesn't exist
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User()
        admin_user.username = 'admin'
        admin_user.set_password('dancerboy')
        db.session.add(admin_user)
        db.session.commit()
        print(f"Создан новый пользователь admin с паролем dancerboy")
    else:
        print(f"Пользователь admin уже существует")
    
    db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
