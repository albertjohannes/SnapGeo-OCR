# SnapGeo OCR - Deployment Guide

## Local Development & Testing

### Prerequisites
- Python 3.10+
- Tesseract OCR: `brew install tesseract` (macOS) or `apt install tesseract-ocr` (Ubuntu)

### Setup
```bash
# Clone and setup
git clone <repository-url>
cd snapgeo-ocr
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Local Testing with Postman

#### 1. Health Check
- **Method:** GET
- **URL:** `http://localhost:8000/health`
- **Expected Response:**
```json
{"status": "healthy"}
```

#### 2. OCR Endpoint Test
- **Method:** POST
- **URL:** `http://localhost:8000/ocr`
- **Body Type:** form-data
- **Key:** `file` (File type)
- **Value:** Select image file with GPS overlay

**Success Response:**
```json
{
  "raw_text": "07 August 2025 06.03.16\n6.26891158S 107.25537723E\n...",
  "latitude": -6.26891158,
  "longitude": 107.25537723
}
```

**Error Response (invalid file):**
```json
{
  "error": "Unable to extract GPS coordinates from image",
  "raw_text": "Some extracted text..."
}
```

#### 3. API Documentation
- **URL:** `http://localhost:8000/docs`
- Interactive Swagger UI for testing

## GitHub Setup

### Repository Structure
```
snapgeo-ocr/
├── main.py
├── ocr_service.py
├── requirements.txt
├── CLAUDE.md
├── .gitignore
├── runtime.txt          # For Render deployment
└── docs/
    ├── product/PRD.md
    ├── technical/ARCHITECTURE.md
    ├── planning/prompt_plan.md
    └── deployment/DEPLOYMENT.md
```

### Required Files for Deployment

#### `.gitignore`
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Testing
test-images/
*.log
```

#### `runtime.txt` (for Render)
```
python-3.11.0
```

## Render.com Deployment

### 1. Prepare for Deployment

#### Update requirements.txt for production:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pillow==10.1.0
pytesseract==0.3.10
python-multipart==0.0.6
gunicorn==21.2.0
```

#### Create `render.yaml` (optional):
```yaml
services:
  - type: web
    name: snapgeo-ocr
    env: python
    buildCommand: |
      apt-get update && apt-get install -y tesseract-ocr
      pip install -r requirements.txt
    startCommand: gunicorn main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

### 2. Deploy to Render

#### Via GitHub Integration:
1. Push code to GitHub repository
2. Connect GitHub repo to Render
3. Configure build settings:
   - **Build Command:** 
     ```bash
     apt-get update && apt-get install -y tesseract-ocr && pip install -r requirements.txt
     ```
   - **Start Command:**
     ```bash
     gunicorn main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
     ```
   - **Environment:** Python 3.11.0

#### Manual Deploy:
1. Install Render CLI
2. Deploy from command line:
   ```bash
   render deploy
   ```

### 3. Environment Configuration

#### Environment Variables (if needed):
- `PORT`: Auto-configured by Render
- `PYTHON_VERSION`: 3.11.0
- `TESSERACT_CONFIG`: Custom config if needed

### 4. Health Checks
Render will use the `/health` endpoint for monitoring:
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2025-08-07T12:00:00Z"}
```

## Production Considerations

### Performance Optimization
```python
# In main.py, add for production
import multiprocessing

# Configure for Render (2 workers recommended for free tier)
workers = min(multiprocessing.cpu_count(), 2)
```

### CORS Configuration (if needed for frontend)
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### File Size Limits
```python
from fastapi import FastAPI, UploadFile, File, HTTPException

@app.post("/ocr")
async def ocr_handler(file: UploadFile = File(..., max_length=10*1024*1024)):  # 10MB limit
    # Existing code...
```

## Testing Production Deployment

### 🔥 Render Free Tier Optimization - CRITICAL

**Before any OCR processing, ALWAYS warm up the service first:**

```bash
# 1. Wake up service (20-30s on cold start, <1s if warm)
curl https://your-app.onrender.com/health

# 2. Wait 2-3 seconds for full initialization

# 3. Now OCR requests will be fast (2-7s instead of 20-30s)
curl -X POST https://your-app.onrender.com/ocr -F "file=@image.jpg"
```

**📊 Performance Impact:**
- **Without warm-up**: Each OCR request has 20-30s delay
- **With warm-up**: Only first health check is slow, OCR is fast
- **Batch processing**: Essential for multiple images

### Postman Collection for Production
Create collection with base URL: `https://your-app-name.onrender.com`

#### Recommended Testing Order:
1. **Service Warm-up:** `GET /health` (wait for response)
2. **OCR Processing:** `POST /ocr` (now fast!)
3. **API Docs:** `GET /docs`

#### Python Production Client Example:
```python
import requests
import time

def warmup_service(base_url):
    """Essential for Render free tier"""
    print("🔥 Warming up service...")
    start_time = time.time()
    
    health_response = requests.get(f"{base_url}/health")
    warmup_time = time.time() - start_time
    
    if warmup_time > 10:
        print(f"⏰ Cold start: {warmup_time:.1f}s - waiting...")
        time.sleep(3)
    
    print("✅ Service ready!")
    return health_response.json()

# Usage
BASE_URL = "https://your-app.onrender.com"
warmup_service(BASE_URL)  # Call first!
# Now process images normally
```

### Load Testing
```bash
# Using curl for basic load test
for i in {1..10}; do
  curl -X POST https://your-app.onrender.com/ocr \
    -F "file=@test-image.jpg" &
done
wait
```

## Monitoring & Logs

### Render Dashboard
- View logs in real-time
- Monitor resource usage
- Check deployment status

### Application Logs
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Use in endpoints
logger.info(f"Processing OCR request for file: {file.filename}")
```

## Troubleshooting

### Common Issues

#### Tesseract Not Found
- Ensure build command installs tesseract-ocr
- Check PATH configuration

#### Memory Limits
- Optimize image processing
- Consider file size limits
- Monitor memory usage

#### Slow Response Times
- **RENDER FREE TIER**: Use warm-up strategy (see above) - most common issue
- Implement image preprocessing for large images
- Consider async processing for large files  
- Monitor OCR processing time vs cold start time

### Debug Commands
```bash
# Test locally with production settings
gunicorn main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Check Tesseract installation
tesseract --version
```

## Scaling Considerations

### Horizontal Scaling
- Stateless design supports multiple instances
- Database not required for current functionality
- Load balancer configuration for high traffic

### Performance Metrics
- Response time monitoring
- OCR accuracy tracking
- Error rate analysis
- Memory and CPU utilization