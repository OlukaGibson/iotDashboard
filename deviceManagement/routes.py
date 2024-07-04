from flask import Blueprint, redirect, url_for, render_template, request

from .extentions import db
from .models import Devices, MetadataValues

device_management = Blueprint('device_management', __name__)

@device_management.route('/')
def device_storage():
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