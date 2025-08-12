# SnapGeo OCR API Documentation

## 🚀 Interactive API Documentation

FastAPI automatically generates comprehensive interactive API documentation:

### 📋 Swagger UI (Recommended)
**URL:** `http://localhost:8000/docs`

- **Interactive interface** to test all endpoints
- **Request/response examples** with real data
- **File upload interface** for testing OCR
- **Detailed parameter descriptions** and validation rules
- **Authentication support** (when implemented)

### 📖 ReDoc Documentation  
**URL:** `http://localhost:8000/redoc`

- **Clean, readable format** for API reference
- **Detailed schemas** and response formats
- **Code examples** in multiple languages
- **Printable documentation** format

### 🔧 OpenAPI Schema
**URL:** `http://localhost:8000/openapi.json`

- **Machine-readable API specification**
- **Schema for code generation** in any language
- **Integration with API tools** like Postman, Insomnia

---

## 📍 API Endpoints

### 1. Extract GPS Coordinates
**POST** `/ocr`

Extract GPS coordinates from images with GPS overlays using advanced OCR.

#### Request
- **Content-Type:** `multipart/form-data`
- **Parameter:** `file` (required) - Image file (JPG, JPEG, PNG)
- **Max File Size:** Configured by deployment (typically 10MB)

#### Response Examples

**✅ Success Response (High Confidence)**
```json
{
  "raw_text": "7°33'15.8\"S 110°38'38.7\"E\nSpeed: 0.0km/h\nAltitude: 125.3msnm",
  "latitude": -7.55492507,
  "longitude": 110.64424782,
  "latitude_reconstructed": true,
  "longitude_reconstructed": false,
  "confidence": {
    "score": 0.85,
    "level": "high",
    "method": "fragment_reconstruction",
    "explanation": "Coordinates reconstructed from detected fragments"
  },
  "ocr_method": "ultra_crop2_ultra_coords"
}
```

**✅ Success Response (Medium Confidence)**
```json
{
  "raw_text": "Kecamatan Boyolali\nJawa Tengah\nAltitude: 291.1msnm",
  "latitude": -7.5,
  "longitude": 110.6,
  "coordinates_estimated_from_location": true,
  "location_context": "Estimated coordinates based on detected location names",
  "confidence": {
    "score": 0.60,
    "level": "medium", 
    "method": "geographic_estimation",
    "explanation": "Coordinates estimated from detected location names"
  }
}
```

**❌ Error Response (No Coordinates Found)**
```json
{
  "error": "GPS coordinates not found, but extracted other location metadata",
  "location_info": ["Jakarta", "Jawa Barat", "Indonesia"],
  "raw_text": "Street view without GPS overlay"
}
```

**❌ Error Response (Invalid File)**
```json
{
  "detail": "File must be an image (JPG, JPEG, PNG)"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `latitude` | float | GPS latitude in decimal degrees (negative for South) |
| `longitude` | float | GPS longitude in decimal degrees (positive for East) |
| `confidence` | object | Confidence scoring information |
| `confidence.score` | float | Confidence score (0.0-1.0) |
| `confidence.level` | string | Human-readable confidence level |
| `confidence.method` | string | Extraction method used |
| `confidence.explanation` | string | Detailed explanation of confidence |
| `raw_text` | string | Original OCR text for debugging |
| `latitude_reconstructed` | boolean | True if latitude was reconstructed from fragments |
| `longitude_reconstructed` | boolean | True if longitude was reconstructed from fragments |
| `ocr_method` | string | Specific OCR configuration that succeeded |

#### Confidence Levels

| Level | Score Range | Reliability | Use Case |
|-------|-------------|-------------|----------|
| **very_high** | 0.90-1.00 | Production ready | Direct usage in applications |
| **high** | 0.80-0.89 | Highly reliable | Safe for most use cases |
| **medium_high** | 0.70-0.79 | Good quality | Generally reliable |
| **medium** | 0.60-0.69 | Moderate | Use with validation |
| **medium_low** | 0.50-0.59 | Lower quality | Requires verification |
| **low** | 0.00-0.49 | Use with caution | Manual review recommended |

### 2. Health Check
**GET** `/health`

Check service health status for monitoring and load balancers.

#### Response
```json
{
  "status": "healthy"
}
```

---

## 🧪 Testing the API

### 🔥 Render Free Tier Optimization

For production deployment on Render's free tier, **always warm up the service first**:

```bash
# 1. Wake up service (20-30s first time, <1s if already warm)
curl https://snapgeo-ocr.onrender.com/health

