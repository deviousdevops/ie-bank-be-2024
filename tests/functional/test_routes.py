import pytest
from datetime import datetime
from iebank_api.models import User, Account, Transaction
import json
from iebank_api import db
from werkzeug.security import generate_password_hash

@pytest.fixture(scope='module')
def test_client():
    from iebank_api import app
    testing_client = app.test_client()

    ctx = app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()

@pytest.fixture(scope='module')
def init_database():
    # Create the database and the database table
    db.create_all()

    # Insert user data
    user1 = User(username='testuser', email='test@example.com', password=generate_password_hash('test1234'), country='USA', date_of_birth=datetime.strptime('1990-01-01', '%Y-%m-%d'), role='user', status='active')
    user2 = User(username='admin', email='admin@example.com', password=generate_password_hash('adminpass'), country='USA', date_of_birth=datetime.strptime('1980-01-01', '%Y-%m-%d'), role='admin', status='active')
    db.session.add(user1)
    db.session.add(user2)

    # Commit the changes for the users
    db.session.commit()

    yield db  # this is where the testing happens!

    db.drop_all()

@pytest.fixture
def sample_user(init_database):
    user = User.query.filter_by(username='testuser').first()
    return user

@pytest.fixture
def admin_user(init_database):
    user = User.query.filter_by(username='admin').first()
    return user

