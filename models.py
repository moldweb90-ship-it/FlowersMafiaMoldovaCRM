from app import db
from sqlalchemy import event
from sqlalchemy.orm import Session
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    full_name = db.Column(db.String(200), nullable=True)
    organization = db.Column(db.String(200), nullable=True)
    
    # Роль и статус пользователя
    role = db.Column(db.String(20), default='user', nullable=False)  # 'admin' или 'user'
    status = db.Column(db.String(20), default='pending', nullable=False)  # 'pending', 'active', 'suspended'
    
    # Метаданные одобрения
    approved_at = db.Column(db.DateTime, nullable=True)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """Устанавливает хеш пароля"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Проверяет пароль"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Проверяет, является ли пользователь администратором"""
        return self.role == 'admin'
    
    def is_active_user(self):
        """Проверяет, активен ли пользователь"""
        return self.status == 'active'
    
    def can_manage_users(self):
        """Проверяет, может ли пользователь управлять другими пользователями"""
        return self.is_admin()
    
    def __repr__(self):
        return f'<User {self.username}>'

class Flower(db.Model):
    __tablename__ = 'flowers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationship to bouquet compositions
    compositions = db.relationship('BouquetComposition', back_populates='flower', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Flower {self.name}>'

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationship to bouquets
    bouquets = db.relationship('Bouquet', back_populates='category')
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Bouquet(db.Model):
    __tablename__ = 'bouquets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    final_price = db.Column(db.Float, nullable=False, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    published = db.Column(db.Boolean, nullable=False, default=True)
    
    # Relationships
    category = db.relationship('Category', back_populates='bouquets')
    compositions = db.relationship('BouquetComposition', back_populates='bouquet', cascade='all, delete-orphan')
    
    def calculate_price(self):
        """Calculate the final price of the bouquet"""
        # Get global settings (now these are system-wide settings)
        delivery_cost_value = GlobalSetting.get_value('delivery_cost', None, '500')
        markup_percentage_value = GlobalSetting.get_value('markup_percentage', None, '17')
        
        delivery_cost = float(delivery_cost_value) if delivery_cost_value else 500.0
        markup_percentage = float(markup_percentage_value) if markup_percentage_value else 17.0
        
        # Calculate base cost from flowers
        base_cost = sum(comp.quantity * comp.flower.price_per_unit for comp in self.compositions)
        
        # Add delivery cost
        total_with_delivery = base_cost + delivery_cost
        
        # Apply markup
        final_price = total_with_delivery * (1 + markup_percentage / 100)
        
        # Round to nearest 10
        return round(final_price / 10) * 10
    
    def update_price(self):
        """Update the stored final price"""
        self.final_price = self.calculate_price()
    
    def __repr__(self):
        return f'<Bouquet {self.name}>'

class BouquetComposition(db.Model):
    __tablename__ = 'bouquet_composition'
    
    id = db.Column(db.Integer, primary_key=True)
    bouquet_id = db.Column(db.Integer, db.ForeignKey('bouquets.id'), nullable=False)
    flower_id = db.Column(db.Integer, db.ForeignKey('flowers.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    
    # Relationships
    bouquet = db.relationship('Bouquet', back_populates='compositions')
    flower = db.relationship('Flower', back_populates='compositions')
    
    def __repr__(self):
        return f'<BouquetComposition {self.bouquet.name} - {self.flower.name}>'

class GlobalSetting(db.Model):
    __tablename__ = 'global_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), nullable=False)
    value = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Null for global settings
    
    @staticmethod
    def get_value(key, user_id=None, default=None):
        """Get a setting value by key for a specific user or global setting"""
        from flask_login import current_user
        
        # Global settings like delivery_cost and markup_percentage
        if key in ['delivery_cost', 'markup_percentage', 'site_sync_endpoint', 'site_sync_token']:
            setting = GlobalSetting.query.filter_by(key=key, user_id=None).first()
            return setting.value if setting else default
        
        # User-specific settings
        if not user_id and current_user.is_authenticated:
            user_id = current_user.id
        setting = GlobalSetting.query.filter_by(key=key, user_id=user_id).first()
        return setting.value if setting else default
    
    @staticmethod
    def set_value(key, value, user_id=None):
        """Set a setting value by key for a specific user or global setting"""
        from flask_login import current_user
        
        # Global settings like delivery_cost and markup_percentage
        if key in ['delivery_cost', 'markup_percentage', 'site_sync_endpoint', 'site_sync_token']:
            setting = GlobalSetting.query.filter_by(key=key, user_id=None).first()
            if setting:
                setting.value = str(value)
            else:
                setting = GlobalSetting(key=key, value=str(value), user_id=None)
                db.session.add(setting)
            db.session.commit()
            return setting
        
        # User-specific settings
        if not user_id and current_user.is_authenticated:
            user_id = current_user.id
        setting = GlobalSetting.query.filter_by(key=key, user_id=user_id).first()
        if setting:
            setting.value = str(value)
        else:
            setting = GlobalSetting(key=key, value=str(value), user_id=user_id)
            db.session.add(setting)
        db.session.commit()
        return setting
    
    def __repr__(self):
        return f'<GlobalSetting {self.key}: {self.value}>'

def recalculate_bouquet_prices(bouquet_ids=None):
    """
    Recalculate bouquet prices using a single SQL UPDATE statement.
    
    Args:
        bouquet_ids: Optional list of bouquet IDs to update. If None, updates ALL bouquets.
    
    Returns:
        Number of bouquets updated
    """
    from sqlalchemy import text
    
    # Get global settings
    delivery_cost = float(GlobalSetting.get_value('delivery_cost', None, '500'))
    markup_percentage = float(GlobalSetting.get_value('markup_percentage', None, '17'))
    
    # Build the SQL query
    if bouquet_ids:
        # Update only specific bouquets
        bouquet_id_list = ','.join(str(id) for id in bouquet_ids)
        sql = text(f"""
            UPDATE bouquets
            SET final_price = ROUND((COALESCE(base_costs.base_cost, 0) + :delivery_cost) * (1 + :markup_percentage / 100) / 10) * 10
            FROM (
                SELECT 
                    bc.bouquet_id,
                    SUM(bc.quantity * f.price_per_unit) as base_cost
                FROM bouquet_composition bc
                JOIN flowers f ON bc.flower_id = f.id
                WHERE bc.bouquet_id IN ({bouquet_id_list})
                GROUP BY bc.bouquet_id
            ) as base_costs
            WHERE bouquets.id = base_costs.bouquet_id
        """)
    else:
        # Update ALL bouquets
        sql = text("""
            UPDATE bouquets
            SET final_price = ROUND((COALESCE(base_costs.base_cost, 0) + :delivery_cost) * (1 + :markup_percentage / 100) / 10) * 10
            FROM (
                SELECT 
                    bc.bouquet_id,
                    SUM(bc.quantity * f.price_per_unit) as base_cost
                FROM bouquet_composition bc
                JOIN flowers f ON bc.flower_id = f.id
                GROUP BY bc.bouquet_id
            ) as base_costs
            WHERE bouquets.id = base_costs.bouquet_id
        """)
    
    # Execute the update
    result = db.session.execute(sql, {'delivery_cost': delivery_cost, 'markup_percentage': markup_percentage})
    db.session.commit()
    
    return result.rowcount

# Event listeners for automatic price recalculation
@event.listens_for(Flower.price_per_unit, 'set')
def recalculate_bouquet_prices_on_flower_price_change(target, value, oldvalue, initiator):
    """Recalculate bouquet prices when a flower price changes"""
    if value != oldvalue and target.id:  # Only if price actually changed and flower exists
        try:
            # Get IDs of all bouquets that use this flower
            bouquet_ids = db.session.query(Bouquet.id).join(BouquetComposition).filter(
                BouquetComposition.flower_id == target.id
            ).all()
            
            if bouquet_ids:
                bouquet_ids_list = [bid[0] for bid in bouquet_ids]
                # Use SQL-based recalculation for affected bouquets
                recalculate_bouquet_prices(bouquet_ids_list)
        except Exception as e:
            print(f"Error recalculating bouquet prices after flower price change: {e}")

@event.listens_for(BouquetComposition.quantity, 'set')
def recalculate_bouquet_price_on_composition_change(target, value, oldvalue, initiator):
    """Recalculate bouquet price when composition quantity changes"""
    if value != oldvalue and target.bouquet_id:
        try:
            # Recalculate only the affected bouquet
            recalculate_bouquet_prices([target.bouquet_id])
        except Exception as e:
            print(f"Error recalculating bouquet price after composition change: {e}")
