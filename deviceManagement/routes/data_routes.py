from flask import request, jsonify
from ..extentions import db
from ..models import Profiles, Devices, ConfigValues, MetadataValues,DeviceData, Firmware
from datetime import datetime, timedelta
from . import device_management, clean_data

"""
Device data related routes for data management
"""
# Data updates from devices
@device_management.route('/update', methods=['GET'])
def update_device_data():
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

    # Create a new entry in the DeviceData table
    # Create a new entry in the DeviceData table
    new_entry = DeviceData(
        created_at=datetime.now(),
        deviceID=device.deviceID,
        entryID=DeviceData.get_next_entry_id(device.deviceID),
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

                new_entry = DeviceData(
                    deviceID=device.deviceID,
                    created_at=created_at,
                    entryID=DeviceData.get_next_entry_id(device.deviceID),
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

                new_entry = DeviceData(
                    deviceID=device.deviceID,
                    created_at=created_at,
                    entryID=DeviceData.get_next_entry_id(device.deviceID),
                    **fields
                )
                db.session.add(new_entry)

            db.session.commit()
            return {'message': 'success'}, 200

        else:
            return {'message': 'Invalid update format!'}, 400

    except Exception as e:
        return {'message': 'Server error', 'error': str(e)}, 500

"""
Metadata related routes
"""
# meta dataupdate from devices
@device_management.route('/metadataupdate', methods=['GET'])
def update_meta_data():
    writekey = request.args.get('api_key')
    
    device = db.session.query(Devices).filter_by(writekey=writekey).first()
    
    if not device:
        return {'message': 'Invalid API key!'}, 403
    
    # Get the profile associated with the device
    profile = db.session.query(Profiles).filter_by(id=device.profile).first()


    metadata_label = {}
    for i in range(1, 16):
        metadata_label[f'metadata{i}'] = getattr(profile, f'metadata{i}', None)
        

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
    db.session.add(new_entry)
    db.session.commit()

    return {'message': 'Device data updated successfully!'}, 200

"""
Config data  related routes
"""
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

#fetch config data by device
@device_management.route('/device/<int:deviceID>/getconfig', methods=['GET'])
def get_config_data(deviceID):
    device = db.session.query(Devices).filter_by(deviceID=deviceID).first()
    if not device:
        return {'message': 'Device not found!'}, 404
    
    # Get the profile associated with the device
    profile = db.session.query(Profiles).filter_by(id=device.profile).first()
    if not profile:
        return {'message': 'Profile not found for this device!'}, 404
    
    # Fetch the latest configuration data by ordering by created_at in descending order
    config_data = db.session.query(ConfigValues).filter_by(deviceID=deviceID).order_by(ConfigValues.created_at.desc()).first()
    
    if not config_data:
        return {'message': 'No config data found for this device!'}, 404
    
    configuration = {
        "deviceID": device.deviceID,
        # "created_at": config_data.created_at,
        "fileDownloadState": device.fileDownloadState,
        "configs": {}
    }
    
    # Add target firmware version info if file download is true
    if device.fileDownloadState and device.targetFirmwareVersion:
        target_firmware = db.session.query(Firmware).filter_by(id=device.targetFirmwareVersion).first()
        if target_firmware:
            configuration["firmwareVersion"] = target_firmware.firmwareVersion
            # configuration["targetFirmware"] = {
            #     "id": target_firmware.id,
            #     "version": target_firmware.firmwareVersion,
            #     "type": target_firmware.firmware_type
            # }
    
    # Populate the configuration fields with their actual names from the profile
    for i in range(1, 11):
        config_name = getattr(profile, f'config{i}')
        config_value = getattr(config_data, f'config{i}', None)
        
        if config_name is not None and config_value is not None:
            configuration["configs"][config_name] = config_value
    
    return jsonify(configuration)







# # Define a route to retrieve device data
# def get_device_data(deviceID):
#     # Retrieve the device from the database
#     device = db.session.query(Devices).filter_by(deviceID=deviceID).first()
    
#     # Retrieve the api_key from the query parameters
#     readkey = device.readkey
    
#     # Check if the device exists and the provided readkey matches the device's readkey
#     if device and readkey == device.readkey:
#         # Retrieve all entries from the MetadataValues table for the device
#         entries = db.session.query(MetadataValues).filter_by(deviceID=deviceID).all()
#         entries_list = []
#         for entry in entries:
#             entry_dict = {
#                 'deviceID': entry.deviceID,
#                 'created_at': entry.created_at,
#                 'fields': {}
#             }
#             for i in range(1, 16):
#                 entry_dict['fields'][f'field{i}'] = getattr(entry, f'field{i}')
            
#             entries_list.append(entry_dict)
        
#         return jsonify(entries_list)
    
#     return {'message': 'Invalid API key!'}, 403

# #fetch config data by device
# @device_management.route('/device/<int:deviceID>/getconfig', methods=['GET'])
# def get_config_data(deviceID):
#     device = db.session.query(Devices).filter_by(deviceID=deviceID).first()
#     if not device:
#         return {'message': 'Device not found!'}, 404
    
#     # Fetch the latest configuration data by ordering by created_at in descending order
#     config_data = db.session.query(ConfigValues).filter_by(deviceID=deviceID).order_by(ConfigValues.created_at.desc()).first()
    
#     if not config_data:
#         return {'message': 'No config data found for this device!'}, 404
    
#     configuration = {
#         "deviceID": device.deviceID,
#         "created_at": config_data.created_at,
#         "configs": {}
#     }
    
#     # Populate the configuration fields
#     for i in range(1, 11):
#         config_value = getattr(config_data, f'config{i}', None)
#         if config_value is not None:
#             configuration["configs"][f'config{i}'] = config_value
    
#     return jsonify(configuration)