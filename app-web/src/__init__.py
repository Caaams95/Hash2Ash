import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from dotenv import load_dotenv
import psycopg2
import boto3
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SECURITY_PASSWORD_SALT'] = os.getenv("SECURITY_PASSWORD_SALT")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
mail = Mail(app)
db = SQLAlchemy(app)
#db.init_app(app) # Initialize the database

login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

app.config['MAIL_SERVER'] = 'smtp-mail.outlook.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_ASCII_ATTACHMENTS'] = False
app.config['MAIL_DEFAULT_CHARSET'] = 'utf-8'


app.config['BUCKET_NAME'] = os.getenv("BUCKET_NAME")
app.config['AWS_ACCESS_KEY'] = os.getenv("AWS_ACCESS_KEY")
app.config['AWS_SECRET_KEY'] = os.getenv("AWS_SECRET_KEY")
app.config['AWS_REGION_NAME'] = os.getenv("AWS_REGION_NAME")

app.config['STRIPE_API_KEY'] = os.getenv("STRIPE_API_KEY")

s3 = boto3.client('s3', aws_access_key_id=app.config['AWS_ACCESS_KEY'], aws_secret_access_key=app.config['AWS_SECRET_KEY'], region_name=app.config['AWS_REGION_NAME'])

from src import routes