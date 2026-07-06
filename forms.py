from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, IntegerField, FieldList, FormField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length, ValidationError, EqualTo, Email, Optional
from models import Flower, Category, Bouquet

class FlowerForm(FlaskForm):
    name = StringField('Название цветка', validators=[
        DataRequired(message='Название цветка обязательно'),
        Length(min=2, max=100, message='Название должно быть от 2 до 100 символов')
    ])
    price_per_unit = FloatField('Цена за единицу (лей)', validators=[
        DataRequired(message='Цена обязательна'),
        NumberRange(min=0.01, message='Цена должна быть больше 0')
    ])

class CategoryForm(FlaskForm):
    name = StringField('Название категории', validators=[
        DataRequired(message='Название категории обязательно'),
        Length(min=2, max=100, message='Название должно быть от 2 до 100 символов')
    ])

class BouquetCompositionForm(FlaskForm):
    flower_id = SelectField('Flower', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[
        DataRequired(message='Quantity is required'),
        NumberRange(min=1, message='Quantity must be at least 1')
    ])

class BouquetForm(FlaskForm):
    name = StringField('Название букета', validators=[
        DataRequired(message='Название букета обязательно'),
        Length(min=2, max=100, message='Название должно быть от 2 до 100 символов')
    ])
    sku = StringField('Артикул', validators=[
        DataRequired(message='Артикул обязателен'),
        Length(min=1, max=50, message='Артикул должен быть от 1 до 50 символов')
    ])
    category_id = SelectField('Категория', coerce=int, validators=[DataRequired()])
    published = BooleanField('Опубликован', default=True)
    
    def __init__(self, *args, **kwargs):
        super(BouquetForm, self).__init__(*args, **kwargs)
        
        # Populate category choices
        self.category_id.choices = [(0, 'Select a category')] + [
            (category.id, category.name) for category in Category.query.order_by(Category.name).all()
        ]
        
        # Initialize composition data as empty list
        self.composition_data = []
    
    def validate_category_id(self, field):
        if field.data == 0:
            raise ValidationError('Please select a category')

class GlobalSettingsForm(FlaskForm):
    delivery_cost = FloatField('Стоимость доставки (лей)', validators=[
        DataRequired(message='Стоимость доставки обязательна'),
        NumberRange(min=0, message='Стоимость доставки не может быть отрицательной')
    ])
    markup_percentage = FloatField('Процент наценки (%)', validators=[
        DataRequired(message='Процент наценки обязателен'),
        NumberRange(min=0, max=1000, message='Процент наценки должен быть от 0 до 1000')
    ])
    site_sync_endpoint = StringField('Endpoint синхронизации сайта', validators=[
        Optional(),
        Length(max=500, message='URL endpoint не должен быть длиннее 500 символов')
    ])
    site_sync_token = StringField('Секретный token синхронизации', validators=[
        Optional(),
        Length(max=200, message='Token не должен быть длиннее 200 символов')
    ])

class ExportForm(FlaskForm):
    category_id = SelectField('Category (Optional)', coerce=int)
    
    def __init__(self, *args, **kwargs):
        super(ExportForm, self).__init__(*args, **kwargs)
        
        # Populate category choices
        self.category_id.choices = [(0, 'All Categories')] + [
            (category.id, category.name) for category in Category.query.order_by(Category.name).all()
        ]


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[
        DataRequired(message='Логин обязателен'),
        Length(min=3, max=80, message='Логин должен быть от 3 до 80 символов')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Пароль обязателен')
    ])
    remember_me = BooleanField('Запомнить меня')


class UserForm(FlaskForm):
    username = StringField('Логин', validators=[
        DataRequired(message='Логин обязателен'),
        Length(min=3, max=80, message='Логин должен быть от 3 до 80 символов')
    ])
    current_password = PasswordField('Текущий пароль', validators=[
        DataRequired(message='Введите текущий пароль для подтверждения')
    ])
    new_password = PasswordField('Новый пароль', validators=[
        DataRequired(message='Новый пароль обязателен'),
        Length(min=6, message='Пароль должен содержать минимум 6 символов')
    ])
    confirm_password = PasswordField('Подтвердите новый пароль', validators=[
        DataRequired(message='Подтверждение пароля обязательно'),
        EqualTo('new_password', message='Пароли должны совпадать')
    ])

class RegisterForm(FlaskForm):
    username = StringField('Логин', validators=[
        DataRequired(message='Логин обязателен'),
        Length(min=3, max=80, message='Логин должен быть от 3 до 80 символов')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email обязателен'),
        Email(message='Введите корректный email адрес'),
        Length(max=120, message='Email не должен превышать 120 символов')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Пароль обязателен'),
        Length(min=6, message='Пароль должен содержать минимум 6 символов')
    ])
    confirm_password = PasswordField('Подтвердите пароль', validators=[
        DataRequired(message='Подтверждение пароля обязательно'),
        EqualTo('password', message='Пароли должны совпадать')
    ])
    full_name = StringField('Полное имя', validators=[
        Length(max=200, message='Полное имя не должно превышать 200 символов')
    ])
    organization = StringField('Организация', validators=[
        Length(max=200, message='Название организации не должно превышать 200 символов')
    ])
    submit = SubmitField('Зарегистрироваться')
