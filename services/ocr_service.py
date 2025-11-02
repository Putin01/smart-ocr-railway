# services/ocr_service.py - OCR Service mới cho hệ thống
import os
import logging
from typing import Dict, Any
from services.smart_ocr import extract_text_from_image

logger = logging.getLogger(__name__)

class OCRService:
    """OCR Service cho hệ thống Smart OCR"""
    
    def __init__(self):
        self.initialized = False
        self._initialize()
    
    def _initialize(self):
        """Khởi tạo service"""
        try:
            # Test OCR engine
            test_result = extract_text_from_image(__file__)  # Test với chính file này
            if not test_result['success']:
                logger.warning("OCR engine cần khởi tạo lại...")
            
            self.initialized = True
            logger.info("✅ OCR Service đã sẵn sàng")
            
        except Exception as e:
            logger.error(f"❌ Lỗi khởi tạo OCR Service: {e}")
    
    def process_document(self, image_path: str) -> Dict[str, Any]:
        """
        Xử lý document với OCR mới
        
        Args:
            image_path: Đường dẫn đến file ảnh
            
        Returns:
            Dict chứa kết quả OCR
        """
        if not os.path.exists(image_path):
            return {
                'success': False,
                'error': f'File không tồn tại: {image_path}',
                'text': '',
                'confidence': 0.0
            }
        
        try:
            logger.info(f"🔄 OCR đang xử lý: {os.path.basename(image_path)}")
            
            result = extract_text_from_image(image_path)
            
            if result['success']:
                logger.info(f"✅ OCR thành công: {result['confidence']:.2%} độ tin cậy")
            else:
                logger.error(f"❌ OCR thất bại: {result['error']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Lỗi xử lý OCR: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0.0
            }
    
    def batch_process(self, image_paths: list) -> list:
        """Xử lý nhiều ảnh cùng lúc"""
        results = []
        for image_path in image_paths:
            results.append(self.process_document(image_path))
        return results

# Singleton instance cho toàn hệ thống
ocr_service = OCRService()

# API cũ để tương thích ngược
def process_image_ocr(image_path: str) -> Dict[str, Any]:
    """API cũ - tương thích ngược"""
    return ocr_service.process_document(image_path)

def extract_text(image_path: str) -> str:
    """Trích xuất text đơn giản - tương thích ngược"""
    result = ocr_service.process_document(image_path)
    return result['text'] if result['success'] else ''

if __name__ == '__main__':
    # Test service
    service = OCRService()
    test_image = "uploads/66e5febd.png"
    
    if os.path.exists(test_image):
        result = service.process_document(test_image)
        print(f"🎯 Kết quả: {result['confidence']:.2%} độ tin cậy")
        print(f"📝 Text: {result['text'][:100]}...")
    else:
        print("⚠️ Không tìm thấy ảnh test")
