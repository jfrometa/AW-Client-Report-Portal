from datetime import date
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

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


def seed_doe_family():
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
            individual_id=client1.id,
            category="retirement",
            account_type="Roth IRA",
            institution_name="Fidelity",
            account_name="Alice's Roth IRA",
            account_number_last_four="7778",
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

    db.session.add(
        TrustAsset(
            household_id=household.id,
            property_address="456 Oak Ave, Austin, TX 78701",
        )
    )
    db.session.flush()

    liabilities = [
        Liability(
            household_id=household.id,
            loan_type="Mortgage",
            interest_rate=3.8,
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
            account_id=by_name["Alice's IRA"].id,
            total_balance=120000.0,
            cash_balance=0.0,
            as_of_date=report.report_date,
        ),
        BalanceEntry(
            report_id=report.id,
            account_id=by_name["Alice's Roth IRA"].id,
            total_balance=80000.0,
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

    trust_asset = TrustAsset.query.filter_by(household_id=household.id).first()
    db.session.add(
        TrustValue(
            report_id=report.id,
            trust_asset_id=trust_asset.id,
            zillow_value=520000.0,
            as_of_date=report.report_date,
        )
    )

    liability_by_type = {l.loan_type: l for l in liabilities}
    db.session.add(
        LiabilityValue(
            report_id=report.id,
            liability_id=liability_by_type["Mortgage"].id,
            current_balance=350000.0,
            as_of_date=report.report_date,
        )
    )

    db.session.commit()
    return household


def seed_johnson_family():
    existing = Household.query.filter_by(household_name="Johnson Family").first()
    if existing:
        return existing

    household = Household(
        household_name="Johnson Family",
        monthly_salary=18000.0,
        expense_budget=13000.0,
        deductibles_total=4000.0,
    )
    db.session.add(household)
    db.session.flush()

    db.session.add(
        Individual(
            household_id=household.id,
            designation="client1",
            first_name="Mike",
            last_name="Johnson",
            dob=date(1970, 10, 5),
            ssn_last_four="9876",
        )
    )
    db.session.add(
        Individual(
            household_id=household.id,
            designation="client2",
            first_name="Lisa",
            last_name="Johnson",
            dob=date(1972, 3, 18),
            ssn_last_four="5432",
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
            account_type="401(k)",
            institution_name="Vanguard",
            account_name="Mike's 401(k)",
            account_number_last_four="2222",
        ),
        Account(
            individual_id=client1.id,
            category="retirement",
            account_type="Roth IRA",
            institution_name="Vanguard",
            account_name="Mike's Roth IRA",
            account_number_last_four="2223",
        ),
        Account(
            individual_id=client2.id,
            category="retirement",
            account_type="Pension",
            institution_name="State Teachers",
            account_name="Lisa's Pension",
            account_number_last_four="3333",
        ),
        Account(
            household_id=household.id,
            category="non_retirement",
            account_type="Joint Checking",
            institution_name="Pinnacle Bank",
            account_name="Joint Checking",
            account_number_last_four="4444",
        ),
        Account(
            household_id=household.id,
            category="non_retirement",
            account_type="Brokerage",
            institution_name="TD Ameritrade",
            account_name="TD Joint Brokerage",
            account_number_last_four="5555",
        ),
        Account(
            household_id=household.id,
            category="private_reserve",
            account_type="Savings",
            institution_name="Pinnacle Bank",
            account_name="Private Reserve Account",
            account_number_last_four="6666",
        ),
    ]
    db.session.add_all(accounts)
    db.session.flush()

    db.session.add(
        TrustAsset(
            household_id=household.id,
            property_address="789 Pine Rd, Chicago, IL 60601",
        )
    )
    db.session.flush()

    liabilities = [
        Liability(
            household_id=household.id,
            loan_type="Mortgage",
            interest_rate=4.2,
        ),
        Liability(
            household_id=household.id,
            loan_type="Auto Loan",
            interest_rate=3.5,
        ),
    ]
    db.session.add_all(liabilities)
    db.session.commit()
    return household


def seed_williams_family():
    existing = Household.query.filter_by(household_name="Williams Family").first()
    if existing:
        return existing

    household = Household(
        household_name="Williams Family",
        monthly_salary=25000.0,
        expense_budget=18000.0,
        deductibles_total=6000.0,
    )
    db.session.add(household)
    db.session.flush()

    db.session.add(
        Individual(
            household_id=household.id,
            designation="client1",
            first_name="Tom",
            last_name="Williams",
            dob=date(1965, 7, 12),
            ssn_last_four="1111",
        )
    )
    db.session.add(
        Individual(
            household_id=household.id,
            designation="client2",
            first_name="Sarah",
            last_name="Williams",
            dob=date(1968, 11, 25),
            ssn_last_four="2222",
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
            institution_name="Fidelity",
            account_name="Tom's Traditional IRA",
            account_number_last_four="7777",
        ),
        Account(
            individual_id=client1.id,
            category="retirement",
            account_type="401(k)",
            institution_name="Fidelity",
            account_name="Tom's 401(k)",
            account_number_last_four="7778",
        ),
        Account(
            individual_id=client2.id,
            category="retirement",
            account_type="Roth IRA",
            institution_name="Charles Schwab",
            account_name="Sarah's Roth IRA",
            account_number_last_four="8888",
        ),
        Account(
            individual_id=client2.id,
            category="retirement",
            account_type="Pension",
            institution_name="City of Chicago",
            account_name="Sarah's Pension",
            account_number_last_four="9999",
        ),
        Account(
            household_id=household.id,
            category="non_retirement",
            account_type="Brokerage",
            institution_name="Charles Schwab",
            account_name="Schwab Joint Brokerage",
            account_number_last_four="0000",
        ),
        Account(
            household_id=household.id,
            category="private_reserve",
            account_type="Savings",
            institution_name="Pinnacle Bank",
            account_name="Private Reserve Account",
            account_number_last_four="1111",
        ),
    ]
    db.session.add_all(accounts)
    db.session.flush()

    db.session.add(
        TrustAsset(
            household_id=household.id,
            property_address="1010 Lake Shore Dr, Chicago, IL 60611",
        )
    )
    db.session.flush()

    liabilities = [
        Liability(
            household_id=household.id,
            loan_type="Mortgage",
            interest_rate=3.2,
        ),
        Liability(
            household_id=household.id,
            loan_type="Auto Loan",
            interest_rate=2.5,
        ),
    ]
    db.session.add_all(liabilities)
    db.session.commit()
    return household


def seed_davis_family():
    existing = Household.query.filter_by(household_name="Davis Family").first()
    if existing:
        return existing

    household = Household(
        household_name="Davis Family",
        monthly_salary=19000.0,
        expense_budget=14000.0,
        deductibles_total=3500.0,
    )
    db.session.add(household)
    db.session.flush()

    db.session.add(
        Individual(
            household_id=household.id,
            designation="client1",
            first_name="Chris",
            last_name="Davis",
            dob=date(1985, 1, 30),
            ssn_last_four="3333",
        )
    )
    db.session.add(
        Individual(
            household_id=household.id,
            designation="client2",
            first_name="Emily",
            last_name="Davis",
            dob=date(1987, 9, 14),
            ssn_last_four="4444",
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
            account_type="Roth IRA",
            institution_name="Vanguard",
            account_name="Chris's Roth IRA",
            account_number_last_four="5555",
        ),
        Account(
            individual_id=client2.id,
            category="retirement",
            account_type="401(k)",
            institution_name="TIAA",
            account_name="Emily's 401(k)",
            account_number_last_four="6666",
        ),
        Account(
            household_id=household.id,
            category="non_retirement",
            account_type="Joint Savings",
            institution_name="Pinnacle Bank",
            account_name="Joint Savings",
            account_number_last_four="7777",
        ),
        Account(
            household_id=household.id,
            category="private_reserve",
            account_type="Savings",
            institution_name="Pinnacle Bank",
            account_name="Private Reserve Account",
            account_number_last_four="8888",
        ),
    ]
    db.session.add_all(accounts)
    db.session.flush()

    db.session.add(
        TrustAsset(
            household_id=household.id,
            property_address="222 Cedar Ln, Denver, CO 80202",
        )
    )
    db.session.flush()

    liabilities = [
        Liability(
            household_id=household.id,
            loan_type="Mortgage",
            interest_rate=4.0,
        ),
        Liability(
            household_id=household.id,
            loan_type="Auto Loan",
            interest_rate=3.0,
        ),
    ]
    db.session.add_all(liabilities)
    db.session.commit()
    return household


def seed_bob_wilson():
    existing = Household.query.filter_by(household_name="Bob Wilson").first()
    if existing:
        return existing

    household = Household(
        household_name="Bob Wilson",
        monthly_salary=16000.0,
        expense_budget=12000.0,
        deductibles_total=2500.0,
    )
    db.session.add(household)
    db.session.flush()

    db.session.add(
        Individual(
            household_id=household.id,
            designation="client1",
            first_name="Bob",
            last_name="Wilson",
            dob=date(1979, 4, 20),
            ssn_last_four="5555",
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
            account_type="Traditional IRA",
            institution_name="Schwab",
            account_name="Bob's Traditional IRA",
            account_number_last_four="9999",
        ),
        Account(
            individual_id=client1.id,
            category="retirement",
            account_type="Roth IRA",
            institution_name="Schwab",
            account_name="Bob's Roth IRA",
            account_number_last_four="1010",
        ),
        Account(
            household_id=household.id,
            category="non_retirement",
            account_type="Brokerage",
            institution_name="E*TRADE",
            account_name="E*TRADE Brokerage",
            account_number_last_four="1111",
        ),
        Account(
            household_id=household.id,
            category="private_reserve",
            account_type="Savings",
            institution_name="Pinnacle Bank",
            account_name="Private Reserve Account",
            account_number_last_four="1212",
        ),
    ]
    db.session.add_all(accounts)
    db.session.flush()

    db.session.add(
        TrustAsset(
            household_id=household.id,
            property_address="333 Spruce St, Seattle, WA 98101",
        )
    )
    db.session.flush()

    liabilities = [
        Liability(
            household_id=household.id,
            loan_type="Mortgage",
            interest_rate=3.5,
        ),
        Liability(
            household_id=household.id,
            loan_type="Auto Loan",
            interest_rate=2.8,
        ),
    ]
    db.session.add_all(liabilities)
    db.session.commit()
    return household


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_doe_family()
        seed_alice_smith()
        seed_johnson_family()
        seed_williams_family()
        seed_davis_family()
        seed_bob_wilson()
        print("Seed complete: Doe Family, Alice Smith, Johnson Family, Williams Family, Davis Family, Bob Wilson")


if __name__ == "__main__":
    main()
