from datetime import date, datetime

from . import db


class Household(db.Model):
    __tablename__ = "households"

    id = db.Column(db.Integer, primary_key=True)
    household_name = db.Column(db.String(200), nullable=False)
    monthly_salary = db.Column(db.Float, default=0.0)
    expense_budget = db.Column(db.Float, default=0.0)
    deductibles_total = db.Column(db.Float, default=0.0)
    private_reserve_target_override = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    individuals = db.relationship(
        "Individual", backref="household", lazy=True, cascade="all, delete-orphan"
    )
    accounts = db.relationship(
        "Account", backref="household", lazy=True, cascade="all, delete-orphan"
    )
    trust_assets = db.relationship(
        "TrustAsset", backref="household", lazy=True, cascade="all, delete-orphan"
    )
    liabilities = db.relationship(
        "Liability", backref="household", lazy=True, cascade="all, delete-orphan"
    )
    reports = db.relationship(
        "Report", backref="household", lazy=True, cascade="all, delete-orphan"
    )

    @property
    def display_name(self):
        if self.household_name:
            return self.household_name
        people = sorted(self.individuals, key=lambda x: x.designation or "")
        if len(people) == 0:
            return "Household"
        if len(people) == 1:
            return people[0].full_name
        if people[0].last_name and people[0].last_name == people[1].last_name:
            return f"{people[0].last_name} Family"
        return f"{people[0].full_name} & {people[1].full_name}"


class Individual(db.Model):
    __tablename__ = "individuals"

    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.Integer, db.ForeignKey("households.id"), nullable=False)
    designation = db.Column(db.String(20), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date)
    ssn_last_four = db.Column(db.String(4))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    accounts = db.relationship(
        "Account",
        backref="individual",
        lazy=True,
        cascade="all, delete-orphan",
        foreign_keys="Account.individual_id",
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def age(self):
        if not self.dob:
            return None
        today = date.today()
        years = today.year - self.dob.year
        if (today.month, today.day) < (self.dob.month, self.dob.day):
            years -= 1
        return years


class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.Integer, db.ForeignKey("households.id"))
    individual_id = db.Column(db.Integer, db.ForeignKey("individuals.id"))
    attributed_individual_id = db.Column(db.Integer, db.ForeignKey("individuals.id"))

    institution_name = db.Column(db.String(120))
    account_type = db.Column(db.String(50), nullable=False)
    account_name = db.Column(db.String(200))
    account_number_last_four = db.Column(db.String(4))
    category = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attributed_individual = db.relationship(
        "Individual", foreign_keys=[attributed_individual_id]
    )

    balance_entries = db.relationship(
        "BalanceEntry", backref="account", lazy=True, cascade="all, delete-orphan"
    )


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.Integer, db.ForeignKey("households.id"), nullable=False)
    report_date = db.Column(db.Date, default=datetime.utcnow)
    status = db.Column(db.String(20), default="draft")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    balance_entries = db.relationship(
        "BalanceEntry", backref="report", lazy=True, cascade="all, delete-orphan"
    )
    trust_values = db.relationship(
        "TrustValue", backref="report", lazy=True, cascade="all, delete-orphan"
    )
    liability_values = db.relationship(
        "LiabilityValue", backref="report", lazy=True, cascade="all, delete-orphan"
    )


class BalanceEntry(db.Model):
    __tablename__ = "balance_entries"

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey("reports.id"), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False)
    total_balance = db.Column(db.Float, default=0.0)
    cash_balance = db.Column(db.Float, default=0.0)
    as_of_date = db.Column(db.Date, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class TrustAsset(db.Model):
    __tablename__ = "trust_assets"

    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.Integer, db.ForeignKey("households.id"), nullable=False)
    property_address = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    values = db.relationship(
        "TrustValue", backref="trust_asset", lazy=True, cascade="all, delete-orphan"
    )


class TrustValue(db.Model):
    __tablename__ = "trust_values"

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey("reports.id"), nullable=False)
    trust_asset_id = db.Column(
        db.Integer, db.ForeignKey("trust_assets.id"), nullable=False
    )
    zillow_value = db.Column(db.Float, default=0.0)
    as_of_date = db.Column(db.Date, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Liability(db.Model):
    __tablename__ = "liabilities"

    id = db.Column(db.Integer, primary_key=True)
    household_id = db.Column(db.Integer, db.ForeignKey("households.id"), nullable=False)
    loan_type = db.Column(db.String(100), nullable=False)
    interest_rate = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    values = db.relationship(
        "LiabilityValue", backref="liability", lazy=True, cascade="all, delete-orphan"
    )


class LiabilityValue(db.Model):
    __tablename__ = "liability_values"

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey("reports.id"), nullable=False)
    liability_id = db.Column(db.Integer, db.ForeignKey("liabilities.id"), nullable=False)
    current_balance = db.Column(db.Float, default=0.0)
    as_of_date = db.Column(db.Date, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
