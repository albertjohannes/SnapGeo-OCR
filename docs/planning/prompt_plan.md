# SnapGeo OCR - Implementation Plan

## Overview
This document provides atomic, executable tasks for implementing the SnapGeo OCR microservice using Claude Code. Each task is scoped for single-session completion with clear acceptance criteria.

## Prerequisites Check
- [ ] Verify Python 3.10+ installation: `python --version`
- [ ] Verify Tesseract OCR installation: `tesseract --version`
- [ ] Create virtual environment: `python -m venv venv`
- [ ] Activate virtual environment: `source venv/bin/activate`

## Phase 1: Core Application Structure

### Task 1.1: Create requirements.txt
**Scope:** Define Python dependencies  
**Acceptance:** File exists with exact dependencies  
**Command:** Create `/requirements.txt`
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pillow==10.1.0
pytesseract==0.3.10
python-multipart==0.0.6
```

### Task 1.2: Create main.py - Basic FastAPI App
**Scope:** Implement FastAPI application with single endpoint  
**Acceptance:** Server starts and responds to health check  
**Command:** Create `/main.py`
```python
from fastapi import FastAPI, UploadFile, File, HTTPException
from ocr_service import extract_info_from_image
import logging

app = FastAPI(title="SnapGeo OCR", version="1.0.0")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/ocr")
async def ocr_handler(file: UploadFile = File(...)):
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    contents = await file.read()
    return extract_info_from_image(contents)
```

### Task 1.3: Create ocr_service.py - OCR Processing
**Scope:** Implement OCR processing with GPS coordinate extraction  
**Acceptance:** Function processes image bytes and returns JSON  
**Command:** Create `/ocr_service.py`
```python
from PIL import Image
import pytesseract
import io
import re
import logging

def extract_info_from_image(image_bytes: bytes) -> dict:
    try:
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Extract text using OCR
        raw_text = pytesseract.image_to_string(image)
        
        # Parse GPS coordinates using regex
        # Pattern matches: "6.26891158S 107.25537723E"
        gps_pattern = r"(\d+\.\d+)[S]\s+(\d+\.\d+)[E]"
        match = re.search(gps_pattern, raw_text, re.IGNORECASE)
        
        if match:
            # Convert to decimal degrees (South = negative, East = positive)
            latitude = -float(match.group(1))
            longitude = float(match.group(2))
            
            return {
                "raw_text": raw_text.strip(),
                "latitude": latitude,
                "longitude": longitude
            }
        else:
            return {
                "error": "Unable to extract GPS coordinates from image",
                "raw_text": raw_text.strip()
            }
            
    except Exception as e:
        return {
            "error": f"Processing failed: {str(e)}"
        }
```

## Phase 2: Testing and Validation

### Task 2.1: Install Dependencies
**Scope:** Install all required packages  
**Acceptance:** All imports work without errors  
**Command:** `pip install -r requirements.txt`

### Task 2.2: Test Server Startup
**Scope:** Verify FastAPI application starts correctly  
**Acceptance:** Server runs on localhost:8000  
**Commands:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# Test health endpoint
curl http://localhost:8000/health
```

### Task 2.3: Create Test Image (if needed)
**Scope:** Create or obtain test image with GPS overlay  
**Acceptance:** Image contains readable GPS coordinates in format "X.XXXXXXXS Y.YXXXXXXE"  
**Note:** Use existing test image or create one with GPS overlay text

### Task 2.4: Test OCR Endpoint
**Scope:** Validate /ocr endpoint with test image  
**Acceptance:** Returns valid JSON with coordinates or error  
**Command:**
```bash
curl -X POST http://localhost:8000/ocr -F "file=@test-image.jpg"
```

## Phase 3: Error Handling and Edge Cases

### Task 3.1: Add Input Validation
**Scope:** Enhance file upload validation  
**Acceptance:** Rejects non-image files with 400 status  
**Implementation:** Modify `main.py` ocr_handler function
- Check file.content_type starts with 'image/'
- Add file size limits if needed
- Return appropriate HTTP status codes

### Task 3.2: Add Logging
**Scope:** Add structured logging for debugging  
**Acceptance:** Logs show processing steps and errors  
**Implementation:** Add logging to both files
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### Task 3.3: Test Error Scenarios
**Scope:** Validate error handling works correctly  
**Acceptance:** All error cases return proper JSON responses  
**Commands:**
```bash
# Test with non-image file
curl -X POST http://localhost:8000/ocr -F "file=@test.txt"

# Test with image without GPS data
curl -X POST http://localhost:8000/ocr -F "file=@no-gps-image.jpg"
```

## Phase 4: Enhanced Features (Optional)

### Task 4.1: Add API Documentation
**Scope:** Configure FastAPI automatic docs  
**Acceptance:** Swagger docs available at /docs  
**Implementation:** Add metadata to FastAPI app
```python
app = FastAPI(
    title="SnapGeo OCR",
    description="Extract GPS coordinates from images with OCR",
    version="1.0.0"
)
```

### Task 4.2: Add CORS Support (if needed)
**Scope:** Enable cross-origin requests for frontend integration  
**Acceptance:** Frontend can call API from different domain  
**Implementation:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Task 4.3: Enhance GPS Regex (Future)
**Scope:** Support additional coordinate formats  
**Acceptance:** Handles North/East and North/West combinations  
**Implementation:** Extend regex patterns and coordinate conversion logic

## Verification Commands

### Final Integration Test
```bash
# 1. Start server
uvicorn main:app --reload

# 2. Test health endpoint
curl http://localhost:8000/health

# 3. Test OCR with valid GPS image
curl -X POST http://localhost:8000/ocr -F "file=@gps-test-image.jpg"

# 4. Test error handling
curl -X POST http://localhost:8000/ocr -F "file=@invalid.txt"

# 5. Check API documentation
open http://localhost:8000/docs
```

## Success Criteria
- [ ] Server starts without errors
- [ ] Health endpoint returns 200 status
- [ ] OCR endpoint processes images and returns JSON
- [ ] GPS coordinates extracted correctly from test images
- [ ] Error responses formatted properly
- [ ] API documentation accessible
- [ ] All curl commands work as expected

## Notes for Claude Code Execution
- Each task should be completed in sequence
- Test thoroughly before moving to next phase
- Save all output and error messages for debugging
- Use exact file paths and commands as specified
- Validate each step before proceeding