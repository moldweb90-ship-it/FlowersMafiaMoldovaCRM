from flask import render_template, request, redirect, url_for, flash, session
from functools import wraps
from app import app, db
from models import User, Flower, Category, Bouquet, BouquetComposition, GlobalSetting
from forms import LoginForm

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if session.get('logged_in'):
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data) and user.status == 'active':
            # Успешный вход
            session.clear()  # Очищаем старую сессию
            session['logged_in'] = True
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
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
@login_required
def index():
    """Главная страница"""
    user_id = session['user_id']
    flower_count = Flower.query.filter_by(user_id=user_id).count()
    category_count = Category.query.filter_by(user_id=user_id).count()
    bouquet_count = Bouquet.query.filter_by(user_id=user_id).count()
    recent_bouquets = Bouquet.query.filter_by(user_id=user_id).order_by(Bouquet.id.desc()).limit(10).all()
    
    return render_template('index.html', 
                         flower_count=flower_count,
                         category_count=category_count,
                         bouquet_count=bouquet_count,
                         recent_bouquets=recent_bouquets)

# Тестовый маршрут для проверки
@app.route('/test')
def test():
    return f"Сессия: {dict(session)}"