from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, 'templates'),
        static_folder=os.path.join(base_dir, 'static')
    )

    # Database config
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'zyftway.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Secret key for sessions
    app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey')

    db.init_app(app)

    # Import and register routes
    from backend.routes import init_app as init_routes
    init_routes(app)

    return app
