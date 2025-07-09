from flask import request, jsonify
import random
import string
from datetime import datetime, timedelta
from ..firestore_helpers import session as db
from ..models import Devices, Firmware, Profiles, MetadataValues, ConfigValues, DeviceData
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
    total_devices = db.query(Devices).count()

    # Total number of profiles
    total_profiles = db.query(Profiles).count()

    # Total number of firmware versions
    total_firmware_versions = db.query(Firmware).count()

    # Latest firmware and its upload time
    latest_firmware = db.query(Firmware).order_by('created_at', 'DESCENDING').limit(1).first()
    latest_firmware_info = {
        'firmwareVersion': latest_firmware.firmwareVersion,
        'uploaded_at': latest_firmware.created_at
    } if latest_firmware else None

    # Number of online and offline devices
    # Online devices are those that have posted data in the last 3 hours
    three_hours_ago = datetime.now() - timedelta(hours=3)
    
    # Get device data from the last 3 hours
    recent_device_data = db.query(DeviceData).filter(lambda doc: doc.created_at >= three_hours_ago).all()
    
    # Get distinct device IDs that have posted data in the last 3 hours
    online_device_ids = list(set([data.deviceID for data in recent_device_data]))
    
    # Count the number of online devices
    online_devices = len(online_device_ids)
    offline_devices = total_devices - online_devices

    # Devices posting activity by hour
    hourly_activity = []
    for hour in range(24):
        start_time = datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)
        
        # Get device data for this hour
        hour_device_data = db.query(DeviceData).filter(
            lambda doc: doc.created_at >= start_time and doc.created_at < end_time
        ).all()
        
        # Count distinct devices that posted in this hour
        devices_posted = len(set([data.deviceID for data in hour_device_data]))
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