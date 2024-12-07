from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging
from datetime import timedelta, datetime
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///local.db')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.permanent_session_lifetime = timedelta(days=1)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Configure CORS
CORS(app, supports_credentials=True)

# Select environment based on the ENV environment variable
env = os.getenv('ENV')
if env == 'local':
    app.config.from_object('config.LocalConfig')
elif env == 'development':
    app.config.from_object('config.DevelopmentConfig')
elif env == 'ghci':
    app.config.from_object('config.GithubCIConfig')

# Configure Azure Application Insights
app.config['APPINSIGHTS_INSTRUMENTATIONKEY'] = os.environ.get('APPINSIGHTS_INSTRUMENTATIONKEY')

if app.config['APPINSIGHTS_INSTRUMENTATIONKEY']:
    handler = AzureLogHandler(connection_string=f'InstrumentationKey={app.config["APPINSIGHTS_INSTRUMENTATIONKEY"]}')
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)

from iebank_api.models import Account, User, Transaction

def create_admin_user():
    with app.app_context():
        # Define the admin user details
        username = 'adminuser'
        email = 'adminuser@example.com'
        password = 'adminpassword123'
        country = 'USA'
        date_of_birth = '2004-06-29'
        role = 'admin'
        status = 'active'

        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Convert date_of_birth to a datetime object
        date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d')

        # Create the new admin user
        new_user = User(
            username=username,
            email=email,
            password=hashed_password,
            country=country,
            date_of_birth=date_of_birth,
            role=role,
            status=status
        )

        # Add the new user to the database
        # if the new user does not already exist
        if User.query.filter_by(username=username).first():
            print(f"Admin user '{username}' already exists.")
            return
        
        db.session.add(new_user)
        db.session.commit()

        print(f"Admin user '{username}' created successfully.")

with app.app_context():
    db.create_all()
    create_admin_user()

from iebank_api import routes
