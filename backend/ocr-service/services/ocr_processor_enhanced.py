"""
Enhanced OCR Processor with PP-StructureV2 Support
Optimized for multi-vendor invoice processing
"""

import os
import time
import cv2
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from PIL import Image
from paddleocr import PaddleOCR, PPStructure
from loguru import logger
from models.schemas import OcrResult, BoundingBox


class EnhancedOcrProcessor:
    """
    Production-ready OCR processor with:
    - PP-OCRv4 for text extraction
    - PP-StructureV2 for layout analysis
    - Table recognition
    - Image preprocessing
    - Batch processing support
    """
    
    def __init__(
        self, 
        use_structure: bool = True,
        use_gpu: bool = False,
        enable_table_recognition: bool = True
    ):
        """
        Initialize enhanced OCR engines
        
        Args:
            use_structure: Enable PP-StructureV2 for layout analysis
            use_gpu: Use GPU acceleration (requires CUDA)
            enable_table_recognition: Enable table extraction
        """
        try:
            # Standard PP-OCRv4 for text extraction
            self.ocr = PaddleOCR(
                use_angle_cls=False,  # Disabled for speed
                lang='en',
                use_gpu=use_gpu,
                det_db_thresh=0.3,
                det_db_box_thresh=0.5,
                show_log=False,
                # Performance optimizations
                use_mp=True,
                total_process_num=4,
                det_limit_side_len=2048,
                rec_batch_num=8
            )
            
            # PP-StructureV2 for layout + table analysis
            self.use_structure = use_structure
            if use_structure:
                self.structure = PPStructure(
                    use_gpu=use_gpu,
                    show_log=False,
                    layout=True,  # Layout analysis
                    table=enable_table_recognition,  # Table recognition
                    ocr=True,  # OCR within structure
                    recovery=False  # Disable docx recovery for speed
                )
                logger.info("✓ PP-StructureV2 initialized with layout analysis")
            
            logger.info("✓ Enhanced OCR Processor initialized successfully")
            
        except Exception as e:
            logger.error(f"✗ Failed to initialize OCR engines: {e}")
            raise
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Advanced preprocessing for better OCR accuracy
        
        Steps:
        1. Resize if too large (max 2048px)
        2. Denoise
        3. Enhance contrast
        4. Deskew (optional)
        """
        try:
            # Resize if too large
            h, w = image.shape[:2]
            max_dim = 2048
            if max(h, w) > max_dim:
                scale = max_dim / max(h, w)
                new_w, new_h = int(w * scale), int(h * scale)
                image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
                logger.debug(f"Resized image from {w}x{h} to {new_w}x{new_h}")
            
            # Convert to grayscale if not already
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(gray, h=10)
            
            # Enhance contrast using CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)
            
            # Convert back to BGR for PaddleOCR
            if len(image.shape) == 3:
                result = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
            else:
                result = enhanced
            
            return result
            
        except Exception as e:
            logger.warning(f"Preprocessing failed, using original: {e}")
            return image
    
    def process_image(
        self, 
        image_path: str, 
        page_number: int = 1,
        preprocess: bool = True
    ) -> Tuple[List[OcrResult], Dict[str, Any], float]:
        """
        Process single image with both OCR and structure analysis
        
        Returns:
            - ocr_results: List of text regions with bounding boxes
            - structure_data: Layout and table information
            - processing_time: Time taken
        """
        try:
            start_time = time.time()
            
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Cannot read image: {image_path}")
            
            # Preprocess
            if preprocess:
                img = self.preprocess_image(img)
            
            h, w = img.shape[:2]
            
            # 1. Standard OCR for text extraction
            ocr_result = self.ocr.ocr(img, cls=False)
            
            # 2. Structure analysis (if enabled)
            structure_data = {}
            if self.use_structure:
                structure_result = self.structure(img)
                structure_data = self._parse_structure_result(structure_result, page_number)
            
            # Parse OCR results
            ocr_results = []
            if ocr_result and len(ocr_result) > 0 and ocr_result[0]:
                for line in ocr_result[0]:
                    try:
                        bbox_coords = line[0]
                        text = line[1][0]
                        confidence = float(line[1][1])
                        
                        # Filter low confidence
                        if confidence < 0.5:
                            continue
                        
                        # Calculate normalized bounding box
                        x_coords = [point[0] for point in bbox_coords]
                        y_coords = [point[1] for point in bbox_coords]
                        
                        x = min(x_coords)
                        y = min(y_coords)
                        width = max(x_coords) - x
                        height = max(y_coords) - y
                        
                        bbox = BoundingBox(
                            x=x / w,
                            y=y / h,
                            width=width / w,
                            height=height / h
                        )
                        
                        ocr_results.append(OcrResult(
                            text=text,
                            confidence=confidence,
                            bbox=bbox,
                            page=page_number
                        ))
                    except Exception as e:
                        logger.warning(f"Skipping malformed OCR line: {e}")
                        continue
            
            processing_time = time.time() - start_time
            logger.info(f"✓ Page {page_number}: {len(ocr_results)} regions, {processing_time:.2f}s")
            
            return ocr_results, structure_data, processing_time
            
        except Exception as e:
            logger.error(f"✗ Error processing {image_path}: {e}")
            raise
    
    def _parse_structure_result(self, structure_result: List[Dict], page_number: int) -> Dict[str, Any]:
        """Parse PP-StructureV2 output into structured format"""
        parsed = {
            'page': page_number,
            'layout_elements': [],
            'tables': []
        }
        
        for element in structure_result:
            elem_type = element.get('type', 'unknown')
            bbox = element.get('bbox', [])
            
            if elem_type == 'table' and 'res' in element:
                # Table detected
                table_data = {
                    'bbox': bbox,
                    'cells': element['res'].get('html', ''),
                    'confidence': element.get('score', 0.0)
                }
                parsed['tables'].append(table_data)
            
            elif elem_type in ['text', 'title', 'figure']:
                parsed['layout_elements'].append({
                    'type': elem_type,
                    'bbox': bbox,
                    'text': element.get('res', {}).get('text', ''),
                    'confidence': element.get('score', 0.0)
                })
        
        return parsed
    
    def process_batch(
        self, 
        image_paths: List[str],
        preprocess: bool = True
    ) -> Tuple[List[OcrResult], List[Dict[str, Any]], float]:
        """
        Process multiple images efficiently
        
        Returns:
            - Combined OCR results from all pages
            - Structure data for each page
            - Total processing time
        """
        all_ocr_results = []
        all_structure_data = []
        total_time = 0
        
        for idx, image_path in enumerate(image_paths, start=1):
            try:
                ocr_results, structure_data, proc_time = self.process_image(
                    image_path, 
                    page_number=idx,
                    preprocess=preprocess
                )
                
                all_ocr_results.extend(ocr_results)
                all_structure_data.append(structure_data)
                total_time += proc_time
                
            except Exception as e:
                logger.error(f"✗ Failed to process page {idx}: {e}")
                continue
        
        logger.info(f"✓ Batch processed: {len(image_paths)} pages in {total_time:.2f}s")
        return all_ocr_results, all_structure_data, total_time


# Singleton instance (optional - can be used for testing)
enhanced_ocr_processor = EnhancedOcrProcessor(
    use_structure=False,  # Disable for now to avoid dependencies
    use_gpu=False,
    enable_table_recognition=False
)
