#!/bin/bash

# InvestigatorAI Docker Deployment Script
# This script sets up and starts the complete InvestigatorAI system with Docker

set -e  # Exit on any error

echo "🚀 Starting InvestigatorAI Docker Deployment"
echo "=============================================="

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

# Go to project root
cd "$(dirname "$0")/../.."

# Check for environment file
if [ ! -f ".env" ]; then
    echo "📝 No .env file found. Creating from template..."
    if [ -f "docker.env.example" ]; then
        cp docker.env.example .env
        echo "✅ Created .env file from docker.env.example"
        echo ""
        echo "⚠️  IMPORTANT: Please edit .env and add your API keys:"
        echo "   - OPENAI_API_KEY"
        echo "   - TAVILY_SEARCH_API_KEY"
        echo "   - EXCHANGE_RATE_API_KEY (optional)"
        echo "   - LANGSMITH_API_KEY (optional)"
        echo ""
        echo "💡 You can edit the file with: nano .env"
        echo ""
        read -p "Press Enter after you've configured your API keys..."
    else
        echo "❌ docker.env.example not found. Please create .env manually."
        exit 1
    fi
fi

echo "🔧 Building Docker images..."
docker-compose build --no-cache

echo "🗄️ Starting infrastructure services (Redis, Qdrant)..."
docker-compose up -d redis qdrant

echo "⏳ Waiting for infrastructure services to be healthy..."
sleep 10

# Wait for Redis to be ready
echo "🔍 Checking Redis health..."
until docker-compose exec redis redis-cli ping | grep -q "PONG"; do
    echo "   Waiting for Redis..."
    sleep 2
done
echo "✅ Redis is ready"

# Wait for Qdrant to be ready
echo "🔍 Checking Qdrant health..."
until curl -s http://localhost:6333/health | grep -q "ok"; do
    echo "   Waiting for Qdrant..."
    sleep 2
done
echo "✅ Qdrant is ready"

echo "🚀 Starting API backend..."
docker-compose up -d api

echo "⏳ Waiting for API to be healthy..."
sleep 15

# Wait for API to be ready
echo "🔍 Checking API health..."
until curl -s http://localhost:8000/health | grep -q "healthy"; do
    echo "   Waiting for API..."
    sleep 5
done
echo "✅ API is ready"

echo "🌐 Starting frontend..."
docker-compose up -d frontend

echo "⏳ Waiting for frontend to be ready..."
sleep 10

# Check frontend
echo "🔍 Checking frontend..."
until curl -s http://localhost:3000 &> /dev/null; do
    echo "   Waiting for frontend..."
    sleep 3
done
echo "✅ Frontend is ready"

echo ""
echo "🎉 InvestigatorAI is now running!"
echo "=================================="
echo ""
echo "📱 Application URLs:"
echo "   Frontend:      http://localhost:3000"
echo "   API:           http://localhost:8000"
echo "   API Docs:      http://localhost:8000/docs"
echo "   API Health:    http://localhost:8000/health"
echo ""
echo "🛠️  Management URLs:"
echo "   Redis UI:      http://localhost:8081 (run: docker-compose --profile ui up -d)"
echo "   Qdrant UI:     http://localhost:6333/dashboard"
echo ""
echo "📊 Useful commands:"
echo "   View logs:     docker-compose logs -f"
echo "   Stop all:      docker-compose down"
echo "   Restart:       docker-compose restart"
echo ""
echo "🔧 Troubleshooting:"
echo "   Check status:  docker-compose ps"
echo "   View API logs: docker-compose logs api"
echo "   Check health:  curl http://localhost:8000/health"
echo ""
echo "✨ Happy investigating!"