from flask import request, jsonify
import random
import string
from datetime import datetime
from ..extentions import db
from ..models import Devices, Firmware, Profiles, MetadataValues, ConfigValues, DeviceData
from . import device_management, clean_data

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
        previousFirmwareVersion = previousFirmware.firmwareVersion if previousFirmware else currentFirmwareVersion
        targetFirmwareVersion = targetFirmware.firmwareVersion if targetFirmware else currentFirmwareVersion

        # Fetch the profile name
        profile = db.session.query(Profiles).filter_by(id=device.profile).first()
        profile_name = profile.name if profile else None

        # Fetch the last time the device posted metadata
        last_metadata_entry = db.session.query(DeviceData).filter_by(deviceID=device.deviceID).order_by(DeviceData.created_at.desc()).first()
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
            'last_posted_time': last_posted_time,
            'created_at': device.created_at,
            'firmwareDownloadState': device.firmwareDownloadState,
        }
        
        devices_list.append(device_dict)
    
    return jsonify(devices_list)

# Retrieve a specific device
@device_management.route('/get_device/<int:deviceID>', methods=['GET'])
def get_device(deviceID):
    device = db.session.query(Devices).filter_by(deviceID=deviceID).first()

    if not device:
        return {'message': 'Device not found!'}, 404

    currentFirmwareID = device.currentFirmwareVersion
    previousFirmwareID = device.previousFirmwareVersion
    targetFirmwareID = device.targetFirmwareVersion

    currentFirmware = db.session.query(Firmware).filter_by(id=currentFirmwareID).first()   #currentFirmwareVersion
    previousFirmware = db.session.query(Firmware).filter_by(id=previousFirmwareID).first() #previousFirmwareVersion
    targetFirmware = db.session.query(Firmware).filter_by(id=targetFirmwareID).first()     #targetFirmwareVersion
    
    currentFirmwareVersion = currentFirmware.firmwareVersion if currentFirmware else None
    previousFirmwareVersion = previousFirmware.firmwareVersion if previousFirmware else None
    targetFirmwareVersion = targetFirmware.firmwareVersion if targetFirmware else None

    deviceProfile = db.session.query(Profiles).filter_by(id=device.profile).first()
    
    if deviceProfile:
        profile_dict = {
            'id': deviceProfile.id,
            'name': deviceProfile.name,
            'description': deviceProfile.description,
            'created_at': deviceProfile.created_at,
            'fields': {},
            'configs': {},
            'metadata': {}  # Add the missing 'metadata' key
        }
        for i in range(1, 16):
            if getattr(deviceProfile, f'field{i}') is not None:
                profile_dict['fields'][f'field{i}'] = getattr(deviceProfile, f'field{i}')
            if getattr(deviceProfile, f'metadata{i}') is not None:
                profile_dict['metadata'][f'metadata{i}'] = getattr(deviceProfile, f'metadata{i}')
        
        for i in range(1, 11):
            if getattr(deviceProfile, f'config{i}') is not None:
                profile_dict['configs'][f'config{i}'] = getattr(deviceProfile, f'config{i}')
    else:
        profile_dict = None

    # first 100 records of device data starting from the latest
    device_data = db.session.query(DeviceData).filter_by(deviceID=deviceID).order_by(DeviceData.created_at.desc()).limit(100).all()
    config_data = db.session.query(ConfigValues).filter_by(deviceID=deviceID).order_by(ConfigValues.created_at.desc()).limit(100).all()
    meta_data = db.session.query(MetadataValues).filter_by(deviceID=deviceID).order_by(MetadataValues.created_at.desc()).limit(100).all()
    # device_data = db.session.query(DeviceData).filter_by(deviceID=deviceID).limit(100).all()
    # config_data = db.session.query(ConfigValues).filter_by(deviceID=deviceID).limit(100).all()
    # meta_data = db.session.query(MetadataValues).filter_by(deviceID=deviceID).limit(100).all()
    device_data_list = []
    config_data_list = []
    meta_data_list = []
    for data in meta_data:
        data_dict = {
            'entryID': data.id,
            'created_at': data.created_at,
        }
        for i in range(1, 16):
            if getattr(data, f'metadata{i}', None):
                data_dict[f'metadata{i}'] = getattr(data, f'metadata{i}', None)
        meta_data_list.append(data_dict)

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
        'meta_data': meta_data_list,
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

#device self configuration
@device_management.route('/device/<int:networkID>/selfconfig', methods=['GET'])
def self_config(networkID):
    networkID = str(networkID)
    device = db.session.query(Devices).filter_by(networkID=networkID).first()
    if not device:
        return {'message': 'Device not found!'}, 404

    try:
        # Get the associated profile
        profile = db.session.query(Profiles).filter_by(id=device.profile).first()
        
        # Get the latest config values
        latest_config = db.session.query(ConfigValues).filter_by(deviceID=device.deviceID).order_by(ConfigValues.created_at.desc()).first()
        
        # Prepare device basic details
        device_details = {
            'name': device.name,
            'deviceID': device.deviceID,
            'networkID': device.networkID,
            'writekey': device.writekey,
            'configs': {}
        }
        
        # Add profile configurations and their values
        if profile and latest_config:
            for i in range(1, 11):
                config_name = getattr(profile, f'config{i}')
                if config_name:  # Only include configs that are defined in the profile
                    config_value = getattr(latest_config, f'config{i}')
                    device_details['configs'][config_name] = config_value

        return jsonify(device_details)

    except Exception as e:
        return {'message': 'Device self-configuration failed!', 'error': str(e)}, 500