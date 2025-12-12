#!/bin/bash

# ====================================
# Start Taxini Backend
# ====================================

echo "🚀 Starting Taxini Backend..."

cd "$(dirname "$0")/backend"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env with your actual credentials!"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d .venv ]; then
    echo "📦 Installing dependencies with uv..."
    uv pip install -e .
fi

# Activate virtual environment
source .venv/bin/activate

# Run database migrations (skip if database not available)
echo "📊 Running database migrations..."
if alembic upgrade head 2>/dev/null; then
    echo "✅ Migrations completed"
else
    echo "⚠️  Migrations skipped (database not available)"
    echo "   Backend will still start for API testing"
fi

# Start the backend server
echo "✅ Starting FastAPI server..."
echo "📍 Backend will be available at: http://localhost:8000"
echo "📚 API docs at: http://localhost:8000/docs"
echo ""

uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
