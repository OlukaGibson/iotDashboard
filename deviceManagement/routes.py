from flask import Blueprint, redirect, url_for, render_template, request, send_file, jsonify
import os
from .extentions import db
from .models import Devices, MetadataValues, Firmware, DeviceFiles, Profiles, ConfigValues
from google.cloud import storage
import io
import json
from google.oauth2 import service_account
from dotenv import load_dotenv
from intelhex import IntelHex
from datetime import datetime, timedelta
import random
import string


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
    port = request.environ.get('SERVER_PORT')
    scheme = request.scheme
    print('Device storage is full!')
    return {
        'message': 'Device storage is full!',
        'port': port,
        'scheme': scheme
    }

@device_management.route('/dashboard_summary', methods=['GET'])
def dashboard_summary():
    # Total number of devices
    total_devices = db.session.query(Devices).count()

    # Total number of profiles
    total_profiles = db.session.query(Profiles).count()

    # Total number of firmware versions
    total_firmware_versions = db.session.query(Firmware).count()

    # Latest firmware and its upload time
    latest_firmware = db.session.query(Firmware).order_by(Firmware.created_at.desc()).first()
    latest_firmware_info = {
        'firmwareVersion': latest_firmware.firmwareVersion,
        'uploaded_at': latest_firmware.created_at
    } if latest_firmware else None

    # Number of online and offline devices
    online_devices = db.session.query(Devices).filter_by(fileDownloadState=True).count()
    offline_devices = total_devices - online_devices

    # Devices posting activity by hour
    hourly_activity = []
    for hour in range(24):
        start_time = datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)
        devices_posted = db.session.query(MetadataValues.deviceID).filter(
            MetadataValues.created_at >= start_time,
            MetadataValues.created_at < end_time
        ).distinct().count()
        hourly_activity.append({'hour': hour, 'devices_posted': devices_posted})

    # Return the summary
    return jsonify({
        'total_devices': total_devices,
        'total_profiles': total_profiles,
        'total_firmware_versions': total_firmware_versions,
        'latest_firmware': latest_firmware_info,
        'online_devices': online_devices,
        'offline_devices': offline_devices,
        'hourly_activity': hourly_activity
    })

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
    firmware_type = request.form.get('firmware_type', 'beta')  # Default to 'beta' if not specified

    # Read the file as binary data - don't decode
    firmware_content = firmware.read()
    firmware_bootloader_content = firmware_bootloader.read() if firmware_bootloader else None

    changes = {}
    for i in range(1, 11):
        changes[f'change{i}'] = clean_data(request.form.get(f'change{i}', None))

    # uploading firmware to google cloud storage
    if firmware.filename.endswith('.hex'):
        # For hex files, parse them using IntelHex
        firmware_hex = IntelHex(io.BytesIO(firmware_content))
        bin_data = io.BytesIO()
        firmware_hex.tobinfile(bin_data)
        bin_data.seek(0)
        
        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.bucket(os.getenv('BUCKET_NAME'))

        # Store binary version
        blob = bucket.blob(f'firmware/firmware_file_bin/{firmwareVersion}.bin')
        blob.upload_from_file(bin_data)
        
        # Store hex version
        blob = bucket.blob(f'firmware/firmware_file_hex/{firmwareVersion}.hex')
        blob.upload_from_string(firmware_content)
    else:
        # For binary files, store them directly
        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.bucket(os.getenv('BUCKET_NAME'))
        
        blob = bucket.blob(f'firmware/firmware_file_bin/{firmwareVersion}.bin')
        blob.upload_from_string(firmware_content)

    # Store bootloader if provided
    if firmware_bootloader:
        blob = bucket.blob(f'firmware/firmware_file_bootloader/{firmwareVersion}.hex')
        blob.upload_from_string(firmware_bootloader_content)

    # Create a new firmware record in the database
    new_firmware = Firmware(
        firmwareVersion=firmwareVersion,
        firmware_string=f'firmware/firmware_file_bin/{firmwareVersion}.bin',
        firmware_string_hex=f'firmware/firmware_file_hex/{firmwareVersion}.hex' if firmware.filename.endswith('.hex') else None,
        firmware_string_bootloader=f'firmware/firmware_file_bootloader/{firmwareVersion}.hex' if firmware_bootloader else None,
        firmware_type=firmware_type,
        description=description,
        **changes,
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
            'firmware_type': version.firmware_type,
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
            'firmware_type': firmware.firmware_type,
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
# Add a new device
@device_management.route('/adddevice', methods=['POST'])
def add_device():
    # Generate random 16-character alphanumeric strings for writekey and readkey
    writekey = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    readkey = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))

    # Determine the next deviceID by finding the maximum existing deviceID and adding 1
    last_device = db.session.query(Devices).order_by(Devices.deviceID.desc()).first()
    deviceID = (last_device.deviceID + 1) if last_device else 1  # Start from 1 if no devices exist

    # Extract other fields from form data with default value None if not present
    name = clean_data(request.form.get('name'))
    networkID = clean_data(request.form.get('networkID'))
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
        networkID=networkID,
        currentFirmwareVersion=currentFirmwareVersion,
        previousFirmwareVersion=previousFirmwareVersion,
        targetFirmwareVersion=targetFirmwareVersion,
        fileDownloadState=fileDownloadState,
        profile=profile
    )

    # Add the new device to the database and commit the transaction
    db.session.add(new_device)
    db.session.commit()

    return {
        'message': 'New device added successfully!',
        'deviceID': deviceID,
        'readkey': readkey,
        'writekey': writekey
    }

