import os
from flask import Flask
from .extentions import db
from .routes import device_management
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    # Remove SQLAlchemy configurations
    # app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')

    # db.init_app(app) - Not needed for Firestore
    # migrate.init_app(app, db) - Not needed for Firestore

    CORS(app, origins="*")

    app.register_blueprint(device_management)

    return app