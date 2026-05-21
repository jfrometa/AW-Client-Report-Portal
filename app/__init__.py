from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()

db = SQLAlchemy()

def ensure_schema():
    existing_cols = set()
    result = db.session.execute(text("PRAGMA table_info(clients)"))
    for row in result:
        existing_cols.add(row[1])

    if "deductibles_total" not in existing_cols:
        db.session.execute(text("ALTER TABLE clients ADD COLUMN deductibles_total REAL DEFAULT 0"))
    if "private_reserve_target_override" not in existing_cols:
        db.session.execute(text("ALTER TABLE clients ADD COLUMN private_reserve_target_override REAL"))
    if "private_reserve_target" in existing_cols:
        pass
    db.session.commit()

def create_app():
    app = Flask(__name__)
    
    database_path = os.getenv('RAILWAY_DATABASE_PATH', '/app/instance/portal.db')
    db_dir = os.path.dirname(database_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{database_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-for-internal-portal')

    db.init_app(app)

    with app.app_context():
        from .routes import main_bp
        from . import models
        app.register_blueprint(main_bp)
        db.create_all()
        ensure_schema()

    return app
