import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db, Report

app = create_app()

with app.app_context():
    reports = Report.query.all()
    print(f"Total reports: {len(reports)}")
    for report in reports:
        print(f"\nReport {report.id}: {report.report_date}")
        print(f"  Snapshot inflow: {report.snapshot_monthly_salary}")
        print(f"  Snapshot outflow: {report.snapshot_expense_budget}")
        print(f"  Snapshot deductibles: {report.snapshot_deductibles_total}")
        print(f"  Snapshot target: {report.snapshot_private_reserve_target}")
        print(f"  Balance entries: {len(report.balance_entries)}")
