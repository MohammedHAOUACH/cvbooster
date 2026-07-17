#!/bin/bash
# Initialization script for CVBooster VPS deployment

set -e

echo "=== CVBooster Initialization Script ==="

# Create directories
echo "Creating directories..."
mkdir -p uploads/original-cvs
mkdir -p uploads/generated-cvs
mkdir -p data

# Generate JWT secret if not exists
if [ -z "$JWT_SECRET" ]; then
    echo "Generating JWT_SECRET..."
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    echo "JWT_SECRET=$JWT_SECRET" >> .env
fi

# Create .env from example if not exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "" >> .env
    echo "# Generated JWT Secret" >> .env
    echo "JWT_SECRET=$JWT_SECRET" >> .env
fi

# Check required environment variables
echo "Checking environment variables..."
REQUIRED_VARS=(
    "GOOGLE_CLIENT_ID"
    "GOOGLE_CLIENT_SECRET"
    "GOOGLE_REDIRECT_URI"
    "JWT_SECRET"
)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "⚠️  Warning: $var is not set"
    else
        echo "✓ $var is set"
    fi
done

# Set permissions
echo "Setting permissions..."
chmod 755 uploads
chmod 755 data
chmod 644 uploads/original-cvs
chmod 644 uploads/generated-cvs

echo ""
echo "=== Initialization Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit .env with your Google OAuth credentials"
echo "2. Edit .env with your OpenRouter API key"
echo "3. Run: docker compose up -d --build"
echo "4. Visit: http://your-vps-ip"
echo ""
echo "Google OAuth Setup:"
echo "- Go to: https://console.cloud.google.com/"
echo "- Create a new project"
echo "- Enable Google+ API"
echo "- Create OAuth 2.0 credentials"
echo "- Set authorized redirect URI: http://your-vps-ip/api/auth/google/callback"
echo ""
