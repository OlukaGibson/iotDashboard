# Profile Routes API Documentation

## 1. Add Profile

**Endpoint:** `POST /addprofile`

**Description:**
Add a new profile with fields, configs, and metadata.

**Parameters (form-data):**
- `name` (string, required): Profile name
- `description` (string, optional): Profile description
- `field1` ... `field15` (string, optional): Custom field labels
- `metadata1` ... `metadata15` (string, optional): Metadata for each field
- `config1` ... `config10` (string, optional): Configuration values

**Example Request:**
```http
POST /addprofile
Content-Type: multipart/form-data

name=Temperature Sensor
field1=Temperature
metadata1=Unit: Celsius
config1=Sample Rate: 1min
```

**Example Response:**
```json
{
  "message": "New profile added successfully!"
}
```

**Error Codes:**
- `400 Bad Request`: Missing required parameters
- `500 Internal Server Error`: Database or server error

---

## 2. Get Profiles

**Endpoint:** `GET /get_profiles`

**Description:**
Retrieve all profiles and device counts per profile.

**Parameters:**
- None

**Example Request:**
```http
GET /get_profiles
```

**Example Response:**
```json
[
  {
    "id": 1,
    "name": "Temperature Sensor",
    "description": "Profile for temperature sensors",
    "device_count": 5
  },
  {
    "id": 2,
    "name": "Humidity Sensor",
    "description": "Profile for humidity sensors",
    "device_count": 3
  }
]
```

**Error Codes:**
- `500 Internal Server Error`: Database or server error

---

## Notes
- All endpoints are under the `/deviceManagement` blueprint.
- Authentication may be required for some endpoints (not shown in code excerpt).
