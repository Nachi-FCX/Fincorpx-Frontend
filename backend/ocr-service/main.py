import os
import time
import shutil
import json
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from loguru import logger
from typing import Optional

from config import settings
from models.schemas import (
    OcrResponse, ErrorResponse, HealthResponse,
    OcrRequest, InvoiceData
)
from services.ocr_processor import ocr_processor
from services.pdf_converter import pdf_converter
from services.invoice_parser import invoice_parser

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logger.add(
    "logs/ocr_service_{time}.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO"
)

# Create temp directory
os.makedirs(settings.TEMP_DIR, exist_ok=True)

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "service": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "running"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service=settings.API_TITLE,
        version=settings.API_VERSION
    )

@app.post("/api/ocr/extract", response_model=OcrResponse, tags=["OCR"])
async def extract_text(
    file: UploadFile = File(...),
    use_angle_cls: bool = True,
    confidence_threshold: float = 0.5
):
    """
    Extract text from uploaded image or PDF file
    
    Args:
        file: Image or PDF file (max 10MB)
        use_angle_cls: Use angle classification (default: True)
        confidence_threshold: Minimum confidence threshold (default: 0.5)
        
    Returns:
        OCR results with extracted text and bounding boxes
    """
    temp_files = []
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_ext} not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
            )
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Seek back to start
        
        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB"
            )
        
        # Save uploaded file
        temp_file_path = os.path.join(settings.TEMP_DIR, file.filename)
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        temp_files.append(temp_file_path)
        
        logger.info(f"Processing file: {file.filename} ({file_size / 1024:.1f} KB)")
        
        start_time = time.time()
        
        # Process based on file type
        if file_ext == '.pdf':
            # Convert PDF to images
            pdf_start = time.time()
            image_paths = pdf_converter.pdf_to_images(temp_file_path)
            pdf_time = time.time() - pdf_start
            logger.info(f"PDF conversion took: {pdf_time:.2f}s for {len(image_paths)} pages")
            
            temp_files.extend(image_paths)
            
            # Get page count
            total_pages = len(image_paths)
            
            # Process all pages
            ocr_start = time.time()
            ocr_results, processing_time = ocr_processor.process_multiple_images(image_paths)
            ocr_time = time.time() - ocr_start
            logger.info(f"OCR processing took: {ocr_time:.2f}s")
            
        else:
            # Process single image
            total_pages = 1
            ocr_start = time.time()
            ocr_results, processing_time = ocr_processor.process_image(temp_file_path, page_number=1)
            ocr_time = time.time() - ocr_start
            logger.info(f"OCR processing took: {ocr_time:.2f}s")
        
        # Calculate average confidence
        avg_confidence = ocr_processor.calculate_average_confidence(ocr_results)
        
        # Parse invoice data
        parse_start = time.time()
        invoice_data = invoice_parser.parse_invoice(ocr_results)
        parse_time = time.time() - parse_start
        logger.info(f"Invoice parsing took: {parse_time:.2f}s")
        
        total_time = time.time() - start_time
        
        logger.info(
            f"Processed {file.filename}: "
            f"{len(ocr_results)} text regions, "
            f"avg confidence: {avg_confidence:.2f}, "
            f"time: {total_time:.2f}s"
        )
        
        ocr_response = OcrResponse(
            success=True,
            message=f"Successfully processed {total_pages} page(s)",
            ocr_results=ocr_results,
            extracted_data=invoice_data,
            processing_time=total_time,
            total_pages=total_pages,
            confidence_score=avg_confidence
        )
        
        # Use model_dump_json() then parse to ensure proper datetime serialization
        return json.loads(ocr_response.model_dump_json(by_alias=True))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )
    finally:
        # Cleanup temporary files
        pdf_converter.cleanup_temp_files(temp_files)

@app.post("/api/ocr/extract-invoice", response_model=InvoiceData, tags=["OCR"])
async def extract_invoice(
    file: UploadFile = File(...)
):
    """
    Extract structured invoice data from uploaded file
    
    Args:
        file: Invoice image or PDF file
        
    Returns:
        Structured invoice data
    """
    try:
        # Get full OCR response (returns dict from extract_text)
        ocr_response_dict = await extract_text(file)
        
        # Extract just the invoice data from the response
        if not ocr_response_dict.get('extracted_data'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to extract invoice data"
            )
        
        # Return only the extracted invoice data
        return ocr_response_dict['extracted_data']
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting invoice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error extracting invoice: {str(e)}"
        )

@app.get("/api/ocr/config", tags=["Config"])
async def get_config():
    """Get current OCR configuration"""
    return {
        "use_gpu": settings.OCR_USE_GPU,
        "language": settings.OCR_LANGUAGE,
        "confidence_threshold": settings.CONFIDENCE_THRESHOLD,
        "max_upload_size_mb": settings.MAX_UPLOAD_SIZE / (1024 * 1024),
        "allowed_extensions": settings.ALLOWED_EXTENSIONS,
        "pdf_dpi": settings.PDF_DPI
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP exception handler"""
    logger.error(f"HTTP exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error": f"HTTP {exc.status_code}",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )
