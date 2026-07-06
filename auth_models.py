from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
import enum
import os

# Основная база данных для авторизации и управления пользователями
AUTH_DATABASE_URL = os.environ.get("DATABASE_URL")
auth_engine = create_engine(AUTH_DATABASE_URL)
AuthSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=auth_engine)
AuthBase = declarative_base()

class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"

class UserStatus(enum.Enum):
    PENDING = "pending"    # Ожидает одобрения
    ACTIVE = "active"      # Активен
    SUSPENDED = "suspended" # Заблокирован

class AuthUser(AuthBase):
    """Пользователи в основной базе данных"""
    __tablename__ = 'auth_users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Роли и статусы
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING, nullable=False)
    
    # Имя базы данных пользователя
    database_name = Column(String(100), unique=True, nullable=True)
    
    # Метаданные
    full_name = Column(String(200), nullable=True)
    organization = Column(String(200), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(Integer, nullable=True)  # ID админа, который одобрил
    
    def set_password(self, password):
        """Устанавливает хеш пароля"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Проверяет пароль"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Проверяет, является ли пользователь администратором"""
        return self.role == UserRole.ADMIN
    
    def is_active(self):
        """Проверяет, активен ли пользователь"""
        return self.status == UserStatus.ACTIVE
    
    def __repr__(self):
        return f'<AuthUser {self.username}>'

def get_auth_session():
    """Получить сессию для работы с основной базой данных"""
    return AuthSessionLocal()

def create_auth_tables():
    """Создать таблицы в основной базе данных"""
    AuthBase.metadata.create_all(bind=auth_engine)

def init_admin_user():
    """Инициализировать админа при первом запуске"""
    session = get_auth_session()
    try:
        # Проверяем, есть ли уже админ
        admin = session.query(AuthUser).filter_by(username='admin').first()
        if not admin:
            admin = AuthUser(
                username='admin',
                email='admin@flowercrm.local',
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
                database_name='main',  # Основная база данных
                full_name='Администратор системы',
                organization='Flower CRM',
                approved_at=datetime.utcnow()
            )
            admin.set_password('dancerboy')
            session.add(admin)
            session.commit()
            print("Создан администратор системы: admin/dancerboy")
        return admin
    finally:
        session.close()