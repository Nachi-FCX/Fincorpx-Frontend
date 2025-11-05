"""Utility functions for the OCR service"""
import os
import uuid
from datetime import datetime
from typing import List

def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename with timestamp and UUID"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    ext = os.path.splitext(original_filename)[1]
    return f"{timestamp}_{unique_id}{ext}"

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Remove special characters (keep alphanumeric and basic punctuation)
    # text = re.sub(r'[^\w\s.,;:!?-]', '', text)
    return text.strip()

def format_amount(amount: float) -> str:
    """Format amount in Indian currency format"""
    return f"₹{amount:,.2f}"

def validate_gstin(gstin: str) -> bool:
    """Validate GSTIN format"""
    import re
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    return bool(re.match(pattern, gstin))

def validate_pan(pan: str) -> bool:
    """Validate PAN format"""
    import re
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    return bool(re.match(pattern, pan))
