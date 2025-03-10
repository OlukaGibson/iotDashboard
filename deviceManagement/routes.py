from flask import Blueprint, redirect, url_for, render_template, request, send_file, jsonify
import os
from .extentions import db
from .models import Devices, MetadataValues, Firmware, DeviceFiles, Profiles
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


def clean_data(data):
    return None if data == "" else data


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
    firmware = request.files.get('firmware')
    firmware_bootloader = request.files.get('firmware_bootloader', None)
    firmwareVersion = request.form.get('firmwareVersion')
    description = clean_data(request.form.get('description', None))

    # Read the file as a string (assuming it's a text-based hex file)
    firmware_content = firmware.read().decode('utf-8')
    firmware_bootloader_content = firmware_bootloader.read().decode('utf-8') if firmware_bootloader else None

    changes = {}
    for i in range(1, 11):
        changes[f'change{i}'] = clean_data(request.form.get(f'change{i}', None))

    # uploading firmware to google cloud storage
    if firmware.filename.endswith('.hex'):
        firmware_hex = IntelHex(io.StringIO(firmware_content))
        bin_data = io.BytesIO()
        firmware_hex.tobinfile(bin_data)
        bin_data.seek(0)

        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.bucket(os.getenv('BUCKET_NAME'))

        # bin file storage
        blob = bucket.blob(f'firmware/firmware_file_bin/{firmwareVersion}.bin')
        blob.upload_from_file(bin_data, content_type='application/octet-stream')
        firmware_string = f'firmware/firmware_file_bin/{firmwareVersion}.bin'

        # hex file storage
        blob_hex = bucket.blob(f'firmware/firmware_file_hex/{firmwareVersion}.hex')
        blob_hex.upload_from_string(firmware_content, content_type='text/plain')
        firmware_string_hex = f'firmware/firmware_file_hex/{firmwareVersion}.hex'

        # bootloader file storage
        if firmware_bootloader:
            blob_bootloader = bucket.blob(f'firmware/firmware_file_bootloader/{firmwareVersion}_bootloader.hex')
            blob_bootloader.upload_from_string(firmware_bootloader_content, content_type='text/plain')
            firmware_string_bootloader = f'firmware/firmware_file_bootloader/{firmwareVersion}_bootloader.hex'
        else:
            firmware_string_bootloader = None

    else:
        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.bucket(os.getenv('BUCKET_NAME'))
        blob = bucket.blob(f'firmware/firmware_file/{firmwareVersion}{os.path.splitext(firmware.filename)[1]}')
        blob.upload_from_file(firmware, content_type=firmware.content_type)
        firmware_string = f'firmware/firmware_file/{firmwareVersion}{os.path.splitext(firmware.filename)[1]}'
        firmware_string_hex = None
        firmware_string_bootloader = None

    # Add firmware to database
    new_firmware = Firmware(
        firmwareVersion=firmwareVersion,
        firmware_string=firmware_string,
        firmware_string_hex=firmware_string_hex,
        firmware_string_bootloader=firmware_string_bootloader,
        description=description,
        **changes
    )

    db.session.add(new_firmware)
    db.session.commit()

    return {'message': 'Firmware uploaded successfully!'}

# Define a route to download firmware bin file
@device_management.route('/firmware/<string:firmwareVersion>/download/firwmwarebin', methods=['GET'])
def firmware_download(firmwareVersion):
    firmware = db.session.query(Firmware).filter_by(firmwareVersion=firmwareVersion).first()
    
    if firmware:
        firmware_string = firmware.firmware_string
        if not firmware_string:
            return {'message': 'Firmware bin file not found!'}, 404
        
        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.bucket(os.getenv('BUCKET_NAME'))
        blob = bucket.blob(firmware_string)

        file_data = blob.download_as_string()
        file_buffer = io.BytesIO(file_data)
        file_buffer.seek(0)

        return send_file(
            file_buffer,
            as_attachment=True,
            download_name=f'{firmwareVersion}.bin',
            mimetype='application/octet-stream'
        )
    
    return {'message': 'Firmware version not found!'}, 404

