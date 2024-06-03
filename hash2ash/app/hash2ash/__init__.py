import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = '521ba9c2817a7aa7e4c28bc8e0bc35ec'
app.config['SECURITY_PASSWORD_SALT'] = '6aae363f950e2d410f9dfb7d5cca9fd4'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///appdb.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp-mail.outlook.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'hash2ash@outlook.fr'
app.config['MAIL_PASSWORD'] = 'amdd4ud5e[j#cTaFdX7=Hg:uDL>Q'
app.config['MAIL_ASCII_ATTACHMENTS'] = False
app.config['MAIL_DEFAULT_CHARSET'] = 'utf-8'
mail = Mail(app)

from hash2ash import routes