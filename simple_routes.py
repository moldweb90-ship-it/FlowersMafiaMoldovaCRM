import csv
import io
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from flask import render_template, request, redirect, url_for, flash, make_response, jsonify, session
from functools import wraps
from app import app, db
from models import Flower, Category, Bouquet, BouquetComposition, GlobalSetting, User
from forms import FlowerForm, CategoryForm, BouquetForm, GlobalSettingsForm, ExportForm, LoginForm, UserForm, RegisterForm

def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Простая проверка без сложных условий
        if form.username.data == 'admin' and form.password.data == 'dancerboy':
            session['user_id'] = 1
            session['username'] = 'admin'
            session['role'] = 'admin'
            session.permanent = True
            flash('Добро пожаловать в систему!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль', 'error')
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('Вы успешно вышли из системы', 'info')
    return redirect(url_for('login'))

@app.route('/')
def index():
    """Главная страница с полной админкой"""
    # Временно используем user_id = 1 для диагностики
    user_id = session.get('user_id', 1)
    flower_count = Flower.query.filter_by(user_id=user_id).count()
    category_count = Category.query.filter_by(user_id=user_id).count()
    bouquet_count = Bouquet.query.filter_by(user_id=user_id).count()
    recent_bouquets = Bouquet.query.filter_by(user_id=user_id).order_by(Bouquet.id.desc()).limit(10).all()
    
    return render_template('index.html', 
                         flower_count=flower_count,
                         category_count=category_count,
                         bouquet_count=bouquet_count,
                         recent_bouquets=recent_bouquets)

@app.route('/flowers')
def flowers_index():
    """List all flowers"""
    user_id = session.get('user_id', 1)
    flowers = Flower.query.filter_by(user_id=user_id).all()
    return render_template('flowers/index.html', flowers=flowers)

@app.route('/flowers/new', methods=['GET', 'POST'])
def flowers_new():
    """Create a new flower"""
    form = FlowerForm()
    if form.validate_on_submit():
        flower = Flower()
        flower.name = form.name.data
        flower.price_per_unit = form.price_per_unit.data
        flower.user_id = session['user_id']
        db.session.add(flower)
        db.session.commit()
        flash('Цветок успешно добавлен!', 'success')
        return redirect(url_for('flowers_index'))
    
    return render_template('flowers/form.html', form=form, title='Добавить цветок')

@app.route('/categories')
  
def categories_index():
    """List all categories"""
    categories = Category.query.filter_by(user_id=session['user_id']).all()
    return render_template('categories/index.html', categories=categories)

@app.route('/bouquets')

def bouquets_index():
    """List all bouquets"""
    bouquets = Bouquet.query.filter_by(user_id=session['user_id']).all()
    return render_template('bouquets/index.html', bouquets=bouquets)

@app.route('/settings')

def settings_index():
    """Global settings page"""
    form = GlobalSettingsForm()
    
    delivery_cost = GlobalSetting.get_value('delivery_cost', session['user_id'], 0.0)
    markup_percentage = GlobalSetting.get_value('markup_percentage', session['user_id'], 0.0)
    
    if request.method == 'GET':
        form.delivery_cost.data = float(delivery_cost)
        form.markup_percentage.data = float(markup_percentage)
    
    if form.validate_on_submit():
        GlobalSetting.set_value('delivery_cost', str(form.delivery_cost.data), session['user_id'])
        GlobalSetting.set_value('markup_percentage', str(form.markup_percentage.data), session['user_id'])
        
        flash('Настройки успешно сохранены!', 'success')
        return redirect(url_for('settings_index'))
    
    return render_template('settings/index.html', form=form)

@app.route('/export')

def export_index():
    """Export page"""
    form = ExportForm()
    categories = Category.query.filter_by(user_id=session['user_id']).all()
    form.category_id.choices = [(0, 'All Categories')] + [(c.id, c.name) for c in categories]
    
    return render_template('export/index.html', form=form)

# Добавляем недостающие функции для работы ссылок
@app.route('/categories/new')
def categories_new():
    return redirect(url_for('categories_index'))

@app.route('/bouquets/new')
def bouquets_new():
    return redirect(url_for('bouquets_index'))