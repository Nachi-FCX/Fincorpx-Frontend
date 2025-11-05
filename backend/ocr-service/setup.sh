#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  Fincorpx OCR Service Setup${NC}"
echo -e "${BLUE}================================${NC}\n"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.10+${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 found${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${BLUE}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
fi

# Create necessary directories
mkdir -p temp logs
echo -e "${GREEN}✓ Directories created${NC}"

# Check for poppler
if ! command -v pdftoppm &> /dev/null; then
    echo -e "${RED}⚠ Warning: Poppler is not installed${NC}"
    echo -e "${RED}  PDF processing will not work${NC}"
    echo -e "${RED}  Install with: brew install poppler (macOS)${NC}"
    echo -e "${RED}             or: sudo apt install poppler-utils (Linux)${NC}\n"
fi

echo -e "\n${GREEN}================================${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${GREEN}================================${NC}\n"

echo -e "${BLUE}To start the service:${NC}"
echo -e "  python main.py"
echo -e "\n${BLUE}Or with auto-reload:${NC}"
echo -e "  uvicorn main:app --reload --port 8000"
echo -e "\n${BLUE}API Documentation:${NC}"
echo -e "  http://localhost:8000/docs\n"

# Ask if user wants to start the service
read -p "Start the service now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "\n${GREEN}Starting OCR service...${NC}\n"
    python main.py
fi
