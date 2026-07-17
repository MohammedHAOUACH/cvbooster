#!/bin/bash
# Test script for CVBooster deployment

set -e

echo "=== CVBooster Deployment Test ==="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Docker
echo "1. Checking Docker..."
if docker --version > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker is installed${NC}"
else
    echo -e "${RED}✗ Docker is not installed${NC}"
    exit 1
fi

# Check Docker Compose
echo "2. Checking Docker Compose..."
if docker compose version > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker Compose is installed${NC}"
else
    echo -e "${RED}✗ Docker Compose is not installed${NC}"
    exit 1
fi

# Check .env file
echo "3. Checking .env file..."
if [ -f .env ]; then
    echo -e "${GREEN}✓ .env file exists${NC}"
    
    # Check required variables
    if grep -q "GOOGLE_CLIENT_ID" .env && ! grep -q "GOOGLE_CLIENT_ID=test" .env; then
        echo -e "${GREEN}✓ Google OAuth configured${NC}"
    else
        echo -e "${YELLOW}⚠ Google OAuth not configured (using test values)${NC}"
    fi
    
    if grep -q "OPENROUTER_API_KEY=" .env && ! grep -q "OPENROUTER_API_KEY=" .env | grep -q "^OPENROUTER_API_KEY=$"; then
        echo -e "${GREEN}✓ OpenRouter API key configured${NC}"
    else
        echo -e "${YELLOW}⚠ OpenRouter API key not configured${NC}"
    fi
else
    echo -e "${RED}✗ .env file not found${NC}"
    echo "Run: cp .env.example .env and edit it"
    exit 1
fi

# Check docker-compose.yml
echo "4. Checking docker-compose.yml..."
if [ -f docker-compose.yml ]; then
    echo -e "${GREEN}✓ docker-compose.yml exists${NC}"
else
    echo -e "${RED}✗ docker-compose.yml not found${NC}"
    exit 1
fi

# Check backend files
echo "5. Checking backend files..."
if [ -f backend/src/main.py ] && [ -f backend/Dockerfile ]; then
    echo -e "${GREEN}✓ Backend files exist${NC}"
else
    echo -e "${RED}✗ Backend files missing${NC}"
    exit 1
fi

# Check frontend files
echo "6. Checking frontend files..."
if [ -f frontend/Dockerfile ]; then
    echo -e "${GREEN}✓ Frontend files exist${NC}"
else
    echo -e "${RED}✗ Frontend files missing${NC}"
    exit 1
fi

# Check nginx config
echo "7. Checking nginx configuration..."
if [ -f nginx/nginx.conf ]; then
    echo -e "${GREEN}✓ nginx.conf exists${NC}"
else
    echo -e "${RED}✗ nginx.conf not found${NC}"
    exit 1
fi

# Check directories
echo "8. Creating required directories..."
mkdir -p uploads/original-cvs uploads/generated-cvs data
echo -e "${GREEN}✓ Directories created${NC}"

echo ""
echo "=== Pre-build Checks Complete ==="
echo ""
echo "Ready to build and run?"
echo ""
echo "Commands:"
echo "  docker compose build          # Build images"
echo "  docker compose up -d          # Start services"
echo "  docker compose logs -f api    # View API logs"
echo "  docker compose logs -f frontend  # View frontend logs"
echo ""
echo "After starting, visit: http://localhost"
echo ""
