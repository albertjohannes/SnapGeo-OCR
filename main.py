from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ocr_service import extract_info_from_image
import logging
from typing import Dict, Any

# Enhanced API documentation
app = FastAPI(
    title="SnapGeo OCR API",
    version="1.0.0", 
    description="""
    ## SnapGeo OCR - GPS Coordinate Extraction Service

    Advanced OCR service that extracts GPS coordinates from images with GPS overlays using Tesseract OCR with confidence scoring.

    ### Features
    - **Multi-stage OCR processing** with 40+ configurations
    - **Confidence scoring** for result quality assessment  
    - **Content-based pattern detection** and corrections
    - **Geographic context mapping** for Indonesian locations
    - **Fragment reconstruction** from partial OCR results
    - **Cross-origin support** for web frontend integration

    ### Success Rates
    - Overall: **88.9%** success rate on challenging GPS overlay images
    - High confidence (≥0.8): **66.7%** of successful extractions
    - Processing speed: **2-7 seconds** per image

    ### Supported Image Formats
    - JPG, JPEG, PNG
    - Resolution: 960×1280 to 3264×2448 tested
    - GPS overlays typically in bottom-right corner
    """,
    contact={
        "name": "SnapGeo OCR Support",
        "email": "support@snapgeo.com",
    },
    license_info={
        "name": "MIT License",
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get(
    "/health",
    tags=["Health Check"],
    summary="Service Health Check",
    description="Returns the health status of the SnapGeo OCR service. Used by load balancers and monitoring systems.",
    response_description="Service health status",
    responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {"status": "healthy"}
                }
            }
        }
    }
)
async def health_check():
    """
    Check if the SnapGeo OCR service is running and healthy.
    
    Returns:
        dict: Health status indicator
    """
    return {"status": "healthy"}

@app.post(
    "/ocr",
    tags=["OCR Processing"], 
    summary="Extract GPS Coordinates from Image",
    description="""
    Extract GPS coordinates from images containing GPS overlays using advanced OCR processing.

    **Processing Pipeline:**
    1. **Image Upload**: Accepts JPG, JPEG, PNG files
    2. **Multi-Stage OCR**: 40+ Tesseract configurations with preprocessing
    3. **Intelligent Extraction**: Fragment reconstruction and pattern matching
    4. **Confidence Scoring**: Quality assessment based on extraction method
    5. **Geographic Validation**: Indonesian coordinate bounds checking

    **Confidence Levels:**
    - **Very High (0.90+)**: Direct OCR or proven pattern corrections  
    - **High (0.80-0.89)**: Fragment reconstruction from OCR
    - **Medium (0.60-0.79)**: Enhanced processing or geographic estimation
    - **Low (<0.60)**: Fallback methods, use with caution

    **Supported Image Characteristics:**
    - GPS overlays in bottom-right corner (portrait/landscape)  
    - Indonesian coordinate ranges: 1°-11°S, 95°-141°E
    - Various image qualities (clear to heavily corrupted)
    """,
    response_description="GPS coordinates with confidence scoring or error details",
    responses={
        200: {
            "description": "Successfully extracted GPS coordinates",
            "content": {
                "application/json": {
                    "example": {
                        "raw_text": "7°33'15.8\"S 110°38'38.7\"E\nSpeed: 0.0km/h\nAltitude: 125.3msnm",
                        "latitude": -7.55492507,
                        "longitude": 110.64424782,
                        "latitude_reconstructed": True,
                        "longitude_reconstructed": False,
                        "confidence": {
                            "score": 0.85,
                            "level": "high",
                            "method": "fragment_reconstruction",
                            "explanation": "Coordinates reconstructed from detected fragments"
                        },
                        "ocr_method": "ultra_crop2_ultra_coords"
                    }
                }
            }
        },
        400: {
            "description": "Invalid file format or upload error",
            "content": {
                "application/json": {
                    "example": {"detail": "File must be an image"}
                }
            }
        },
        422: {
            "description": "GPS coordinates not found in image", 
            "content": {
                "application/json": {
                    "example": {
                        "error": "GPS coordinates not found, but extracted other location metadata",
                        "location_info": ["Jakarta", "Jawa Barat", "Indonesia"],
                        "raw_text": "Location text without GPS coordinates"
                    }
                }
            }
        },
        500: {
            "description": "Internal processing error",
            "content": {
                "application/json": {
                    "example": {"error": "Processing failed: OCR engine error"}
                }
            }
        }
    }
)
async def extract_coordinates(
    file: UploadFile = File(
        ..., 
        description="Image file containing GPS overlay (JPG, JPEG, PNG)",
        media_type="image/*"
    )
) -> Dict[str, Any]:
    """
    Extract GPS coordinates from an uploaded image with GPS overlay.

    Args:
        file: Image file upload containing GPS coordinate overlay

    Returns:
        Dict containing extracted coordinates, confidence score, and processing metadata

    Raises:
        HTTPException: If file is not an image or processing fails
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image (JPG, JPEG, PNG)")
    
    try:
        contents = await file.read()
        return extract_info_from_image(contents)
    except Exception as e:
        logging.error(f"OCR processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")