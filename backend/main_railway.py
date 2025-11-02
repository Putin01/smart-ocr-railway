from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os
import easyocr
import cv2
import numpy as np
from PIL import Image
import io

app = FastAPI(title="Smart OCR System - Railway")

# Cau hinh CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Khoi tao OCR Reader...")
reader = easyocr.Reader(['vi', 'en'], gpu=False)
print("OCR Reader ready!")

@app.get('/')
async def home():
    return HTMLResponse('Smart OCR System - Railway')

@app.post('/ocr')
async def ocr_endpoint(file: UploadFile = File(...)):
    try:
        content = await file.read()
        image = Image.open(io.BytesIO(content))
        image_np = np.array(image)
        
        results = reader.readtext(image_np)
        text_lines = [result[1] for result in results]
        confidence_scores = [result[2] for result in results]
        
        full_text = '\n'.join(text_lines)
        avg_confidence = np.mean(confidence_scores) if confidence_scores else 0
        
        return {
            "success": True,
            "filename": file.filename,
            "text": full_text,
            "confidence": float(avg_confidence),
            "total_lines": len(text_lines),
            "engine": "EasyOCR-HighAccuracy"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "filename": file.filename
        }

@app.get('/health')
async def health_check():
    return {"status": "healthy", "service": "Smart OCR System"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
