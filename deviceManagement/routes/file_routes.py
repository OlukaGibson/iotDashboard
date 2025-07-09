from flask import request, jsonify
from ..firestore_helpers import session as db
from ..models import Profiles, Devices, DeviceFiles
from . import device_management, clean_data, credentials
from google.cloud import storage
import os
from datetime import datetime

"""
File management related routes for file management
"""
# Define a route to upload a file
@device_management.route('/device/<int:deviceID>/fileupload', methods=['POST'])
def file_upload(deviceID):
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file part in the request'}), 400
    
    device = db.query(Devices).filter_by(deviceID=deviceID).first()
    writekey = request.args.get('api_key')

    if not device or writekey != device.writekey:
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

        # Create a new entry in the DeviceFiles collection
        new_file = DeviceFiles(
            deviceID=deviceID,
            file=blob_path
        )
        db.add(new_file)
        db.commit()

        return jsonify({'message': 'File uploaded successfully!', 'file_path': blob_path}), 200

    except Exception as e:
        # Log the error or print it to the console
        print(f"File upload failed: {e}")
        return jsonify({'error': 'File upload failed', 'details': str(e)}), 500

# Get files for a specific device
@device_management.route('/device/<int:deviceID>/files', methods=['GET'])
def get_device_files(deviceID):
    try:
        device = db.query(Devices).filter_by(deviceID=deviceID).first()
        
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        # Get all files for this device
        device_files = db.query(DeviceFiles).filter_by(deviceID=deviceID).order_by('created_at', 'DESCENDING').all()
        
        files_list = []
        for file_record in device_files:
            files_list.append({
                'file_path': file_record.file,
                'uploaded_at': file_record.created_at
            })
        
        return jsonify({
            'deviceID': deviceID,
            'files': files_list
        }), 200
        
    except Exception as e:
        print(f"Get device files failed: {e}")
        return jsonify({'error': 'Failed to retrieve device files', 'details': str(e)}), 500

# Download a specific file
@device_management.route('/device/<int:deviceID>/file/download', methods=['GET'])
def download_file(deviceID):
    file_path = request.args.get('file_path')
    readkey = request.args.get('api_key')
    
    if not file_path:
        return jsonify({'error': 'File path is required'}), 400
    
    device = db.query(Devices).filter_by(deviceID=deviceID).first()
    
    if not device or readkey != device.readkey:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    try:
        storage_client = storage.Client(credentials=credentials)
        bucket_name = os.getenv('BUCKET_NAME')
        if not bucket_name:
            raise ValueError("Bucket name not set in environment variables")

        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_path)
        
        if not blob.exists():
            return jsonify({'error': 'File not found'}), 404
        
        # Generate a signed URL for download (valid for 1 hour)
        from datetime import timedelta
        signed_url = blob.generate_signed_url(
            expiration=datetime.now() + timedelta(hours=1),
            method='GET'
        )
        
        return jsonify({
            'download_url': signed_url,
            'file_path': file_path
        }), 200
        
    except Exception as e:
        print(f"File download failed: {e}")
        return jsonify({'error': 'File download failed', 'details': str(e)}), 500