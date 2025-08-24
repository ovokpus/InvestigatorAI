#!/usr/bin/env python3
"""
Standalone Vector Database Initialization Service

This service runs after Qdrant starts and before the API starts.
It processes all regulatory documents and loads them into the vector database.
This is a standalone script that doesn't depend on the API codebase.
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict, Any
import requests
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
            logger.info(f"⏳ Waiting for Qdrant... (attempt {attempt + 1}/{max_retries}) - {str(e)[:50]}")
            time.sleep(3)  # Longer wait for Railway startup
    
    logger.error(f"❌ Qdrant not ready after {max_retries} attempts")
    return False

def create_qdrant_collection(config: Config) -> bool:
    """Create Qdrant collection if it doesn't exist, return True if already populated"""
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams
        
        # Configure client for Railway container - REST API only
        if config.qdrant_url:
            client = QdrantClient(
                url=config.qdrant_url, 
                timeout=60, 
                prefer_grpc=False,  # Force REST API for Railway
                api_key=None,       # No auth needed for Railway container
                https=True          # Railway uses HTTPS
            )
        elif config.qdrant_port == 443:
            client = QdrantClient(url=f"https://{config.qdrant_host}", timeout=60, prefer_grpc=False)
        else:
            client = QdrantClient(host=config.qdrant_host, port=config.qdrant_port, timeout=60, prefer_grpc=False)
        
        # Check if collection exists with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                collection_info = client.get_collection(config.collection_name)
                logger.info(f"✅ Collection '{config.collection_name}' already exists with {collection_info.points_count} documents")
                return collection_info.points_count > 0
            except Exception as e:
                if "not found" in str(e).lower() or "does not exist" in str(e).lower():
                    # Collection doesn't exist, try to create it
                    logger.info(f"📋 Creating collection '{config.collection_name}' (attempt {attempt + 1}/{max_retries})...")
                    try:
                        client.create_collection(
                            collection_name=config.collection_name,
                            vectors_config=VectorParams(size=3072, distance=Distance.COSINE)  # text-embedding-3-large dimensions
                        )
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
        from qdrant_client import QdrantClient
        from qdrant_client.models import PointStruct
        import uuid
        
        # Initialize components for Railway container - REST API only
        if config.qdrant_url:
            client = QdrantClient(
                url=config.qdrant_url, 
                timeout=600, 
                prefer_grpc=False,  # Force REST API for Railway
                api_key=None,       # No auth needed for Railway container
                https=True          # Railway uses HTTPS
            )
        elif config.qdrant_port == 443:
            client = QdrantClient(url=f"https://{config.qdrant_host}", timeout=600, prefer_grpc=False)
        else:
            client = QdrantClient(host=config.qdrant_host, port=config.qdrant_port, timeout=600, prefer_grpc=False)
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
                
                # Create embeddings and points
                for i, chunk in enumerate(chunks):
                    embedding = embeddings.embed_query(chunk.page_content)
                    
                    point = PointStruct(
                        id=str(uuid.uuid4()),
                        vector=embedding,
                        payload={
                            "content": chunk.page_content,
                            "source": pdf_file.name,
                            "chunk_index": i,
                            "metadata": chunk.metadata
                        }
                    )
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
                        client.upsert(
                            collection_name=config.collection_name,
                            points=batch
                        )
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
    logger.info("🚀 Starting standalone vector database initialization...")
    
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