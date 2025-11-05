from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

class BoundingBox(BaseModel):
    x: float
    y: float
    width: float
    height: float

class OcrResult(BaseModel):
    text: str
    confidence: float
    bbox: BoundingBox
    page: int

class InvoiceLineItem(BaseModel):
    line_number: Optional[int] = None
    product_code: Optional[str] = None
    description: Optional[str] = None
    hsn_code: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    rate: Optional[float] = None
    discount: Optional[float] = None
    tax_rate: Optional[float] = None
    cgst: Optional[float] = None
    sgst: Optional[float] = None
    igst: Optional[float] = None
    amount: Optional[float] = None
    confidence: Optional[float] = None
    bbox: Optional[BoundingBox] = None

class InvoiceData(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    # Header Information
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    po_number: Optional[str] = None
    
    # Vendor Information
    vendor_name: Optional[str] = None
    vendor_gstin: Optional[str] = None
    vendor_address: Optional[str] = None
    vendor_pan: Optional[str] = None
    vendor_state: Optional[str] = None
    
    # Buyer Information
    buyer_name: Optional[str] = None
    buyer_gstin: Optional[str] = None
    buyer_address: Optional[str] = None
    buyer_state: Optional[str] = None
    
    # Financial Summary
    subtotal: Optional[float] = None
    total_cgst: Optional[float] = None
    total_sgst: Optional[float] = None
    total_igst: Optional[float] = None
    total_cess: Optional[float] = None
    total_discount: Optional[float] = None
    total_amount: Optional[float] = None
    
    # Line Items
    line_items: List[InvoiceLineItem] = []
    
    # Additional
    currency: Optional[str] = "INR"
    payment_terms: Optional[str] = None
    notes: Optional[str] = None
    is_inter_state: Optional[bool] = None

class OcrResponse(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    success: bool
    message: str
    ocr_results: List[OcrResult] = []
    extracted_data: Optional[InvoiceData] = None
    processing_time: Optional[float] = None
    total_pages: Optional[int] = None
    confidence_score: Optional[float] = None

class OcrRequest(BaseModel):
    use_angle_cls: bool = True
    language: str = "en"
    detect_direction: bool = True
    confidence_threshold: float = 0.5

class ErrorResponse(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    success: bool = False
    message: str
    error: str
    timestamp: datetime = Field(default_factory=datetime.now)

class HealthResponse(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    status: str
    service: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)
