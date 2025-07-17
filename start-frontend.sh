#!/bin/bash

echo "🎨 Starting Job Dashboard Frontend..."

# Navigate to the frontend directory
cd job-dashboard

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start the development server
echo "🎯 Starting Next.js development server on http://localhost:3000"
echo "🔄 The app will automatically reload when you make changes"
echo ""
npm run dev