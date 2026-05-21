from datetime import date

from app import create_app, db
from app.models import (
    Household,
    Individual,
    Account,
    TrustAsset,
    Liability,
    Report,
    BalanceEntry,
    TrustValue,
    LiabilityValue,
)


def seed_john_doe_family():
    existing = Household.query.filter_by(household_name="Doe Family").first()
    if existing:
        return existing

    household = Household(
        household_name="Doe Family",
        monthly_salary=15000.0,
        expense_budget=11000.0,
        deductibles_total=5000.0,
    )
    db.session.add(household)
    db.session.flush()

    db.session.add(
        Individual(
            household_id=household.id,
            designation="client1",
            first_name="John",
            last_name="Doe",
            dob=date(1976, 5, 15),
            ssn_last_four="1234",
        )
    )
    db.session.add(
        Individual(
            household_id=household.id,
            designation="client2",
            first_name="Jane",
            last_name="Doe",
            dob=date(1978, 8, 22),
            ssn_last_four="5678",
        )
    )
    db.session.flush()

    client1 = Individual.query.filter_by(
        household_id=household.id, designation="client1"
    ).first()
    client2 = Individual.query.filter_by(
        household_id=household.id, designation="client2"
    ).first()

    accounts = [
        Account(
            individual_id=client1.id,
            category="retirement",
            account_type="Traditional IRA",
            institution_name="Schwab",
            account_name="John's Traditional IRA",
            account_number_last_four="4412",
        ),
        Account(
            individual_id=client1.id,
            category="retirement",
            account_type="Roth IRA",
            institution_name="Schwab",
            account_name="John's Roth IRA",
            account_number_last_four="4413",
        ),
        Account(
            individual_id=client2.id,
            category="retirement",
            account_type="401(k)",
            institution_name="Fidelity",
            account_name="Jane's 401(k)",
            account_number_last_four="8891",
        ),
        Account(
            household_id=household.id,
            category="non_retirement",
            account_type="Brokerage",
            institution_name="Schwab",
            account_name="Schwab Joint Brokerage",
            account_number_last_four="9901",
        ),
        Account(
            household_id=household.id,
            category="private_reserve",
            account_type="Savings",
            institution_name="Pinnacle Bank",
            account_name="Private Reserve Account",
            account_number_last_four="0000",
        ),
    ]
    db.session.add_all(accounts)
    db.session.flush()

    db.session.add(
        TrustAsset(
            household_id=household.id,
            property_address="123 Main St, Atlanta, GA 30301",
        )
    )
    db.session.flush()

    liabilities = [
        Liability(
            household_id=household.id,
            loan_type="Mortgage",
            interest_rate=4.5,
        ),
        Liability(
            household_id=household.id,
            loan_type="Auto Loan",
            interest_rate=2.9,
        ),
    ]
    db.session.add_all(liabilities)
    db.session.flush()

    report = Report(household_id=household.id, report_date=date(2026, 3, 31))
    db.session.add(report)
    db.session.flush()

    by_name = {a.account_name: a for a in accounts}
    balance_entries = [
        BalanceEntry(
            report_id=report.id,
            account_id=by_name["John's Traditional IRA"].id,
            total_balance=11000.0,
            cash_balance=1000.0,
            as_of_date=report.report_date,
        ),
        BalanceEntry(
            report_id=report.id,
            account_id=by_name["John's Roth IRA"].id,
            total_balance=15000.0,
            cash_balance=500.0,
            as_of_date=report.report_date,
        ),
        BalanceEntry(
            report_id=report.id,
            account_id=by_name["Jane's 401(k)"].id,
            total_balance=50000.0,
            cash_balance=0.0,
            as_of_date=report.report_date,
        ),
        BalanceEntry(
            report_id=report.id,
            account_id=by_name["Schwab Joint Brokerage"].id,
            total_balance=50000.0,
            cash_balance=2000.0,
            as_of_date=report.report_date,
        ),
        BalanceEntry(
            report_id=report.id,
            account_id=by_name["Private Reserve Account"].id,
            total_balance=72000.0,
            cash_balance=72000.0,
            as_of_date=report.report_date,
        ),
    ]
    db.session.add_all(balance_entries)

    trust_asset = TrustAsset.query.filter_by(household_id=household.id).first()
    db.session.add(
        TrustValue(
            report_id=report.id,
            trust_asset_id=trust_asset.id,
            zillow_value=450000.0,
            as_of_date=report.report_date,
        )
    )

    liability_by_type = {l.loan_type: l for l in liabilities}
    liability_values = [
        LiabilityValue(
            report_id=report.id,
            liability_id=liability_by_type["Mortgage"].id,
            current_balance=200000.0,
            as_of_date=report.report_date,
        ),
        LiabilityValue(
            report_id=report.id,
            liability_id=liability_by_type["Auto Loan"].id,
            current_balance=15000.0,
            as_of_date=report.report_date,
        ),
    ]
    db.session.add_all(liability_values)

    db.session.commit()
    return household


def seed_alice_smith():
    existing = Household.query.filter_by(household_name="Alice Smith").first()
    if existing:
        return existing

    household = Household(
        household_name="Alice Smith",
        monthly_salary=22000.0,
        expense_budget=14000.0,
        deductibles_total=3000.0,
    )
    db.session.add(household)
    db.session.flush()

    db.session.add(
        Individual(
            household_id=household.id,
            designation="client1",
            first_name="Alice",
            last_name="Smith",
            dob=date(1982, 2, 2),
            ssn_last_four="4321",
        )
    )
    db.session.flush()

    client1 = Individual.query.filter_by(
        household_id=household.id, designation="client1"
    ).first()

    accounts = [
        Account(
            individual_id=client1.id,
            category="retirement",
            account_type="IRA",
            institution_name="Schwab",
            account_name="Alice's IRA",
            account_number_last_four="7777",
        ),
        Account(
            household_id=household.id,
            category="non_retirement",
            account_type="Brokerage",
            institution_name="Schwab",
            account_name="Schwab Brokerage",
            account_number_last_four="8888",
        ),
        Account(
            household_id=household.id,
            category="private_reserve",
            account_type="Savings",
            institution_name="Pinnacle Bank",
            account_name="Private Reserve Account",
            account_number_last_four="0000",
        ),
    ]
    db.session.add_all(accounts)
    db.session.flush()

    report = Report(household_id=household.id, report_date=date(2026, 3, 31))
    db.session.add(report)
    db.session.flush()

    by_name = {a.account_name: a for a in accounts}
    balance_entries = [
        BalanceEntry(
            report_id=report.id,
            account_id=by_name["Alice's IRA"].id,
            total_balance=120000.0,
            cash_balance=0.0,
            as_of_date=report.report_date,
        ),
        BalanceEntry(
            report_id=report.id,
            account_id=by_name["Schwab Brokerage"].id,
            total_balance=85000.0,
            cash_balance=5000.0,
            as_of_date=report.report_date,
        ),
        BalanceEntry(
            report_id=report.id,
            account_id=by_name["Private Reserve Account"].id,
            total_balance=90000.0,
            cash_balance=90000.0,
            as_of_date=report.report_date,
        ),
    ]
    db.session.add_all(balance_entries)

    db.session.commit()
    return household


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_john_doe_family()
        seed_alice_smith()
        print("Seed complete: Doe Family, Alice Smith")


if __name__ == "__main__":
    main()
