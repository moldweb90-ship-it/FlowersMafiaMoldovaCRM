import os
import logging
from datetime import timedelta

from flask import Flask, session, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
app.secret_key = 'flower-crm-super-secret-key-2024-multiuser'
print(f"Установлен secret_key: {app.secret_key[:20]}...")

# Настройки сессий для HTTP (не HTTPS)
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
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к системе необходимо войти в систему.'
login_manager.login_message_category = 'info'

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///crm.db")
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

# Глобальная переменная для хранения движка базы данных пользователя
user_db_engine = None

def get_user_db_engine():
    """Получить движок базы данных текущего пользователя"""
    return getattr(g, 'user_db_engine', None)

def set_user_db_engine(engine):
    """Установить движок базы данных для текущего пользователя"""
    g.user_db_engine = engine

# initialize the app with the extension
db.init_app(app)

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from auth_models import get_auth_session, AuthUser
    auth_session = get_auth_session()
    try:
        user = auth_session.query(AuthUser).get(int(user_id))
        return user
    except Exception as e:
        print(f"Ошибка при загрузке пользователя: {e}")
        return None
    finally:
        auth_session.close()

with app.app_context():
    # Создаем таблицы для авторизации
    from auth_models import create_auth_tables, init_admin_user
    create_auth_tables()
    
    # Import models
    import models  # noqa: F401
    
    # Create all tables in main database
    db.create_all()
    
    # Initialize admin user and migrate existing data
    admin_user = init_admin_user()
    
    # Мигрируем существующие данные в базу администратора
    from models import GlobalSetting, User
    
    # Проверяем и создаем базовые настройки для админа
    if not GlobalSetting.query.filter_by(key='delivery_cost').first():
        delivery_setting = GlobalSetting(key='delivery_cost', value='600')
        db.session.add(delivery_setting)
    
    if not GlobalSetting.query.filter_by(key='markup_percentage').first():
        markup_setting = GlobalSetting(key='markup_percentage', value='17')
        db.session.add(markup_setting)
    
    db.session.commit()
    print("Система многопользовательской авторизации инициализирована")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)