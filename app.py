from flask import Flask, render_template, session, redirect, url_for
import jwt
from config import Config
from models.user import User
from routes.auth import auth_bp
from routes.surveys import surveys_bp
from routes.public import public_bp
from routes.analytics import analytics_bp

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY


app.register_blueprint(auth_bp)
app.register_blueprint(surveys_bp)
app.register_blueprint(public_bp)
app.register_blueprint(analytics_bp)


@app.route('/')
def index():
    """Главная страница"""
    user = None
    token = session.get('token')
    if token:
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            user = User.find_by_id(payload['user_id'])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            session.pop('token', None)

    if user:
        return redirect(url_for('surveys.dashboard'))

    return render_template('index.html')


@app.errorhandler(404)
def not_found(e):
    return render_template('survey/closed.html',
                           message='Страница не найдена'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('survey/closed.html',
                           message='Ошибка сервера'), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)