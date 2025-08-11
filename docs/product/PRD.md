# SnapGeo OCR - Product Requirements Document

## Product Overview

SnapGeo is a backend OCR microservice that extracts geolocation information from images containing GPS overlays, converting visual GPS data into structured JSON format for frontend applications.

## Business Objectives

- Enable automated extraction of GPS coordinates from screenshots and images
- Provide reliable OCR-based geolocation parsing for frontend applications
- Support Next.js and other web applications requiring location data processing

## User Stories and Acceptance Criteria

### Epic 1: Image Upload and Processing

#### User Story 1.1: Upload Image with GPS Overlay
**As a** frontend application  
**I want to** upload an image containing GPS coordinates via API  
**So that** I can extract structured location data

**Acceptance Criteria:**
- [ ] API accepts POST requests to `/ocr` endpoint
- [ ] Supports multipart/form-data with `file` field
- [ ] Accepts JPG and PNG image formats
- [ ] Returns 400 error for invalid file formats
- [ ] Returns 413 error for files exceeding size limit
- [ ] Response time < 5 seconds for images up to 10MB

**Testable Outcomes:**

*Postman Tests:*
- POST `http://localhost:8000/ocr` with form-data `file` field containing GPS image
- Expected: 200 status with coordinates JSON
- POST `http://localhost:8000/ocr` with form-data `file` field containing text file
- Expected: 400 error response

*curl Tests:*
```bash
# Test successful upload
curl -X POST http://localhost:8000/ocr -F "file=@test-gps-image.jpg"
# Expected: 200 status with GPS data

# Test invalid format
curl -X POST http://localhost:8000/ocr -F "file=@test.txt"
# Expected: 400 error with format message
```

### Epic 2: GPS Coordinate Extraction

#### User Story 2.1: Extract Basic GPS Coordinates
**As a** frontend application  
**I want to** receive latitude and longitude from GPS overlay images  
**So that** I can display location information to users

**Acceptance Criteria:**
- [ ] Extracts latitude in decimal degrees (negative for South)
- [ ] Extracts longitude in decimal degrees (positive for East)
- [ ] Handles coordinate format: "X.XXXXXXXS Y.YXXXXXXE"
- [ ] Returns raw OCR text for debugging purposes
- [ ] Accuracy: >90% for clear, high-contrast GPS overlays

**Testable Outcomes:**

*Postman Tests:*
- POST `http://localhost:8000/ocr` with GPS overlay image
- Expected JSON response with extracted coordinates
- Verify latitude is negative (South) and longitude is positive (East)

*Expected Response:*
```json
{
  "raw_text": "07 August 2025 06.03.16\n6.26891158S 107.25537723E\n...",
  "latitude": -6.26891158,
  "longitude": 107.25537723
}
```

#### User Story 2.2: Handle Missing GPS Data
**As a** frontend application  
**I want to** receive clear error messages when GPS data cannot be extracted  
**So that** I can inform users and handle failures gracefully

**Acceptance Criteria:**
- [ ] Returns structured error response for images without GPS data
- [ ] Returns structured error response for unreadable text
- [ ] Includes raw OCR text in error response for debugging
- [ ] HTTP status 422 for processing failures

**Testable Outcomes:**

*Postman Tests:*
- POST `http://localhost:8000/ocr` with image without GPS data
- Expected 422 status with structured error response
- Verify raw_text field is included for debugging

*Expected Error Response:*
```json
{
  "error": "Unable to extract GPS coordinates from image",
  "raw_text": "Some unrelated text without coordinates"
}
```

### Epic 3: Extended Metadata Support (Future)

#### User Story 3.1: Extract Additional GPS Metadata
**As a** frontend application  
**I want to** receive altitude, speed, and direction data when available  
**So that** I can provide comprehensive location information

**Acceptance Criteria:**
- [ ] Extracts altitude in meters (optional field)
- [ ] Extracts speed in km/h (optional field) 
- [ ] Extracts direction as bearing/cardinal (optional field)
- [ ] Gracefully handles partial metadata availability

## API Specifications

### Endpoint: `POST /ocr`

**Request:**
- Content-Type: `multipart/form-data`
- Field: `file` (required) - Image file containing GPS overlay

**Response (Success - 200):**
```json
{
  "raw_text": "string",
  "latitude": "float",
  "longitude": "float",
  "altitude": "float (optional)",
  "speed": "float (optional)", 
  "direction": "string (optional)"
}
```

**Response (Error - 422):**
```json
{
  "error": "string",
  "raw_text": "string (optional)"
}
```

## Non-Functional Requirements

### Performance
- Response time: < 5 seconds for images up to 10MB
- Concurrent requests: Support 10+ simultaneous OCR operations
- Memory usage: < 1GB RAM under normal load

### Reliability  
- Uptime: 99.5% availability target
- OCR accuracy: >90% for clear GPS overlays
- Error rate: <5% for valid image inputs

### Security
- File validation: Strict image format checking
- Resource limits: File size and processing time limits
- No data persistence: Images processed in memory only

## Success Metrics

- OCR accuracy rate for GPS coordinate extraction
- API response time percentiles (p50, p95, p99)
- Error rate by image type and quality
- Frontend integration success rate