# Retrieve all devices
@device_management.route('/get_devices', methods=['GET'])
def get_devices():
    devices = db.session.query(Devices).all()
    
    devices_list = []
    for device in devices:

        currentFirmwareID = device.currentFirmwareVersion
        previousFirmwareID = device.previousFirmwareVersion
        targetFirmwareID = device.targetFirmwareVersion

        currentFirmware = db.session.query(Firmware).filter_by(id=currentFirmwareID).first()   # currentFirmwareVersion
        previousFirmware = db.session.query(Firmware).filter_by(id=previousFirmwareID).first() # previousFirmwareVersion
        targetFirmware = db.session.query(Firmware).filter_by(id=targetFirmwareID).first()     # targetFirmwareVersion

        currentFirmwareVersion = currentFirmware.firmwareVersion if currentFirmware else None
        previousFirmwareVersion = previousFirmware.firmwareVersion if previousFirmware else None
        targetFirmwareVersion = targetFirmware.firmwareVersion if targetFirmware else None

        # Fetch the profile name
        profile = db.session.query(Profiles).filter_by(id=device.profile).first()
        profile_name = profile.name if profile else None

        # Fetch the last time the device posted metadata
        last_metadata_entry = db.session.query(MetadataValues).filter_by(deviceID=device.deviceID).order_by(MetadataValues.created_at.desc()).first()
        last_posted_time = last_metadata_entry.created_at if last_metadata_entry else None

        device_dict = {
            'id': device.id,
            'name': device.name,
            'readkey': device.readkey,
            'writekey': device.writekey,
            'deviceID': device.deviceID,
            'networkID': device.networkID,
            'currentFirmwareVersion': currentFirmwareVersion,
            'previousFirmwareVersion': previousFirmwareVersion,
            'targetFirmwareVersion': targetFirmwareVersion,
            'fileDownloadState': device.fileDownloadState,
            'profile': device.profile,
            'profile_name': profile_name,
            'last_posted_time': last_posted_time,  # Added last posted time
            'created_at': device.created_at
        }
        
        devices_list.append(device_dict)
    
    return jsonify(devices_list)

