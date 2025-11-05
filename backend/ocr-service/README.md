# Invoice OCR Service

Self-hosted OCR service using PaddleOCR for invoice processing. No external API costs, complete control over your data.

## 🚀 Features

- ✅ **PaddleOCR** - State-of-the-art OCR engine
- ✅ **PDF Support** - Multi-page PDF processing
- ✅ **Invoice Parsing** - Automatic extraction of invoice fields
- ✅ **High Accuracy** - Text detection with confidence scores
- ✅ **Fast Processing** - Optimized for speed
- ✅ **RESTful API** - Easy integration
- ✅ **Docker Ready** - Containerized deployment
- ✅ **No External APIs** - Fully self-hosted

## 📋 Requirements

- Python 3.10+
- Poppler (for PDF processing)
- 2GB+ RAM
- CPU (GPU optional for faster processing)

## 🔧 Installation

### Option 1: Local Setup

1. **Clone and navigate to directory**
```bash
cd backend/ocr-service
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install Poppler** (for PDF support)
```bash
# macOS
brew install poppler

# Ubuntu/Debian
sudo apt-get install poppler-utils

# Windows
# Download from: https://github.com/oschwartz10612/poppler-windows/releases
```

5. **Create environment file**
```bash
cp .env.example .env
```

6. **Run the service**
```bash
python main.py
```

The service will start at `http://localhost:8000`

### Option 2: Docker Setup

1. **Build and run with Docker Compose**
```bash
docker-compose up -d
```

2. **Check logs**
```bash
docker-compose logs -f
```

3. **Stop service**
```bash
docker-compose down
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints

#### 1. Health Check
```bash
GET /health
```

#### 2. Extract Text (OCR)
```bash
POST /api/ocr/extract
Content-Type: multipart/form-data

file: <image or PDF file>
use_angle_cls: true (optional)
confidence_threshold: 0.5 (optional)
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully processed 1 page(s)",
  "ocr_results": [
    {
      "text": "INVOICE",
      "confidence": 0.98,
      "bbox": {
        "x": 0.1,
        "y": 0.05,
        "width": 0.2,
        "height": 0.03
      },
      "page": 1
    }
  ],
  "extracted_data": {
    "invoice_number": "INV-2024-001",
    "invoice_date": "2024-11-04",
    "vendor_gstin": "29ABCDE1234F1Z5",
    "total_amount": 10000.00,
    "line_items": []
  },
  "processing_time": 2.45,
  "total_pages": 1,
  "confidence_score": 0.92
}
```

#### 3. Extract Invoice Data
```bash
POST /api/ocr/extract-invoice
Content-Type: multipart/form-data

file: <invoice PDF or image>
```

**Response:**
```json
{
  "invoice_number": "INV-2024-001",
  "invoice_date": "2024-11-04",
  "vendor_name": "ABC Company",
  "vendor_gstin": "29ABCDE1234F1Z5",
  "total_amount": 10000.00,
  "total_cgst": 900.00,
  "total_sgst": 900.00,
  "subtotal": 8200.00,
  "line_items": [
    {
      "line_number": 1,
      "description": "Product A",
      "quantity": 10,
      "rate": 820.00,
      "amount": 8200.00
    }
  ]
}
```

#### 4. Get Configuration
```bash
GET /api/ocr/config
```

## 🧪 Testing

### Using cURL

```bash
# Test health
curl http://localhost:8000/health

# Upload invoice
curl -X POST http://localhost:8000/api/ocr/extract \
  -F "file=@invoice.pdf"
```

### Using Python

```python
import requests

# Upload file
with open('invoice.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/ocr/extract',
        files={'file': f}
    )
    
data = response.json()
print(f"Found {len(data['ocr_results'])} text regions")
print(f"Invoice Number: {data['extracted_data']['invoice_number']}")
```

## ⚙️ Configuration

Edit `.env` file:

```env
# OCR Settings
OCR_USE_GPU=False          # Set to True if GPU available
OCR_LANGUAGE=en            # Language code (en, hi, etc.)
CONFIDENCE_THRESHOLD=0.5   # Minimum confidence (0-1)

# Processing
PDF_DPI=300                # PDF conversion quality
IMAGE_MAX_SIZE=4096        # Max image dimension

# API
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 📊 Performance

- **Single Page PDF**: ~2-3 seconds
- **Multi-page PDF (10 pages)**: ~15-20 seconds
- **Image**: ~1-2 seconds

*Performance varies based on hardware and image quality*

## 🐛 Troubleshooting

### Issue: "Poppler not found"
```bash
# Install poppler
brew install poppler  # macOS
sudo apt install poppler-utils  # Linux
```

### Issue: "Out of memory"
- Reduce `PDF_DPI` in `.env`
- Reduce `IMAGE_MAX_SIZE`
- Process fewer pages at once

### Issue: "Low accuracy"
- Increase `PDF_DPI` for better quality
- Ensure images are clear and not skewed
- Adjust `CONFIDENCE_THRESHOLD`

## 🔐 Security Notes

- Service runs on localhost by default
- Add authentication for production use
- Validate file types and sizes
- Temporary files are auto-cleaned
- Consider rate limiting for public APIs

## 📦 Project Structure

```
ocr-service/
├── main.py                 # FastAPI application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose setup
├── .env.example          # Environment template
├── models/
│   └── schemas.py        # Pydantic models
├── services/
│   ├── ocr_processor.py  # PaddleOCR wrapper
│   ├── pdf_converter.py  # PDF to image conversion
│   └── invoice_parser.py # Invoice field extraction
├── temp/                 # Temporary files
└── logs/                 # Application logs
```

## 🚀 Deployment

### Production Considerations

1. **Use Gunicorn/Uvicorn workers**
```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

2. **Add Nginx reverse proxy**
```nginx
location /api/ocr {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    client_max_body_size 10M;
}
```

3. **Enable HTTPS**
4. **Add authentication**
5. **Set up monitoring**
6. **Configure log rotation**

## 📄 License

MIT License

## 🤝 Support

For issues or questions, contact the development team.

---

**Built with ❤️ for Fincorpx**
