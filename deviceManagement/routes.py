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

# Define a route for landing page
@device_management.route('/')
def device_storage():
    print('Device storage is full!')
    return {'message': 'Device storage is full!'}


"""
Device related routes for device management
"""
# Define a route to add a new device
@device_management.route('/device', methods=['GET', 'POST'])
def add_device():
    if request.method == 'POST':
        data = request.get_json()

        # Extract fields from request data with default value None if not present
        name = data.get('name')
        readkey = data.get('readkey')
        writekey = data.get('writekey')
        deviceID = data.get('deviceID')
        currentFirmwareVersion = data.get('currentFirmwareVersion', None)
        previousFirmwareVersion = data.get('previousFirmwareVersion', None)
        fileDownloadState = data.get('fileDownloadState', None)
        
        fields = {}
        for i in range(1, 21):
            fields[f'field{i}'] = data.get(f'field{i}', None)
        
        # Create a new device object
        new_device = Devices(name=name, readkey=readkey, writekey=writekey, deviceID=deviceID, currentFirmwareVersion=currentFirmwareVersion, previousFirmwareVersion=previousFirmwareVersion, fileDownloadState=fileDownloadState, **fields)

        # Add the new device to the database and commit the transaction
        db.session.add(new_device)
        db.session.commit()

        return {'message': 'New device added!'}
    
    return {'message': 'Use POST method to add a new device!'}

# Define a route to retrieve all devices
@device_management.route('/devices', methods=['GET'])
def get_devices():
    devices = db.session.query(Devices).all()
    devices_list = []
    for device in devices:
        device_dict = {
            'name': device.name,
            'readkey': device.readkey,
            'writekey': device.writekey,
            'deviceID': device.deviceID,
            'currentFirmwareVersion': device.currentFirmwareVersion,
            'previousFirmwareVersion': device.previousFirmwareVersion,
            'fileDownloadState': device.fileDownloadState,
            'fields': {}
        }
        for i in range(1, 21):
            device_dict['fields'][f'field{i}'] = getattr(device, f'field{i}')
        
        devices_list.append(device_dict)
    
    return jsonify(devices_list)

# Define a route to retrieve a specific device
@device_management.route('/device/<int:deviceID>', methods=['GET'])
def get_device(deviceID):
    device = db.session.query(Devices).filter_by(deviceID=deviceID).first()
    if device:
        device_dict = {
            'name': device.name,
            'readkey': device.readkey,
            'writekey': device.writekey,
            'deviceID': device.deviceID,
            'currentFirmwareVersion': device.currentFirmwareVersion,
            'previousFirmwareVersion': device.previousFirmwareVersion,
            'fileDownloadState': device.fileDownloadState,
            'fields': {}
        }
        for i in range(1, 21):
            device_dict['fields'][f'field{i}'] = getattr(device, f'field{i}')
        
        return jsonify(device_dict)
    
    return {'message': 'Device not found!'}, 404


"""
Data related routes for data management
"""
# Define a route to update device data
@device_management.route('/device/<int:deviceID>/update', methods=['GET'])
def update_device_data(deviceID):
    # Retrieve the device from the database
    device = db.session.query(Devices).filter_by(deviceID=deviceID).first()
    print('device is ', device)
    
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
            deviceID=device.deviceID,
            **fields
        )

        # Add the new entry to the database and commit
        db.session.add(new_entry)
        db.session.commit()

        return {'message': 'Device data updated successfully!'}
    
    return {'message': 'Invalid API key!'}, 403

# Define a route to retrieve device data
@device_management.route('/device/<int:deviceID>/data', methods=['GET'])
def get_device_data(deviceID):
    # Retrieve the device from the database
    device = db.session.query(Devices).filter_by(deviceID=deviceID).first()
    
    # Retrieve the api_key from the query parameters
    readkey = request.args.get('api_key')
    
    # Check if the device exists and the provided readkey matches the device's readkey
    if device and readkey == device.readkey:
        # Retrieve all entries from the MetadataValues table for the device
        entries = db.session.query(MetadataValues).filter_by(deviceID=deviceID).all()
        entries_list = []
        for entry in entries:
            entry_dict = {
                'deviceID': entry.deviceID,
                'fields': {}
            }
            for i in range(1, 21):
                entry_dict['fields'][f'field{i}'] = getattr(entry, f'field{i}')
            
            entries_list.append(entry_dict)
        
        return jsonify(entries_list)
    
    return {'message': 'Invalid API key!'}, 403



"""
Firmware management related routes for firmware management
"""
# Define a route to upload firmware
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

# Define a route to download firmware
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

# Define a route to retrieve all firmware versions
@device_management.route('/firmware', methods=['GET'])
def get_firmware():
    firmware = db.session.query(Firmware).all()
    firmware_list = []
    for version in firmware:
        firmware_list.append({
            'firmwareVersion': version.firmwareVersion,
            'description': version.description,
            'created_at': version.created_at
        })
    
    return jsonify(firmware_list)