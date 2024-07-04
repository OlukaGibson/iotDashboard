import os
from flask import Flask
from .extentions import db, migrate
from .routes import device_management

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(device_management)

    return app