# Quick Start Guide - Invoice OCR Service

## 🚀 Get Started in 5 Minutes

### 1. Navigate to Backend Directory
```bash
cd backend/ocr-service
```

### 2. Run Setup Script (macOS/Linux)
```bash
chmod +x setup.sh
./setup.sh
```

The script will:
- Create virtual environment
- Install dependencies
- Create .env file
- Set up directories
- Offer to start the service

### 3. Manual Setup (Windows or alternative)
```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux

# Start service
python main.py
```

### 4. Test the Service

Open browser: http://localhost:8000/docs

Or use cURL:
```bash
curl http://localhost:8000/health
```

### 5. Upload Test Invoice
```bash
curl -X POST http://localhost:8000/api/ocr/extract \
  -F "file=@your-invoice.pdf"
```

## 🐳 Docker Quick Start

```bash
# Build and run
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 📝 Frontend Integration

Add to your frontend service (`src/services/invoice/invoiceOcrService.ts`):

```typescript
import axios from 'axios';

const OCR_API_URL = 'http://localhost:8000/api/ocr';

export const uploadInvoice = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post(`${OCR_API_URL}/extract`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  
  return response.data;
};
```

## ⚙️ Common Configuration

Edit `.env`:

```env
# For better accuracy
PDF_DPI=400
CONFIDENCE_THRESHOLD=0.6

# For faster processing
PDF_DPI=200
CONFIDENCE_THRESHOLD=0.4

# Enable GPU (if available)
OCR_USE_GPU=True
```

## 🔍 Troubleshooting

**Issue: "Module not found"**
```bash
pip install -r requirements.txt
```

**Issue: "Poppler not found"**
```bash
# macOS
brew install poppler

# Ubuntu/Debian
sudo apt install poppler-utils
```

**Issue: "Port already in use"**
```bash
# Change port in .env
PORT=8001
```

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/ocr/extract` | POST | OCR text extraction |
| `/api/ocr/extract-invoice` | POST | Extract invoice data |
| `/api/ocr/config` | GET | Get configuration |
| `/docs` | GET | Swagger UI |
| `/redoc` | GET | ReDoc |

## ✅ Next Steps

1. Test with sample invoices
2. Integrate with frontend
3. Tune confidence thresholds
4. Add custom field patterns
5. Deploy to production

---

**Need Help?** Check the main README.md for detailed documentation.
