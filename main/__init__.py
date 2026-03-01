"""
This module initializes the Flask application and its core components, such as
SQLAlchemy for database interactions using Neon PostgreSQL.
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

# Create the Flask application instance
app = Flask(__name__)

# Configure application settings
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', '13ceb0bdfde20b0c64765791628ba245')

# Setup PostgreSQL Database via Neon
db_url = os.getenv("NEON_DATABASE_URL")
if not db_url:
    # Fallback to local sqlite for development if needed, but Neon is required for prod
    db_url = 'sqlite:///main.db'

app.config['SQLALCHEMY_DATABASE_URI'] = db_url

# Initialize Database & Auth
db = SQLAlchemy(app)

from flask_bcrypt import Bcrypt
from flask_login import LoginManager

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'sign_in'
login_manager.login_message_category = 'info'

from main import routes
from main import filters
