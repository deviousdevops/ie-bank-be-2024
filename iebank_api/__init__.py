from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging
from datetime import timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.permanent_session_lifetime = timedelta(days=1)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Configure CORS
CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": os.environ.get('CORS_ORIGINS', 'http://localhost:8080').split(','),
        "allow_headers": ["Content-Type", "Authorization", "x-access-token"],
        "expose_headers": ["Access-Control-Allow-Origin"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    }
})

# Select environment based on the ENV environment variable
env = os.getenv('ENV', 'local')
if env == 'local':
    app.config.from_object('config.LocalConfig')
elif env == 'dev':
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

with app.app_context():
    db.create_all()

from iebank_api import routes
