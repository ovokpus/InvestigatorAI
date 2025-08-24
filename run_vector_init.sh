#!/bin/bash

# Railway Qdrant Configuration
export QDRANT_URL="https://qdrant-production-1cff.up.railway.app"

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY environment variable is not set"
    echo "Please set it with: export OPENAI_API_KEY='your-key-here'"
    exit 1
fi

# Optional configuration (with defaults)
export EMBEDDING_MODEL="${EMBEDDING_MODEL:-text-embedding-3-large}"
export VECTOR_COLLECTION_NAME="${VECTOR_COLLECTION_NAME:-regulatory_documents}"
export PDF_DATA_PATH="${PDF_DATA_PATH:-data/pdf_downloads}"
export CHUNK_SIZE="${CHUNK_SIZE:-1000}"
export CHUNK_OVERLAP="${CHUNK_OVERLAP:-200}"

echo "🚀 Starting vector database initialization..."
echo "📍 Qdrant URL: $QDRANT_URL"
echo "📚 PDF Path: $PDF_DATA_PATH"
echo "🔧 Collection: $VECTOR_COLLECTION_NAME"
echo ""

# Run the initialization script
python scripts/init_vector_database.py
