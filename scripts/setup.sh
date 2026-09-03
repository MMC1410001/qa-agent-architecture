#!/bin/bash

# QA-OS Setup Script
set -e

echo "================================================"
echo "QA-OS Setup"
echo "================================================"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "${BLUE}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo -e "${BLUE}Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -r requirements.txt

# Create necessary directories
echo -e "${BLUE}Creating directories...${NC}"
mkdir -p logs
mkdir -p data
mkdir -p artifacts

# Copy .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${BLUE}Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please update .env file with your configuration${NC}"
fi

# Install Playwright browsers
echo -e "${BLUE}Installing Playwright browsers...${NC}"
python -m playwright install chromium firefox

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}QA-OS setup complete!${NC}"
echo -e "${GREEN}================================================${NC}"

echo ""
echo "Next steps:"
echo "1. Update .env file with your configuration"
echo "2. Run: python src/main.py"
echo "3. Visit: http://localhost:8000/docs"
echo ""
