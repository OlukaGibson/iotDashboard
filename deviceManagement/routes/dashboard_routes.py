from flask import request, jsonify
import random
import string
from datetime import datetime, timedelta
from ..extentions import db
from ..models import Devices, Firmware, Profiles, MetadataValues, ConfigValues
from . import device_management, clean_data


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
