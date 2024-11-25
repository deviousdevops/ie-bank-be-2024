from datetime import datetime
from iebank_api import db
from iebank_api.models import Account, Transaction, User

def test_create_account(init_database, sample_user):
    """Test creating an account."""
    test_user = User.query.filter_by(username='testuser').first()
    account = Account(name='Test Account', currency='€', balance = '1000',country='Spain',user_id=sample_user.id)
    print("debug")
    db.session.add(account)
    db.session.commit()

    retrieved_account = Account.query.filter_by(name='Test Account').first()
    assert retrieved_account is not None
    assert retrieved_account.name == 'Test Account'
    assert retrieved_account.currency == '€'
    assert retrieved_account.country == 'Spain'
    assert retrieved_account.balance == 1000.0
    assert retrieved_account.user_id == test_user.id

def test_account_balance_default(init_database, sample_user):
    """Test the default balance of an account."""
    test_user = User.query.filter_by(username='testuser').first()
    account = Account(name='Test Account', currency='€', country='Spain', user_id=sample_user.id)
    db.session.add(account)
    db.session.commit()

    retrieved_account = Account.query.filter_by(name='Test Account').first()
    assert retrieved_account.balance == 0.0

def test_account_creation_date(init_database, sample_user):
    """Test the creation date of an account."""
    test_user = User.query.filter_by(username='testuser').first()
    account = Account(name='Test Account', currency='€', country='Spain', balance='1000',  user_id=sample_user.id)
    db.session.add(account)
    db.session.commit()

    retrieved_account = Account.query.filter_by(name='Test Account').first()
    assert retrieved_account.created_at is not None
    assert isinstance(retrieved_account.created_at, datetime)

def test_create_transaction(init_database, sample_user):
    """Test creating a transaction."""
    test_user = User.query.filter_by(username='testuser').first()
    from_account = Account(name='From Account', currency='€', country='Spain', user_id=test_user.id)
    to_account = Account(name='To Account', currency='€', country='Spain', user_id=test_user.id)
    db.session.add(from_account)
    db.session.add(to_account)
    db.session.commit()

    transaction = Transaction(from_account_id=from_account.id, to_account_id=to_account.id, amount=100.0, currency='EUR')
    db.session.add(transaction)
    db.session.commit()

    retrieved_transaction = Transaction.query.filter_by(id=transaction.id).first()
    assert retrieved_transaction is not None
    assert retrieved_transaction.from_account_id == from_account.id
    assert retrieved_transaction.to_account_id == to_account.id
    assert retrieved_transaction.amount == 100.0
    assert retrieved_transaction.currency == 'EUR'
    assert retrieved_transaction.status == 'Completed'
    assert retrieved_transaction.created_at is not None
    assert isinstance(retrieved_transaction.created_at, datetime)