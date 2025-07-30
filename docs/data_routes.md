# Data Routes API Documentation

## 1. Update Device Data

**Endpoint:** `GET /update`

**Description:**
Update device data using API key and field values.

**Parameters (query):**
- `api_key` (string, required): Device write key
- `field1` ... `field15` (string, optional): Data fields

**Example Request:**
```http
GET /update?api_key=YOUR_WRITE_KEY&field1=23.5&field2=45.2
```

**Example Response:**
```json
{
  "message": "Device data updated successfully!"
}
```

**Error Codes:**
- `403 Forbidden`: Invalid API key
- `500 Internal Server Error`: Database or server error

---

## 2. Bulk Data Update

**Endpoint:** `POST /devices/<deviceID>/bulk_update_json`

**Description:**
Bulk update device data using a JSON payload.

**Parameters (JSON body):**
- `write_api_key` (string, required): Device write key
- `updates` (array, required): List of update objects
  - Each update object: `created_at` (string, optional), `delta_t` (int, optional), `field1` ... `field15` (string, optional)

**Example Request:**
```json
{
  "write_api_key": "YOUR_WRITE_KEY",
  "updates": [
    {"created_at": "2025-07-30 12:00:00", "field1": "23.5"},
    {"created_at": "2025-07-30 12:01:00", "field1": "24.0"}
  ]
}
```

**Example Response:**
```json
{
  "message": "success"
}
```

**Error Codes:**
- `404 Not Found`: Device not found
- `400 Bad Request`: No data or invalid format
- `403 Forbidden`: Invalid API key
- `500 Internal Server Error`: Server error

---

## 3. Update Metadata

**Endpoint:** `GET /metadataupdate`

**Description:**
Update device metadata using API key and metadata fields.

**Parameters (query):**
- `api_key` (string, required): Device write key
- `metadata1` ... `metadata15` (string, optional): Metadata fields

**Example Request:**
```http
GET /metadataupdate?api_key=YOUR_WRITE_KEY&metadata1=location&metadata2=type
```

**Example Response:**
```json
{
  "message": "Device data updated successfully!"
}
```

**Error Codes:**
- `403 Forbidden`: Invalid API key
- `500 Internal Server Error`: Database or server error

---

## 4. Update Config Data

**Endpoint:** `POST /update_config_data`

**Description:**
Update configuration data for a device.

**Parameters (form-data):**
- `deviceID` (int, required): Device ID
- `config1` ... `config10` (string, optional): Configuration values

**Example Request:**
```http
POST /update_config_data
Content-Type: multipart/form-data

deviceID=1
config1=10
config2=20
```

**Example Response:**
```json
{
  "message": "Device config data updated successfully!"
}
```

**Error Codes:**
- `400 Bad Request`: Device ID missing
- `404 Not Found`: Device or profile not found
- `500 Internal Server Error`: Database or server error

---

## 5. Mass Edit Config Data

**Endpoint:** `POST /mass_edit_config_data`

**Description:**
Mass update configuration data for multiple devices.

**Parameters (JSON body):**
- `deviceIDs` (array, required): List of device IDs
- `configLabels` (object, required): Config labels
- `configValues` (object, required): Config values

**Example Request:**
```json
{
  "deviceIDs": [1, 2, 3],
  "configLabels": {"config1": "Sample Rate"},
  "configValues": {"config1": "10"}
}
```

**Example Response:**
```json
{
  "message": "Updated configs for 3 devices, 0 failed",
  "results": {
    "success": [1, 2, 3],
    "failed": []
  }
}
```

**Error Codes:**
- `400 Bad Request`: Missing or invalid data
- `500 Internal Server Error`: Transaction failed

---

## 6. Get Config Data

**Endpoint:** `GET /device/<deviceID>/getconfig`

**Description:**
Fetch the latest configuration data for a device.

**Parameters:**
- `deviceID` (int, required): Device ID (in URL)

**Example Request:**
```http
GET /device/1/getconfig
```

**Example Response:**
```json
{
  "deviceID": 1,
  "fileDownloadState": true,
  "configs": {
    "Sample Rate": "10",
    "Threshold": "50"
  },
  "firmwareVersion": "v1.2.3",
  "firmwareCRC32": "abcdef12"
}
```

**Error Codes:**
- `404 Not Found`: Device, profile, or config data not found
- `500 Internal Server Error`: Server error

---

## Notes
- All endpoints are under the `/deviceManagement` blueprint.
- Authentication may be required for some endpoints (not shown in code excerpt).
