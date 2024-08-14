from flask import Blueprint, redirect, url_for, render_template, request, send_file, jsonify
import os
from .extentions import db
from .models import Devices, MetadataValues, Firmware
from google.cloud import storage
import io
import json
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()

device_management = Blueprint('device_management', __name__)

# Load the JSON credentials from the environment variable
google_credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

# Parse the JSON credentials 
credentials_dict = json.loads(google_credentials_json)
credentials = service_account.Credentials.from_service_account_info(credentials_dict)


@device_management.route('/')
def device_storage():
    print('Device storage is full!')
    return {'message': 'Device storage is full!'}

@device_management.route('/device', methods=['GET', 'POST'])
def add_device():
    if request.method == 'POST':
        data = request.get_json()

        # Extract fields from request data with default value None if not present
        name = data.get('name')
        readkey = data.get('readkey')
        writekey = data.get('writekey')
        file_download_state = data.get('file_download_state')
        
        fields = {}
        for i in range(1, 21):
            fields[f'field{i}'] = data.get(f'field{i}', None)
        
        # Create a new device object
        new_device = Devices(name=name, readkey=readkey, writekey=writekey, file_download_state=file_download_state, **fields)

        # Add the new device to the database and commit the transaction
        db.session.add(new_device)
        db.session.commit()

        return {'message': 'New device added!'}
    
    return {'message': 'Use POST method to add a new device!'}

@device_management.route('/device/<int:id>/update', methods=['GET'])
def update_device_data(id):
    # Retrieve the device from the database
    device = db.session.get(Devices, id)
    
    # Retrieve the api_key from the query parameters
    writekey = request.args.get('api_key')
    
    # Check if the device exists and the provided writekey matches the device's writekey
    if device and writekey == device.writekey:
        # Retrieve optional fields from the query parameters using a loop
        fields = {}
        for i in range(1, 21):
            fields[f'field{i}'] = request.args.get(f'field{i}', None)

        # Create a new entry in the MetadataValues table
        new_entry = MetadataValues(
            deviceID=device.id,
            **fields
        )

        # Add the new entry to the database and commit
        db.session.add(new_entry)
        db.session.commit()

        return {'message': 'Device data updated successfully!'}
    
    return {'message': 'Invalid API key!'}, 403

@device_management.route('/firmwareupload', methods=['POST'])
def firmware_upload():
    # Retrieve the file from the request
    file = request.files['file']
    firmwareVersion = request.form['firmwareVersion']
    description = request.form['description']
    
    storage_client = storage.Client(credentials=credentials)

    bucket = storage_client.bucket(os.getenv('BUCKET_NAME'))

    # Create a new blob object
    blob = bucket.blob(f'{firmwareVersion}.hex')
    blob.upload_from_file(file)
    db.session.add(Firmware(firmwareVersion, description))
    db.session.commit()

    print('firmwareVersion is ', firmwareVersion)

    return {'message': 'Firmware uploaded successfully!'}

@device_management.route('/firmware/<string:firmwareVersion>/download', methods=['GET'])
def firmware_download(firmwareVersion):
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(os.getenv('BUCKET_NAME'))
    blob = bucket.blob(f'{firmwareVersion}.hex')
    
    # Download the blob into a bytes buffer
    file_data = blob.download_as_string()
    file_buffer = io.BytesIO(file_data)
    file_buffer.seek(0)

    print('firmwareVersion is ', firmwareVersion)

    return send_file(
        file_buffer,
        as_attachment=True,
        download_name=f'{firmwareVersion}.hex',
        mimetype='application/octet-stream'
    )

