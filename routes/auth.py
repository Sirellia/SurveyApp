from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import jwt
from datetime import datetime, timezone, timedelta
from config import Config
from models.user import User

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = session.get('token')
        if not token:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('auth.login'))
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            user = User.find_by_id(payload['user_id'])
            if not user:
                session.pop('token', None)
                flash('Пользователь не найден', 'error')
                return redirect(url_for('auth.login'))
            request.current_user = user
        except jwt.ExpiredSignatureError:
            session.pop('token', None)
            flash('Сессия истекла, войдите снова', 'warning')
            return redirect(url_for('auth.login'))
        except jwt.InvalidTokenError:
            session.pop('token', None)
            flash('Ошибка авторизации', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def generate_token(user_id):
    payload = {
        'user_id': str(user_id),
        'exp': datetime.now(timezone.utc) + timedelta(days=30)
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('token'):
        return redirect(url_for('surveys.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        full_name = request.form.get('full_name', '').strip()

        errors = []
        if not email or '@' not in email:
            errors.append('Введите корректный email')
        if len(password) < 6:
            errors.append('Пароль должен быть не менее 6 символов')
        if len(full_name) < 2:
            errors.append('Имя должно быть не менее 2 символов')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html',
                                   email=email, full_name=full_name)

        if User.find_by_email(email):
            flash('Пользователь с таким email уже существует', 'error')
            return render_template('auth/register.html',
                                   email=email, full_name=full_name)

        try:
            user = User.create(email, password, full_name)
            token = generate_token(user['_id'])
            session['token'] = token
            flash('Регистрация успешна! Добро пожаловать!', 'success')
            return redirect(url_for('surveys.dashboard'))
        except Exception as e:
            flash(f'Ошибка при регистрации: {str(e)}', 'error')
            return render_template('auth/register.html',
                                   email=email, full_name=full_name)

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('token'):
        return redirect(url_for('surveys.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = User.find_by_email(email)
        if not user or not User.check_password(user, password):
            flash('Неверный email или пароль', 'error')
            return render_template('auth/login.html', email=email)

        token = generate_token(user['_id'])
        session['token'] = token
        flash(f'Добро пожаловать, {user["full_name"]}!', 'success')
        return redirect(url_for('surveys.dashboard'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.pop('token', None)
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('auth.login'))