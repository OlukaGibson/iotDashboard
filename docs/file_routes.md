# File Routes API Documentation

## 1. Upload Device File

**Endpoint:** `POST /device/<deviceID>/fileupload`

**Description:**
Upload a CSV file for a device. The file is stored in Google Cloud Storage and recorded in the DeviceFiles table.

**Parameters:**
- `deviceID` (int, required): Device ID (in URL)
- `file` (file, required): CSV file to upload (form-data)
- `api_key` (string, required): Device write key (query parameter)

**Example Request:**
```http
POST /device/1/fileupload?api_key=YOUR_WRITE_KEY
Content-Type: multipart/form-data

file=@data.csv
```

**Example Response:**
```json
{
  "message": "File uploaded successfully!",
  "file_path": "data/1/2025-07-30/2025-07-30_14-23-00.csv"
}
```

**Error Codes:**
- `400 Bad Request`: No file part in the request
- `403 Forbidden`: Unauthorized access (invalid device or API key)
- `500 Internal Server Error`: File upload failed (details in response)

---

## Notes
- All endpoints are under the `/deviceManagement` blueprint.
- Authentication may be required for some endpoints (not shown in code excerpt).