# 2. Wait 2-3 seconds for full initialization

# 3. Now all OCR requests will be fast (2-7s)
curl -X POST "https://snapgeo-ocr.onrender.com/ocr" \
     -F "file=@your-gps-image.jpg"
```

**📊 Performance Impact:**
- **Without warm-up**: Each OCR request may have 20-30s delay
- **With warm-up**: Only first health check is slow, all OCR requests fast
- **Best for**: Batch processing, demos, production use

### Using cURL (Local Development)
```bash
# Extract coordinates from image
curl -X POST "http://localhost:8000/ocr" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your-gps-image.jpg"

# Health check
curl -X GET "http://localhost:8000/health"
```

### Using Python (Production with Warm-up)
```python
import requests
import time

# Production URL
BASE_URL = "https://snapgeo-ocr.onrender.com"

def warmup_service():
    """Warm up Render free tier service to avoid cold starts"""
    print("🔥 Warming up service...")
    start_time = time.time()
    
    health_response = requests.get(f"{BASE_URL}/health")
    warmup_time = time.time() - start_time
    
    if warmup_time > 10:
        print(f"⏰ Cold start detected: {warmup_time:.1f}s")
        print("⏱️ Waiting 3 seconds for full initialization...")
        time.sleep(3)
    else:
        print(f"🚀 Service already warm: {warmup_time:.1f}s")
    
    print("✅ Service ready for OCR processing!")
    return health_response.json()

def extract_coordinates(image_path):
    """Extract coordinates with optimized performance"""
    with open(image_path, 'rb') as f:
        files = {'file': (image_path, f, 'image/jpeg')}
        response = requests.post(f'{BASE_URL}/ocr', files=files)
        return response.json()

# Usage example
if __name__ == "__main__":
    # 1. Warm up service first
    warmup_service()
    
    # 2. Process images (all will be fast now)
    result = extract_coordinates('gps-image.jpg')
    
    if 'latitude' in result:
        confidence = result['confidence']
        print(f"Coordinates: {result['latitude']}, {result['longitude']}")
        print(f"Confidence: {confidence['score']} ({confidence['level']})")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
```

### Using Python (Local Development)
```python
import requests

# Extract coordinates
with open('gps-image.jpg', 'rb') as f:
    files = {'file': ('gps-image.jpg', f, 'image/jpeg')}
    response = requests.post('http://localhost:8000/ocr', files=files)
    result = response.json()
    
    if 'latitude' in result:
        confidence = result['confidence']
        print(f"Coordinates: {result['latitude']}, {result['longitude']}")
        print(f"Confidence: {confidence['score']} ({confidence['level']})")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

# Health check
health = requests.get('http://localhost:8000/health')
print(f"Service status: {health.json()['status']}")
```

### Using JavaScript/Fetch
```javascript
// Extract coordinates
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/ocr', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    if (data.latitude && data.longitude) {
        console.log(`Coordinates: ${data.latitude}, ${data.longitude}`);
        console.log(`Confidence: ${data.confidence.score} (${data.confidence.level})`);
    } else {
        console.error('Error:', data.error);
    }
});
```

---

## 🔧 Integration Guide

### Frontend Integration
- **CORS Enabled:** Ready for web frontend integration
- **File Upload:** Standard HTML file input or drag-drop interface
- **Progress Indicator:** Processing takes 2-7 seconds per image
- **Error Handling:** Check for `error` field in response

### API Client Generation
Use the OpenAPI schema to generate API clients:

```bash
# Generate Python client
openapi-generator generate -i http://localhost:8000/openapi.json -g python -o snapgeo-client

# Generate TypeScript client  
openapi-generator generate -i http://localhost:8000/openapi.json -g typescript-axios -o snapgeo-ts-client

# Generate Java client
openapi-generator generate -i http://localhost:8000/openapi.json -g java -o snapgeo-java-client
```

### Batch Processing (Production with Warm-up)
For multiple images on Render free tier, **warm up first** then process:

```python
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE_URL = "https://snapgeo-ocr.onrender.com"

