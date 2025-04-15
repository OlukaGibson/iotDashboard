from flask import request, jsonify
from ..extentions import db
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
