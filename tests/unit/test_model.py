from datetime import datetime
from iebank_api import db
from iebank_api.models import Account, Transaction, User
from sqlalchemy.exc import IntegrityError
import pytest

def test_create_multiple_accounts(init_database, sample_user):
    """Test creating multiple accounts for a single user."""
    # Retrieve the test user
    test_user = User.query.filter_by(username='testuser').first()
    # Create the two accounts
    account1 = Account(name='Test Account 1', currency='€', balance=1000, country='Spain', user_id=sample_user.id)
    db.session.add(account1)
    account2 = Account(name='Test Account 2', currency='€', balance=500, country='Spain', user_id=sample_user.id)
    db.session.add(account2)

    db.session.commit()
    retrieved_account1 = Account.query.filter_by(name='Test Account 1').first()
    retrieved_account2 = Account.query.filter_by(name='Test Account 2').first()

    # Assert both accounts were created successfully
    assert retrieved_account1 is not None
    assert retrieved_account1.name == 'Test Account 1'
    assert retrieved_account1.currency == '€'
    assert retrieved_account1.country == 'Spain'
    assert retrieved_account1.balance == 1000.0
    assert retrieved_account1.user_id == test_user.id

    assert retrieved_account2 is not None
    assert retrieved_account2.name == 'Test Account 2'
    assert retrieved_account2.currency == '€'
    assert retrieved_account2.country == 'Spain'
    assert retrieved_account2.balance == 500.0
    assert retrieved_account2.user_id == test_user.id

    # Assert the user has two accounts
    user_accounts = Account.query.filter_by(user_id=test_user.id).all()
    assert len(user_accounts) == 2


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

def test_create_user(init_database):
    """Test creating a user."""
    user = User(
        username="testuser",
        email="testuser@example.com",
        password="hashedpassword123",
        country="Spain",
        date_of_birth=datetime(1990, 1, 1),
    )

    db.session.add(user)
    db.session.commit()
    retrieved_user = User.query.filter_by(username="testuser").first()

    # Assert the retrieved user is not None and matches expected values
    assert retrieved_user is not None
    assert retrieved_user.username == "testuser"
    assert retrieved_user.email == "testuser@example.com"
    assert retrieved_user.country == "Spain"
    assert retrieved_user.date_of_birth == datetime(1990, 1, 1)
    assert retrieved_user.role == "user"
    assert retrieved_user.status == "Active"
    assert retrieved_user.failed_login_attempts == 0
    assert retrieved_user.created_at is not None
    assert isinstance(retrieved_user.created_at, datetime)

def test_user_unique_constraints(init_database):
    """Test that username and email must be unique."""
    # Create the first user
    user1 = User(
        username="testuser",
        email="testuser@example.com",
        password="hashedpassword123",
        country="Spain",
        date_of_birth=datetime(1990, 1, 1),
    )
    db.session.add(user1)
    db.session.commit()

    # Attempt to create another user with the same username/email
    user2 = User(
        username="testuser",  # Duplicate 
        email="testuser@example.com",  # Duplicate
        password="anotherpassword",
        country="Spain",
        date_of_birth=datetime(1995, 1, 1),
    )
    db.session.add(user2)

    with pytest.raises(IntegrityError):  # Expecting an IntegrityError for duplicates
        db.session.commit()
