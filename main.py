from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from typing import List, Optional
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Smart OCR System API",
    description="AI-powered OCR with Document Classification",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services with error handling
services_ready = False
ocr_service = None
classifier = None

try:
    from services.ocr_service import OCRService
    from document_classifier import DocumentClassifier
    ocr_service = OCRService()
    classifier = DocumentClassifier()
    services_ready = True
    logger.info("✅ All services initialized successfully")
except ImportError as e:
    logger.warning(f"Optional service not available: {e}")
except Exception as e:
    logger.error(f"Service initialization failed: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Smart OCR System API", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway monitoring"""
    status = "healthy" if services_ready else "degraded"
    return {"status": status, "version": "2.0.0", "service": "smart-ocr"}

@app.post("/ocr")
async def process_ocr(
    file: UploadFile = File(...),
    language: str = "vi",
    classify_document: bool = True
):
    """Process OCR on uploaded image and optionally classify document type"""
    if not services_ready:
        raise HTTPException(status_code=503, detail="OCR service not available")
    
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read file content
        contents = await file.read()
        
        # Process OCR
        ocr_result = ocr_service.process_image(contents, language=language)
        
        # Classify document if requested
        classification_result = {}
        if classify_document and ocr_result["text"]:
            doc_type, confidence, metadata = classifier.classify(ocr_result["text"])
            classification_result = {
                "document_type": doc_type,
                "confidence": confidence,
                "metadata": metadata
            }
        
        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "ocr_result": ocr_result,
            "classification": classification_result,
            "processing_time": ocr_result.get("processing_time", 0)
        })
        
    except Exception as e:
        logger.error(f"OCR processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/classify")
async def classify_document(text: str):
    """Classify document type from text"""
    if not services_ready:
        raise HTTPException(status_code=503, detail="Classification service not available")
    
    try:
        doc_type, confidence, metadata = classifier.classify(text)
        
        return {
            "success": True,
            "document_type": doc_type,
            "confidence": confidence,
            "metadata": metadata
        }
        
    except Exception as e:
        logger.error(f"Classification error: {e}")
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")

@app.get("/supported-documents")
async def get_supported_documents():
    """Get list of supported document types"""
    if not services_ready:
        return {"supported_documents": [], "total_types": 0, "note": "Service not available"}
    
    return {
        "supported_documents": list(classifier.category_keywords.keys()),
        "total_types": len(classifier.category_keywords)
    }

# Railway sẽ sử dụng PORT environment variable
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        workers=1,
        access_log=True
    )
