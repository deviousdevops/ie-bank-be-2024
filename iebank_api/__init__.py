from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging
from datetime import timedelta

def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local.db'
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
        app.permanent_session_lifetime = timedelta(days=1)

        # Select environment based on the ENV environment variable
        if os.getenv('ENV') == 'local':
            print("Running in local mode")
            app.config.from_object('config.LocalConfig')
        elif os.getenv('ENV') == 'dev':
            print("Running in development mode")
            app.config.from_object('config.DevelopmentConfig')
        elif os.getenv('ENV') == 'uat':
            print("Running in uat mode")
            app.config.from_object('config.UATConfig')
        elif os.getenv('ENV') == 'ghci':
            print("Running in github mode")
            app.config.from_object('config.GithubCIConfig')
    else:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Configure CORS
    if os.getenv('ENV') == 'production':
        CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:8080"}})
    else:
        CORS(app, supports_credentials=True, resources={
            r"/*": {
                "origins": "http://localhost:8080",
                "allow_headers": ["Content-Type", "Authorization", "x-access-token"],
                "expose_headers": ["Access-Control-Allow-Origin"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
            }
        })

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

    return app

# Initialize SQLAlchemy and Migrate outside of create_app
db = SQLAlchemy()
migrate = Migrate()
