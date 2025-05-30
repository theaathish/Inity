#!/bin/bash
# Build script for Inity - Cross-platform build
# Developed by Aathish at Strucureo

set -e

echo "🏗️  Building Inity for multiple platforms..."
echo "Developed by Aathish at Strucureo"
echo "============================================"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run build script
echo "Starting build process..."
python build.py

echo "✅ Build completed!"
