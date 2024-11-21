from iebank_api import db
from datetime import datetime
import string, random

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    account_number = db.Column(db.String(20), nullable=False, unique=True)
    balance = db.Column(db.Float, nullable=False, default=0.0)
    currency = db.Column(db.String(1), nullable=False, default="€")
    country = db.Column(db.String(32), nullable=False, default="Spain")
    status = db.Column(db.String(10), nullable=False, default="Active")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='accounts')
    transactions_from = db.relationship('Transaction', foreign_keys='Transaction.from_account_id', back_populates='from_account', cascade='all, delete-orphan')
    transactions_to = db.relationship('Transaction', foreign_keys='Transaction.to_account_id', back_populates='to_account', cascade='all, delete-orphan')

    def __repr__(self):
        return '<Account %r>' % self.account_number

    def __init__(self, name, currency, country, user_id):
        self.name = name
        self.account_number = ''.join(random.choices(string.digits, k=20))
        self.currency = currency
        self.balance = 0.0
        self.status = "Active"
        self.country = country
        self.user_id = user_id

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False)
    country = db.Column(db.String(32), nullable=False, default="Spain")
    state = db.Column(db.String(32), nullable=False, default="Madrid")
    date_of_birth = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    failed_login_attempts = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(10), nullable=False, default="Active")
    role = db.Column(db.Enum('admin', 'user', name='roles'), nullable=False, default='user')
    accounts = db.relationship('Account', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return '<User %r>' % self.username

    def __init__(self, username, email, password, country, state, date_of_birth, role, status):
        self.username = username
        self.email = email
        self.password = password
        self.country = country
        self.state = state
        self.date_of_birth = date_of_birth
        self.role = role
        self.status = status
        self.failed_login_attempts = 0

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    to_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(10), nullable=False, default="Pending")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    from_account = db.relationship('Account', foreign_keys=[from_account_id], back_populates='transactions_from')
    to_account = db.relationship('Account', foreign_keys=[to_account_id], back_populates='transactions_to')

    def __repr__(self):
        return '<Transaction %r>' % self.id

    def __init__(self, from_account_id, to_account_id, amount):
        self.from_account_id = from_account_id
        self.to_account_id = to_account_id
        self.amount = amount
        self.status = "Pending"

Account.transactions = db.relationship('Transaction', back_populates='account', cascade='all, delete-orphan')