from flask import request, jsonify
from ..firestore_helpers import session as db
from ..models import Profiles, Devices, ConfigValues, MetadataValues, DeviceData, Firmware
from datetime import datetime, timedelta
from . import device_management, clean_data, calculate_crc32, credentials
import os
from google.cloud import storage
import tempfile


"""
Device data related routes for data management
"""
# Data updates from devices
@device_management.route('/update', methods=['GET'])
def update_device_data():
    writekey = request.args.get('api_key')
    
    device = db.query(Devices).filter_by(writekey=writekey).first()
    
    if not device:
        return {'message': 'Invalid API key!'}, 403
    
    # Get the profile associated with the device (by name instead of ID)
    profile = db.query(Profiles).filter_by(name=device.profile).first()

    field_label = {}
    for i in range(1, 16):
        field_label[f'field{i}'] = getattr(profile, f'field{i}', None) if profile else None

    # Updating data fields
    fields = {}
    for i in range(1, 16):
        if field_label[f'field{i}']:
            fields[f'field{i}'] = clean_data(request.args.get(f'field{i}', None))
        else:
            fields[f'field{i}'] = None

    # Create a new entry in the DeviceData table
    new_entry = DeviceData(
        created_at=datetime.now(),
        deviceID=device.deviceID,
        entryID=DeviceData.get_next_entry_id(device.deviceID),
        **fields
    )

    # Add the new entry to the database and commit
    db.add(new_entry)
    db.commit()

    return {'message': 'Device data updated successfully!'}, 200

#Bulk data update route
@device_management.route('/devices/<int:deviceID>/bulk_update_json', methods=['POST'])
def bulk_update(deviceID):
    device = db.query(Devices).filter_by(deviceID=deviceID).first()
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

                new_entry = DeviceData(
                    deviceID=device.deviceID,
                    created_at=created_at,
                    entryID=DeviceData.get_next_entry_id(device.deviceID),
                    **fields
                )
                db.add(new_entry)

            db.commit()
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

                new_entry = DeviceData(
                    deviceID=device.deviceID,
                    created_at=created_at,
                    entryID=DeviceData.get_next_entry_id(device.deviceID),
                    **fields
                )
                db.add(new_entry)

            db.commit()
            return {'message': 'success'}, 200

        else:
            return {'message': 'Invalid update format!'}, 400

    except Exception as e:
        db.rollback()
        return {'message': 'Server error', 'error': str(e)}, 500

"""
Metadata related routes
"""
# meta dataupdate from devices
@device_management.route('/metadataupdate', methods=['GET'])
def update_meta_data():
    writekey = request.args.get('api_key')
    
    device = db.query(Devices).filter_by(writekey=writekey).first()
    
    if not device:
        return {'message': 'Invalid API key!'}, 403
    
    # Get the profile associated with the device (by name instead of ID)
    profile = db.query(Profiles).filter_by(name=device.profile).first()

    metadata_label = {}
    for i in range(1, 16):
        metadata_label[f'metadata{i}'] = getattr(profile, f'metadata{i}', None) if profile else None

    # Updating data metadata
    metadatas = {}
    for i in range(1, 16):
        if metadata_label[f'metadata{i}']:
            metadatas[f'metadata{i}'] = clean_data(request.args.get(f'metadata{i}', None))
        else:
            metadatas[f'metadata{i}'] = None

    # Create a new entry in the MetadataValues table
    new_entry = MetadataValues(
        created_at=datetime.now(),
        deviceID=device.deviceID,
        **metadatas
    )

    # Add the new entry to the database and commit
    db.add(new_entry)
    db.commit()

    return {'message': 'Device metadata updated successfully!'}, 200

"""
Config data related routes
"""
#update config data by user
@device_management.route('/update_config_data', methods=['POST'])
def update_config_data():
    deviceID = request.form.get('deviceID')
    if not deviceID:
        return {'message': 'Device ID is required!'}, 400
    
    device = db.query(Devices).filter_by(deviceID=int(deviceID)).first()
    if not device:
        return {'message': 'Device not found!'}, 404

    profile = db.query(Profiles).filter_by(name=device.profile).first()
    if not profile:
        return {'message': 'Profile not found for the device!'}, 404

    # Get the latest configuration to use for fallback values
    latest_configs = db.query(ConfigValues).filter_by(deviceID=int(deviceID)).order_by('created_at', 'DESCENDING').limit(1).all()
    latest_config = latest_configs[0] if latest_configs else None
    
    configs = {}
    for i in range(1, 11):
        config_name = getattr(profile, f'config{i}', None)
        if config_name:  # Only update if the configuration has a name in the profile
            new_value = clean_data(request.form.get(f'config{i}', None))
            # If new value is None and there's a previous configuration, use that value
            if new_value is None and latest_config is not None:
                configs[f'config{i}'] = getattr(latest_config, f'config{i}', None)
            else:
                configs[f'config{i}'] = new_value
        else:
            configs[f'config{i}'] = None
    
    new_entry = ConfigValues(
        created_at=datetime.now(),
        deviceID=int(deviceID),
        **configs
    )

    db.add(new_entry)
    db.commit()

    return {'message': 'Device config data updated successfully!'}, 200

