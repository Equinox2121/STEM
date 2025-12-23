from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import random
import string
from datetime import timedelta
from werkzeug.security import generate_password_hash
import os

db = SQLAlchemy()
DB_NAME = 'database.db'

# Running everything in here
def create_app():
    app = Flask(__name__)

    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        secret_key = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(256))

    app.config['SECRET_KEY'] = secret_key

    # Set the database up
    db_url = os.getenv("DATABASE_URL")

    if db_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    else:
        # Local SQLite for development backup
        print("Using local database.")
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///database.db'
    db.init_app(app)

    # From views.py import the variable 'views', same for auth.py
    from .views import views
    from .auth import auth

    # URL prefix is the prefix to whatever is in .route(x)
    app.register_blueprint(views, url_prefix = '/')
    app.register_blueprint(auth, url_prefix = '/')

    # Create the database
    from .models import User, Misc, Table, Report
    with app.app_context():
        db.create_all()

    # Login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login' # Redirect here when not logged in
    login_manager.init_app(app)

    # Tells the ID of the user we are looking for
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    # Set the session lifetime after inactivity
    @app.before_request
    def before_request():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes = 60)
        session.modified = True

    return app

# Create a database if there is no database file already
def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')

        # Create default Admin Account -INCOMPLETE-
        from .models import Admin
        ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "Admin")
        ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")
        ADMIN_KEY = os.getenv("ADMIN_KEY", ''.join(random.choices(string.ascii_letters + string.digits, k=256)))

        new_admin = Admin(
            student_email=ADMIN_EMAIL,
            password=generate_password_hash(ADMIN_PASSWORD, method='pbkdf2:sha256'),
            key=generate_password_hash(ADMIN_KEY, method='pbkdf2:sha256')
        )
        db.session.add(new_admin)
        db.session.commit()