# Define a route to download firmware hex file
@device_management.route('/firmware/<string:firmwareVersion>/download/firwmwarehex', methods=['GET'])
def firmware_download_hex(firmwareVersion):
    firmware = db.session.query(Firmware).filter_by(firmwareVersion=firmwareVersion).first()

    if firmware:
        firmware_string = firmware.firmware_string_hex
        if not firmware_string:
            return {'message': 'Firmware hex file not found!'}, 404
        
        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.bucket(os.getenv('BUCKET_NAME'))
        blob = bucket.blob(firmware_string)

        file_data = blob.download_as_string()
        file_buffer = io.BytesIO(file_data)
        file_buffer.seek(0)

        return send_file(
            file_buffer,
            as_attachment=True,
            download_name=f'{firmwareVersion}.hex',
            mimetype='text/plain'
        )
    
    return {'message': 'Firmware version not found!'}, 404

# Define a route to download firmware bootloader file
@device_management.route('/firmware/<string:firmwareVersion>/download/firwmwarebootloader', methods=['GET'])
def firmware_download_bootloader(firmwareVersion):
    firmware = db.session.query(Firmware).filter_by(firmwareVersion=firmwareVersion).first()

    if firmware:
        firmware_string = firmware.firmware_string_bootloader
        if not firmware_string:
            return {'message': 'Firmware bootloader file not found!'}, 404
        
        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.bucket(os.getenv('BUCKET_NAME'))
        blob = bucket.blob(firmware_string)

        file_data = blob.download_as_string()
        file_buffer = io.BytesIO(file_data)
        file_buffer.seek(0)

        return send_file(
            file_buffer,
            as_attachment=True,
            download_name=f'{firmwareVersion}_bootloader.hex',
            mimetype='text/plain'
        )
    
    return {'message': 'Firmware version not found!'}, 404

# Define a route to retrieve all firmware versions
@device_management.route('/firmware/display', methods=['GET'])
def get_firmwares():
    firmwares = db.session.query(Firmware).all()
    firmwares_list = []
    for version in firmwares:
        changes = {}
        for i in range(1, 11):
            change_value = getattr(version, f'change{i}')
            if change_value is not None:
                changes[f'change{i}'] = change_value

        firmwares_list.append({
            'id': version.id,
            'firmwareVersion': version.firmwareVersion,
            'firmware_string': version.firmware_string,
            'firmware_string_hex': version.firmware_string_hex,
            'firmware_string_bootloader': version.firmware_string_bootloader,
            'description': version.description,
            'created_at': version.created_at,
            'changes': changes,
            'updated_at': version.updated_at
        })
    
    return jsonify(firmwares_list)

# Define a route to retrieve a specific firmware version
@device_management.route('/firmware/<string:firmwareVersion>', methods=['GET'])
def get_firmware(firmwareVersion):
    firmware = db.session.query(Firmware).filter_by(firmwareVersion=firmwareVersion).first()
    if firmware:
        firmware_dict = {
            'firmwareVersion': firmware.firmwareVersion,
            'firmware_string': firmware.firmware_string,
            'firmware_string_hex': firmware.firmware_string_hex,
            'firmware_string_bootloader': firmware.firmware_string_bootloader,
            'description': firmware.description,
            'created_at': firmware.created_at,
            'updated_at': firmware.updated_at,
            'changes': {
            }
        }
        for i in range(1, 11):
            if getattr(firmware, f'change{i}'):
                firmware_dict['changes'][f'change{i}'] = getattr(firmware, f'change{i}')
        
        return jsonify(firmware_dict)
    
    return {'message': 'Firmware version not found!'}, 404


