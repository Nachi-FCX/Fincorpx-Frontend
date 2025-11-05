import os
import time
from typing import List, Tuple
from paddleocr import PaddleOCR
import numpy as np
from PIL import Image
from loguru import logger
from config import settings
from models.schemas import OcrResult, BoundingBox

class OcrProcessor:
    """PaddleOCR wrapper for text extraction from images"""
    
    def __init__(self):
        """Initialize PaddleOCR"""
        try:
            self.ocr = PaddleOCR(
                use_angle_cls=settings.OCR_USE_ANGLE_CLS,
                lang=settings.OCR_LANGUAGE,
                use_gpu=settings.OCR_USE_GPU,
                det_db_thresh=settings.OCR_DET_DB_THRESH,
                det_db_box_thresh=settings.OCR_DET_DB_BOX_THRESH,
                show_log=False
            )
            logger.info("PaddleOCR initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {str(e)}")
            raise
    
    def process_image(self, image_path: str, page_number: int = 1) -> Tuple[List[OcrResult], float]:
        """
        Process a single image and extract text with bounding boxes
        
        Args:
            image_path: Path to the image file
            page_number: Page number (for PDF documents)
            
        Returns:
            Tuple of (list of OCR results, processing time)
        """
        try:
            start_time = time.time()
            
            # Read image
            img = Image.open(image_path)
            img_array = np.array(img)
            
            # Get image dimensions
            img_height, img_width = img_array.shape[:2]
            
            # Perform OCR
            result = self.ocr.ocr(img_array, cls=settings.OCR_USE_ANGLE_CLS)
            
            # Parse results
            ocr_results = []
            if result and len(result) > 0 and result[0]:
                for line in result[0]:
                    bbox_coords = line[0]
                    text = line[1][0]
                    confidence = float(line[1][1])
                    
                    # Filter by confidence threshold
                    if confidence < settings.CONFIDENCE_THRESHOLD:
                        continue
                    
                    # Convert bbox to our format
                    # PaddleOCR returns [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                    x_coords = [point[0] for point in bbox_coords]
                    y_coords = [point[1] for point in bbox_coords]
                    
                    x = min(x_coords)
                    y = min(y_coords)
                    width = max(x_coords) - x
                    height = max(y_coords) - y
                    
                    # Normalize coordinates (0-1 range)
                    bbox = BoundingBox(
                        x=x / img_width,
                        y=y / img_height,
                        width=width / img_width,
                        height=height / img_height
                    )
                    
                    ocr_results.append(OcrResult(
                        text=text,
                        confidence=confidence,
                        bbox=bbox,
                        page=page_number
                    ))
            
            processing_time = time.time() - start_time
            logger.info(f"Processed image: {len(ocr_results)} text regions found in {processing_time:.2f}s")
            
            return ocr_results, processing_time
            
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {str(e)}")
            raise
    
    def process_multiple_images(self, image_paths: List[str]) -> Tuple[List[OcrResult], float]:
        """
        Process multiple images (e.g., from multi-page PDF)
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            Tuple of (combined OCR results, total processing time)
        """
        all_results = []
        total_time = 0
        
        for idx, image_path in enumerate(image_paths, start=1):
            try:
                results, proc_time = self.process_image(image_path, page_number=idx)
                all_results.extend(results)
                total_time += proc_time
            except Exception as e:
                logger.error(f"Failed to process page {idx}: {str(e)}")
                continue
        
        return all_results, total_time
    
    def calculate_average_confidence(self, results: List[OcrResult]) -> float:
        """Calculate average confidence score from OCR results"""
        if not results:
            return 0.0
        
        total_confidence = sum(r.confidence for r in results)
        return total_confidence / len(results)
    
    def get_text_by_region(self, results: List[OcrResult], region: BoundingBox, page: int = 1) -> List[str]:
        """
        Get all text within a specific region
        
        Args:
            results: List of OCR results
            region: Bounding box region to search
            page: Page number
            
        Returns:
            List of text strings in the region
        """
        texts = []
        for result in results:
            if result.page != page:
                continue
            
            # Check if bbox overlaps with region
            if self._bbox_overlaps(result.bbox, region):
                texts.append(result.text)
        
        return texts
    
    def _bbox_overlaps(self, bbox1: BoundingBox, bbox2: BoundingBox) -> bool:
        """Check if two bounding boxes overlap"""
        x1_min, y1_min = bbox1.x, bbox1.y
        x1_max, y1_max = bbox1.x + bbox1.width, bbox1.y + bbox1.height
        
        x2_min, y2_min = bbox2.x, bbox2.y
        x2_max, y2_max = bbox2.x + bbox2.width, bbox2.y + bbox2.height
        
        # Check for overlap
        return not (x1_max < x2_min or x2_max < x1_min or y1_max < y2_min or y2_max < y1_min)

# Singleton instance
ocr_processor = OcrProcessor()
