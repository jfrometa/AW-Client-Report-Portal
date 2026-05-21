import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db, Report
from app.routes import get_private_reserve_target

app = create_app()

with app.app_context():
    reports = Report.query.all()
    print(f"Backfilling {len(reports)} reports...")
    updated = 0
    for report in reports:
        if report.snapshot_monthly_salary == 0.0 and report.snapshot_expense_budget == 0.0:
            household = report.household
            report.snapshot_monthly_salary = household.monthly_salary or 0.0
            report.snapshot_expense_budget = household.expense_budget or 0.0
            report.snapshot_deductibles_total = household.deductibles_total or 0.0
            report.snapshot_private_reserve_target = get_private_reserve_target(household)
            updated += 1
    db.session.commit()
    print(f"Backfilled {updated} reports!")
