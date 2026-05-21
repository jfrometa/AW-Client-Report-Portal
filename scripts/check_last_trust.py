import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db, Household, Report

app = create_app()

with app.app_context():
    households = Household.query.all()
    for hh in households:
        print(f"\nHousehold: {hh.display_name}")
        last_report = Report.query.filter_by(household_id=hh.id).order_by(Report.report_date.desc()).first()
        if last_report:
            print(f"  Last report: {last_report.id}")
            print(f"  Trust values: {len(last_report.trust_values)}")
            if last_report.trust_values:
                tv = last_report.trust_values[0]
                print(f"  TV zillow value: {tv.zillow_value}")
                print(f"  TV id: {tv.id}")
                print(f"  last_trust_value would be: {tv.zillow_value}")