def warmup_service():
    """Essential for Render free tier batch processing"""
    print("🔥 Warming up service for batch processing...")
    start_time = time.time()
    
    health_response = requests.get(f"{BASE_URL}/health")
    warmup_time = time.time() - start_time
    
    if warmup_time > 10:
        print(f"⏰ Cold start: {warmup_time:.1f}s - waiting for full initialization...")
        time.sleep(3)
    
    print("✅ Service warm! Ready for fast batch processing.")
    return warmup_time

def process_image(image_path):
    """Process single image (will be fast after warm-up)"""
    with open(image_path, 'rb') as f:
        files = {'file': (image_path.name, f, 'image/jpeg')}
        response = requests.post(f'{BASE_URL}/ocr', files=files)
        return image_path.name, response.json()

def batch_process_images(image_directory):
    """Optimized batch processing for Render free tier"""
    # 1. Warm up service first (critical!)
    warmup_time = warmup_service()
    
    # 2. Get all images
    image_paths = list(Path(image_directory).glob('*.jpg'))
    print(f"📊 Processing {len(image_paths)} images...")
    
    # 3. Process images (max 3 concurrent for Render free tier)
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(process_image, image_paths))
    
    # 4. Report results
    total_time = time.time() - start_time
    successful = sum(1 for _, result in results if 'confidence' in result)
    
    print(f"\n🎉 Batch Processing Complete!")
    print(f"⏰ Warm-up time: {warmup_time:.1f}s")
    print(f"📊 Processing time: {total_time:.1f}s")
    print(f"✅ Success rate: {successful}/{len(image_paths)} ({successful/len(image_paths)*100:.1f}%)")
    
    for filename, result in results:
        if 'confidence' in result:
            conf = result['confidence']
            print(f"  {filename}: {conf['score']:.2f} confidence ({conf['level']})")
        else:
            print(f"  {filename}: Failed - {result.get('error', 'Unknown error')}")
    
    return results

# Usage
if __name__ == "__main__":
    results = batch_process_images('images/')
```

### Batch Processing (Local Development)
For local development without warm-up concerns:

```python
import requests
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

def process_image(image_path):
    with open(image_path, 'rb') as f:
        files = {'file': (image_path.name, f, 'image/jpeg')}
        response = requests.post('http://localhost:8000/ocr', files=files)
        return image_path.name, response.json()

# Process multiple images concurrently (max 3-5 concurrent requests)
image_paths = list(Path('images').glob('*.jpg'))
with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(process_image, image_paths))

for filename, result in results:
    if 'confidence' in result:
        conf = result['confidence']
        print(f"{filename}: {conf['score']:.2f} confidence ({conf['level']})")
```

---

## 🚨 Error Handling

### HTTP Status Codes
- **200:** Success - coordinates extracted
- **400:** Bad Request - invalid file format
- **422:** Unprocessable Entity - no coordinates found
- **500:** Internal Server Error - processing failed

### Best Practices
1. **Always check confidence scores** before using coordinates
2. **Handle errors gracefully** with user-friendly messages
3. **Implement retries** for network errors (not processing errors)
4. **Validate coordinate ranges** for your specific use case
5. **Log confidence levels** for monitoring and improvement

---

## 📈 Performance Expectations

### Processing Times
- **Simple images:** 2-3 seconds
- **Complex images:** 4-7 seconds  
- **Poor quality images:** 5-10 seconds

### Success Rates by Image Quality
- **Perfect quality:** ~95% success rate
- **Good quality:** ~85% success rate
- **Poor quality:** ~70% success rate
- **Very poor quality:** ~60% success rate

### Recommended Usage
- **Production:** Use confidence ≥ 0.8 for automatic processing
- **Semi-automatic:** Use confidence ≥ 0.6 with manual review
- **Manual review:** All results with confidence < 0.6

---

## 🔗 Quick Links

- **Swagger UI:** `http://localhost:8000/docs` (Interactive testing)
- **ReDoc:** `http://localhost:8000/redoc` (Clean documentation)
- **OpenAPI Schema:** `http://localhost:8000/openapi.json` (Machine-readable)
- **Health Check:** `http://localhost:8000/health` (Service status)