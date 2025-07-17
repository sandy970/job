#!/bin/bash

echo "🚀 Starting Job Dashboard Backend..."

# Navigate to the backend directory
cd job-api

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/lib/python*/site-packages/fastapi" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Install Playwright browsers if needed
if [ ! -d "venv/lib/python*/site-packages/playwright" ]; then
    echo "Installing Playwright browsers..."
    playwright install
fi

# Check for environment file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from example..."
    cp .env.example .env
    echo "✏️  Please edit .env with your configuration"
fi

# Start the server
echo "🎯 Starting FastAPI server on http://localhost:8000"
echo "📚 API documentation will be available at http://localhost:8000/docs"
echo ""
python main.py