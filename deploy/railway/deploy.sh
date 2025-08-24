#!/bin/bash

# Railway Setup Using Existing .env File
# This script reads your API keys from the root .env file and configures Railway

set -e

echo "🔧 InvestigatorAI Railway Setup from .env"
echo "========================================"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found in root directory"
    echo "Please create a .env file with your API keys first"
    exit 1
fi

echo "✅ Found .env file"

# Check Railway CLI
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Install with:"
    echo "   npm install -g @railway/cli"
    exit 1
fi

# Check authentication
if ! railway whoami &> /dev/null; then
    echo "🔐 Please log in to Railway:"
    railway login
fi

echo "✅ Railway CLI ready"

# Link project if not already linked
if ! railway status &> /dev/null; then
    echo "🔗 Linking to Railway project..."
    railway link
fi

echo "✅ Connected to Railway project"

# Read API keys from .env file
echo ""
echo "🔑 Reading API keys from .env file..."

# Function to extract value from .env file
get_env_value() {
    local key=$1
    local value=$(grep "^${key}=" .env 2>/dev/null | cut -d '=' -f2- | sed 's/^["'\'']//' | sed 's/["'\'']$//')
    echo "$value"
}

# Extract API keys
OPENAI_KEY=$(get_env_value "OPENAI_API_KEY")
TAVILY_KEY=$(get_env_value "TAVILY_SEARCH_API_KEY")
LANGSMITH_KEY=$(get_env_value "LANGSMITH_API_KEY")
LANGSMITH_PROJECT=$(get_env_value "LANGSMITH_PROJECT")

# Validate required keys
if [ -z "$OPENAI_KEY" ]; then
    echo "❌ OPENAI_API_KEY not found in .env file"
    exit 1
fi

if [ -z "$TAVILY_KEY" ]; then
    echo "❌ TAVILY_SEARCH_API_KEY not found in .env file"
    exit 1
fi

echo "✅ Found OpenAI API key"
echo "✅ Found Tavily API key"
if [ ! -z "$LANGSMITH_KEY" ]; then
    echo "✅ Found LangSmith API key"
fi

# Configure services
echo ""
echo "🔧 Configuring Railway services..."

# Redis configuration
echo "1️⃣ Configuring Redis..."
railway variables set --service redis \
    REDIS_ARGS="--appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru" || echo "⚠️  Redis may already be configured"

# Qdrant configuration
echo "2️⃣ Configuring Qdrant..."
railway variables set --service qdrant \
    QDRANT__SERVICE__HTTP_PORT=6333 \
    QDRANT__SERVICE__GRPC_PORT=6334 \
    QDRANT__LOG_LEVEL=INFO || echo "⚠️  Qdrant may already be configured"

# API service configuration
echo "3️⃣ Configuring API service (repo)..."

# Core settings
railway variables set --service repo \
    PORT=8000 \
    PYTHONPATH=/app \
    LOG_LEVEL=INFO \
    DEBUG=false

# Service connections
railway variables set --service repo \
    REDIS_HOST='${{redis.RAILWAY_PRIVATE_DOMAIN}}' \
    REDIS_PORT=6379 \
    QDRANT_HOST='${{qdrant.RAILWAY_PRIVATE_DOMAIN}}' \
    QDRANT_PORT=6333

# Performance settings
railway variables set --service repo \
    CACHE_ENABLED=true \
    BM25_ENABLED=true \
    DEFAULT_RETRIEVAL_METHOD=auto \
    ENABLE_PERFORMANCE_LOGGING=true

# Security and resource settings
railway variables set --service repo \
    ALLOWED_ORIGINS='https://*.railway.app,https://*.up.railway.app' \
    RATE_LIMIT_REQUESTS=10 \
    RATE_LIMIT_WINDOW=60 \
    MAX_MEMORY_MB=1024 \
    CLEANUP_THRESHOLD=0.8

# Set API keys from .env file
echo "4️⃣ Setting API keys from .env..."
railway variables set --service repo \
    OPENAI_API_KEY="$OPENAI_KEY" \
    TAVILY_SEARCH_API_KEY="$TAVILY_KEY"

# Set LangSmith if available
if [ ! -z "$LANGSMITH_KEY" ]; then
    PROJECT_NAME=${LANGSMITH_PROJECT:-"InvestigatorAI-Railway"}
    railway variables set --service repo \
        LANGSMITH_API_KEY="$LANGSMITH_KEY" \
        LANGSMITH_PROJECT="$PROJECT_NAME" \
        LANGSMITH_TRACING=true
    echo "✅ LangSmith monitoring configured"
fi

# Additional environment variables from .env if they exist
echo "5️⃣ Setting additional configuration..."

# Model settings
EMBEDDING_MODEL=$(get_env_value "EMBEDDING_MODEL")
LLM_MODEL=$(get_env_value "LLM_MODEL")
LLM_TEMPERATURE=$(get_env_value "LLM_TEMPERATURE")
LLM_MAX_TOKENS=$(get_env_value "LLM_MAX_TOKENS")

if [ ! -z "$EMBEDDING_MODEL" ]; then
    railway variables set --service repo EMBEDDING_MODEL="$EMBEDDING_MODEL"
fi

if [ ! -z "$LLM_MODEL" ]; then
    railway variables set --service repo LLM_MODEL="$LLM_MODEL"
fi

if [ ! -z "$LLM_TEMPERATURE" ]; then
    railway variables set --service repo LLM_TEMPERATURE="$LLM_TEMPERATURE"
fi

if [ ! -z "$LLM_MAX_TOKENS" ]; then
    railway variables set --service repo LLM_MAX_TOKENS="$LLM_MAX_TOKENS"
fi

echo ""
echo "✅ Configuration complete!"
echo ""

# Ask if user wants to deploy now
read -p "🚀 Deploy API service now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Deploying API service..."
    railway up --service repo --detach
    
    echo ""
    echo "✅ Deployment started!"
    echo ""
    echo "📊 Monitor deployment:"
    echo "   railway logs --service repo --follow"
    echo ""
    echo "🌐 Get your API URL:"
    echo "   railway domain"
    echo ""
    echo "📖 Open Railway dashboard:"
    echo "   railway open"
else
    echo ""
    echo "🚀 Ready to deploy when you are!"
    echo ""
    echo "To deploy your API service:"
    echo "   railway up --service repo"
    echo ""
    echo "To monitor deployment:"
    echo "   railway logs --service repo --follow"
fi
