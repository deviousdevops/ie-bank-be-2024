from iebank_api import app, db
from iebank_api.models import User, Account, Transaction
import pytest
from werkzeug.security import generate_password_hash

@pytest.fixture
def testing_client():
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def login_user(testing_client):
    user = User(
        username='testuser',
        email='testuser@example.com',
        password=generate_password_hash('password', method='sha256'),
        country='Spain',
        state='Madrid',
        date_of_birth='1980-01-01',
        role='user',
        status='Active'
    )
    db.session.add(user)
    db.session.commit()
    response = testing_client.post('/login', json={
        'username': 'testuser',
        'password': 'password'
    })
    assert response.status_code == 200

@pytest.fixture
def login_admin(testing_client):
    admin = User(
        username='admin',
        email='admin@example.com',
        password=generate_password_hash('adminpassword', method='sha256'),
        country='Spain',
        state='Madrid',
        date_of_birth='1980-01-01',
        role='admin',
        status='Active'
    )
    db.session.add(admin)
    db.session.commit()
    response = testing_client.post('/login', json={
        'username': 'admin',
        'password': 'adminpassword'
    })
    assert response.status_code == 200

def test_root_endpoint(testing_client):
    response = testing_client.get('/')
    assert response.status_code == 200
    assert response.data == b'Hello, World!'

def test_skull_endpoint(testing_client):
    response = testing_client.get('/skull')
    assert response.status_code == 200
    assert b'This is the BACKEND SKULL' in response.data

def test_register_user(testing_client):
    response = testing_client.post('/register', json={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password',
        'country': 'Spain',
        'state': 'Madrid',
        'date_of_birth': '1980-01-01',
        'role': 'user',
        'status': 'Active'
    })
    assert response.status_code == 200

def test_login_user(testing_client):
    response = testing_client.post('/login', json={
        'username': 'testuser',
        'password': 'password'
    })
    assert response.status_code == 200

def test_login_user_wrong_password(testing_client):
    response = testing_client.post('/login', json={
        'username': 'testuser',
        'password': 'wrong_password'
    })
    assert response.status_code == 500

def test_login_user_wrong_username(testing_client):
    response = testing_client.post('/login', json={
        'username': 'wrong_username',
        'password': 'password'
    })
    assert response.status_code == 500

def test_get_accounts(testing_client, login_user):
    response = testing_client.get('/accounts')
    assert response.status_code == 200

