from flask import Blueprint, redirect, url_for, render_template, request, send_file, jsonify
import os
from .extentions import db
from .models import Devices, MetadataValues, Firmware
from google.cloud import storage
import io
import json
from google.oauth2 import service_account
from dotenv import load_dotenv
from intelhex import IntelHex
from datetime import datetime

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
Firmware management related routes for firmware management
"""
# Define a route to upload firmware
@device_management.route('/firmwareupload', methods=['POST'])
def firmware_upload():
    file = request.files['file']
    firmwareVersion = request.form['firmwareVersion']
    description = request.form['description']
    documentation = request.form.get('documentation', None)
    documentationLink = request.form.get('documentationLink', None)
    
    # Read the file as a string (assuming it's a text-based hex file)
    file_content = file.read().decode('utf-8')  # Decode the file to string

    changes = {}
    for i in range(1, 11):
        changes[f'change{i}'] = request.form.get(f'change{i}', None)

    # Initialize IntelHex with the decoded string
    hex_file = IntelHex(io.StringIO(file_content))  # Use StringIO for string input
    bin_data = io.BytesIO()
    hex_file.tobinfile(bin_data)
    bin_data.seek(0)

    # Upload to Google Cloud Storage
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(os.getenv('BUCKET_NAME'))
    blob = bucket.blob(f'{firmwareVersion}.bin')
    blob.upload_from_file(bin_data, content_type='application/octet-stream')

    # Add firmware to database
    new_firmware = Firmware(
        firmwareVersion=firmwareVersion, 
        description=description,
        documentation=documentation,
        documentationLink=documentationLink,
        **changes
    )
    
    db.session.add(new_firmware)
    db.session.commit()
    
    return {'message': 'Firmware uploaded successfully!'}

# Define a route to download firmware
@device_management.route('/firmware/<string:firmwareVersion>/download', methods=['GET'])
def firmware_download(firmwareVersion):
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(os.getenv('BUCKET_NAME'))
    blob = bucket.blob(f'{firmwareVersion}.bin')
    
    file_data = blob.download_as_string()
    file_buffer = io.BytesIO(file_data)
    file_buffer.seek(0)

    return send_file(
        file_buffer,
        as_attachment=True,
        download_name=f'{firmwareVersion}.bin',
        mimetype='application/octet-stream'
    )

# Define a route to retrieve all firmware versions
@device_management.route('/firmware/display', methods=['GET'])
def get_firmwares():
    firmware = db.session.query(Firmware).all()
    firmware_list = []
    for version in firmware:
        firmware_list.append({
            'firmwareVersion': version.firmwareVersion,
            'description': version.description,
            'documentation': version.documentation,
            'documentationLink': version.documentationLink,
            'created_at': version.created_at,
            'changes': {
                'change1': version.change1,
                'change2': version.change2,
                'change3': version.change3,
                'change4': version.change4,
                'change5': version.change5,
                'change6': version.change6,
                'change7': version.change7,
                'change8': version.change8,
                'change9': version.change9,
                'change10': version.change10
            },
            'created_at': version.created_at
        })
    
    return jsonify(firmware_list)

# Define a route to retrieve a specific firmware version
@device_management.route('/firmware/<string:firmwareVersion>', methods=['GET'])
def get_firmware(firmwareVersion):
    firmware = db.session.query(Firmware).filter_by(firmwareVersion=firmwareVersion).first()
    if firmware:
        firmware_dict = {
            'firmwareVersion': firmware.firmwareVersion,
            'description': firmware.description,
            'documentation': firmware.documentation,
            'documentationLink': firmware.documentationLink,
            'created_at': firmware.created_at,
            'changes': {
                # 'change1': firmware.change1,
                # 'change2': firmware.change2,
                # 'change3': firmware.change3,
                # 'change4': firmware.change4,
                # 'change5': firmware.change5,
                # 'change6': firmware.change6,
                # 'change7': firmware.change7,
                # 'change8': firmware.change8,
                # 'change9': firmware.change9,
                # 'change10': firmware.change10
            }
        }
        for i in range(1, 11):
            firmware_dict['changes'][f'change{i}'] = getattr(firmware, f'change{i}')
        
        return jsonify(firmware_dict)
    
    return {'message': 'Firmware version not found!'}, 404


"""
Device related routes for device management
"""
# Define a route to add a new device
@device_management.route('/adddevice', methods=['GET', 'POST'])
def add_device():
    if request.method == 'POST':
        # Extract fields from form data with default value None if not present
        name = request.form.get('name')
        readkey = request.form.get('readkey')
        writekey = request.form.get('writekey')
        deviceID = request.form.get('deviceID')
        currentFirmwareVersion = request.form.get('currentFirmwareVersion', None)
        previousFirmwareVersion = request.form.get('previousFirmwareVersion', None)
        targetFirmwareVersion = request.form.get('targetFirmwareVersion', None)
        fileDownloadState = request.form.get('fileDownloadState', False)
        
        # Extract dynamic fields from form data (field1 to field20)
        fields = {}
        for i in range(1, 21):
            fields[f'field{i}'] = request.form.get(f'field{i}', None)
        
        # Create a new device object
        new_device = Devices(
            name=name,
            readkey=readkey,
            writekey=writekey,
            deviceID=deviceID,
            currentFirmwareVersion=currentFirmwareVersion,
            previousFirmwareVersion=previousFirmwareVersion,
            targetFirmwareVersion=targetFirmwareVersion,
            fileDownloadState=fileDownloadState,
            **fields
        )

        # Add the new device to the database and commit the transaction
        db.session.add(new_device)
        db.session.commit()

        return {'message': 'New device added successfully!'}
    
    return {'message': 'Use POST method to add a new device!'}


# Define a route to retrieve all devices
@device_management.route('/get_devices', methods=['GET'])
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
            'targetFirmwareVersion': device.targetFirmwareVersion,
            'created_at': device.created_at,
            'fields': {}
        }
        for i in range(1, 21):
            device_dict['fields'][f'field{i}'] = getattr(device, f'field{i}')
        
        devices_list.append(device_dict)
    
    return jsonify(devices_list)

# Define a route to retrieve a specific device
@device_management.route('/get_device/<int:deviceID>', methods=['GET'])
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

# Edit device data
@device_management.route('/device/<int:deviceID>/edit', methods=['GET', 'POST'])
def edit_device(deviceID):
    device = db.session.query(Devices).filter_by(deviceID=deviceID).first()

    if not device:
        return {'message': 'Device not found!'}, 404

    if request.method == 'POST':
        # Extract form data with default value as current device data if not provided
        name = request.form.get('name', device.name)
        readkey = request.form.get('readkey', device.readkey)
        writekey = request.form.get('writekey', device.writekey)
        currentFirmwareVersion = request.form.get('currentFirmwareVersion', device.currentFirmwareVersion)
        previousFirmwareVersion = request.form.get('previousFirmwareVersion', device.previousFirmwareVersion)
        targetFirmwareVersion = request.form.get('targetFirmwareVersion', device.targetFirmwareVersion)
        fileDownloadState = request.form.get('fileDownloadState', device.fileDownloadState)

        fields = {}
        for i in range(1, 21):
            fields[f'field{i}'] = request.form.get(f'field{i}', getattr(device, f'field{i}'))

        device.name = name
        device.readkey = readkey
        device.writekey = writekey
        device.currentFirmwareVersion = currentFirmwareVersion
        device.previousFirmwareVersion = previousFirmwareVersion
        device.targetFirmwareVersion = targetFirmwareVersion
        device.fileDownloadState = fileDownloadState

        # Update dynamic fields
        for field, value in fields.items():
            setattr(device, field, value)

        # Commit the changes to the database
        db.session.commit()

        return {'message': 'Device updated successfully!'}

    return {'message': 'Use POST method to update device data!'}



"""
Data related routes for data management
"""
# Define a route to update device data
@device_management.route('/device/<int:deviceID>/update', methods=['GET'])
def update_device_data(deviceID):
    device = db.session.query(Devices).filter_by(deviceID=deviceID).first()
    # print('device is ', device)
    
    # Retrieve the api_key from the query parameters
    writekey = request.args.get('api_key')
    
    # Check if the device exists and the provided writekey matches the device's writekey
    if device and writekey == device.writekey:
        # Updating data fields
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

        if device.fileDownloadState:
            firmwareID = device.targetFirmwareVersion
            firmware = db.session.query(Firmware).filter_by(id=firmwareID).first()
            firmwareVersion = firmware.firmwareVersion
            # firmwareVersion
            storage_client = storage.Client(credentials=credentials)
            bucket = storage_client.bucket(os.getenv('BUCKET_NAME'))
            blob = bucket.blob(f'{firmwareVersion}.bin')
    
            file_data = blob.download_as_string()
            file_buffer = io.BytesIO(file_data)
            file_buffer.seek(0)

            device.fileDownloadState = False
            db.session.commit()

            return send_file(
                file_buffer,
                as_attachment=True,
                download_name=f'{firmwareVersion}.bin',
                mimetype='application/octet-stream'
            )

        return {'message': 'Device data updated successfully!'}
    
    return {'message': 'Invalid API key!'}, 403

# Define a route to retrieve device data
@device_management.route('/device/<int:deviceID>/data', methods=['GET'])
def get_device_data(deviceID):
    # Retrieve the device from the database
    device = db.session.query(Devices).filter_by(deviceID=deviceID).first()
    
    # Retrieve the api_key from the query parameters
    readkey = device.readkey
    
    # Check if the device exists and the provided readkey matches the device's readkey
    if device and readkey == device.readkey:
        # Retrieve all entries from the MetadataValues table for the device
        entries = db.session.query(MetadataValues).filter_by(deviceID=deviceID).all()
        entries_list = []
        for entry in entries:
            entry_dict = {
                'deviceID': entry.deviceID,
                'created_at': entry.created_at,
                'fields': {}
            }
            for i in range(1, 21):
                entry_dict['fields'][f'field{i}'] = getattr(entry, f'field{i}')
            
            entries_list.append(entry_dict)
        
        return jsonify(entries_list)
    
    return {'message': 'Invalid API key!'}, 403


"""
File management related routes for file management
"""
# Define a route to upload a file
@device_management.route('/device/<int:deviceID>/fileupload', methods=['POST'])
def file_upload(deviceID):
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file part in the request'}), 400
    
    device = db.session.query(Devices).filter_by(deviceID=deviceID).first()
    writekey = request.args.get('api_key')

    # if not device or writekey != device.writekey:
    #     return jsonify({'error': 'Unauthorized access'}), 403

    try:
        storage_client = storage.Client(credentials=credentials)
        bucket_name = os.getenv('BUCKET_NAME')
        if not bucket_name:
            raise ValueError("Bucket name not set in environment variables")

        bucket = storage_client.bucket(bucket_name)
        
        # Get current date and time for the file path
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        blob_path = f'data/{deviceID}/{current_date}/{current_time}.csv'
        blob = bucket.blob(blob_path)
        
        blob.upload_from_file(file, content_type='text/csv')
        
        return jsonify({'message': 'File uploaded successfully!', 'file_path': blob_path}), 200

    except Exception as e:
        # Log the error or print it to the console
        print(f"File upload failed: {e}")
        return jsonify({'error': 'File upload failed', 'details': str(e)}), 500
    
# def firmware_upload():
#     file = request.files['file']
#     firmwareVersion = request.form['firmwareVersion']
#     description = request.form['description']
#     documentation = request.form.get('documentation', None)
#     documentationLink = request.form.get('documentationLink', None)
    
#     # Read the file as a string (assuming it's a text-based hex file)
#     file_content = file.read().decode('utf-8')  # Decode the file to string

#     changes = {}
#     for i in range(1, 11):
#         changes[f'change{i}'] = request.form.get(f'change{i}', None)

#     # Initialize IntelHex with the decoded string
#     hex_file = IntelHex(io.StringIO(file_content))  # Use StringIO for string input
#     bin_data = io.BytesIO()
#     hex_file.tobinfile(bin_data)
#     bin_data.seek(0)

#     # Upload to Google Cloud Storage
#     storage_client = storage.Client(credentials=credentials)
#     bucket = storage_client.bucket(os.getenv('BUCKET_NAME'))
#     blob = bucket.blob(f'{firmwareVersion}.bin')
#     blob.upload_from_file(bin_data, content_type='application/octet-stream')

#     # Add firmware to database
#     new_firmware = Firmware(
#         firmwareVersion=firmwareVersion, 
#         description=description,
#         documentation=documentation,
#         documentationLink=documentationLink,
#         **changes
#     )
    
#     db.session.add(new_firmware)
#     db.session.commit()
    
#     return {'message': 'Firmware uploaded successfully!'}