"""
Device related routes for device management
"""
# Define a route to add a new device
@device_management.route('/adddevice', methods=['POST'])
def add_device():
    # Extract fields from form data with default value None if not present
    name = clean_data(request.form.get('name'))
    readkey = clean_data(request.form.get('readkey'))
    writekey = clean_data(request.form.get('writekey'))
    deviceID = clean_data(request.form.get('deviceID'))
    imsi = clean_data(request.form.get('imsi'))
    imei = clean_data(request.form.get('imei'))
    currentFirmwareVersion = clean_data(request.form.get('currentFirmwareVersion'))
    previousFirmwareVersion = clean_data(request.form.get('previousFirmwareVersion'))
    targetFirmwareVersion = clean_data(request.form.get('targetFirmwareVersion'))
    profile = clean_data(request.form.get('profile'))
    fileDownloadState = request.form.get('fileDownloadState', 'False').lower() in ['true', '1', 't', 'y', 'yes']
    
    # Create a new device object
    new_device = Devices(
        name=name,
        readkey=readkey,
        writekey=writekey,
        deviceID=deviceID,
        imsi=imsi,
        imei=imei,
        currentFirmwareVersion=currentFirmwareVersion,
        previousFirmwareVersion=previousFirmwareVersion,
        targetFirmwareVersion=targetFirmwareVersion,
        fileDownloadState=fileDownloadState,
        profile=profile
    )

    # Add the new device to the database and commit the transaction
    db.session.add(new_device)
    db.session.commit()

    return {'message': 'New device added successfully!'}

# Define a route to retrieve all devices
@device_management.route('/get_devices', methods=['GET'])
def get_devices():
    devices = db.session.query(Devices).all()
    devices_list = []
    for device in devices:
        device_dict = {
            'id': device.id,
            'name': device.name,
            'readkey': device.readkey,
            'writekey': device.writekey,
            'deviceID': device.deviceID,
            'imsi': device.imsi,
            'imei': device.imei,
            'currentFirmwareVersion': device.currentFirmwareVersion,
            'previousFirmwareVersion': device.previousFirmwareVersion,
            'fileDownloadState': device.fileDownloadState,
            'targetFirmwareVersion': device.targetFirmwareVersion,
            'created_at': device.created_at
        }
        
        devices_list.append(device_dict)
    
    return jsonify(devices_list)

# Define a route to retrieve a specific device
@device_management.route('/get_device/<int:deviceID>', methods=['GET'])
def get_device(deviceID):
    device = db.session.query(Devices).filter_by(deviceID=deviceID).first()
    
    deviceProflie = db.session.query(Profiles).filter_by(id=device.profile).first()
    if deviceProflie:
        profile_dict = {
            'id': deviceProflie.id,
            'name': deviceProflie.name,
            'description': deviceProflie.description,
            'created_at': deviceProflie.created_at,
            'fields': {},
            'field_marks': {}
        }
        for i in range(1, 21):
            if getattr(deviceProflie, f'field{i}'):
                profile_dict['fields'][f'field{i}'] = getattr(deviceProflie, f'field{i}')
                profile_dict['field_marks'][f'field{i}_mark'] = getattr(deviceProflie, f'field{i}_mark')
    else:
        profile_dict = None

    if device:
         # first 100 records of device data
        device_data = db.session.query(MetadataValues).filter_by(deviceID=deviceID).limit(100).all()
        device_data_list = []
        for data in device_data:
            data_dict = {
                'entryID': data.id,
                'created_at': data.created_at,
            }

            device_data_list.append(data_dict)
            
        device_dict = {
            'id': device.id,
            'created_at': device.created_at,
            'name': device.name,
            'readkey': device.readkey,
            'writekey': device.writekey,
            'deviceID': device.deviceID,
            'profile': device.profile,
            'currentFirmwareVersion': device.currentFirmwareVersion,
            'previousFirmwareVersion': device.previousFirmwareVersion,
            'imsi': device.imsi,
            'imei': device.imei,
            'fileDownloadState': device.fileDownloadState,
            'device_data': device_data_list,
            'profile': profile_dict
        }
        
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
        imsi = request.form.get('imsi', device.imsi)
        imei = request.form.get('imei', device.imei)
        currentFirmwareVersion = request.form.get('currentFirmwareVersion', device.currentFirmwareVersion)
        previousFirmwareVersion = request.form.get('previousFirmwareVersion', device.previousFirmwareVersion)
        targetFirmwareVersion = request.form.get('targetFirmwareVersion', device.targetFirmwareVersion)
        fileDownloadState = request.form.get('fileDownloadState', device.fileDownloadState)

        fields = {}
        field_marks = {}
        for i in range(1, 21):
            fields[f'field{i}'] = request.form.get(f'field{i}', getattr(device, f'field{i}'))
            field_marks[f'field{i}_mark'] = request.form.get(f'field{i}_mark', getattr(device, f'field{i}_mark'))

        device.name = name
        device.readkey = readkey
        device.writekey = writekey
        device.imsi = imsi
        device.imei = imei
        device.currentFirmwareVersion = currentFirmwareVersion
        device.previousFirmwareVersion = previousFirmwareVersion
        device.targetFirmwareVersion = targetFirmwareVersion
        device.fileDownloadState = fileDownloadState

        # Update fields
        # for field, value in fields.items():
        #     setattr(device, field, value)

        # Update fields and field_marks
        for i in range(1, 21):
            setattr(device, f'field{i}', fields[f'field{i}'])
            setattr(device, f'field{i}_mark', field_marks[f'field{i}_mark'])
            

        # Commit the changes to the database
        db.session.commit()

        return {'message': 'Device updated successfully!'}

    return {'message': 'Use POST method to update device data!'}