def test_create_account(testing_client, login_user):
    response = testing_client.post('/accounts', json={
        'name': 'John Doe',
        'currency': '€',
        'country': 'Spain'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'John Doe'
    assert data['currency'] == '€'
    assert data['country'] == 'Spain'

def test_get_account_by_id(testing_client, login_user):
    create_response = testing_client.post('/accounts', json={
        'name': 'Alice',
        'currency': '€',
        'country': 'France'
    })
    assert create_response.status_code == 200
    account_data = create_response.get_json()
    account_id = account_data['id']

    response = testing_client.get(f'/accounts/{account_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Alice'
    assert data['currency'] == '€'
    assert data['country'] == 'France'
    assert data['id'] == account_id

def test_update_account(testing_client, login_user):
    create_response = testing_client.post('/accounts', json={
        'name': 'Bob',
        'currency': '£',
        'country': 'UK'
    })
    assert create_response.status_code == 200
    account_data = create_response.get_json()
    account_id = account_data['id']

    update_response = testing_client.put(f'/accounts/{account_id}', json={
        'name': 'Robert'
    })
    assert update_response.status_code == 200
    updated_data = update_response.get_json()
    assert updated_data['name'] == 'Robert'
    assert updated_data['currency'] == '£'
    assert updated_data['country'] == 'UK'
    assert updated_data['id'] == account_id

    get_response = testing_client.get(f'/accounts/{account_id}')
    assert get_response.status_code == 200
    get_data = get_response.get_json()
    assert get_data['name'] == 'Robert'

def test_delete_account(testing_client, login_user):
    create_response = testing_client.post('/accounts', json={
        'name': 'Charlie',
        'currency': '$',
        'country': 'USA'
    })
    assert create_response.status_code == 200
    account_data = create_response.get_json()
    account_id = account_data['id']

    delete_response = testing_client.delete(f'/accounts/{account_id}')
    assert delete_response.status_code == 200

    get_all_response = testing_client.get('/accounts')
    assert get_all_response.status_code == 200
    accounts_data = get_all_response.get_json()
    account_ids = [account['id'] for account in accounts_data.get('accounts', [])]
    assert account_id not in account_ids

def test_get_nonexistent_account(testing_client, login_user):
    response = testing_client.get('/accounts/9999')
    assert response.status_code == 500

def test_update_nonexistent_account(testing_client, login_user):
    response = testing_client.put('/accounts/9999', json={'name': 'DoesNotExist'})
    assert response.status_code == 500

def test_delete_nonexistent_account(testing_client, login_user):
    response = testing_client.delete('/accounts/9999')
    assert response.status_code == 500

def test_create_account_missing_fields(testing_client, login_user):
    response = testing_client.post('/accounts', json={'name': 'Incomplete'})
    assert response.status_code == 500

def test_create_transaction(testing_client, login_user):
    create_response = testing_client.post('/accounts', json={
        'name': 'Alice',
        'currency': '€',
        'country': 'France'
    })
    assert create_response.status_code == 200
    account_data = create_response.get_json()
    account_id = account_data['id']

    response = testing_client.post('/transactions', json={
        'account_id': account_id,
        'amount': 100.0
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['account_id'] == account_id
    assert data['amount'] == 100.0

def test_get_transactions(testing_client, login_user):
    response = testing_client.get('/transactions')
    assert response.status_code == 200

def test_send_money(testing_client, login_user):
    create_response_1 = testing_client.post('/accounts', json={
        'name': 'Alice',
        'currency': '€',
        'country': 'France'
    })
    assert create_response_1.status_code == 200
    account_data_1 = create_response_1.get_json()
    account_id_1 = account_data_1['id']

    create_response_2 = testing_client.post('/accounts', json={
        'name': 'Bob',
        'currency': '£',
        'country': 'UK'
    })
    assert create_response_2.status_code == 200
    account_data_2 = create_response_2.get_json()
    account_id_2 = account_data_2['id']

    update_response = testing_client.put(f'/accounts/{account_id_1}', json={
        'name': 'Alice',
        'balance': 200.0
    })
    assert update_response.status_code == 200

    response = testing_client.post('/send_money', json={
        'from_account_id': account_id_1,
        'to_account_id': account_id_2,
        'amount': 50.0
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Transaction successful'

def test_admin_create_user(testing_client, login_admin):
    response = testing_client.post('/admin/users', json={
        'username': 'newadmin',
        'email': 'newadmin@example.com',
        'password': 'adminpassword',
        'country': 'Spain',
        'state': 'Madrid',
        'date_of_birth': '1980-01-01',
        'role': 'admin',
        'status': 'Active'
    })
    assert response.status_code == 200

def test_admin_update_user(testing_client, login_admin):
    create_response = testing_client.post('/admin/users', json={
        'username': 'newadmin',
        'email': 'newadmin@example.com',
        'password': 'adminpassword',
        'country': 'Spain',
        'state': 'Madrid',
        'date_of_birth': '1980-01-01',
        'role': 'admin',
        'status': 'Active'
    })
    assert create_response.status_code == 200
    user_data = create_response.get_json()
    user_id = user_data['id']

    update_response = testing_client.put(f'/admin/users/{user_id}', json={
        'username': 'updatedadmin',
        'email': 'updatedadmin@example.com',
        'password': 'newadminpassword',
        'country': 'Spain',
        'state': 'Madrid',
        'date_of_birth': '1980-01-01',
        'role': 'admin',
        'status': 'Active'
    })
    assert update_response.status_code == 200
    updated_data = update_response.get_json()
    assert updated_data['username'] == 'updatedadmin'
    assert updated_data['email'] == 'updatedadmin@example.com'

def test_admin_delete_user(testing_client, login_admin):
    create_response = testing_client.post('/admin/users', json={
        'username': 'newadmin',
        'email': 'newadmin@example.com',
        'password': 'adminpassword',
        'country': 'Spain',
        'state': 'Madrid',
        'date_of_birth': '1980-01-01',
        'role': 'admin',
        'status': 'Active'
    })
    assert create_response.status_code == 200
    user_data = create_response.get_json()
    user_id = user_data['id']

    delete_response = testing_client.delete(f'/admin/users/{user_id}')
    assert delete_response.status_code == 200

    get_response = testing_client.get(f'/admin/users/{user_id}')
    assert get_response.status_code == 500