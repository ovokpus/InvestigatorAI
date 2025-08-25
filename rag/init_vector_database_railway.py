#!/usr/bin/env python3
"""
Railway-Compatible Vector Database Initialization Service

This version uses REST API directly instead of qdrant-client library
to work with Railway Qdrant containers.
"""

import os
import sys
import time
import logging
import requests
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from root .env file
def load_env_file():
    """Load environment variables from .env file in project root"""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        logger.info(f"📋 Loading environment variables from {env_path}")
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Only set if not already in environment (command line takes precedence)
                    if key not in os.environ:
                        os.environ[key] = value.strip('"').strip("'")
        logger.info("✅ Environment variables loaded from .env file")
    else:
        logger.warning(f"⚠️  No .env file found at {env_path}")

# Load .env file before anything else
load_env_file()

class Config:
    """Standalone configuration class"""
    def __init__(self):
        # Qdrant configuration - support both URL and host/port patterns
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        self.qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        
        # API configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
        
        # Vector database configuration
        self.collection_name = os.getenv("VECTOR_COLLECTION_NAME", "regulatory_documents")
        self.pdf_data_path = os.getenv("PDF_DATA_PATH", "data/pdf_downloads")
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        if self.qdrant_url:
            logger.info(f"📋 Vector init config - Qdrant URL: {self.qdrant_url}")
        else:
            logger.info(f"📋 Vector init config - Qdrant: {self.qdrant_host}:{self.qdrant_port}")

