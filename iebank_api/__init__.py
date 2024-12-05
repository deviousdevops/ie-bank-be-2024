from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging
from datetime import timedelta
from create_admin import create_admin_user

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

with app.app_context():
    db.create_all()
    create_admin_user(app, db)

from iebank_api import routes
