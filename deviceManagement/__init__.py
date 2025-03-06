import os
from flask import Flask
from .extentions import db, migrate
from .routes import device_management
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')

    db.init_app(app)
    migrate.init_app(app, db)

    CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])

    app.register_blueprint(device_management)

    return app
