#!/bin/bash

# Start Redis and Qdrant containers for InvestigatorAI
echo "🚀 Starting InvestigatorAI containers..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found. Please run from project root."
    exit 1
fi

# Start the containers
echo "📦 Starting Redis and Qdrant containers..."
docker-compose up -d redis qdrant

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check Redis health
echo "🔍 Checking Redis health..."
if docker-compose exec redis redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis is ready"
else
    echo "❌ Redis failed to start"
fi

# Check Qdrant health
echo "🔍 Checking Qdrant health..."
if curl -s -f http://localhost:6333/health > /dev/null; then
    echo "✅ Qdrant is ready"
else
    echo "❌ Qdrant failed to start"
fi

echo ""
echo "🎉 Container services are ready!"
echo ""
echo "📊 Service URLs:"
echo "   Redis:  localhost:6379"
echo "   Qdrant: http://localhost:6333"
echo ""
echo "🛠️  Management UIs (optional):"
echo "   Redis Commander: docker-compose --profile ui up -d redis-commander"
echo "   Then visit: http://localhost:8081"
echo ""
echo "📝 To stop containers: docker-compose down"
echo "📝 To view logs: docker-compose logs -f"