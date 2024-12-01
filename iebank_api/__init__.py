from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging
from datetime import timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.permanent_session_lifetime = timedelta(days=1)  # Set session lifetime

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Configure CORS to allow credentials and specify allowed origins for production
if os.getenv('ENV') == 'production':
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:8080"}})
else:
    # For local development
    CORS(app, supports_credentials=True, resources={
        r"/*": {
            "origins": "http://localhost:8080",
            "allow_headers": ["Content-Type", "Authorization", "x-access-token"],  # Allow x-access-token header
            "expose_headers": ["Access-Control-Allow-Origin"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        }
    })

# Select environment based on the ENV environment variable
if os.getenv('ENV') == 'local':
    print("Running in local mode")
    app.config.from_object('config.LocalConfig')
elif os.getenv('ENV') == 'dev':
    print("Running in development mode")
    app.config.from_object('config.DevelopmentConfig')
elif os.getenv('ENV') == 'ghci':
    print("Running in github mode")
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

with app.app_context():
    # Uncomment to add the country column to the account table
    # query = text("ALTER TABLE account ADD COLUMN country VARCHAR(32)")
    # db.session.execute(query)
    # db.session.commit()

    db.create_all()

from iebank_api import routes
