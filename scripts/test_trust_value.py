import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db, Report

app = create_app()

with app.app_context():
    reports = Report.query.all()
    for report in reports:
        print(f"\nReport {report.id}: {report.report_date}")
        print(f"  Number of trust_values: {len(report.trust_values)}")
        for tv in report.trust_values:
            print(f"    TrustValue: {tv.id}, zillow_value: {tv.zillow_value}")
