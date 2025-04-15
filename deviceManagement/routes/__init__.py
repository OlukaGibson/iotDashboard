from flask import Blueprint
import os
import json
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()

# Create main blueprint
device_management = Blueprint('device_management', __name__)

# Load the JSON credentials from the environment variable
google_credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

# Parse the JSON credentials 
credentials_dict = json.loads(google_credentials_json)
credentials = service_account.Credentials.from_service_account_info(credentials_dict)

def clean_data(data):
    return None if data == "" else data

# Import all routes
from .dashboard_routes import *
from .device_routes import * 
from .data_routes import *
from .profile_routes import *
from .file_routes import *
from .firmware_routes import *