@device_management.route('/mass_edit_config_data', methods=['POST'])
def mass_edit_config_data():
    json_data = request.get_json()
    if not json_data:
        return {'message': 'No data provided!'}, 400
    
    device_ids = json_data.get('deviceIDs')
    config_labels = json_data.get('configLabels')
    config_values = json_data.get('configValues')
    
    if not device_ids or not isinstance(device_ids, list):
        return {'message': 'No device IDs provided or invalid format!'}, 400
        
    if not config_labels or not config_values:
        return {'message': 'Config labels or values missing!'}, 400
    
    # Track results
    results = {
        'success': [],
        'failed': []
    }
    
    for device_id in device_ids:
        try:
            # Get device
            device = db.query(Devices).filter_by(deviceID=device_id).first()
            if not device:
                results['failed'].append({
                    'deviceID': device_id,
                    'error': 'Device not found'
                })
                continue
                
            # Get device profile (by name instead of ID)
            profile = db.query(Profiles).filter_by(name=device.profile).first()
            if not profile:
                results['failed'].append({
                    'deviceID': device_id,
                    'error': 'Profile not found for device'
                })
                continue
                
            # Get latest config for fallback values
            latest_configs = db.query(ConfigValues).filter_by(deviceID=device_id).order_by('created_at', 'DESCENDING').limit(1).all()
            latest_config = latest_configs[0] if latest_configs else None
            
            # Prepare configs dict
            configs = {}
            
            # For each possible config field
            for i in range(1, 11):
                config_key = f'config{i}'
                profile_config_name = getattr(profile, config_key, None)
                
                # If this config exists in the profile
                if profile_config_name:
                    # Check if this config is in the input JSON
                    if config_key in config_values:
                        new_value = config_values.get(config_key)
                        # If value is empty string, treat as None (no change)
                        if new_value == "":
                            # Use previous value if available
                            if latest_config:
                                configs[config_key] = getattr(latest_config, config_key, None)
                            else:
                                configs[config_key] = None
                        else:
                            # Use the new value
                            configs[config_key] = clean_data(new_value)
                    else:
                        # Config not in input, use previous value if available
                        if latest_config:
                            configs[config_key] = getattr(latest_config, config_key, None)
                        else:
                            configs[config_key] = None
                else:
                    # Config doesn't exist in profile
                    configs[config_key] = None
            
            # Create new config entry
            new_config = ConfigValues(
                created_at=datetime.now(),
                deviceID=device_id,
                **configs
            )
            
            db.add(new_config)
            results['success'].append(device_id)
            
        except Exception as e:
            results['failed'].append({
                'deviceID': device_id,
                'error': str(e)
            })
    
    # Commit all changes at once
    try:
        db.commit()
        return {
            'message': f'Updated configs for {len(results["success"])} devices, {len(results["failed"])} failed',
            'results': results
        }, 200
    except Exception as e:
        db.rollback()
        return {'message': f'Transaction failed: {str(e)}'}, 500

#fetch config data by device
@device_management.route('/device/<int:deviceID>/getconfig', methods=['GET'])
def get_config_data(deviceID):    
    device = db.query(Devices).filter_by(deviceID=deviceID).first()
    if not device:
        return {'message': 'Device not found!'}, 404
    
    # Get the profile associated with the device (by name instead of ID)
    profile = db.query(Profiles).filter_by(name=device.profile).first()
    if not profile:
        return {'message': 'Profile not found for this device!'}, 404
    
    # Fetch the latest configuration data by ordering by created_at in descending order
    config_data_list = db.query(ConfigValues).filter_by(deviceID=deviceID).order_by('created_at', 'DESCENDING').limit(1).all()
    config_data = config_data_list[0] if config_data_list else None
    
    if not config_data:
        return {'message': 'No config data found for this device!'}, 404
    
    configuration = {
        "deviceID": device.deviceID,
        "fileDownloadState": device.fileDownloadState,
        "configs": {}
    }
    
    # Add target firmware version info if file download is true
    if device.fileDownloadState and device.targetFirmwareVersion:
        target_firmware = db.query(Firmware).filter_by(firmwareVersion=device.targetFirmwareVersion).first()
        if target_firmware:
            configuration["firmwareVersion"] = target_firmware.firmwareVersion
            
            # Add CRC32 of the firmware file by downloading it temporarily and calculating
            if target_firmware.firmware_string:
                try:
                    storage_client = storage.Client(credentials=credentials)
                    bucket = storage_client.bucket(os.getenv('BUCKET_NAME'))
                    blob = bucket.blob(target_firmware.firmware_string)
                    
                    # Create temporary file to calculate CRC32
                    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                        temp_path = temp_file.name
                        blob.download_to_filename(temp_path)
                    
                    # Calculate CRC32 of the temporary file
                    configuration["firmwareCRC32"] = calculate_crc32(temp_path)
                    
                    # Clean up the temporary file
                    os.unlink(temp_path)
                except Exception as e:
                    print(f"Error calculating CRC32 for firmware file: {str(e)}")
    
    # Populate the configuration fields with their actual names from the profile
    for i in range(1, 11):
        config_name = getattr(profile, f'config{i}')
        config_value = getattr(config_data, f'config{i}', None)
        
        if config_name is not None and config_value is not None:
            configuration["configs"][config_name] = config_value
    
    return jsonify(configuration)