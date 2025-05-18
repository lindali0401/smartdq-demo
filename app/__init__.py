import os
from flask import Flask, request, session
from flask_babel import Babel
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)
app.secret_key = "super-secret-key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# app.config['BABEL_DEFAULT_LOCALE'] = 'de'
# babel = Babel(app)

def get_locale():
    return session.get('lang') or request.accept_languages.best_match(['en', 'de'])

app.config['BABEL_DEFAULT_LOCALE'] = 'de'
babel = Babel(app, locale_selector=get_locale)

app.secret_key = 'ihA7hd94!skas38@fJaaJK923klz0X'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

from app import routes