# Retrieve a specific device
@device_management.route('/get_device/<int:deviceID>', methods=['GET'])
def get_device(deviceID):
    device = db.session.query(Devices).filter_by(deviceID=deviceID).first()

    currentFirmwareID = device.currentFirmwareVersion
    previousFirmwareID = device.previousFirmwareVersion
    targetFirmwareID = device.targetFirmwareVersion

    currentFirmware = db.session.query(Firmware).filter_by(id=currentFirmwareID).first()   #currentFirmwareVersion
    previousFirmware = db.session.query(Firmware).filter_by(id=previousFirmwareID).first() #previousFirmwareVersion
    targetFirmware = db.session.query(Firmware).filter_by(id=targetFirmwareID).first()     #targetFirmwareVersion
    
    currentFirmwareVersion = currentFirmware.firmwareVersion if currentFirmware else None
    previousFirmwareVersion = previousFirmware.firmwareVersion if previousFirmware else None
    targetFirmwareVersion = targetFirmware.firmwareVersion if targetFirmware else None

    if not device:
        return {'message': 'Device not found!'}, 404

    deviceProfile = db.session.query(Profiles).filter_by(id=device.profile).first()
    
    if deviceProfile:
        profile_dict = {
            'id': deviceProfile.id,
            'name': deviceProfile.name,
            'description': deviceProfile.description,
            'created_at': deviceProfile.created_at,
            'fields': {},
            'configs': {}
        }
        for i in range(1, 16):
            if getattr(deviceProfile, f'field{i}') is not None:
                profile_dict['fields'][f'field{i}'] = getattr(deviceProfile, f'field{i}')
        
        for i in range(1, 11):
            if getattr(deviceProfile, f'config{i}') is not None:
                profile_dict['configs'][f'config{i}'] = getattr(deviceProfile, f'config{i}')
    else:
        profile_dict = None

    # first 100 records of device data
    device_data = db.session.query(MetadataValues).filter_by(deviceID=deviceID).limit(100).all()
    config_data = db.session.query(ConfigValues).filter_by(deviceID=deviceID).limit(100).all()
    device_data_list = []
    config_data_list = []
    for data in config_data:
        data_dict = {
            'entryID': data.id,
            'created_at': data.created_at,
        }
        for i in range(1, 11):
            if getattr(data, f'config{i}', None):
                data_dict[f'config{i}'] = getattr(data, f'config{i}', None)
        config_data_list.append(data_dict)

    for data in device_data:
        data_dict = {
            'entryID': data.id,
            'created_at': data.created_at,
        }
        for i in range(1, 16):
            if getattr(data, f'field{i}', None):
                data_dict[f'field{i}'] = getattr(data, f'field{i}', None)
        device_data_list.append(data_dict)
        
    device_dict = {
        'id': device.id,
        'created_at': device.created_at,
        'name': device.name,
        'readkey': device.readkey,
        'writekey': device.writekey,
        'deviceID': device.deviceID,
        'profile': device.profile,
        'currentFirmwareVersion': currentFirmwareVersion,
        'targetFirmwareVersion': targetFirmwareVersion,
        'previousFirmwareVersion': previousFirmwareVersion,
        'networkID': device.networkID,
        'fileDownloadState': device.fileDownloadState,
        'device_data': device_data_list,
        'config_data': config_data_list,
        'profile': profile_dict
    }
    
    return jsonify(device_dict)

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
        networkID = request.form.get('networkID', device.networkID)
        currentFirmwareVersion = request.form.get('currentFirmwareVersion', device.currentFirmwareVersion)
        previousFirmwareVersion = request.form.get('previousFirmwareVersion', device.previousFirmwareVersion)
        targetFirmwareVersion = request.form.get('targetFirmwareVersion', device.targetFirmwareVersion)
        fileDownloadState = request.form.get('fileDownloadState', device.fileDownloadState)

        fields = {}
        configs = {}
        for i in range(1, 16):
            fields[f'field{i}'] = request.form.get(f'field{i}', getattr(device, f'field{i}'))

        for i in range(1, 11):
            configs[f'config{i}'] = request.form.get(f'config{i}', getattr(device, f'config{i}'))

        device.name = name
        device.readkey = readkey
        device.writekey = writekey
        device.networkID = networkID
        device.currentFirmwareVersion = currentFirmwareVersion
        device.previousFirmwareVersion = previousFirmwareVersion
        device.targetFirmwareVersion = targetFirmwareVersion
        device.fileDownloadState = fileDownloadState

        # Update fields
        for i in range(1, 16):
            setattr(device, f'field{i}', fields[f'field{i}'])
        
        for i in range(1, 11):
            setattr(device, f'config{i}', configs[f'config{i}'])

        # Commit the changes to the database
        db.session.commit()

        return {'message': 'Device updated successfully!'}

    return {'message': 'Use POST method to update device data!'}

