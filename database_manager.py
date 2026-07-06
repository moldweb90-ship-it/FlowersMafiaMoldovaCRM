import os
import uuid
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from auth_models import get_auth_session, AuthUser, UserStatus
from models import Base, GlobalSetting
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Менеджер для создания и управления пользовательскими базами данных"""
    
    def __init__(self):
        self.main_db_url = os.environ.get("DATABASE_URL")
        # Извлекаем базовый URL без имени базы данных
        self.base_db_url = self.main_db_url.rsplit('/', 1)[0]
    
    def generate_database_name(self, username):
        """Генерирует уникальное имя базы данных для пользователя"""
        # Создаем безопасное имя базы данных
        safe_username = ''.join(c for c in username if c.isalnum() or c in '_-').lower()
        unique_id = str(uuid.uuid4()).replace('-', '')[:8]
        return f"flower_crm_{safe_username}_{unique_id}"
    
    def create_user_database(self, user_id):
        """Создает новую базу данных для пользователя"""
        auth_session = get_auth_session()
        try:
            user = auth_session.query(AuthUser).filter_by(id=user_id).first()
            if not user:
                raise ValueError(f"Пользователь с ID {user_id} не найден")
            
            if user.database_name:
                logger.info(f"База данных для пользователя {user.username} уже существует")
                return user.database_name
            
            # Генерируем имя базы данных
            db_name = self.generate_database_name(user.username)
            
            # Создаем базу данных
            admin_engine = create_engine(self.main_db_url)
            with admin_engine.connect() as conn:
                # Используем autocommit для DDL операций
                conn = conn.execution_options(autocommit=True)
                conn.execute(text(f'CREATE DATABASE "{db_name}"'))
            
            logger.info(f"Создана база данных: {db_name}")
            
            # Подключаемся к новой базе данных и создаем таблицы
            user_db_url = f"{self.base_db_url}/{db_name}"
            user_engine = create_engine(user_db_url)
            
            # Создаем все таблицы в новой базе данных
            Base.metadata.create_all(bind=user_engine)
            logger.info(f"Созданы таблицы в базе данных {db_name}")
            
            # Инициализируем базовые настройки
            self._initialize_user_settings(user_engine)
            
            # Обновляем информацию о пользователе
            user.database_name = db_name
            auth_session.commit()
            
            logger.info(f"База данных {db_name} успешно создана для пользователя {user.username}")
            return db_name
            
        except Exception as e:
            auth_session.rollback()
            logger.error(f"Ошибка при создании базы данных для пользователя {user_id}: {e}")
            raise
        finally:
            auth_session.close()
    
    def _initialize_user_settings(self, engine):
        """Инициализирует базовые настройки для нового пользователя"""
        UserSession = sessionmaker(bind=engine)
        session = UserSession()
        try:
            # Создаем базовые настройки
            settings = [
                GlobalSetting(key='delivery_cost', value='500'),
                GlobalSetting(key='markup_percentage', value='15')
            ]
            
            for setting in settings:
                session.add(setting)
            
            session.commit()
            logger.info("Инициализированы базовые настройки для нового пользователя")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Ошибка при инициализации настроек: {e}")
            raise
        finally:
            session.close()
    
    def get_user_database_url(self, username):
        """Получает URL базы данных пользователя"""
        auth_session = get_auth_session()
        try:
            user = auth_session.query(AuthUser).filter_by(username=username).first()
            if not user or not user.database_name:
                return None
            
            if user.username == 'admin':
                # Администратор использует основную базу данных
                return self.main_db_url
            
            return f"{self.base_db_url}/{user.database_name}"
        finally:
            auth_session.close()
    
    def approve_user(self, user_id, approved_by_id):
        """Одобряет пользователя и создает для него базу данных"""
        auth_session = get_auth_session()
        try:
            user = auth_session.query(AuthUser).filter_by(id=user_id).first()
            if not user:
                raise ValueError(f"Пользователь с ID {user_id} не найден")
            
            if user.status == UserStatus.ACTIVE:
                logger.info(f"Пользователь {user.username} уже активен")
                return
            
            # Создаем базу данных для пользователя
            db_name = self.create_user_database(user_id)
            
            # Обновляем статус пользователя
            user.status = UserStatus.ACTIVE
            user.approved_by = approved_by_id
            user.approved_at = datetime.utcnow()
            
            auth_session.commit()
            logger.info(f"Пользователь {user.username} одобрен и активирован")
            
        except Exception as e:
            auth_session.rollback()
            logger.error(f"Ошибка при одобрении пользователя {user_id}: {e}")
            raise
        finally:
            auth_session.close()

# Глобальный экземпляр менеджера
db_manager = DatabaseManager()