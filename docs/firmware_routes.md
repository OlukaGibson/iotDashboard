# Firmware Routes API Documentation

## 1. Upload Firmware

**Endpoint:** `POST /firmwareupload`

**Description:**
Upload firmware (hex or bin) and optionally a bootloader. Stores files in Google Cloud Storage and records in the Firmware table.

**Parameters (form-data):**
- `firmware` (file, required): Firmware file (.hex or .bin)
- `firmware_bootloader` (file, optional): Bootloader file (.hex)
- `firmwareVersion` (string, required): Firmware version
- `description` (string, optional): Description
- `firmware_type` (string, optional): Firmware type (default: beta)
- `change1` ... `change10` (string, optional): Change log entries

**Example Request:**
```http
POST /firmwareupload
Content-Type: multipart/form-data

firmware=@firmware.hex
firmwareVersion=v1.2.3
description=Initial release
firmware_type=stable
change1=Added new feature
```

**Example Response:**
```json
{
  "message": "Firmware uploaded successfully!"
}
```

**Error Codes:**
- `400 Bad Request`: Missing required parameters
- `500 Internal Server Error`: File upload or database error

---

## 2. Download Firmware Bin

**Endpoint:** `GET /firmware/<firmwareVersion>/download/firmwarebin`

**Description:**
Download the binary firmware file for a given version. Supports HTTP Range requests.

**Parameters:**
- `firmwareVersion` (string, required): Firmware version (in URL)

**Example Request:**
```http
GET /firmware/v1.2.3/download/firmwarebin
```

**Example Response:**
- Binary file download
- Partial content if Range header is provided

**Error Codes:**
- `404 Not Found`: Firmware or file not found
- `400 Bad Request`: Invalid Range header

---

## 3. Download Firmware Hex

**Endpoint:** `GET /firmware/<firmwareVersion>/download/firmwarehex`

**Description:**
Download the hex firmware file for a given version.

**Parameters:**
- `firmwareVersion` (string, required): Firmware version (in URL)

**Example Request:**
```http
GET /firmware/v1.2.3/download/firmwarehex
```

**Example Response:**
- Hex file download

**Error Codes:**
- `404 Not Found`: Firmware or file not found

---

## 4. Download Firmware Bootloader

**Endpoint:** `GET /firmware/<firmwareVersion>/download/firmwarebootloader`

**Description:**
Download the bootloader hex file for a given firmware version.

**Parameters:**
- `firmwareVersion` (string, required): Firmware version (in URL)

**Example Request:**
```http
GET /firmware/v1.2.3/download/firmwarebootloader
```

**Example Response:**
- Bootloader hex file download

**Error Codes:**
- `404 Not Found`: Firmware or file not found

---

## 5. Display All Firmware Versions

**Endpoint:** `GET /firmware/display`

**Description:**
Retrieve all firmware versions, their metadata, file sizes, and device counts.

**Parameters:**
- None

**Example Request:**
```http
GET /firmware/display
```

**Example Response:**
```json
[
  {
    "id": 1,
    "firmwareVersion": "v1.2.3",
    "firmware_string": "firmware/firmware_file_bin/v1.2.3.bin",
    "firmware_string_hex": "firmware/firmware_file_hex/v1.2.3.hex",
    "firmware_string_bootloader": "firmware/firmware_file_bootloader/v1.2.3.hex",
    "firmware_type": "stable",
    "description": "Initial release",
    "created_at": "2025-07-30T12:00:00",
    "updated_at": "2025-07-30T12:10:00",
    "changes": {"change1": "Added new feature"},
    "devices_count": 10,
    "file_sizes": {"bin": 102400, "hex": 20480, "bootloader": 4096}
  }
]
```

**Error Codes:**
- `500 Internal Server Error`: Database or storage error

---

## 6. Get Specific Firmware Version

**Endpoint:** `GET /firmware/<firmwareVersion>`

**Description:**
Retrieve metadata for a specific firmware version.

**Parameters:**
- `firmwareVersion` (string, required): Firmware version (in URL)

**Example Request:**
```http
GET /firmware/v1.2.3
```

**Example Response:**
```json
{
  "firmwareVersion": "v1.2.3",
  "firmware_string": "firmware/firmware_file_bin/v1.2.3.bin",
  "firmware_string_hex": "firmware/firmware_file_hex/v1.2.3.hex",
  "firmware_string_bootloader": "firmware/firmware_file_bootloader/v1.2.3.hex",
  "description": "Initial release",
  "firmware_type": "stable",
  "created_at": "2025-07-30T12:00:00",
  "updated_at": "2025-07-30T12:10:00",
  "changes": {"change1": "Added new feature"}
}
```

**Error Codes:**
- `404 Not Found`: Firmware version not found

---

## 7. Update Firmware Type

**Endpoint:** `POST /firmware/updatefirmware_type`

**Description:**
Update the type of a firmware version.

**Parameters (form-data):**
- `firmwareVersion` (string, required): Firmware version
- `firmware_type` (string, required): New firmware type

**Example Request:**
```http
POST /firmware/updatefirmware_type
Content-Type: multipart/form-data

firmwareVersion=v1.2.3
firmware_type=stable
```

**Example Response:**
```json
{
  "message": "Firmware type updated successfully!"
}
```

**Error Codes:**
- `400 Bad Request`: Invalid input
- `404 Not Found`: Firmware version not found

---

## Notes
- All endpoints are under the `/deviceManagement` blueprint.
- Authentication may be required for some endpoints (not shown in code excerpt).
