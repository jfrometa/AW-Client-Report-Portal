from datetime import date

from app import create_app, db
from app.models import Account, Balance, Client, Report


def seed_john_doe():
    existing = Client.query.filter_by(first_name="John", last_name="Doe").first()
    if existing:
        return existing

    client = Client(
        first_name="John",
        last_name="Doe",
        dob=date(1976, 5, 15),
        ssn_last_four="1234",
        monthly_salary=15000.0,
        expense_budget=11000.0,
        deductibles_total=5000.0,
    )
    db.session.add(client)
    db.session.flush()

    accounts = [
        Account(
            client_id=client.id,
            account_type="retirement",
            account_name="Traditional IRA",
            account_number_last_four="4412",
            owner="client1",
        ),
        Account(
            client_id=client.id,
            account_type="retirement",
            account_name="Roth IRA",
            account_number_last_four="4413",
            owner="client1",
        ),
        Account(
            client_id=client.id,
            account_type="retirement",
            account_name="401(k)",
            account_number_last_four="8891",
            owner="client2",
        ),
        Account(
            client_id=client.id,
            account_type="non-retirement",
            account_name="Schwab Joint Brokerage",
            account_number_last_four="9901",
            owner="joint",
        ),
        Account(
            client_id=client.id,
            account_type="private_reserve",
            account_name="Private Reserve Account",
            account_number_last_four="0000",
            owner="joint",
        ),
        Account(
            client_id=client.id,
            account_type="trust",
            account_name="Primary Residence (Zillow)",
            account_number_last_four="",
            owner="joint",
        ),
        Account(
            client_id=client.id,
            account_type="liability",
            account_name="Mortgage (4.5%)",
            account_number_last_four="",
            owner="joint",
        ),
        Account(
            client_id=client.id,
            account_type="liability",
            account_name="Auto Loan (2.9%)",
            account_number_last_four="",
            owner="joint",
        ),
    ]
    db.session.add_all(accounts)
    db.session.flush()

    report = Report(client_id=client.id, report_date=date(2026, 3, 31), status="completed")
    db.session.add(report)
    db.session.flush()

    by_name = {a.account_name: a for a in accounts}
    balances = [
        Balance(report_id=report.id, account_id=by_name["Traditional IRA"].id, balance=11000.0),
        Balance(report_id=report.id, account_id=by_name["Roth IRA"].id, balance=15000.0),
        Balance(report_id=report.id, account_id=by_name["401(k)"].id, balance=50000.0),
        Balance(report_id=report.id, account_id=by_name["Schwab Joint Brokerage"].id, balance=50000.0),
        Balance(report_id=report.id, account_id=by_name["Private Reserve Account"].id, balance=72000.0),
        Balance(report_id=report.id, account_id=by_name["Primary Residence (Zillow)"].id, balance=450000.0),
        Balance(report_id=report.id, account_id=by_name["Mortgage (4.5%)"].id, balance=200000.0),
        Balance(report_id=report.id, account_id=by_name["Auto Loan (2.9%)"].id, balance=15000.0),
    ]
    db.session.add_all(balances)
    db.session.commit()
    return client


def seed_alice_smith():
    existing = Client.query.filter_by(first_name="Alice", last_name="Smith").first()
    if existing:
        return existing

    client = Client(
        first_name="Alice",
        last_name="Smith",
        dob=date(1982, 2, 2),
        ssn_last_four="4321",
        monthly_salary=22000.0,
        expense_budget=14000.0,
        deductibles_total=3000.0,
    )
    db.session.add(client)
    db.session.flush()

    accounts = [
        Account(
            client_id=client.id,
            account_type="retirement",
            account_name="IRA",
            account_number_last_four="7777",
            owner="client1",
        ),
        Account(
            client_id=client.id,
            account_type="non-retirement",
            account_name="Schwab Brokerage",
            account_number_last_four="8888",
            owner="client1",
        ),
        Account(
            client_id=client.id,
            account_type="private_reserve",
            account_name="Private Reserve Account",
            account_number_last_four="0000",
            owner="client1",
        ),
    ]
    db.session.add_all(accounts)
    db.session.flush()

    report = Report(client_id=client.id, report_date=date(2026, 3, 31), status="completed")
    db.session.add(report)
    db.session.flush()

    by_name = {a.account_name: a for a in accounts}
    balances = [
        Balance(report_id=report.id, account_id=by_name["IRA"].id, balance=120000.0),
        Balance(report_id=report.id, account_id=by_name["Schwab Brokerage"].id, balance=85000.0),
        Balance(report_id=report.id, account_id=by_name["Private Reserve Account"].id, balance=90000.0),
    ]
    db.session.add_all(balances)
    db.session.commit()
    return client


def main():
    app = create_app()
    with app.app_context():
        seed_john_doe()
        seed_alice_smith()
        print("Seed complete: John Doe, Alice Smith")


if __name__ == "__main__":
    main()

