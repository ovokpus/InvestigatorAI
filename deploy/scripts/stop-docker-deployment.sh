#!/bin/bash

# InvestigatorAI Docker Deployment Stop Script
# This script safely stops and cleans up the Docker deployment

set -e  # Exit on any error

echo "🛑 Stopping InvestigatorAI Docker Deployment"
echo "============================================"

# Go to project root
cd "$(dirname "$0")/../.."

# Show current status
echo "📊 Current deployment status:"
docker-compose ps

echo ""
echo "🔄 Stopping all services..."

# Stop all services gracefully
docker-compose down

echo ""
echo "🧹 Cleaning up..."

# Option to remove volumes (ask user)
read -p "🗑️  Do you want to remove data volumes (Redis data, Qdrant storage)? [y/N]: " -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Removing volumes..."
    docker-compose down -v
    echo "✅ Volumes removed"
else
    echo "💾 Volumes preserved"
fi

# Option to remove images (ask user)
read -p "🗑️  Do you want to remove built Docker images? [y/N]: " -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Removing images..."
    docker-compose down --rmi local
    echo "✅ Images removed"
else
    echo "💾 Images preserved"
fi

# Show final status
echo ""
echo "📊 Final status:"
docker-compose ps

echo ""
echo "✅ InvestigatorAI Docker deployment stopped successfully!"
echo ""
echo "🔄 To start again, run:"
echo "   ./deploy/scripts/start-docker-deployment.sh"
echo ""
echo "🧹 To clean everything including images and volumes:"
echo "   docker-compose down -v --rmi all"
echo "   docker system prune -f"