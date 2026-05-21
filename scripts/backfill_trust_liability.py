import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db, Report, TrustValue, LiabilityValue, TrustAsset, Liability

app = create_app()

with app.app_context():
    reports = Report.query.all()
    updated = 0
    for report in reports:
        household = report.household
        if not report.trust_values:
            trust_asset = TrustAsset.query.filter_by(household_id=household.id).first()
            if trust_asset:
                db.session.add(
                    TrustValue(
                        report_id=report.id,
                        trust_asset_id=trust_asset.id,
                        zillow_value=0.0,
                        as_of_date=report.report_date
                    )
                )
                updated += 1
        if not report.liability_values:
            liabilities = Liability.query.filter_by(household_id=household.id).all()
            for liability in liabilities:
                db.session.add(
                    LiabilityValue(
                        report_id=report.id,
                        liability_id=liability.id,
                        current_balance=0.0,
                        as_of_date=report.report_date
                    )
                )
                updated += 1
    db.session.commit()
    print(f"Backfilled {updated} values!")