#device self configuration
@device_management.route('/device/<int:orgID>/selfconfig', methods=['GET'])
def self_config(orgID):
    if orgID != 1234:
        return {'message': 'Invalid organization ID!'}, 403
    
    imsi = clean_data(request.args.get('imsi', None))
    if imsi == '234502106051372':
        try:
            name = 'AQ_123' #clean_data(request.args.get('name', None))
            readkey = 'testreadkey' #clean_data(request.args.get('readkey', None)) 
            writekey = 'testwritekey' #clean_data(request.args.get('writekey', None))
            currentFirmwareVersion = None #clean_data(request.args.get('currentFirmwareVersion', None))
            previousFirmwareVersion = None #clean_data(request.args.get('previousFirmwareVersion', None))
            targetFirmwareVersion = None #clean_data(request.args.get('targetFirmwareVersion', None))
            fileDownloadState = request.args.get('fileDownloadState', 'False').lower() in ['true', '1', 't', 'y', 'yes']
            # if readkey is null assign a random string of length 8
            # if readkey is None:
            #     readkey = 'testwritekey'#.join(random.choices(string.ascii_letters + string.digits, k=8))

            # if writekey is None:
            #     writekey = 'testwritekey'#.join(random.choices(string.ascii_letters + string.digits, k=8))

            fields = {}
            field_marks = {}
            for i in range(1, 21):
                fields[f'field{i}'] = clean_data(request.args.get(f'field{i}', None))
                field_marks[f'field{i}_mark'] = clean_data(request.args.get(f'field{i}_mark', 'False').lower() in ['true', '1', 't', 'y', 'yes'])

            new_device = Devices(
                name=name,
                readkey=readkey,
                writekey=writekey,
                deviceID=12345,
                fileDownloadState=fileDownloadState,
                currentFirmwareVersion=currentFirmwareVersion,
                previousFirmwareVersion=previousFirmwareVersion,
                targetFirmwareVersion=targetFirmwareVersion,
                **fields,
                **field_marks
            )

            db.session.add(new_device)
            db.session.commit()

            return {'message': 'Device self-configured successfully!'}
        
        except Exception as e:
            return {'message': 'Device self-configuration failed!', 'error': str(e)}, 500

    return {'message': 'Invalid IMSI!'}, 403

""""
Profile related routes for profile management
"""        
# Define a route to add a new profile
@device_management.route('/addprofile', methods=['POST'])
def add_profile():
    name = clean_data(request.form.get('name'))
    description = clean_data(request.form.get('description', None))
    # Extract dynamic fields and their marks from form data (field1 to field20)
    fields = {}
    field_marks = {}
    for i in range(1, 21):
        fields[f'field{i}'] = clean_data(request.form.get(f'field{i}', None))
        field_marks[f'field{i}_mark'] = clean_data(request.form.get(f'field{i}_mark', 'False').lower() in ['true', '1', 't', 'y', 'yes'])

    new_profile = Profiles(
        name=name,
        description=description,
        **fields,
        **field_marks
    )

    db.session.add(new_profile)
    db.session.commit()

    return {'message': 'New profile added successfully!'}

