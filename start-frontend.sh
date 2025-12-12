#!/bin/bash

# ====================================
# Start Taxini Frontend
# ====================================

echo "🚀 Starting Taxini Frontend..."

cd "$(dirname "$0")/frontend"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit frontend/.env with your actual credentials!"
    exit 1
fi

# Check if node_modules exists
if [ ! -d node_modules ]; then
    echo "📦 Installing dependencies with npm..."
    npm install
fi

# Start the development server
echo "✅ Starting Vite development server..."
echo "📍 Frontend will be available at: http://localhost:3000"
echo ""

npm run dev
