from flask import Flask, Response, request, jsonify, send_file
import os
import io
from intelhex import IntelHex
from ..extentions import db
from ..models import Firmware, Devices
from google.cloud import storage
from . import device_management, clean_data, credentials
import logging


"""
Firmware management related routes for firmware management
"""
# Define a route to upload firmware
@device_management.route('/firmwareupload', methods=['POST'])
def firmware_upload():
    firmware = request.files.get('firmware')
    firmware_bootloader = request.files.get('firmware_bootloader', None)
    firmwareVersion = request.form.get('firmwareVersion')
    description = clean_data(request.form.get('description', None))
    firmware_type = request.form.get('firmware_type', 'beta')  # Default to 'beta' if not specified

    # Read the file as binary data - don't decode
    firmware_content = firmware.read()
    firmware_bootloader_content = firmware_bootloader.read() if firmware_bootloader else None

    changes = {}
    for i in range(1, 11):
        changes[f'change{i}'] = clean_data(request.form.get(f'change{i}', None))

    # uploading firmware to google cloud storage
    if firmware.filename.endswith('.hex'):
        # For hex files, properly decode content as UTF-8 or ASCII for IntelHex
        try:
            # Try UTF-8 first
            firmware_content_str = firmware_content.decode('utf-8')
        except UnicodeDecodeError:
            # Fall back to ASCII if UTF-8 fails
            firmware_content_str = firmware_content.decode('ascii', errors='ignore')
        
        # Create a BytesIO for the binary output
        bin_data = io.BytesIO()
        
        # Create IntelHex from the string content
        firmware_hex = IntelHex()
        firmware_hex.loadhex(io.StringIO(firmware_content_str))
        firmware_hex.tobinfile(bin_data)
        bin_data.seek(0)
        
        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.bucket(os.getenv('BUCKET_NAME'))

        # Store binary version
        blob = bucket.blob(f'firmware/firmware_file_bin/{firmwareVersion}.bin')
        blob.upload_from_file(bin_data)
        
        # Store hex version
        blob = bucket.blob(f'firmware/firmware_file_hex/{firmwareVersion}.hex')
        blob.upload_from_string(firmware_content)
    else:
        # For binary files, store them directly
        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.bucket(os.getenv('BUCKET_NAME'))
        
        blob = bucket.blob(f'firmware/firmware_file_bin/{firmwareVersion}.bin')
        blob.upload_from_string(firmware_content)

    # Store bootloader if provided
    if firmware_bootloader:
        blob = bucket.blob(f'firmware/firmware_file_bootloader/{firmwareVersion}.hex')
        blob.upload_from_string(firmware_bootloader_content)

    # Create a new firmware record in the database
    new_firmware = Firmware(
        firmwareVersion=firmwareVersion,
        firmware_string=f'firmware/firmware_file_bin/{firmwareVersion}.bin',
        firmware_string_hex=f'firmware/firmware_file_hex/{firmwareVersion}.hex' if firmware.filename.endswith('.hex') else None,
        firmware_string_bootloader=f'firmware/firmware_file_bootloader/{firmwareVersion}.hex' if firmware_bootloader else None,
        firmware_type=firmware_type,
        description=description,
        **changes,
    )

    db.session.add(new_firmware)
    db.session.commit()

    return {'message': 'Firmware uploaded successfully!'}

# Define a route to download firmware bin file
@device_management.route('/firmware/<string:firmwareVersion>/download/firmwarebin', methods=['GET'])
def firmware_download(firmwareVersion):
    firmware = db.session.query(Firmware).filter_by(firmwareVersion=firmwareVersion).first()

    if firmware:
        firmware_string = firmware.firmware_string
        if not firmware_string:
            return {'message': 'Firmware bin file not found!'}, 404

        # Fetch binary file from Google Cloud Storage
        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.bucket(os.getenv('BUCKET_NAME'))
        blob = bucket.blob(firmware_string)
        blob.reload()
        
        file_size = blob.size
        range_header = request.headers.get('Range', None)

        if range_header:
            byte_range = range_header.strip().split('=')[-1]
            if '-' not in byte_range:
                return {'message': 'Invalid Range header'}, 400

            parts = byte_range.split('-')
            start = int(parts[0]) if parts[0] else 0
            end = int(parts[1]) if len(parts) > 1 and parts[1] else file_size - 1
            length = end - start + 1

            partial_data = blob.download_as_bytes(start=start, end=end + 1)  # GCS exclusive end

            response = Response(partial_data,
                                206,
                                mimetype='application/octet-stream',
                                direct_passthrough=True)
            response.headers.add('Content-Range', f'bytes {start}-{end}/{file_size}')
            response.headers.add('Accept-Ranges', 'bytes')
            # response.headers.add('Content-Length', str(length))
            return response


        # No Range header: send full file
        file_data = blob.download_as_bytes()
        return Response(
            file_data,
            200,
            mimetype='application/octet-stream',
            headers={
                'Content-Disposition': f'attachment; filename={firmwareVersion}.bin',
                'Content-Length': str(file_size),
                'Accept-Ranges': 'bytes'
            }
        )

    return {'message': 'Firmware version not found!'}, 404


