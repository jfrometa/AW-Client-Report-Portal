from . import db
from datetime import datetime

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date)
    ssn_last_four = db.Column(db.String(4))
    monthly_salary = db.Column(db.Float, default=0.0)
    expense_budget = db.Column(db.Float, default=0.0)
    private_reserve_target = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    accounts = db.relationship('Account', backref='client', lazy=True, cascade="all, delete-orphan")
    reports = db.relationship('Report', backref='client', lazy=True, cascade="all, delete-orphan")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    account_type = db.Column(db.String(50))  # 'retirement', 'non-retirement', 'trust', 'liability'
    account_name = db.Column(db.String(200))
    account_number_last_four = db.Column(db.String(4))
    owner = db.Column(db.String(50))  # 'client1', 'client2', 'joint'
    
    balances = db.relationship('Balance', backref='account', lazy=True, cascade="all, delete-orphan")

class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    report_date = db.Column(db.Date, default=datetime.utcnow)
    status = db.Column(db.String(20), default='draft')  # 'draft', 'completed'
    
    balances = db.relationship('Balance', backref='report', lazy=True, cascade="all, delete-orphan")

class Balance(db.Model):
    __tablename__ = 'balances'
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    cash_balance = db.Column(db.Float, default=0.0) # Specific for TCC investment accounts
    as_of_date = db.Column(db.Date, default=datetime.utcnow)
