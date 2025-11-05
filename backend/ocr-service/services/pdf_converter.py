import os
import fitz  # PyMuPDF
from pdf2image import convert_from_path
from PIL import Image
from typing import List
from loguru import logger
from config import settings

class PdfConverter:
    """Convert PDF files to images for OCR processing"""
    
    def __init__(self):
        self.dpi = settings.PDF_DPI
        self.temp_dir = settings.TEMP_DIR
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def pdf_to_images(self, pdf_path: str) -> List[str]:
        """
        Convert PDF to images using pdf2image
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of image file paths
        """
        try:
            logger.info(f"Converting PDF to images: {pdf_path}")
            
            # Set poppler path for macOS (Homebrew installation)
            poppler_path = "/opt/homebrew/bin" if os.path.exists("/opt/homebrew/bin/pdfinfo") else None
            
            # Convert PDF to images
            images = convert_from_path(
                pdf_path,
                dpi=self.dpi,
                fmt='png',
                thread_count=4,
                poppler_path=poppler_path
            )
            
            # Save images
            image_paths = []
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            
            for idx, image in enumerate(images, start=1):
                # Resize if too large
                if max(image.size) > settings.IMAGE_MAX_SIZE:
                    image.thumbnail((settings.IMAGE_MAX_SIZE, settings.IMAGE_MAX_SIZE), Image.Resampling.LANCZOS)
                
                image_path = os.path.join(self.temp_dir, f"{base_name}_page_{idx}.png")
                image.save(image_path, 'PNG', optimize=True)
                image_paths.append(image_path)
                logger.info(f"Saved page {idx} to {image_path}")
            
            return image_paths
            
        except Exception as e:
            logger.error(f"Error converting PDF to images: {str(e)}")
            raise
    
    def pdf_to_images_pymupdf(self, pdf_path: str) -> List[str]:
        """
        Convert PDF to images using PyMuPDF (faster but may have quality issues)
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of image file paths
        """
        try:
            logger.info(f"Converting PDF to images with PyMuPDF: {pdf_path}")
            
            doc = fitz.open(pdf_path)
            image_paths = []
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            
            # Calculate zoom for desired DPI
            zoom = self.dpi / 72  # 72 is default DPI
            mat = fitz.Matrix(zoom, zoom)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=mat)
                
                image_path = os.path.join(self.temp_dir, f"{base_name}_page_{page_num + 1}.png")
                pix.save(image_path)
                image_paths.append(image_path)
                logger.info(f"Saved page {page_num + 1} to {image_path}")
            
            doc.close()
            return image_paths
            
        except Exception as e:
            logger.error(f"Error converting PDF with PyMuPDF: {str(e)}")
            raise
    
    def get_pdf_page_count(self, pdf_path: str) -> int:
        """Get number of pages in PDF"""
        try:
            doc = fitz.open(pdf_path)
            page_count = len(doc)
            doc.close()
            return page_count
        except Exception as e:
            logger.error(f"Error getting PDF page count: {str(e)}")
            return 0
    
    def optimize_image(self, image_path: str) -> str:
        """
        Optimize image for better OCR results
        
        Args:
            image_path: Path to image file
            
        Returns:
            Path to optimized image
        """
        try:
            img = Image.open(image_path)
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if too large
            if max(img.size) > settings.IMAGE_MAX_SIZE:
                img.thumbnail((settings.IMAGE_MAX_SIZE, settings.IMAGE_MAX_SIZE), Image.Resampling.LANCZOS)
            
            # Save optimized image
            optimized_path = image_path.replace('.png', '_optimized.png')
            img.save(optimized_path, 'PNG', optimize=True, quality=95)
            
            return optimized_path
            
        except Exception as e:
            logger.error(f"Error optimizing image: {str(e)}")
            return image_path
    
    def cleanup_temp_files(self, file_paths: List[str]):
        """Delete temporary files"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Deleted temp file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temp file {file_path}: {str(e)}")

# Singleton instance
pdf_converter = PdfConverter()
