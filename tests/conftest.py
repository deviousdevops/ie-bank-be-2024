import pytest
from iebank_api import db, app
from datetime import datetime
from iebank_api.models import Account, Transaction, User
from werkzeug.security import generate_password_hash

@pytest.fixture(scope="function")
def test_app():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    with app.app_context():
        yield app

@pytest.fixture(scope="function")
def test_client(test_app):
    return test_app.test_client()

@pytest.fixture(scope="function")
def init_database(test_app):
    with test_app.app_context():
        # Import models here to ensure they are registered before creating the tables
        from iebank_api.models import User, Account, Transaction
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture
def sample_user(test_app):
    user = User(
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('test1234'),
        country='Testland',
        date_of_birth=datetime.strptime('1990-01-01', '%Y-%m-%d')
    )
    db.session.add(user)
    db.session.commit()
    yield user
    db.session.delete(user)
    db.session.commit()


@pytest.fixture
def admin_user(test_app):
    admin = User(
        username='admin',
        email='admin@example.com',
        password=generate_password_hash('adminpass'),
        country='Adminland',
        date_of_birth=datetime.strptime('1980-01-01', '%Y-%m-%d'),
        role='admin'
    )
    db.session.add(admin)
    db.session.commit()
    yield admin
    db.session.delete(admin)
    db.session.commit()