from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from PIL import Image
import io
import pytesseract
import os

app = FastAPI(title="Smart OCR System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Smart OCR System API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "smart-ocr"}

@app.post("/ocr")
async def extract_text_from_image(file: UploadFile = File(...)):
    try:
        # Đọc và xử lý ảnh
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        
        # Sử dụng Tesseract OCR (nhẹ hơn EasyOCR)
        extracted_text = pytesseract.image_to_string(image, lang='vie+eng')
        
        return JSONResponse({
            "success": True,
            "extracted_text": extracted_text,
            "language": "vi+en",
            "engine": "tesseract"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing error: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
