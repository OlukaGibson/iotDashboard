from flask import Blueprint
import os
import json
from google.oauth2 import service_account
from dotenv import load_dotenv
import zlib

load_dotenv()

# Create main blueprint
device_management = Blueprint('device_management', __name__)

# Load the JSON credentials from the environment variable
google_credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

if google_credentials_json:
    # Parse the JSON credentials 
    credentials_dict = json.loads(google_credentials_json)
    credentials = service_account.Credentials.from_service_account_info(credentials_dict)
else:
    # Use default credentials if environment variable is not set
    credentials = None

def clean_data(data):
    return None if data == "" else data

def calculate_crc32(file_path):
    """Calculate the CRC32 of a file."""
    crc = 0
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            crc = zlib.crc32(chunk, crc)
    return format(crc & 0xFFFFFFFF, '08X')

# Import all routes
from .profile_routes import *
from .firmware_routes import *
from .device_routes import * 
from .dashboard_routes import *
from .data_routes import *
from .file_routes import *