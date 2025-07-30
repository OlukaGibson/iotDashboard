# Dashboard Routes API Documentation

## 1. Landing Page

**Endpoint:** `GET /`

**Description:**
Returns a message indicating device storage status, along with server port and scheme information.

**Parameters:**
- None

**Example Request:**
```http
GET /
```

**Example Response:**
```json
{
  "message": "Device storage is full!",
  "port": "5000",
  "scheme": "http"
}
```

**Error Codes:**
- `500 Internal Server Error`: Server error

---

## 2. Dashboard Summary

**Endpoint:** `GET /dashboard_summary`

**Description:**
Returns summary statistics for devices, profiles, firmware, online/offline device counts, latest firmware info, and hourly device posting activity.

**Parameters:**
- None

**Example Request:**
```http
GET /dashboard_summary
```

**Example Response:**
```json
{
  "total_devices": 100,
  "total_profiles": 5,
  "total_firmware_versions": 12,
  "latest_firmware": {
    "firmwareVersion": "v1.2.3",
    "uploaded_at": "2025-07-29T14:23:00"
  },
  "online_devices": 80,
  "offline_devices": 20,
  "hourly_activity": [
    {"hour": 0, "devices_posted": 5},
    {"hour": 1, "devices_posted": 3},
    // ...
    {"hour": 23, "devices_posted": 7}
  ]
}
```

**Error Codes:**
- `500 Internal Server Error`: Database or server error

---

## Notes
- All endpoints are under the `/deviceManagement` blueprint.
- Authentication may be required for some endpoints (not shown in code excerpt).