""""
Profile related routes for profile management
"""        
# Define a route to add a new profile
@device_management.route('/addprofile', methods=['POST'])
def add_profile():
    name = clean_data(request.form.get('name'))
    description = clean_data(request.form.get('description', None))

    fields = {}
    for i in range(1, 16):
        fields[f'field{i}'] = clean_data(request.form.get(f'field{i}', None))
    
    configs = {}
    for i in range(1, 11):
        configs[f'config{i}'] = clean_data(request.form.get(f'config{i}', None))

    new_profile = Profiles(
        name=name,
        description=description,
        **fields,
        **configs
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
        # Count the number of devices associated with the profile
        device_count = db.session.query(Devices).filter_by(profile=profile.id).count()

        profile_dict = {
            'id': profile.id,
            'name': profile.name,
            'description': profile.description,
            'created_at': profile.created_at,
            'fields': {},
            'configs': {},
            'device_count': device_count  # Add the device count
        }
        for i in range(1, 16):
            if getattr(profile, f'field{i}'):
                profile_dict['fields'][f'field{i}'] = getattr(profile, f'field{i}')

        for i in range(1, 11):
            if getattr(profile, f'config{i}'):
                profile_dict['configs'][f'config{i}'] = getattr(profile, f'config{i}')
        
        profiles_list.append(profile_dict)
    
    return jsonify(profiles_list)

# Define a route to retrieve a specific profile
@device_management.route('/get_profile/<int:profileID>', methods=['GET'])
def get_profile(profileID):
    profile = db.session.query(Profiles).filter_by(id=profileID).first()
    devices = db.session.query(Devices).filter_by(profile=profileID).all()

    if profile:
        profile_dict = {
            'id': profile.id,
            'name': profile.name,
            'description': profile.description,
            'created_at': profile.created_at,
            'fields': {},
            'configs': {},
            'devices': []
        }
        for i in range(1, 16):
            if getattr(profile, f'field{i}'):
                profile_dict['fields'][f'field{i}'] = getattr(profile, f'field{i}')

        for i in range(1, 11):
            if getattr(profile, f'config{i}'):
                profile_dict['configs'][f'config{i}'] = getattr(profile, f'config{i}')

        # Add device details and most recent config values
        for device in devices:
            recent_config = db.session.query(ConfigValues).filter_by(deviceID=device.deviceID).order_by(ConfigValues.created_at.desc()).first()
            config_values = {}
            if recent_config:
                for i in range(1, 11):
                    if getattr(recent_config, f'config{i}', None):
                        config_values[f'config{i}'] = getattr(recent_config, f'config{i}', None)

            profile_dict['devices'].append({
                'name': device.name,
                'deviceID': device.deviceID,
                'recent_config': config_values
            })

        return jsonify(profile_dict)
    
    return {'message': 'Profile not found!'}, 404


"""
Data related routes for data management
"""
# Singular data update route
@device_management.route('/update', methods=['GET'])
def update_data():
    writekey = request.args.get('api_key')
    
    device = db.session.query(Devices).filter_by(writekey=writekey).first()
    
    if not device:
        return {'message': 'Invalid API key!'}, 403
    
    # Get the profile associated with the device
    profile = db.session.query(Profiles).filter_by(id=device.profile).first()


    field_label = {}
    for i in range(1, 16):
        field_label[f'field{i}'] = getattr(profile, f'field{i}', None)
        

    # Updating data fields
    fields = {}
    for i in range(1, 16):
        if field_label[f'field{i}']:
            fields[f'field{i}'] = clean_data(request.args.get(f'field{i}', None))
        else:
            fields[f'field{i}'] = None

    # Create a new entry in the MetadataValues table
    new_entry = MetadataValues(
        created_at=datetime.now(),
        deviceID=device.deviceID,
        **fields
    )

    # Add the new entry to the database and commit
    db.session.add(new_entry)
    db.session.commit()

    return {'message': 'Device data updated successfully!'}, 200

#Bulk data update route
# https://api.thingspeak.com/channels/<channel_id>/bulk_update.json
@device_management.route('/devices/<int:deviceID>/bulk_update_json', methods=['POST'])
def bulk_update(deviceID):
    device = db.session.query(Devices).filter_by(deviceID=deviceID).first()
    if not device:
        return {'message': 'Device not found!'}, 404

    json_data = request.get_json()
    if not json_data:
        return {'message': 'No data provided!'}, 400

    write_api_key = json_data.get('write_api_key')
    if write_api_key != device.writekey:
        return {'message': 'Invalid API key!'}, 403

    updates = json_data.get('updates')
    if not updates or not isinstance(updates, list):
        return {'message': 'Invalid data format!'}, 400

    try:
        if 'created_at' in updates[0]:
            for update in updates:
                created_at = update.get('created_at')
                created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                fields = {}
                for i in range(1, 16):
                    fields[f'field{i}'] = update.get(f'field{i}', None)

                new_entry = MetadataValues(
                    deviceID=device.deviceID,
                    created_at=created_at,
                    **fields
                )
                db.session.add(new_entry)

            db.session.commit()
            return {'message': 'success'}, 200

        elif 'delta_t' in updates[0]:
            created_at = datetime.now()
            for update in updates:
                if update == updates[0]:
                    created_at = datetime.now()
                else:
                    created_at = created_at - timedelta(seconds=update.get('delta_t'))

                fields = {}
                for i in range(1, 16):
                    fields[f'field{i}'] = update.get(f'field{i}', None)

                new_entry = MetadataValues(
                    deviceID=device.deviceID,
                    created_at=created_at,
                    **fields
                )
                db.session.add(new_entry)

            db.session.commit()
            return {'message': 'success'}, 200

        else:
            return {'message': 'Invalid update format!'}, 400

    except Exception as e:
        return {'message': 'Server error', 'error': str(e)}, 500

#update config data by user
@device_management.route('/update_config_data', methods=['POST'])
def update_config_data():
    deviceID = request.form.get('deviceID')
    if not deviceID:
        return {'message': 'Device ID is required!'}, 400
    
    device = db.session.query(Devices).filter_by(deviceID=deviceID).first()
    if not device:
        return {'message': 'Device not found!'}, 404

    profile = db.session.query(Profiles).filter_by(id=device.profile).first()
    if not profile:
        return {'message': 'Profile not found for the device!'}, 404

    configs = {}
    for i in range(1, 11):
        config_name = getattr(profile, f'config{i}', None)
        if config_name:  # Only update if the configuration has a name in the profile
            configs[f'config{i}'] = clean_data(request.form.get(f'config{i}', None))
        else:
            configs[f'config{i}'] = None


    
    new_entry = ConfigValues(
        created_at=datetime.now(),
        deviceID=deviceID,
        **configs
    )

    db.session.add(new_entry)
    db.session.commit()

    return {'message': 'Device config data updated successfully!'}, 200

# Define a route to retrieve device data
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
            for i in range(1, 16):
                entry_dict['fields'][f'field{i}'] = getattr(entry, f'field{i}')
            
            entries_list.append(entry_dict)
        
        return jsonify(entries_list)
    
    return {'message': 'Invalid API key!'}, 403

#fetch config data by device
@device_management.route('/device/<int:deviceID>/getconfig', methods=['GET'])
def get_config_data(deviceID):
    device = db.session.query(Devices).filter_by(deviceID=deviceID).first()
    if not device:
        return {'message': 'Device not found!'}, 404
    
    # Fetch the latest configuration data by ordering by created_at in descending order
    config_data = db.session.query(ConfigValues).filter_by(deviceID=deviceID).order_by(ConfigValues.created_at.desc()).first()
    
    if not config_data:
        return {'message': 'No config data found for this device!'}, 404
    
    configuration = {
        "deviceID": device.deviceID,
        "created_at": config_data.created_at,
        "configs": {}
    }
    
    # Populate the configuration fields
    for i in range(1, 11):
        config_value = getattr(config_data, f'config{i}', None)
        if config_value is not None:
            configuration["configs"][f'config{i}'] = config_value
    
    return jsonify(configuration)
    
""""
Profile related routes for profile management
"""    
#device self configuration
@device_management.route('/device/<int:networkID>/selfconfig', methods=['GET'])
def self_config(networkID):
    networkID = str(networkID)
    device = db.session.query(Devices).filter_by(networkID=networkID).first()
    if not device:
        return {'message': 'Device not found!'}, 404

    try:
        device_details = {
            'name': device.name,
            'deviceID': device.deviceID,
            'networkID': device.networkID,
            'writekey': device.writekey
        }

        return jsonify(device_details)

    except Exception as e:
        return {'message': 'Device self-configuration failed!', 'error': str(e)}, 500


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