# Define a route to download firmware hex file
@device_management.route('/firmware/<string:firmwareVersion>/download/firmwarehex', methods=['GET'])
def firmware_download_hex(firmwareVersion):
    firmware = db.session.query(Firmware).filter_by(firmwareVersion=firmwareVersion).first()

    if firmware:
        firmware_string = firmware.firmware_string_hex
        if not firmware_string:
            return {'message': 'Firmware hex file not found!'}, 404
        
        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.bucket(os.getenv('BUCKET_NAME'))
        blob = bucket.blob(firmware_string)

        file_data = blob.download_as_string()
        file_buffer = io.BytesIO(file_data)
        file_buffer.seek(0)

        return send_file(
            file_buffer,
            as_attachment=True,
            download_name=f'{firmwareVersion}.hex',
            mimetype='text/plain'
        )
    
    return {'message': 'Firmware version not found!'}, 404

# Define a route to download firmware bootloader file
@device_management.route('/firmware/<string:firmwareVersion>/download/firmwarebootloader', methods=['GET'])
def firmware_download_bootloader(firmwareVersion):
    firmware = db.session.query(Firmware).filter_by(firmwareVersion=firmwareVersion).first()

    if firmware:
        firmware_string = firmware.firmware_string_bootloader
        if not firmware_string:
            return {'message': 'Firmware bootloader file not found!'}, 404
        
        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.bucket(os.getenv('BUCKET_NAME'))
        blob = bucket.blob(firmware_string)

        file_data = blob.download_as_string()
        file_buffer = io.BytesIO(file_data)
        file_buffer.seek(0)

        return send_file(
            file_buffer,
            as_attachment=True,
            download_name=f'{firmwareVersion}_bootloader.hex',
            mimetype='text/plain'
        )
    
    return {'message': 'Firmware version not found!'}, 404

# Define a route to retrieve all firmware versions
@device_management.route('/firmware/display', methods=['GET'])
def get_firmwares():
    firmwares = db.session.query(Firmware).all()
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(os.getenv('BUCKET_NAME'))
    
    firmwares_list = []
    for version in firmwares:
        # Count devices using this firmware version as their current firmware
        current_devices_count = db.session.query(Devices).filter_by(
            currentFirmwareVersion=version.id
        ).count()
        
        # Get file sizes
        bin_size = hex_size = bootloader_size = None
        
        # Get binary file size
        if version.firmware_string:
            try:
                blob = bucket.blob(version.firmware_string)
                # Get metadata directly instead of checking exists first
                blob.reload()
                bin_size = blob.size
            except Exception as e:
                print(f"Error getting bin file size for {version.firmware_string}: {str(e)}")
        
        # Get hex file size
        if version.firmware_string_hex:
            try:
                blob = bucket.blob(version.firmware_string_hex)
                # Get metadata directly instead of checking exists first
                blob.reload()
                hex_size = blob.size
            except Exception as e:
                print(f"Error getting hex file size for {version.firmware_string_hex}: {str(e)}")
        
        # Get bootloader file size
        if version.firmware_string_bootloader:
            try:
                blob = bucket.blob(version.firmware_string_bootloader)
                # Get metadata directly instead of checking exists first
                blob.reload()
                bootloader_size = blob.size
            except Exception as e:
                print(f"Error getting bootloader file size for {version.firmware_string_bootloader}: {str(e)}")
                
        # Collect changes
        changes = {}
        for i in range(1, 11):
            change_value = getattr(version, f'change{i}')
            if change_value is not None:
                changes[f'change{i}'] = change_value

        firmwares_list.append({
            'id': version.id,
            'firmwareVersion': version.firmwareVersion,
            'firmware_string': version.firmware_string,
            'firmware_string_hex': version.firmware_string_hex,
            'firmware_string_bootloader': version.firmware_string_bootloader,
            'firmware_type': version.firmware_type,
            'description': version.description,
            'created_at': version.created_at,
            'updated_at': version.updated_at,
            'changes': changes,
            'devices_count': current_devices_count,
            'file_sizes': {
                'bin': bin_size,
                'hex': hex_size,
                'bootloader': bootloader_size
            }
        })
    
    return jsonify(firmwares_list)

# Define a route to retrieve a specific firmware version
@device_management.route('/firmware/<string:firmwareVersion>', methods=['GET'])
def get_firmware(firmwareVersion):
    firmware = db.session.query(Firmware).filter_by(firmwareVersion=firmwareVersion).first()
    if firmware:
        firmware_dict = {
            'firmwareVersion': firmware.firmwareVersion,
            'firmware_string': firmware.firmware_string,
            'firmware_string_hex': firmware.firmware_string_hex,
            'firmware_string_bootloader': firmware.firmware_string_bootloader,
            'description': firmware.description,
            'firmware_type': firmware.firmware_type,
            'created_at': firmware.created_at,
            'updated_at': firmware.updated_at,
            'changes': {
            }
        }
        for i in range(1, 11):
            if getattr(firmware, f'change{i}'):
                firmware_dict['changes'][f'change{i}'] = getattr(firmware, f'change{i}')
        
        return jsonify(firmware_dict)
    
    return {'message': 'Firmware version not found!'}, 404

@device_management.route('/firmware/updatefirmware_type', methods=['POST'])
def update_firmware_type():
    firmwareVersion = request.form.get('firmwareVersion')
    firmware_type = request.form.get('firmware_type')

    # Validate input
    if not firmwareVersion or not firmware_type:
        return {'message': 'Invalid input!'}, 400

    # Update the firmware type in the database
    firmware = db.session.query(Firmware).filter_by(firmwareVersion=firmwareVersion).first()
    if firmware:
        firmware.firmware_type = firmware_type
        db.session.commit()
        return {'message': 'Firmware type updated successfully!'}
    
    return {'message': 'Firmware version not found!'}, 404