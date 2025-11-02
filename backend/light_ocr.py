from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
import os
import easyocr
import cv2
import numpy as np

app = FastAPI()

# Chỉ load model tiếng Anh để tiết kiệm memory
reader = easyocr.Reader(['en'])

@app.get('/')
async def home():
    return HTMLResponse('''
    <html>
        <head><title>Light OCR System</title></head>
        <body>
            <h1>Light OCR System</h1>
            <form action=\"/ocr\" method=\"post\" enctype=\"multipart/form-data\">
                <input type=\"file\" name=\"file\" accept=\"image/*\">
                <input type=\"submit\" value=\"Upload\">
            </form>
        </body>
    </html>
    ''')

@app.post('/ocr')
async def ocr_endpoint(file: UploadFile = File(...)):
    # Lưu file tạm
    temp_path = f\"temp_{file.filename}\"
    with open(temp_path, \"wb\") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # OCR với model nhẹ
    results = reader.readtext(temp_path)
    
    # Xóa file tạm
    os.remove(temp_path)
    
    # Format kết quả
    text = ' '.join([result[1] for result in results])
    confidence = np.mean([result[2] for result in results]) if results else 0
    
    return {
        \"success\": True,
        \"filename\": file.filename,
        \"text\": text,
        \"confidence\": float(confidence),
        \"line_count\": len(results)
    }
