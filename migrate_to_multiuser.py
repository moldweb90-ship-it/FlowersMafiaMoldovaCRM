#!/usr/bin/env python3
"""
Скрипт миграции для добавления многопользовательской поддержки
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect
from datetime import datetime

def run_migration():
    """Выполняет миграцию базы данных для поддержки многопользовательности"""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("Ошибка: не установлена переменная DATABASE_URL")
        sys.exit(1)
    
    engine = create_engine(database_url)
    inspector = inspect(engine)
    
    print("Начинаем миграцию базы данных...")
    
    with engine.connect() as conn:
        # Начинаем транзакцию
        trans = conn.begin()
        
        try:
            # Проверяем текущую структуру таблицы users
            columns = [col['name'] for col in inspector.get_columns('users')]
            print(f"Текущие столбцы в таблице users: {columns}")
            
            # Добавляем новые столбцы, если их нет
            if 'email' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR(120)"))
                print("Добавлен столбец: email")
            
            if 'full_name' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN full_name VARCHAR(200)"))
                print("Добавлен столбец: full_name")
            
            if 'organization' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN organization VARCHAR(200)"))
                print("Добавлен столбец: organization")
            
            if 'role' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user' NOT NULL"))
                print("Добавлен столбец: role")
            
            if 'status' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'pending' NOT NULL"))
                print("Добавлен столбец: status")
            
            if 'approved_at' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN approved_at TIMESTAMP"))
                print("Добавлен столбец: approved_at")
            
            if 'approved_by' not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN approved_by INTEGER REFERENCES users(id)"))
                print("Добавлен столбец: approved_by")
            
            # Обновляем существующего пользователя admin
            result = conn.execute(text("SELECT id FROM users WHERE username = 'admin'"))
            admin_user = result.fetchone()
            
            if admin_user:
                # Обновляем роль и статус админа
                conn.execute(text("""
                    UPDATE users 
                    SET role = 'admin', 
                        status = 'active',
                        email = 'admin@flowercrm.local',
                        full_name = 'Администратор системы',
                        organization = 'Flower CRM',
                        approved_at = :approved_at
                    WHERE username = 'admin'
                """), {"approved_at": datetime.utcnow()})
                print("Обновлен пользователь admin с правами администратора")
            
            # Добавляем user_id ко всем основным таблицам для разделения данных
            
            # Flowers
            if 'user_id' not in [col['name'] for col in inspector.get_columns('flowers')]:
                conn.execute(text("ALTER TABLE flowers ADD COLUMN user_id INTEGER REFERENCES users(id)"))
                # Привязываем все существующие цветы к админу
                if admin_user:
                    conn.execute(text("UPDATE flowers SET user_id = :admin_id"), {"admin_id": admin_user[0]})
                print("Добавлен user_id в таблицу flowers")
            
            # Categories
            if 'user_id' not in [col['name'] for col in inspector.get_columns('categories')]:
                conn.execute(text("ALTER TABLE categories ADD COLUMN user_id INTEGER REFERENCES users(id)"))
                # Привязываем все существующие категории к админу
                if admin_user:
                    conn.execute(text("UPDATE categories SET user_id = :admin_id"), {"admin_id": admin_user[0]})
                print("Добавлен user_id в таблицу categories")
            
            # Bouquets
            if 'user_id' not in [col['name'] for col in inspector.get_columns('bouquets')]:
                conn.execute(text("ALTER TABLE bouquets ADD COLUMN user_id INTEGER REFERENCES users(id)"))
                # Привязываем все существующие букеты к админу
                if admin_user:
                    conn.execute(text("UPDATE bouquets SET user_id = :admin_id"), {"admin_id": admin_user[0]})
                print("Добавлен user_id в таблицу bouquets")
            
            # Global Settings - делаем персональными
            if 'user_id' not in [col['name'] for col in inspector.get_columns('global_settings')]:
                conn.execute(text("ALTER TABLE global_settings ADD COLUMN user_id INTEGER REFERENCES users(id)"))
                # Привязываем все существующие настройки к админу
                if admin_user:
                    conn.execute(text("UPDATE global_settings SET user_id = :admin_id"), {"admin_id": admin_user[0]})
                print("Добавлен user_id в таблицу global_settings")
            
            # Коммитим все изменения
            trans.commit()
            print("✅ Миграция успешно завершена!")
            print(f"Пользователь 'admin' теперь имеет роль администратора")
            print("Все существующие данные привязаны к администратору")
            
        except Exception as e:
            # Откатываем изменения при ошибке
            trans.rollback()
            print(f"❌ Ошибка при миграции: {e}")
            sys.exit(1)

if __name__ == "__main__":
    run_migration()