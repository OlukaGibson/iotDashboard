from flask import request, jsonify
from ..extentions import db
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