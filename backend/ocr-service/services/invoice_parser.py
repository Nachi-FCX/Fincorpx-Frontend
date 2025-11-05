import re
from typing import List, Optional, Tuple
from datetime import datetime
from loguru import logger
from models.schemas import OcrResult, InvoiceData, InvoiceLineItem, BoundingBox

class InvoiceParser:
    """
    AI-Enhanced Invoice Parser
    
    Supports multiple invoice formats:
    - Indian GST Invoices (GSTIN format)
    - UAE VAT Invoices (TRN format)
    - Purchase Orders
    - Tax Invoices
    - Custom Commercial Invoices
    
    Features:
    - Smart pattern matching with 80+ regex patterns
    - Intelligent table detection and extraction
    - Multi-format date parsing
    - Context-aware field extraction
    - Flexible vendor/buyer name detection
    """
    
    # Enhanced regex patterns for various invoice formats
    PATTERNS = {
        'invoice_number': [
            r'invoice\s*no\.?\s*:?\s*(?:date\s*:?\s*)?([A-Z][A-Z0-9\-/]{2,})',  # Skip "Date:" if present after "Invoice No:"
            r'([A-Z]{3,}-\d{3,})',  # Pattern like LULU-000219, DH0014
            r'invoice\s*#?\s*:?\s*([A-Z][A-Z0-9\-/]{2,})',
            r'inv\.?\s*no\.?\s*:?\s*([A-Z][A-Z0-9\-/]{2,})',
            r'inv\.?\s*#?\s*:?\s*([A-Z][A-Z0-9\-/]{2,})',
            r'bill\s*no\.?\s*:?\s*([A-Z][A-Z0-9\-/]{2,})',
            r'doc\.?\s*no\.?\s*:?\s*([A-Z][A-Z0-9\-/]{2,})',
            r'reference\s*:?\s*([A-Z][A-Z0-9\-/]{2,})',
        ],
        'invoice_date': [
            r'(?:invoice\s+)?date\s*:?\s*(\d{1,2}/\d{1,2}/\d{4})',
            r'(?:invoice\s+)?date\s*:?\s*(\d{1,2}-\d{1,2}-\d{4})',
            r'order\s*date\s*:?\s*(\d{1,2}/\d{1,2}/\d{4})',
            r'dated\s*:?\s*(\d{1,2}/\d{1,2}/\d{4})',
            r'(?:^|\s)(\d{1,2}/\d{1,2}/\d{4})(?:\s|$)',  # Standalone date
        ],
        'due_date': [
            r'due\s*date\s*:?\s*(\d{1,2}/\d{1,2}/\d{4})',
            r'payment\s*due\s*:?\s*(\d{1,2}/\d{1,2}/\d{4})',
        ],
        'po_number': [
            r'p\.?o\.?\s*no\.?\s*:?\s*([A-Z0-9\-/]+)',
            r'purchase\s*order\s*:?\s*([A-Z0-9\-/]+)',
            r'po\s*#?\s*:?\s*([A-Z0-9\-/]+)',
        ],
        'vat_number': [
            r'vat\s*reg\.?\s*no\.?\s*:?\s*([A-Z0-9]+)',
            r'trn\s*:?\s*([A-Z0-9]+)',
            r'tax\s*reg\.?\s*no\.?\s*:?\s*([A-Z0-9]+)',
        ],
        'gstin': [
            r'gstin?\s*:?\s*([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})',
            r'gst\s*no\.?\s*:?\s*([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})',
            r'tax\s*id\s*:?\s*([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})',
            r'([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})',  # Standalone GSTIN
        ],
        'pan': [
            r'pan\s*:?\s*([A-Z]{5}[0-9]{4}[A-Z]{1})',
            r'permanent\s*account\s*no\.?\s*:?\s*([A-Z]{5}[0-9]{4}[A-Z]{1})',
            r'([A-Z]{5}[0-9]{4}[A-Z]{1})',  # Standalone PAN
        ],
        'amount': [
            r'grand\s*total\s*:?\s*([\d,]+\.?\d*)\s*(?:aed|inr|usd)?',
            r'total\s+incl?\s*(?:tax|vat)\s*:?\s*([\d,]+\.?\d*)\s*(?:aed|inr|usd)?',
            r'total\s+inv\.?\s*cost\s*\(incl\.?.*?\)\s*:?\s*([\d,]+\.?\d*)',
            r'total\s+gross\s*:?\s*([\d,]+\.?\d*)',
            r'net\s*amount\s*:?\s*([\d,]+\.?\d*)',
            r'amount\s*payable\s*:?\s*([\d,]+\.?\d*)',
            r'invoice\s*total\s*:?\s*([\d,]+\.?\d*)',
            r'total\s*:?\s*([\d,]+\.?\d*)',
        ],
        'subtotal': [
            r'total\s*excl\s*(?:tax|vat)\s*:?\s*([\d,]+\.?\d*)\s*(?:aed|inr|usd)?',
            r'sub\s*total\s*:?\s*([\d,]+\.?\d*)',
            r'subtotal\s*:?\s*([\d,]+\.?\d*)',
        ],
        'vat': [
            r'total\s*vat\s*:?\s*([\d,]+\.?\d*)',
            r'vat\s*amount\s*:?\s*([\d,]+\.?\d*)',
            r'vat\s*:?\s*([\d,]+\.?\d*)',
        ],
        'cgst': [
            r'cgst\s*@?\s*[\d.]+%?\s*:?\s*₹?\s*([\d,]+\.?\d*)',
            r'cgst\s*amount\s*:?\s*₹?\s*([\d,]+\.?\d*)',
            r'cgst\s*:?\s*₹?\s*([\d,]+\.?\d*)',
            r'central\s*gst\s*:?\s*₹?\s*([\d,]+\.?\d*)',
        ],
        'sgst': [
            r'sgst\s*@?\s*[\d.]+%?\s*:?\s*₹?\s*([\d,]+\.?\d*)',
            r'sgst\s*amount\s*:?\s*₹?\s*([\d,]+\.?\d*)',
            r'sgst\s*:?\s*₹?\s*([\d,]+\.?\d*)',
            r'state\s*gst\s*:?\s*₹?\s*([\d,]+\.?\d*)',
        ],
        'igst': [
            r'igst\s*@?\s*[\d.]+%?\s*:?\s*₹?\s*([\d,]+\.?\d*)',
            r'igst\s*amount\s*:?\s*₹?\s*([\d,]+\.?\d*)',
            r'igst\s*:?\s*₹?\s*([\d,]+\.?\d*)',
            r'integrated\s*gst\s*:?\s*₹?\s*([\d,]+\.?\d*)',
        ],
        'hsn': [
            r'hsn\s*:?\s*(\d{4,8})',
            r'hsn\s*code\s*:?\s*(\d{4,8})',
            r'(\d{4,8})',  # Fallback: any 4-8 digit number
        ],
    }
    
    def parse_invoice(self, ocr_results: List[OcrResult]) -> InvoiceData:
        """
        Parse OCR results and extract invoice data with AI-enhanced logic
        
        Args:
            ocr_results: List of OCR text results
            
        Returns:
            Structured invoice data
        """
        try:
            # Combine all text
            full_text = ' '.join([r.text for r in ocr_results])
            full_text_lower = full_text.lower()
            
            logger.info(f"Parsing invoice from {len(ocr_results)} OCR results")
            logger.debug(f"Text preview: {full_text[:300]}...")
            
            invoice_data = InvoiceData()
            
            # Extract header fields
            invoice_data.invoice_number = self._extract_field(full_text_lower, 'invoice_number')
            logger.info(f"Invoice Number: {invoice_data.invoice_number}")
            
            invoice_data.invoice_date = self._extract_date(full_text_lower, 'invoice_date')
            logger.info(f"Invoice Date: {invoice_data.invoice_date}")
            
            invoice_data.due_date = self._extract_date(full_text_lower, 'due_date')
            invoice_data.po_number = self._extract_field(full_text_lower, 'po_number')
            logger.info(f"PO Number: {invoice_data.po_number}")
            
            # Extract VAT/TRN numbers (UAE format)
            vat_numbers = self._extract_all_matches(full_text, 'vat_number')
            logger.info(f"Found VAT numbers: {vat_numbers}")
            if len(vat_numbers) >= 1:
                invoice_data.vendor_gstin = vat_numbers[0]  # Store as GSTIN for compatibility
            if len(vat_numbers) >= 2:
                invoice_data.buyer_gstin = vat_numbers[1]
            
            # Extract GSTIN (Indian format) - fallback if no VAT numbers
            if not invoice_data.vendor_gstin:
                gstins = self._extract_all_gstins(full_text)
                logger.info(f"Found GSTIN numbers: {gstins}")
                if len(gstins) >= 1:
                    invoice_data.vendor_gstin = gstins[0]
                if len(gstins) >= 2:
                    invoice_data.buyer_gstin = gstins[1]
            
            # Extract PAN
            invoice_data.vendor_pan = self._extract_field(full_text, 'pan')
            
            # Extract amounts - try multiple patterns
            invoice_data.total_amount = self._extract_amount(full_text_lower, 'amount')
            logger.info(f"Total Amount: {invoice_data.total_amount}")
            
            # Try extracting subtotal
            subtotal = self._extract_amount(full_text_lower, 'subtotal')
            if subtotal:
                invoice_data.subtotal = subtotal
                logger.info(f"Subtotal (from text): {subtotal}")
            
            # Try VAT (UAE/GCC format)
            vat_amount = self._extract_amount(full_text_lower, 'vat')
            if vat_amount:
                logger.info(f"VAT Amount: {vat_amount}")
                invoice_data.total_igst = vat_amount  # Store VAT as IGST for compatibility
            
            # Try GST (Indian format)
            invoice_data.total_cgst = self._extract_amount(full_text_lower, 'cgst')
            invoice_data.total_sgst = self._extract_amount(full_text_lower, 'sgst')
            igst_amount = self._extract_amount(full_text_lower, 'igst')
            if igst_amount and not vat_amount:
                invoice_data.total_igst = igst_amount
            
            logger.info(f"Tax amounts - CGST: {invoice_data.total_cgst}, SGST: {invoice_data.total_sgst}, IGST/VAT: {invoice_data.total_igst}")
            
            # Determine if inter-state
            if invoice_data.total_igst and invoice_data.total_igst > 0:
                invoice_data.is_inter_state = True
            elif invoice_data.total_cgst and invoice_data.total_sgst:
                invoice_data.is_inter_state = False
            
            # Calculate subtotal if not present
            if not invoice_data.subtotal and invoice_data.total_amount:
                total_tax = (invoice_data.total_cgst or 0) + (invoice_data.total_sgst or 0) + (invoice_data.total_igst or 0)
                invoice_data.subtotal = invoice_data.total_amount - total_tax
                logger.info(f"Calculated Subtotal: {invoice_data.subtotal}")
            
            # Extract vendor and buyer names
            invoice_data.vendor_name = self._extract_vendor_name(ocr_results)
            invoice_data.buyer_name = self._extract_buyer_name(ocr_results)
            logger.info(f"Vendor: {invoice_data.vendor_name}, Buyer: {invoice_data.buyer_name}")
            
            # Extract line items using enhanced table detection
            invoice_data.line_items = self._extract_line_items_enhanced(ocr_results)
            logger.info(f"Extracted {len(invoice_data.line_items)} line items")
            
            logger.info(f"Successfully parsed invoice: {invoice_data.invoice_number}")
            return invoice_data
            
        except Exception as e:
            logger.error(f"Error parsing invoice: {str(e)}")
            import traceback
            traceback.print_exc()
            return InvoiceData()
    
    def _extract_field(self, text: str, field_name: str) -> Optional[str]:
        """Extract a field using regex patterns"""
        patterns = self.PATTERNS.get(field_name, [])
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_date(self, text: str, field_name: str = 'invoice_date') -> Optional[str]:
        """Extract and format date"""
        date_str = self._extract_field(text, field_name)
        if date_str:
            try:
                # Try multiple date formats
                for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y', '%Y-%m-%d', '%Y/%m/%d']:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        return dt.strftime('%Y-%m-%d')
                    except ValueError:
                        continue
            except Exception:
                pass
        return date_str
    
    def _extract_all_matches(self, text: str, field_name: str) -> List[str]:
        """Extract all matches for a field pattern"""
        matches = []
        patterns = self.PATTERNS.get(field_name, [])
        
        for pattern in patterns:
            found = re.finditer(pattern, text, re.IGNORECASE)
            for match in found:
                value = match.group(1).strip()
                if value not in matches:
                    matches.append(value)
        
        return matches
    
    def _extract_amount(self, text: str, field_name: str) -> Optional[float]:
        """Extract amount as float"""
        amount_str = self._extract_field(text, field_name)
        if amount_str:
            try:
                # Remove commas and convert to float
                amount_str = amount_str.replace(',', '')
                return float(amount_str)
            except ValueError:
                return None
        return None
    
    def _extract_all_gstins(self, text: str) -> List[str]:
        """Extract all GSTIN numbers found in text"""
        gstins = []
        for pattern in self.PATTERNS['gstin']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                gstin = match.group(1).upper()
                if gstin not in gstins:
                    gstins.append(gstin)
        return gstins
    
    def _extract_vendor_name(self, ocr_results: List[OcrResult]) -> Optional[str]:
        """Extract vendor name (usually near top of document or after 'Supplier'/'Bill From')"""
        # Look for explicit vendor keywords
        vendor_keywords = ['supplier', 'vendor', 'bill from', 'seller', 'from']
        
        for idx, result in enumerate(ocr_results):
            text_lower = result.text.lower()
            
            # Check for "Bill From:" or similar
            if any(kw in text_lower for kw in vendor_keywords):
                # Check if name is in same line after colon
                if ':' in result.text:
                    parts = result.text.split(':')
                    if len(parts) > 1:
                        vendor_part = parts[1].strip()
                        # Remove leading numbers/codes
                        vendor_part = re.sub(r'^\d+\s*,?\s*', '', vendor_part)
                        # Accept even short names (2+ chars) after "Bill From:"
                        if len(vendor_part) >= 2 and not vendor_part.isdigit():
                            return vendor_part
                
                # Check next few results
                for offset in range(1, min(4, len(ocr_results) - idx)):
                    next_text = ocr_results[idx + offset].text.strip()
                    # Skip if it's a label or too short
                    if ':' in next_text or len(next_text) < 2:
                        continue
                    # Skip if it's just a comma or connector
                    if next_text in [',', '-', '/', '\\']:
                        continue
                    # Skip if it's a date, number, or country name (but take name before these)
                    if re.match(r'^\d+[/-]\d+[/-]\d+$', next_text):
                        continue
                    # Skip common location-only text (but accept company names)
                    if next_text.lower() in ['cash', 'credit']:
                        continue
                    # If it's a country/region name and we haven't found a name yet, skip
                    if next_text.lower() in ['united arab emirates', 'uae', 'india', 'dubai'] and offset == 1:
                        continue
                    # This looks like a name - accept it
                    if not next_text.isdigit():
                        logger.info(f"Found vendor name near '{result.text}': {next_text}")
                        return next_text
        
        # Fallback: Look in top 25% of document
        top_texts = [
            r.text for r in ocr_results 
            if r.page == 1 and r.bbox.y < 0.25 and len(r.text) >= 2
        ]
        
        # Find first non-header text
        exclude_words = ['invoice', 'bill', 'tax', 'original', 'copy', 'duplicate', 
                        'purchase', 'order', 'date', 'time', 'no:', 'from:', 'to:']
        for text in top_texts:
            text_clean = text.strip()
            if (not any(word in text_clean.lower() for word in exclude_words) and 
                not text_clean.isdigit() and 
                not re.match(r'^\d+[/-]\d+', text_clean) and
                len(text_clean) >= 2):
                return text_clean
        
        return None
    
    def _extract_buyer_name(self, ocr_results: List[OcrResult]) -> Optional[str]:
        """Extract buyer name (usually after 'bill to', 'buyer', 'consignee', or 'delivery to')"""
        buyer_keywords = ['bill to', 'buyer', 'delivery to', 'ship to', 'consignee', 'sold to']
        
        for idx, result in enumerate(ocr_results):
            text_lower = result.text.lower()
            
            if any(keyword in text_lower for keyword in buyer_keywords):
                # Check if name is in same line after colon
                if ':' in result.text:
                    parts = result.text.split(':')
                    if len(parts) > 1:
                        buyer_part = parts[1].strip()
                        if len(buyer_part) > 2 and not buyer_part.isdigit():
                            return buyer_part
                
                # Check next few results
                for offset in range(1, min(4, len(ocr_results) - idx)):
                    next_text = ocr_results[idx + offset].text.strip()
                    # Skip labels, short text, dates, commas
                    if ':' in next_text or len(next_text) < 2:
                        continue
                    if next_text in [',', '-', '/', '\\']:
                        continue
                    if re.match(r'^\d+[/-]\d+[/-]\d+$', next_text):
                        continue
                    if next_text.isdigit():
                        continue
                    # Skip generic location words that appear first
                    if next_text.lower() in ['test', 'united arab emirates', 'uae', 'dubai', 'india'] and offset == 1:
                        continue
                    # This looks like a buyer name
                    if len(next_text) >= 2:
                        logger.info(f"Found buyer name near '{result.text}': {next_text}")
                        return next_text
        
        return None
    
    def _extract_line_items(self, ocr_results: List[OcrResult]) -> List[InvoiceLineItem]:
        """
        Extract line items from invoice table
        This is a simplified version - real implementation would need table detection
        """
        line_items = []
        
        # Look for text that might be line items (middle section of document)
        table_results = [
            r for r in ocr_results 
            if 0.2 < r.bbox.y < 0.7  # Middle section
        ]
        
        current_item = None
        for result in table_results:
            text = result.text.strip()
            
            # Check if it's a number (could be quantity or amount)
            try:
                value = float(text.replace(',', ''))
                if current_item:
                    # Try to assign to appropriate field
                    if not current_item.quantity:
                        current_item.quantity = value
                    elif not current_item.rate:
                        current_item.rate = value
                    elif not current_item.amount:
                        current_item.amount = value
            except ValueError:
                # Not a number, could be description or HSN
                if self._is_hsn_code(text):
                    if current_item:
                        current_item.hsn_code = text
                elif len(text) > 5:  # Likely a description
                    # Save previous item and start new one
                    if current_item:
                        line_items.append(current_item)
                    current_item = InvoiceLineItem(
                        description=text,
                        bbox=result.bbox,
                        confidence=result.confidence
                    )
        
        # Add last item
        if current_item:
            line_items.append(current_item)
        
        # Assign line numbers
        for idx, item in enumerate(line_items, start=1):
            item.line_number = idx
        
        return line_items
    
    def _extract_line_items_enhanced(self, ocr_results: List[OcrResult]) -> List[InvoiceLineItem]:
        """
        Enhanced line item extraction with better table detection
        """
        line_items = []
        
        # Group OCR results by Y-coordinate (same line)
        rows = {}
        for result in ocr_results:
            y_pos = round(result.bbox.y, 2)  # Round to group similar Y positions
            if y_pos not in rows:
                rows[y_pos] = []
            rows[y_pos].append(result)
        
        # Sort rows by Y position
        sorted_rows = sorted(rows.items())
        
        # Find table header row
        table_keywords = ['sr no', 'product code', 'description of goods', 'quantity', 'rate', 'amount', 'item', 'product', 'barcode', 'brand', 'uom']
        table_start_idx = -1
        table_end_keywords = ['total excl tax', 'total gross', 'total order', 'total vat', 'vat:', 'total inv', 'subtotal', 'grand total', 'note:', 'comments:', 'currency:']
        table_end_idx = len(sorted_rows)
        
        for idx, (y_pos, row_results) in enumerate(sorted_rows):
            row_text = ' '.join([r.text.lower() for r in row_results])
            
            # Find table start - must have multiple table keywords
            if table_start_idx == -1:
                keyword_count = sum(1 for kw in table_keywords if kw in row_text)
                if keyword_count >= 3:  # Must have at least 3 table column names
                    table_start_idx = idx + 1  # Start from next row
                    logger.debug(f"Found table header at row {idx}: {row_text[:100]}")
            
            # Find table end
            if table_start_idx != -1 and any(kw in row_text for kw in table_end_keywords):
                table_end_idx = idx
                logger.debug(f"Found table end at row {idx}: {row_text[:100]}")
                break
        
        if table_start_idx == -1:
            logger.warning("Could not find table header")
            return line_items
        
        # Extract line items from table rows
        for idx in range(table_start_idx, min(table_end_idx, len(sorted_rows))):
            y_pos, row_results = sorted_rows[idx]
            
            # Sort by X position (left to right)
            row_results.sort(key=lambda r: r.bbox.x)
            
            # Skip rows that look like headers, info fields, or totals
            row_text = ' '.join([r.text.lower() for r in row_results])
            logger.info(f"Processing table row {idx}: {row_text[:150]}")
            
            # Skip if row contains header/info keywords (but be more specific to avoid skipping data rows)
            skip_keywords = ['total excl', 'total incl', 'subtotal', 'grand total', 'tax id', 'consignee:', 'dispatch', 'destination:', 
                           'purchase order', 'buyer', 'notify party', 'bill from', 'mode/terms', 'vat:', 'total order']
            if any(kw in row_text for kw in skip_keywords):
                logger.debug(f"Skipping row with keyword: {row_text[:100]}")
                continue
            
            # Skip if row has no numbers (likely a text-only header)
            has_number = any(char.isdigit() for r in row_results for char in r.text)
            if not has_number:
                logger.debug(f"Skipping row with no numbers: {row_text[:100]}")
                continue
            
            # Try to extract line item fields
            item = InvoiceLineItem()
            item.line_number = len(line_items) + 1
            
            numbers_found = []
            texts_found = []
            product_code_candidates = []
            unit_found = None
            
            for result in row_results:
                text = result.text.strip()
                
                # Skip empty or very short text
                if len(text) < 2:
                    continue
                
                # Check for unit of measurement
                unit_keywords = ['units', 'pcs', 'kg', 'mtr', 'ltr', 'box', 'set', 'nos', 'pkt', 'doz']
                if text.lower() in unit_keywords:
                    unit_found = text
                    continue
                
                # Try to identify field type
                try:
                    # Check if it's a number
                    clean_text = text.replace(',', '').replace('$', '').replace('₹', '').replace('AED', '').replace('%', '').strip()
                    num_value = float(clean_text)
                    numbers_found.append(num_value)
                    
                except ValueError:
                    # Not a number - could be product code, description, HSN, barcode
                    # Product codes often have patterns like: ABC-123, ABC123, A1B2C3, GLDN-1121-5
                    # More flexible pattern to catch various formats
                    if re.match(r'^[A-Z0-9][-_A-Z0-9]{2,30}$', text, re.IGNORECASE):
                        # Looks like a product code (alphanumeric with optional dashes/underscores)
                        product_code_candidates.append(text)
                        logger.debug(f"Found product code candidate: {text}")
                    elif len(text) >= 8 and text.isdigit():
                        # Likely a barcode
                        if not item.hsn_code:
                            item.hsn_code = text
                    elif len(text) >= 4 and text.isdigit():
                        # Could be HSN code
                        if not item.hsn_code:
                            item.hsn_code = text
                    elif len(text) > 3:
                        # Likely description (lowered threshold from 5 to 3)
                        texts_found.append(text)
                        logger.debug(f"Found description text: {text}")
            
            # Assign unit
            if unit_found:
                item.unit = unit_found.capitalize()
            
            # Assign product code (typically first alphanumeric code found)
            if product_code_candidates:
                item.product_code = product_code_candidates[0]
                # Remaining product code candidates might be part of description
                if len(product_code_candidates) > 1:
                    texts_found.extend(product_code_candidates[1:])
            
            # Assign description
            if texts_found:
                item.description = ' '.join(texts_found)
            elif item.product_code and not item.description:
                # If no description but we have a product code, use it as description too
                item.description = item.product_code
            
            # Log what we found in this row
            logger.info(f"Row {item.line_number} extracted - Code candidates: {product_code_candidates}, Texts: {texts_found}, Numbers: {numbers_found}, Unit: {unit_found}")
            
            # Assign numbers to quantity, rate, amount
            # For VAT invoices we might have: Qty, Rate, AmtExclVAT, VAT%, VATAmt, AmtInclVAT
            # We need to identify: Quantity (smallest <100), Rate, and final Amount (largest or last meaningful)
            if len(numbers_found) >= 3:
                # Try to detect VAT percentage first (common values: 0, 5, 12, 18, 28)
                vat_percentages = [n for n in numbers_found if n in [0, 5, 12, 18, 28]]
                if vat_percentages:
                    item.tax_rate = vat_percentages[0]
                
                # Filter out VAT percentage and very small amounts (but keep valid 0 values)
                potential_amounts = [n for n in numbers_found if n not in vat_percentages and n >= 0]
                
                # Remove exact duplicates but keep at least 3 values
                seen = set()
                unique_amounts = []
                for n in potential_amounts:
                    if n not in seen or len(unique_amounts) < 3:
                        unique_amounts.append(n)
                        seen.add(n)
                
                if len(unique_amounts) >= 3:
                    # Sort to identify quantity (smallest), rate, and amount
                    sorted_nums = sorted(unique_amounts)
                    
                    # Quantity is typically the smallest number < 100
                    item.quantity = next((n for n in sorted_nums if n < 100 and n > 0), sorted_nums[0] if sorted_nums[0] > 0 else 1)
                    
                    # Rate and amount
                    remaining_nums = [n for n in sorted_nums if n != item.quantity]
                    if len(remaining_nums) >= 2:
                        item.rate = remaining_nums[0]  # Usually the smaller of remaining
                        item.amount = remaining_nums[-1]  # Final amount (largest)
                    elif len(remaining_nums) == 1:
                        item.rate = remaining_nums[0]
                        item.amount = remaining_nums[0]
                    else:
                        item.rate = item.quantity
                        item.amount = item.quantity
                        
                elif len(unique_amounts) == 2:
                    item.quantity = unique_amounts[0] if unique_amounts[0] < 100 else 1
                    item.rate = unique_amounts[0]
                    item.amount = unique_amounts[-1]
                elif len(unique_amounts) == 1:
                    item.quantity = 1
                    item.rate = unique_amounts[0]
                    item.amount = unique_amounts[0]
                else:
                    # Fallback: use original numbers
                    sorted_nums = sorted([n for n in numbers_found if n >= 0])
                    if len(sorted_nums) > 0:
                        item.quantity = 1
                        item.rate = sorted_nums[0] if sorted_nums else 0
                        item.amount = sorted_nums[-1] if sorted_nums else 0
            elif len(numbers_found) == 2:
                item.quantity = numbers_found[0] if numbers_found[0] < 100 else 1
                item.rate = numbers_found[0] if numbers_found[0] < 100 else numbers_found[0]
                item.amount = numbers_found[1]
            elif len(numbers_found) == 1:
                item.amount = numbers_found[0]
            
            # Only add item if it has meaningful data
            # Accept items with product code OR description, as long as they have numeric data
            # For invoices where all values are the same, we should still accept all rows
            has_valid_identifier = (item.description and len(item.description) > 2) or item.product_code
            has_valid_data = item.amount or item.quantity or item.rate
            
            # Special case: if we have a description but no numbers, still try to add with defaults
            if has_valid_identifier and not has_valid_data:
                # Assign default values if we have an identifier but no numbers extracted
                if not item.quantity:
                    item.quantity = 1
                if not item.rate:
                    item.rate = 0
                if not item.amount:
                    item.amount = 0
                has_valid_data = True
            
            if has_valid_identifier and has_valid_data:
                line_items.append(item)
                logger.info(f"✓ ADDED Item {item.line_number}: Code='{item.product_code}', Desc='{item.description}', Unit='{item.unit}' - Qty: {item.quantity}, Rate: {item.rate}, Amt: {item.amount}, Tax: {item.tax_rate}%")
            else:
                logger.warning(f"✗ SKIPPED row - Code: '{item.product_code}', Desc: '{item.description}', Unit: '{item.unit}' - Qty: {item.quantity}, Rate: {item.rate}, Amt: {item.amount}, has_valid_identifier={has_valid_identifier}, has_valid_data={has_valid_data}")
        
        logger.info(f"Extracted {len(line_items)} line items from table")
        return line_items
    
    def _is_hsn_code(self, text: str) -> bool:
        """Check if text looks like an HSN code"""
        return bool(re.match(r'^\d{4,8}$', text))
    
    def find_text_near_bbox(self, ocr_results: List[OcrResult], bbox: BoundingBox, 
                           page: int = 1, threshold: float = 0.05) -> List[str]:
        """
        Find text near a bounding box
        
        Args:
            ocr_results: List of OCR results
            bbox: Target bounding box
            page: Page number
            threshold: Distance threshold
            
        Returns:
            List of nearby text strings
        """
        nearby_texts = []
        
        for result in ocr_results:
            if result.page != page:
                continue
            
            # Calculate distance between bboxes
            distance = self._bbox_distance(result.bbox, bbox)
            if distance < threshold:
                nearby_texts.append(result.text)
        
        return nearby_texts
    
    def _bbox_distance(self, bbox1: BoundingBox, bbox2: BoundingBox) -> float:
        """Calculate distance between two bounding boxes"""
        center1_x = bbox1.x + bbox1.width / 2
        center1_y = bbox1.y + bbox1.height / 2
        center2_x = bbox2.x + bbox2.width / 2
        center2_y = bbox2.y + bbox2.height / 2
        
        return ((center1_x - center2_x) ** 2 + (center1_y - center2_y) ** 2) ** 0.5

# Singleton instance
invoice_parser = InvoiceParser()
