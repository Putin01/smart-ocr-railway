import re
import numpy as np
from typing import Dict, List, Tuple, Any
import logging

class DocumentClassifier:
    def __init__(self):
        self.category_keywords = {
            "invoice": ["hóa đơn", "invoice", "số tiền", "thanh toán", "tổng cộng", "đơn giá", "thành tiền"],
            "contract": ["hợp đồng", "điều khoản", "bên a", "bên b", "ký kết", "thỏa thuận", "điều lệ"],
            "id_card": ["căn cước", "chứng minh", "cmnd", "số:", "quốc tịch", "hộ khẩu", "ngày sinh"],
            "driver_license": ["bằng lái", "giấy phép", "hạng", "ngày cấp", "nơi cấp", "điều khiển"],
            "receipt": ["biên lai", "receipt", "phiếu thu", "đã nhận", "số tiền", "người nộp"],
            "resume": ["sơ yếu lý lịch", "cv", "kinh nghiệm", "kỹ năng", "học vấn", "mục tiêu"],
            "certificate": ["chứng chỉ", "bằng cấp", "tốt nghiệp", "xác nhận", "hoàn thành"]
        }
        
        self.logger = logging.getLogger(__name__)
    
    def extract_features(self, text: str) -> Dict[str, float]:
        """Trích xuất đặc trưng từ văn bản"""
        text_lower = text.lower()
        features = {}
        
        # Đếm từ khóa theo danh mục
        for category, keywords in self.category_keywords.items():
            features[f"kw_{category}"] = sum(1 for keyword in keywords if keyword in text_lower)
        
        # Đặc trưng về độ dài và cấu trúc
        features["length"] = len(text)
        features["line_count"] = text.count("\n")
        features["has_dates"] = bool(re.search(r"\d{1,2}/\d{1,2}/\d{4}", text))
        features["has_numbers"] = bool(re.search(r"\d+", text))
        features["has_money"] = bool(re.search(r"\d+[.,]\d+", text))
        features["word_count"] = len(text.split())
        
        return features
    
    def classify(self, text: str) -> Tuple[str, float, Dict[str, Any]]:
        """Phân loại tài liệu và trả về kết quả"""
        if not text or len(text.strip()) < 10:
            return "unknown", 0.0, {}
        
        features = self.extract_features(text)
        
        # Rule-based classification với điểm số
        scores = {}
        for category in self.category_keywords.keys():
            keyword_score = features.get(f"kw_{category}", 0)
            structure_score = 0
            
            # Điểm cấu trúc dựa trên loại tài liệu
            if category == "invoice" and features["has_money"]:
                structure_score += 2
            if category == "id_card" and features["has_dates"]:
                structure_score += 1
            if category == "contract" and features["length"] > 500:
                structure_score += 1
            
            scores[category] = keyword_score + structure_score
        
        # Tìm category có điểm cao nhất
        if scores:
            best_category = max(scores, key=scores.get)
            max_score = scores[best_category]
            
            # Chuẩn hóa confidence score (0-1)
            total_possible = max(len(self.category_keywords[best_category]) + 2, 1)
            confidence = min(max_score / total_possible, 1.0)
            
            # Ngưỡng confidence tối thiểu
            if confidence > 0.3:
                metadata = self.extract_metadata(text, best_category)
                return best_category, round(confidence, 3), metadata
        
        return "unknown", 0.0, {}
    
    def extract_metadata(self, text: str, doc_type: str) -> Dict[str, Any]:
        """Trích xuất metadata dựa trên loại tài liệu"""
        metadata = {}
        text_lower = text.lower()
        
        try:
            if doc_type == "invoice":
                patterns = {
                    "invoice_number": r"số\s*hd:\s*([a-z0-9-]+)",
                    "date": r"ngày\s*(\d{1,2}/\d{1,2}/\d{4})",
                    "total_amount": r"tổng\s*cộng:\s*([\d.,]+)",
                    "customer": r"khách\s*hàng:\s*([^\n]+)"
                }
            elif doc_type == "id_card":
                patterns = {
                    "id_number": r"số:\s*([\d]+)",
                    "name": r"họ\s*và\s*tên:\s*([^\n]+)",
                    "birthday": r"ngày\s*sinh:\s*(\d{1,2}/\d{1,2}/\d{4})"
                }
            else:
                patterns = {}
            
            for key, pattern in patterns.items():
                match = re.search(pattern, text_lower)
                if match:
                    metadata[key] = match.group(1).strip()
                    
        except Exception as e:
            self.logger.warning(f"Error extracting metadata: {e}")
        
        return metadata

if __name__ == "__main__":
    classifier = DocumentClassifier()
    
    test_docs = [
        "HÓA ĐƠN BÁN HÀNG\nSố HD: HD-2024-001\nNgày: 15/01/2024\nKhách hàng: Công ty ABC\nTổng cộng: 10,000,000 VND",
        "CHỨNG MINH NHÂN DÂN\nSố: 001123456789\nHọ và tên: NGUYỄN VĂN A\nNgày sinh: 15/05/1990"
    ]
    
    for i, doc in enumerate(test_docs):
        doc_type, confidence, metadata = classifier.classify(doc)
        print(f"Document {i+1}: {doc_type} (confidence: {confidence})")
        print(f"Metadata: {metadata}")
        print("-" * 50)
