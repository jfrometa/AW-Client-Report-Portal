import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models import Household
import sqlalchemy

def add_active_column():
    app = create_app()
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                with conn.begin():
                    inspector = sqlalchemy.inspect(db.engine)
                    columns = [col['name'] for col in inspector.get_columns('households')]
                    if 'active' not in columns:
                        conn.execute(sqlalchemy.text('ALTER TABLE households ADD COLUMN active BOOLEAN DEFAULT 1 NOT NULL'))
                        print("Added 'active' column to households table.")
                    else:
                        print("'active' column already exists.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    add_active_column()