# Define a route to retrieve all profiles
@device_management.route('/get_profiles', methods=['GET'])
def get_profiles():
    profiles = db.session.query(Profiles).all()
    profiles_list = []
    for profile in profiles:
        profile_dict = {
            'id': profile.id,
            'name': profile.name,
            'description': profile.description,
            'created_at': profile.created_at,
            'fields': {},
            'field_marks': {}
        }
        for i in range(1, 21):
            if getattr(profile, f'field{i}'):
                profile_dict['fields'][f'field{i}'] = getattr(profile, f'field{i}')
                profile_dict['field_marks'][f'field{i}_mark'] = getattr(profile, f'field{i}_mark')
        
        profiles_list.append(profile_dict)
    
    return jsonify(profiles_list)

# Define a route to retrieve a specific profile
@device_management.route('/get_profile/<int:profileID>', methods=['GET'])
def get_profile(profileID):
    profile = db.session.query(Profiles).filter_by(id=profileID).first()
    if profile:
        profile_dict = {
            'id': profile.id,
            'name': profile.name,
            'description': profile.description,
            'created_at': profile.created_at,
            'fields': {},
            'field_marks': {}
        }
        for i in range(1, 21):
            if getattr(profile, f'field{i}'):
                profile_dict['fields'][f'field{i}'] = getattr(profile, f'field{i}')
                profile_dict['field_marks'][f'field{i}_mark'] = getattr(profile, f'field{i}_mark')
        
        return jsonify(profile_dict)
    
    return {'message': 'Profile not found!'}, 404

# Define a route to edit a profile
# @device_management.route('/profile/<int:profileID>/edit', methods=['GET', 'POST'])
# def edit_profile(profileID):
#     profile = db.session.query(Profiles).filter_by(id=profileID).first()

#     if not profile:
#         return {'message': 'Profile not found!'}, 404

#     if request.method == 'POST':
#         name = request.form.get('name', profile.name)
#         description = request.form.get('description', profile.description)

#         fields = {}
#         field_marks = {}
#         for i in range(1, 21):
#             fields[f'field{i}'] = request.form.get(f'field{i}', getattr(profile, f'field{i}'))
#             field_marks[f'field{i}_mark'] = request.form.get(f'field{i}_mark', getattr(profile, f'field{i}_mark'))

#         profile.name = name
#         profile.description = description

#         # Update fields and field_marks
#         for i in range(1, 21):
#             setattr(profile, f'field{i}', fields[f'field{i}'])
#             setattr(profile, f'field{i}_mark', field_marks[f'field{i}_mark'])

#         db.session.commit()

#         return {'message': 'Profile updated successfully!'}

#     return {'message': 'Use POST method to update profile data!'}, 400


"""
Data related routes for data management
"""
# Define a route to update device data
@device_management.route('/device/<int:deviceID>/update', methods=['GET'])
def update_device_data(deviceID):
    device = db.session.query(Devices).filter_by(deviceID=deviceID).first()
    # print('device is ', device)
    # get the values of the fields for the device from device table
    field_label = {}
    for i in range(1, 21):
        field_label[f'field{i}'] = getattr(device, f'field{i}')

    # Retrieve the api_key from the query parameters
    writekey = request.args.get('api_key')
    
    # Check if the device exists and the provided writekey matches the device's writekey
    if device and writekey == device.writekey:
        # Updating data fields
        fields = {}
        for i in range(1, 21):
            if field_label[f'field{i}']:
                fields[f'field{i}'] = clean_data(request.args.get(f'field{i}', None))
            else:
                fields[f'field{i}'] = None

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

    if not device and writekey != device.writekey:
        return jsonify({'error': 'Unauthorized access'}), 403

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

        # Create a new entry in the DeviceFiles table
        new_file = DeviceFiles(
            deviceID=deviceID,
            file=blob_path
        )
        db.session.add(new_file)
        db.session.commit()

        return jsonify({'message': 'File uploaded successfully!', 'file_path': blob_path}), 200

    except Exception as e:
        # Log the error or print it to the console
        print(f"File upload failed: {e}")
        return jsonify({'error': 'File upload failed', 'details': str(e)}), 500
