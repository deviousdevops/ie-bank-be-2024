from iebank_api import db
from datetime import datetime, timezone
import string, random

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    account_number = db.Column(db.String(20), nullable=False, unique=True)
    balance = db.Column(db.Float, nullable=False, default=0.0)
    currency = db.Column(db.String(1), nullable=False, default="€")
    country = db.Column(db.String(32), nullable=False, default="Spain")
    status = db.Column(db.String(10), nullable=False, default="Active")
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='accounts')
    transactions_from = db.relationship('Transaction', foreign_keys='Transaction.from_account_id', back_populates='from_account', cascade='all, delete-orphan')
    transactions_to = db.relationship('Transaction', foreign_keys='Transaction.to_account_id', back_populates='to_account', cascade='all, delete-orphan')

    def __repr__(self):
        return '<Account %r>' % self.account_number

    def __init__(self, name, currency, country, user_id, balance=0.0):
        self.name = name
        self.account_number = ''.join(random.choices(string.digits, k=20))
        self.currency = currency
        self.balance = balance
        self.status = "Active"
        self.country = country
        self.user_id = user_id

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False)
    country = db.Column(db.String(32), nullable=False, default="Spain")
    date_of_birth = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    last_login_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    failed_login_attempts = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(10), nullable=False, default="Active")
    role = db.Column(db.Enum('admin', 'user', name='roles'), nullable=False, default='user')
    accounts = db.relationship('Account', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return '<User %r>' % self.username

    def __init__(self, username, email, password, country, date_of_birth, role='user'):
        self.username = username
        self.email = email
        self.password = password
        self.country = country
        self.date_of_birth = date_of_birth
        self.role = role  # Default value
        self.status = "Active"  # Default value
        self.failed_login_attempts = 0  # Default value

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    to_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="EUR")  # Add currency attribute
    status = db.Column(db.String(10), nullable=False, default="Completed")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    from_account = db.relationship('Account', foreign_keys=[from_account_id], back_populates='transactions_from')
    to_account = db.relationship('Account', foreign_keys=[to_account_id], back_populates='transactions_to')

    def __repr__(self):
        return '<Transaction %r>' % self.id

    def __init__(self, from_account_id, to_account_id, amount, currency="€"):  # Add currency parameter
        self.from_account_id = from_account_id
        self.to_account_id = to_account_id
        self.amount = amount
        self.currency = currency  # Initialize currency