import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db, Report

app = create_app()

with app.app_context():
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text("ALTER TABLE reports ADD COLUMN snapshot_monthly_salary FLOAT DEFAULT 0.0;"))
            conn.execute(db.text("ALTER TABLE reports ADD COLUMN snapshot_expense_budget FLOAT DEFAULT 0.0;"))
            conn.execute(db.text("ALTER TABLE reports ADD COLUMN snapshot_deductibles_total FLOAT DEFAULT 0.0;"))
            conn.execute(db.text("ALTER TABLE reports ADD COLUMN snapshot_private_reserve_target FLOAT DEFAULT 0.0;"))
            conn.commit()
        print("Migration completed successfully!")
    except Exception as e:
        print(f"Migration failed: {e}")
        print("Note: If the columns already exist, this is safe to ignore.")
