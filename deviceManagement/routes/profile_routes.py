from flask import request, jsonify
from ..firestore_helpers import session as db
from ..models import Profiles, Devices, ConfigValues
from . import device_management, clean_data

""""
Profile related routes for profile management
"""        
# Define a route to add a new profile
@device_management.route('/addprofile', methods=['POST'])
def add_profile():
    name = clean_data(request.form.get('name'))
    description = clean_data(request.form.get('description', None))

    fields = {}
    metadata = {}
    for i in range(1, 16):
        fields[f'field{i}'] = clean_data(request.form.get(f'field{i}', None))
        metadata[f'metadata{i}'] = clean_data(request.form.get(f'metadata{i}', None))

    configs = {}
    for i in range(1, 11):
        configs[f'config{i}'] = clean_data(request.form.get(f'config{i}', None))

    new_profile = Profiles(
        name=name,
        description=description,
        **fields,
        **configs,
        **metadata,
    )

    db.add(new_profile)
    db.commit()

    return {'message': 'New profile added successfully!'}

# Define a route to retrieve all profiles
@device_management.route('/get_profiles', methods=['GET'])
def get_profiles():
    profiles = db.query(Profiles).all()
    profiles_list = []
    for profile in profiles:
        # Count the number of devices associated with the profile (by name instead of ID)
        device_count = db.query(Devices).filter_by(profile=profile.name).count()

        profile_dict = {
            'name': profile.name,  # Changed from 'id' to 'name' as primary identifier
            'description': profile.description,
            'created_at': profile.created_at,
            'fields': {},
            'configs': {},
            'metadata': {},
            'device_count': device_count
        }
        for i in range(1, 16):
            if getattr(profile, f'field{i}'):
                profile_dict['fields'][f'field{i}'] = getattr(profile, f'field{i}')
            
            if getattr(profile, f'metadata{i}'):
                profile_dict['metadata'][f'metadata{i}'] = getattr(profile, f'metadata{i}')

        for i in range(1, 11):
            if getattr(profile, f'config{i}'):
                profile_dict['configs'][f'config{i}'] = getattr(profile, f'config{i}')
        
        profiles_list.append(profile_dict)
    
    return jsonify(profiles_list)

# Define a route to retrieve a specific profile (by name instead of ID)
@device_management.route('/get_profile/<string:profileName>', methods=['GET'])
def get_profile(profileName):
    profile = db.query(Profiles).filter_by(name=profileName).first()
    devices = db.query(Devices).filter_by(profile=profileName).all()

    if profile:
        profile_dict = {
            'name': profile.name,  # Changed from 'id' to 'name'
            'description': profile.description,
            'created_at': profile.created_at,
            'fields': {},
            'configs': {},
            'metadata': {},
            'devices': []
        }
        for i in range(1, 16):
            if getattr(profile, f'field{i}'):
                profile_dict['fields'][f'field{i}'] = getattr(profile, f'field{i}')
            if getattr(profile, f'metadata{i}'):
                profile_dict['metadata'][f'metadata{i}'] = getattr(profile, f'metadata{i}')

        for i in range(1, 11):
            if getattr(profile, f'config{i}'):
                profile_dict['configs'][f'config{i}'] = getattr(profile, f'config{i}')

        # Add device details and most recent config values
        for device in devices:
            recent_configs = db.query(ConfigValues).filter_by(deviceID=device.deviceID).order_by('created_at', 'DESCENDING').limit(1).all()
            recent_config = recent_configs[0] if recent_configs else None
            
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

# Define a route to edit a profile (by name instead of ID)
@device_management.route('/edit_profile/<string:profileName>', methods=['POST'])
def edit_profile(profileName):
    profile = db.query(Profiles).filter_by(name=profileName).first()
    
    if not profile:
        return {'message': 'Profile not found!'}, 404
    
    # Update profile attributes
    profile.description = clean_data(request.form.get('description', profile.description))
    
    # Update fields
    for i in range(1, 16):
        field_value = clean_data(request.form.get(f'field{i}', getattr(profile, f'field{i}', None)))
        setattr(profile, f'field{i}', field_value)
        
        metadata_value = clean_data(request.form.get(f'metadata{i}', getattr(profile, f'metadata{i}', None)))
        setattr(profile, f'metadata{i}', metadata_value)
    
    # Update configs
    for i in range(1, 11):
        config_value = clean_data(request.form.get(f'config{i}', getattr(profile, f'config{i}', None)))
        setattr(profile, f'config{i}', config_value)
    
    # Update in Firestore
    from ..extentions import db as firestore_db
    from datetime import datetime
    docs = firestore_db.collection('profiles').where('name', '==', profileName).get()
    if docs:
        doc_ref = docs[0].reference
        doc_ref.update(profile.to_dict())
    
    return {'message': 'Profile updated successfully!'}

# Define a route to delete a profile (by name instead of ID)
@device_management.route('/delete_profile/<string:profileName>', methods=['DELETE'])
def delete_profile(profileName):
    profile = db.query(Profiles).filter_by(name=profileName).first()
    
    if not profile:
        return {'message': 'Profile not found!'}, 404
    
    # Check if any devices are using this profile
    devices_using_profile = db.query(Devices).filter_by(profile=profileName).count()
    
    if devices_using_profile > 0:
        return {'message': f'Cannot delete profile. {devices_using_profile} devices are currently using this profile.'}, 400
    
    # Delete from Firestore
    from ..extentions import db as firestore_db
    docs = firestore_db.collection('profiles').where('name', '==', profileName).get()
    if docs:
        docs[0].reference.delete()
    
    return {'message': 'Profile deleted successfully!'}