from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os
import easyocr
import cv2
import numpy as np
from PIL import Image
import io

app = FastAPI(title="Smart OCR System")

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("🔄 Khởi tạo OCR Reader...")
reader = easyocr.Reader(['vi', 'en'], gpu=False)
print("✅ OCR Reader ready!")

@app.get('/')
async def home():
    return HTMLResponse('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart OCR System - High Accuracy</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 30px; border-radius: 10px; }
            h1 { color: #333; text-align: center; }
            .upload-form { text-align: center; margin: 30px 0; }
            input[type="file"] { margin: 10px 0; }
            input[type="submit"] { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            .result { background: white; padding: 20px; border-radius: 5px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Smart OCR System</h1>
            <p style="text-align: center;">Hệ thống OCR thế hệ mới - Độ chính xác cao</p>
            
            <form class="upload-form" action="/ocr" method="post" enctype="multipart/form-data">
                <input type="file" name="file" accept="image/*" required>
                <br>
                <input type="submit" value="Nhận dạng văn bản">
            </form>
        </div>
    </body>
    </html>
    ''')

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
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
