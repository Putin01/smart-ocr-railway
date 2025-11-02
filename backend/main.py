from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import easyocr
import numpy as np
from PIL import Image
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Starting OCR Reader...")
reader = easyocr.Reader(['vi', 'en'], gpu=False)
print("OCR Reader ready!")

@app.get('/')
async def home():
    return HTMLResponse('''
    <html>
    <body>
        <h1>OCR System</h1>
        <form action="/ocr" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept="image/*">
            <input type="submit" value="Upload">
        </form>
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
        avg_confidence = np.mean(confidence_scores) * 100 if confidence_scores else 0
        
        return {
            "success": True,
            "filename": file.filename,
            "text": full_text,
            "confidence": round(avg_confidence, 2),
            "total_lines": len(text_lines)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