def test_register(test_client, init_database):
    """ Test registration of a new user """
    response = test_client.post('/register', json={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'newpass123',
        'country': 'Newland',
        'date_of_birth': '1995-05-05'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['username'] == 'newuser'
    assert data['email'] == 'newuser@example.com'


def test_login_user(test_client, init_database, sample_user):
    """Test logging in a user."""
    response = test_client.post('/login', json={
        'username': 'testuser',
        'password': 'test1234'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data
    assert 'user' in data
    assert data['user']['username'] == 'testuser'
    assert data['user']['email'] == 'test@example.com'


def test_user_portal(test_client, init_database, sample_user):
    """Test accessing the user portal."""
    # Log in the user first
    response = test_client.post('/login', json={
        'username': 'testuser',
        'password': 'test1234'
    })
    assert response.status_code == 200
    login_data = response.get_json()
    token = login_data['token']

    # Create accounts and transactions for the user
    user = User.query.filter_by(username='testuser').first()
    account1 = Account(name='Account 1', balance=1000.0, currency='USD', country='Spain', user_id=user.id)
    account2 = Account(name='Account 2', balance=2000.0, currency='USD', country='Spain', user_id=user.id)
    db.session.add(account1)
    db.session.add(account2)
    db.session.commit()

    transaction1 = Transaction(from_account_id=account1.id, to_account_id=account2.id, amount=100.0, currency='USD')
    transaction2 = Transaction(from_account_id=account2.id, to_account_id=account1.id, amount=200.0, currency='USD')
    db.session.add(transaction1)
    db.session.add(transaction2)
    db.session.commit()

    # Access the user portal
    response = test_client.get('/user_portal', headers={'x-access-token': token})
    assert response.status_code == 200
    data = response.get_json()
    assert 'accounts' in data
    assert 'transactions' in data
    assert len(data['accounts']) == 2
    assert len(data['transactions']) == 2
    assert data['accounts'][0]['name'] == 'Account 1'
    assert data['accounts'][1]['name'] == 'Account 2'
    assert data['transactions'][0]['amount'] == 100.0
    assert data['transactions'][1]['amount'] == 200.0


def test_admin_portal(test_client, init_database, admin_user):
    """Test accessing the admin portal."""
    # Log in the admin user first
    response = test_client.post('/login', json={
        'username': 'admin',
        'password': 'adminpass'
    })
    assert response.status_code == 200
    login_data = response.get_json()
    token = login_data['token']

    # Access the admin portal with the token
    response = test_client.get('/admin_portal', headers={'x-access-token': token})
    assert response.status_code == 200
    data = response.get_json()
    assert 'users' in data
    assert len(data['users']) > 0
    assert data['users'][0]['username'] == 'admin'
    assert data['users'][0]['email'] == 'admin@example.com'


def test_create_account(test_client, init_database, sample_user):
    """Test creating a new account."""
    # Log in the user first
    response = test_client.post('/login', json={
        'username': 'testuser',
        'password': 'test1234'
    })
    assert response.status_code == 200
    login_data = response.get_json()
    token = login_data['token']

    # Create a new account
    response = test_client.post('/accounts', json={
        'name': 'New Account',
        'currency': 'USD',
        'balance': 10.0,
        'country': 'USA'
    }, headers={'x-access-token': token})
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'New Account'
    assert data['currency'] == 'USD'
    assert data['country'] == 'USA'
    assert data['balance'] == 10.0  # Assuming default balance is 0.0

def test_get_account(test_client, init_database, sample_user):
    """Test getting a specific account by ID."""
    # Log in the user first
    response = test_client.post('/login', json={
        'username': 'testuser',
        'password': 'test1234'
    })
    assert response.status_code == 200
    login_data = response.get_json()
    token = login_data['token']

    # Create a new account
    account = Account(name='New Account', currency='USD', country='USA', user_id=sample_user.id)
    db.session.add(account)
    db.session.commit()

    # Get the account
    response = test_client.get(f'/accounts/{account.id}', headers={'x-access-token': token})
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'New Account'
    assert data['currency'] == 'USD'
    assert data['country'] == 'USA'

def test_update_account(test_client, init_database, sample_user):
    """Test updating a specific account by ID."""
    # Log in the user first
    response = test_client.post('/login', json={
        'username': 'testuser',
        'password': 'test1234'
    })
    assert response.status_code == 200
    login_data = response.get_json()
    token = login_data['token']

    # Create a new account
    account = Account(name='Old Account', currency='USD', country='USA', user_id=sample_user.id)
    db.session.add(account)
    db.session.commit()

    # Update the account
    response = test_client.put(f'/accounts/{account.id}', json={
        'name': 'Updated Account'
    }, headers={'x-access-token': token})
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Updated Account'

def test_delete_account(test_client, init_database, sample_user):
    """Test deleting a specific account by ID."""
    # Log in the user first
    response = test_client.post('/login', json={
        'username': 'testuser',
        'password': 'test1234'
    })
    assert response.status_code == 200
    login_data = response.get_json()
    token = login_data['token']

    # Create a new account
    account = Account(name='Account to Delete', currency='USD', country='USA', user_id=sample_user.id)
    db.session.add(account)
    db.session.commit()

    # Delete the account
    response = test_client.delete(f'/accounts/{account.id}', headers={'x-access-token': token})
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Account to Delete'

def test_create_transaction(test_client, init_database, sample_user):
    """Test creating a new transaction."""
    # Log in the user first
    response = test_client.post('/login', json={
        'username': 'testuser',
        'password': 'test1234'
    })
    assert response.status_code == 200
    login_data = response.get_json()
    token = login_data['token']

    # Create accounts
    account1 = Account(name='Account 1', balance=1000.0, currency='USD', country='Spain', user_id=sample_user.id)
    account2 = Account(name='Account 2', balance=2000.0, currency='USD', country='Spain', user_id=sample_user.id)
    db.session.add(account1)
    db.session.add(account2)
    db.session.commit()

    # Create a transaction
    response = test_client.post('/transactions', json={
        'from_account_number': account1.account_number,
        'to_account_number': account2.account_number,
        'amount': 100.0,
        'currency': 'USD'
    }, headers={'x-access-token': token})
    assert response.status_code == 200
    data = response.get_json()
    assert data['transaction']['amount'] == 100.0
    assert data['transaction']['from_account'] == account1.account_number
    assert data['transaction']['to_account'] == account2.account_number

def test_get_transactions(test_client, init_database, sample_user):
    """Test getting all transactions for the logged-in user."""
    # Log in the user first
    response = test_client.post('/login', json={
        'username': 'testuser',
        'password': 'test1234'
    })
    assert response.status_code == 200
    login_data = response.get_json()
    token = login_data['token']

    # Create accounts and transactions
    account1 = Account(name='Account 1', balance=1000.0, currency='USD', country='Spain',user_id=sample_user.id)
    account2 = Account(name='Account 2',  balance=2000.0, currency='USD', country='Spain',user_id=sample_user.id)
    db.session.add(account1)
    db.session.add(account2)
    db.session.commit()

    transaction1 = Transaction(from_account_id=account1.id, to_account_id=account2.id, amount=100.0, currency='USD')
    transaction2 = Transaction(from_account_id=account2.id, to_account_id=account1.id, amount=200.0, currency='USD')
    db.session.add(transaction1)
    db.session.add(transaction2)
    db.session.commit()

    # Get transactions
    response = test_client.get('/transactions', headers={'x-access-token': token})
    assert response.status_code == 200
    data = response.get_json()
    assert 'transactions' in data
    assert len(data['transactions']) == 2

def test_create_user(test_client, init_database, admin_user):
    """Test creating a new user by admin."""
    # Log in the admin user first
    response = test_client.post('/login', json={
        'username': 'admin',
        'password': 'adminpass'
    })
    assert response.status_code == 200
    login_data = response.get_json()
    token = login_data['token']

    # Create a new user
    response = test_client.post('/admin/users', json={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'country': 'USA',
        'date_of_birth': '1990-01-01',
        'role': 'user',
        'status': 'active'
    }, headers={'x-access-token': token})
    assert response.status_code == 200
    data = response.get_json()
    assert data['username'] == 'newuser'
    assert data['email'] == 'newuser@example.com'


def test_update_user(test_client, init_database, admin_user):
    """Test updating a user by admin."""
    # Log in the admin user first
    response = test_client.post('/login', json={
        'username': 'admin',
        'password': 'adminpass'
    })
    assert response.status_code == 200
    login_data = response.get_json()
    token = login_data['token']

    # Create a user to update
    user = User(
        username='updateuser',
        email='updateuser@example.com',
        password=generate_password_hash('password123'),
        country='USA',
        date_of_birth=datetime.strptime('1990-01-01', '%Y-%m-%d'),
        role='user',
        status='active'
    )
    db.session.add(user)
    db.session.commit()

    # Update the user
    response = test_client.put(f'/admin/users/{user.id}', json={
        'username': 'updateduser',
        'email': 'updateduser@example.com',
        'password': 'newpassword123',
        'country': 'USA',
        'date_of_birth': '1990-01-01',
        'role': 'user',
        'status': 'active'
    }, headers={'x-access-token': token})
    assert response.status_code == 200
    data = response.get_json()
    assert data['username'] == 'updateduser'
    assert data['email'] == 'updateduser@example.com'

def test_delete_user(test_client, init_database, admin_user):
    """Test deleting a user by admin."""
    # Log in the admin user first
    response = test_client.post('/login', json={
        'username': 'admin',
        'password': 'adminpass'
    })
    assert response.status_code == 200
    login_data = response.get_json()
    token = login_data['token']

    # Create a user to delete
    user = User(
        username='deleteuser',
        email='deleteuser@example.com',
        password=generate_password_hash('password123'),
        country='USA',
        date_of_birth=datetime.strptime('1990-01-01', '%Y-%m-%d'),
        role='user',
        status='active'
    )
    db.session.add(user)
    db.session.commit()

    # Delete the user
    response = test_client.delete(f'/admin/users/{user.id}', headers={'x-access-token': token})
    assert response.status_code == 200
    data = response.get_json()
    assert data['username'] == 'deleteuser'
    assert data['email'] == 'deleteuser@example.com'
