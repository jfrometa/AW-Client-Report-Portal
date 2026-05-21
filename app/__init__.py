from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    database_path = os.getenv('RAILWAY_DATABASE_PATH', os.path.join(os.getcwd(), 'instance', 'portal.db'))
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{database_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-for-internal-portal')

    db.init_app(app)

    with app.app_context():
        from .routes import main_bp
        from . import models
        app.register_blueprint(main_bp)
        db.create_all()

    return app
