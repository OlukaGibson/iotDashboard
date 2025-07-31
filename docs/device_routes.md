# Device Management API Routes

This module provides RESTful endpoints for managing IoT devices, firmware, profiles, and device data.

## Endpoints

### 1. Add a New Device

**POST** `/adddevice`

Creates a new device with randomly generated read/write keys and a unique deviceID.

**Request Form Data:**
- `name`
- `networkID`
- `currentFirmwareVersion`
- `previousFirmwareVersion`
- `targetFirmwareVersion`
- `profile`
- `fileDownloadState` (default: False)
- `firmwareDownloadState` (default: 'updated')

**Response:**
```json
{
  "message": "New device added successfully!",
  "deviceID": <int>,
  "readkey": <str>,
  "writekey": <str>
}
```

---

### 2. Get All Devices

**GET** `/get_devices`

Returns a list of all devices with their details, firmware versions, profile name, and last posted metadata time.

**Response:**  
Array of device objects.

---

### 3. Get Device by ID

**GET** `/get_device/<int:deviceID>`

Returns detailed information about a specific device, including profile, firmware versions, and the latest 100 records of device, config, and metadata.

**Response:**  
Device object with nested profile, device_data, config_data, and meta_data.

---

### 4. Edit Device Data

**GET/POST** `/device/<int:deviceID>/edit`

- **GET:** Returns a message to use POST for editing.
- **POST:** Updates device fields and configs.

**Request Form Data:**  
Any device field or config (see model).

**Response:**
```json
{ "message": "Device updated successfully!" }
```

---

### 5. Update Device Firmware

**POST** `/device/<int:deviceID>/update_firmware`

Updates the target firmware version for a device.

**Request JSON:**
- `firmwareID`
- `firmwareVersion`

**Response:**
```json
{ "message": "Device firmware update initiated successfully!" }
```

---

### 6. Device Self Configuration

**GET** `/device/<int:networkID>/selfconfig`

Returns the latest configuration values for a device, mapped to its profile.

**Response:**  
Device details with config names and values.

---

## Error Handling

All endpoints return a JSON error message and appropriate HTTP status code if the device or firmware is not found or if required data is missing.

---

## Models Used

- `Devices`
- `Firmware`
- `Profiles`
- `MetadataValues`
- `ConfigValues`
- `DeviceData`

---

## Notes

- All endpoints require appropriate data in the request.
- Some endpoints limit returned records to the latest 100 entries