class RailwayQdrantClient:
    """REST API client for Railway Qdrant container"""
    
    def __init__(self, base_url: str, timeout: int = 60):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
    def get_collections(self):
        """Get all collections"""
        response = self.session.get(
            f"{self.base_url}/collections",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def create_collection(self, collection_name: str, vector_size: int = 3072):
        """Create a new collection"""
        payload = {
            "vectors": {
                "size": vector_size,
                "distance": "Cosine"
            }
        }
        response = self.session.put(
            f"{self.base_url}/collections/{collection_name}",
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def get_collection_info(self, collection_name: str):
        """Get collection information"""
        response = self.session.get(
            f"{self.base_url}/collections/{collection_name}",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def upsert_points(self, collection_name: str, points: List[Dict[str, Any]]):
        """Upload points to collection"""
        payload = {"points": points}
        response = self.session.put(
            f"{self.base_url}/collections/{collection_name}/points",
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

def wait_for_qdrant(config: Config, max_retries: int = 60) -> bool:
    """Wait for Qdrant to be ready - Extended for Railway"""
    if config.qdrant_url:
        # Use provided URL (Railway managed service)
        url = config.qdrant_url.rstrip('/') + '/'
    else:
        # Use host/port (local deployment)
        protocol = "https" if config.qdrant_port == 443 else "http"
        url = f"{protocol}://{config.qdrant_host}:{config.qdrant_port}/" if config.qdrant_port != 443 else f"{protocol}://{config.qdrant_host}/"
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)  # Increased timeout for Railway
            if response.status_code == 200:
                logger.info(f"✅ Qdrant is ready at {url}")
                return True
        except Exception as e:
            logger.info(f"⏳ Waiting for Qdrant... (attempt {attempt + 1}/{max_retries}) - {str(e)[:50]}...")
            time.sleep(3)  # Longer wait for Railway startup
    
    logger.error(f"❌ Qdrant not ready after {max_retries} attempts")
    return False

def create_qdrant_collection(config: Config) -> bool:
    """Create Qdrant collection if it doesn't exist, return True if already populated"""
    try:
        # Use Railway-compatible REST client
        if config.qdrant_url:
            client = RailwayQdrantClient(config.qdrant_url, timeout=60)
        else:
            protocol = "https" if config.qdrant_port == 443 else "http"
            url = f"{protocol}://{config.qdrant_host}:{config.qdrant_port}"
            client = RailwayQdrantClient(url, timeout=60)
        
        # Check if collection exists with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                collection_info = client.get_collection_info(config.collection_name)
                points_count = collection_info['result']['points_count']
                logger.info(f"✅ Collection '{config.collection_name}' already exists with {points_count} documents")
                return points_count > 0
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    # Collection doesn't exist, try to create it
                    logger.info(f"📋 Creating collection '{config.collection_name}' (attempt {attempt + 1}/{max_retries})...")
                    try:
                        client.create_collection(config.collection_name, vector_size=3072)
                        logger.info(f"✅ Collection '{config.collection_name}' created successfully")
                        return False  # Collection is new, needs to be populated
                    except Exception as create_error:
                        if attempt < max_retries - 1:
                            logger.warning(f"⚠️ Collection creation failed (attempt {attempt + 1}), retrying... {str(create_error)[:100]}")
                            time.sleep(5)
                        else:
                            logger.error(f"❌ Failed to create collection after {max_retries} attempts: {create_error}")
                            return None
                else:
                    raise
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"⚠️ Connection issue (attempt {attempt + 1}), retrying... {str(e)[:100]}")
                    time.sleep(5)
                else:
                    logger.error(f"❌ Failed to connect to Qdrant after {max_retries} attempts: {e}")
                    return None
        
        return False
            
    except Exception as e:
        logger.error(f"❌ Critical error with Qdrant collection: {e}")
        return None

def process_pdf_documents(config: Config) -> bool:
    """Process PDF documents and add to vector store"""
    try:
        from langchain_community.document_loaders import PyPDFLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_openai import OpenAIEmbeddings
        
        # Initialize Railway-compatible client
        if config.qdrant_url:
            client = RailwayQdrantClient(config.qdrant_url, timeout=600)
        else:
            protocol = "https" if config.qdrant_port == 443 else "http"
            url = f"{protocol}://{config.qdrant_host}:{config.qdrant_port}"
            client = RailwayQdrantClient(url, timeout=600)
            
        embeddings = OpenAIEmbeddings(
            openai_api_key=config.openai_api_key,
            model=config.embedding_model
        )
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap
        )
        
        # Find PDF files
        pdf_path = Path(config.pdf_data_path)
        if not pdf_path.exists():
            logger.error(f"❌ PDF directory not found: {pdf_path}")
            return False
            
        pdf_files = list(pdf_path.glob("*.pdf"))
        if not pdf_files:
            logger.error(f"❌ No PDF files found in {pdf_path}")
            return False
            
        logger.info(f"📚 Found {len(pdf_files)} PDF files to process")
        
        # Process each PDF
        all_points = []
        for pdf_file in pdf_files:
            logger.info(f"📄 Processing {pdf_file.name}...")
            
            try:
                # Load and split document
                loader = PyPDFLoader(str(pdf_file))
                documents = loader.load()
                chunks = text_splitter.split_documents(documents)
                
                # Create embeddings in batches for efficiency
                chunk_texts = [chunk.page_content for chunk in chunks]
                
                # Process embeddings in batches of 100 to optimize API calls
                embedding_batch_size = 100
                chunk_embeddings = []
                
                for i in range(0, len(chunk_texts), embedding_batch_size):
                    batch_texts = chunk_texts[i:i + embedding_batch_size]
                    batch_embeddings = embeddings.embed_documents(batch_texts)
                    chunk_embeddings.extend(batch_embeddings)
                
                # Create points with batched embeddings
                for i, (chunk, embedding) in enumerate(zip(chunks, chunk_embeddings)):
                    point = {
                        "id": str(uuid.uuid4()),
                        "vector": embedding,
                        "payload": {
                            "content": chunk.page_content,
                            "source": pdf_file.name,
                            "chunk_index": i,
                            "metadata": chunk.metadata
                        }
                    }
                    all_points.append(point)
                    
                logger.info(f"✅ Processed {pdf_file.name}: {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"❌ Error processing {pdf_file.name}: {e}")
                continue
        
        # Upload all points to Qdrant in batches
        if all_points:
            logger.info(f"📤 Uploading {len(all_points)} document chunks to Qdrant...")
            
            # Upload in smaller batches optimized for Railway
            batch_size = 50  # Reduced batch size for Railway network limits
            total_batches = (len(all_points) + batch_size - 1) // batch_size
            
            for i in range(0, len(all_points), batch_size):
                batch = all_points[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                
                logger.info(f"📦 Uploading batch {batch_num}/{total_batches} ({len(batch)} chunks)...")
                
                # Retry logic for Railway network issues
                max_retries = 3
                for retry in range(max_retries):
                    try:
                        client.upsert_points(config.collection_name, batch)
                        logger.info(f"✅ Batch {batch_num}/{total_batches} uploaded successfully")
                        break
                    except Exception as e:
                        if retry < max_retries - 1:
                            logger.warning(f"⚠️ Batch {batch_num} failed (attempt {retry + 1}), retrying... {str(e)[:100]}")
                            time.sleep(5)  # Wait before retry
                        else:
                            logger.error(f"❌ Error uploading batch {batch_num} after {max_retries} attempts: {e}")
                            return False
                
                # Progress indicator for long uploads
                if batch_num % 10 == 0:
                    progress = (batch_num / total_batches) * 100
                    logger.info(f"📊 Upload progress: {progress:.1f}% ({batch_num}/{total_batches} batches)")
            
            logger.info("✅ Successfully uploaded all document chunks")
            return True
        else:
            logger.error("❌ No document chunks to upload")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error processing documents: {e}")
        return False

def main():
    """Main initialization function"""
    logger.info("🚀 Starting Railway-compatible vector database initialization...")
    
    try:
        # Load configuration
        config = Config()
        logger.info(f"📋 Configuration loaded - Qdrant: {config.qdrant_host}:{config.qdrant_port}")
        
        # Wait for Qdrant to be ready
        if not wait_for_qdrant(config):
            sys.exit(1)
        
        # Create collection and check if already populated
        collection_result = create_qdrant_collection(config)
        if collection_result is None:
            logger.error("❌ Failed to create or connect to Qdrant collection. Exiting...")
            sys.exit(1)
        elif collection_result:
            logger.info("✅ Vector database already initialized. Skipping...")
            return
        
        # Process PDF documents
        logger.info("📚 Processing regulatory documents...")
        if process_pdf_documents(config):
            logger.info("🎉 Vector database initialization complete!")
        else:
            logger.error("❌ Vector database initialization failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
