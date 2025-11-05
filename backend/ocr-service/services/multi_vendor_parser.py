"""
Multi-Vendor Invoice Parser
Automatically detects vendor and extracts structured data from invoices
Supports: Noon, Lulu Hypermarket, Delivery Hero, and generic invoices
"""

import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger
from models.schemas import OcrResult


class MultiVendorInvoiceParser:
    """
    Intelligent parser that automatically detects vendor and extracts data
    using vendor-specific patterns and fallback strategies
    """
    
    # Vendor detection patterns
    VENDOR_PATTERNS = {
        'noon': r'noon\.com|noon\s+(?:uae|com)|shop\s+noon',
        'lulu': r'lulu\s+hypermarket|luluhypermarket|lulu\s+international',
        'delivery_hero': r'delivery\s+hero|deliveryhero|talabat|careem|foodpanda',
        'anf': r'a\s*n\s*f\s+multinational|anf\s+general\s+trading'
    }
    
    # Universal field patterns (work across vendors)
    FIELD_PATTERNS = {
        'po_number': [
            r'(?:purchase\s+order|po|p\.o\.?)\s*#?\s*:?\s*([A-Z0-9\-]{3,20})',
            r'order\s+(?:number|no\.?|#)\s*:?\s*([A-Z0-9\-]{3,20})',
            r'po\s+number\s*:?\s*([A-Z0-9\-]{3,20})'
        ],
        'invoice_number': [
            r'invoice\s+(?:no\.?|number|#)\s*:?\s*([A-Z0-9\-/]{2,20})',
            r'inv\.?\s+(?:no\.?|#)\s*:?\s*([A-Z0-9\-/]{2,20})',
            r'bill\s+no\.?\s*:?\s*([A-Z0-9\-/]{2,20})'
        ],
        'supplier_name': [
            r'(?:supplier|vendor|bill\s+from|seller)\s*:?\s*([A-Z][A-Za-z\s\.,&]{5,80})',
            r'(?:from|sold\s+by)\s*:?\s*([A-Z][A-Za-z\s\.,&]{5,80})'
        ],
        'invoice_date': [
            r'(?:invoice\s+)?date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(?:dated|issued)\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        ],
        'subtotal': [
            r'sub\s*total\s*:?\s*(?:aed|usd|sar)?\s*([\d,]+\.?\d*)',
            r'(?:total\s+)?excl\.?\s+(?:tax|vat)\s*:?\s*(?:aed|usd|sar)?\s*([\d,]+\.?\d*)'
        ],
        'vat_amount': [
            r'vat\s+(?:amount|total|value)\s*:?\s*(?:aed|usd|sar)?\s*([\d,]+\.?\d*)',
            r'tax\s+(?:amount|total)\s*:?\s*(?:aed|usd|sar)?\s*([\d,]+\.?\d*)',
            r'(?:total\s+)?vat\s*:?\s*(?:aed|usd|sar)?\s*([\d,]+\.?\d*)'
        ],
        'total_amount': [
            r'(?:grand\s+)?total\s+(?:incl\.?\s+vat|amount)\s*:?\s*(?:aed|usd|sar)?\s*([\d,]+\.?\d*)',
            r'(?:total\s+)?incl\.?\s+(?:tax|vat)\s*:?\s*(?:aed|usd|sar)?\s*([\d,]+\.?\d*)',
            r'(?:invoice\s+)?total\s*:?\s*(?:aed|usd|sar)?\s*([\d,]+\.?\d*)'
        ]
    }
    
    def detect_vendor(self, full_text: str) -> Optional[str]:
        """Detect which vendor the invoice is from"""
        text_lower = full_text.lower()
        
        for vendor, pattern in self.VENDOR_PATTERNS.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.info(f"✓ Detected vendor: {vendor.upper()}")
                return vendor
        
        logger.warning("⚠ Could not detect vendor, using generic parsing")
        return None
    
    def extract_field(self, text: str, field_name: str) -> Optional[str]:
        """Extract a field using multiple patterns"""
        patterns = self.FIELD_PATTERNS.get(field_name, [])
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                logger.debug(f"✓ Found {field_name}: {value}")
                return value
        
        return None
    
    def extract_currency(self, text: str) -> str:
        """Detect currency from invoice"""
        currencies = {
            'AED': r'\bAED\b|united\s+arab\s+emirates\s+dirham',
            'SAR': r'\bSAR\b|saudi\s+riyal',
            'USD': r'\$|USD',
            'EUR': r'€|EUR'
        }
        
        text_lower = text.lower()
        for currency, pattern in currencies.items():
            if re.search(pattern, text_lower):
                return currency
        
        return 'AED'  # Default to AED for UAE invoices
    
    def parse_amount(self, amount_str: Optional[str]) -> float:
        """Parse amount string to float"""
        if not amount_str:
            return 0.0
        
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[^\d.]', '', amount_str)
            return float(cleaned)
        except (ValueError, AttributeError):
            return 0.0
    
    def parse_date(self, date_str: Optional[str]) -> Optional[str]:
        """Normalize date to ISO format"""
        if not date_str:
            return None
        
        # Common date formats
        formats = [
            '%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d',
            '%d-%m-%Y', '%d.%m.%Y', '%Y/%m/%d'
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return date_str  # Return as-is if can't parse
    
    def extract_line_items_from_ocr(
        self, 
        ocr_results: List[OcrResult]
    ) -> List[Dict[str, Any]]:
        """
        Extract line items from OCR results using position-based heuristics
        """
        # Group OCR results by Y-coordinate (rows)
        rows = {}
        for result in ocr_results:
            # Only consider middle section (0.2-0.7 of page)
            if not (0.2 <= result.bbox.y <= 0.7):
                continue
            
            y_key = round(result.bbox.y, 2)
            if y_key not in rows:
                rows[y_key] = []
            rows[y_key].append(result)
        
        # Sort rows by Y position
        sorted_rows = sorted(rows.items())
        
        line_items = []
        for y_pos, row_results in sorted_rows:
            # Sort by X position (left to right)
            row_results.sort(key=lambda r: r.bbox.x)
            
            # Extract fields from row
            item = self._parse_line_item_row(row_results)
            if item:
                line_items.append(item)
        
        return line_items
    
    def _parse_line_item_row(self, row_results: List[OcrResult]) -> Optional[Dict[str, Any]]:
        """Parse a single row into line item"""
        texts = [r.text for r in row_results]
        row_text = ' '.join(texts)
        
        # Skip header rows
        if any(kw in row_text.lower() for kw in ['sku', 'description', 'quantity', 'price', 'total', 'product code']):
            return None
        
        # Extract numeric values
        numbers = []
        for t in texts:
            if re.search(r'\d+\.?\d*', t):
                try:
                    cleaned = re.sub(r'[^\d.]', '', t)
                    numbers.append(float(cleaned))
                except ValueError:
                    continue
        
        # Extract SKU/product code (alphanumeric, 8-15 chars)
        sku = next((t for t in texts if re.match(r'^[A-Z0-9]{8,15}$', t, re.IGNORECASE)), None)
        
        # Extract description (longest text that's not a number)
        desc_candidates = [t for t in texts if len(t) > 10 and not re.match(r'^\d+\.?\d*$', t)]
        description = max(desc_candidates, key=len) if desc_candidates else None
        
        if not description or len(numbers) < 2:
            return None
        
        # Assign numbers to fields (heuristic: small=qty, medium=price, large=total)
        sorted_nums = sorted(numbers)
        
        return {
            'sku': sku,
            'description': description,
            'qty': sorted_nums[0] if len(sorted_nums) > 0 else 1,
            'unit_price': sorted_nums[1] if len(sorted_nums) > 1 else sorted_nums[0],
            'total_price': sorted_nums[-1] if len(sorted_nums) > 0 else 0
        }
    
    def parse_invoice(
        self, 
        ocr_results: List[OcrResult],
        structure_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main parsing method - returns normalized JSON
        
        Args:
            ocr_results: OCR text extraction results
            structure_data: Optional layout/table data from PP-Structure
            
        Returns:
            Normalized invoice data dictionary
        """
        # Combine all OCR text
        full_text = ' '.join([r.text for r in ocr_results])
        
        # Detect vendor
        vendor = self.detect_vendor(full_text)
        
        # Extract fields
        po_number = self.extract_field(full_text, 'po_number')
        invoice_number = self.extract_field(full_text, 'invoice_number')
        supplier_name = self.extract_field(full_text, 'supplier_name')
        invoice_date = self.parse_date(self.extract_field(full_text, 'invoice_date'))
        
        # Extract amounts
        subtotal_str = self.extract_field(full_text, 'subtotal')
        vat_str = self.extract_field(full_text, 'vat_amount')
        total_str = self.extract_field(full_text, 'total_amount')
        
        subtotal = self.parse_amount(subtotal_str)
        vat_amount = self.parse_amount(vat_str)
        total_amount = self.parse_amount(total_str)
        
        # Extract currency
        currency = self.extract_currency(full_text)
        
        # Extract line items
        line_items = self.extract_line_items_from_ocr(ocr_results)
        
        # Build normalized JSON
        result = {
            'vendor': vendor or 'unknown',
            'purchase_order_number': po_number,
            'invoice_number': invoice_number,
            'supplier_name': supplier_name,
            'invoice_date': invoice_date,
            'subtotal': subtotal,
            'vat_amount': vat_amount,
            'total_amount': total_amount,
            'currency': currency,
            'line_items': line_items,
            'processing_metadata': {
                'total_text_regions': len(ocr_results),
                'tables_detected': len(structure_data.get('tables', [])) if structure_data else 0,
                'confidence': sum(r.confidence for r in ocr_results) / len(ocr_results) if ocr_results else 0
            }
        }
        
        logger.info(f"✓ Parsed invoice: PO={po_number}, Total={total_amount} {currency}, Items={len(line_items)}")
        return result


# Singleton instance
multi_vendor_parser = MultiVendorInvoiceParser()
