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

def wait_for_qdrant(config: Config, max_retries: int = 30) -> bool:
    """Wait for Qdrant to be ready"""
    if config.qdrant_url:
        # Use provided URL (Railway managed service)
        url = config.qdrant_url.rstrip('/') + '/'
    else:
        # Use host/port (local deployment)
        protocol = "https" if config.qdrant_port == 443 else "http"
        url = f"{protocol}://{config.qdrant_host}:{config.qdrant_port}/" if config.qdrant_port != 443 else f"{protocol}://{config.qdrant_host}/"
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ Qdrant is ready at {url}")
                return True
        except Exception as e:
            logger.info(f"⏳ Waiting for Qdrant... (attempt {attempt + 1}/{max_retries})")
            time.sleep(2)
    
    logger.error(f"❌ Qdrant not ready after {max_retries} attempts")
    return False

def create_qdrant_collection(config: Config) -> bool:
    """Create Qdrant collection if it doesn't exist, return True if already populated"""
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, VectorParams
        
        # Configure client - use URL if provided, otherwise host/port
        if config.qdrant_url:
            client = QdrantClient(url=config.qdrant_url)
        elif config.qdrant_port == 443:
            client = QdrantClient(url=f"https://{config.qdrant_host}")
        else:
            client = QdrantClient(host=config.qdrant_host, port=config.qdrant_port)
        
        # Check if collection exists
        try:
            collection_info = client.get_collection(config.collection_name)
            logger.info(f"✅ Collection '{config.collection_name}' already exists with {collection_info.points_count} documents")
            return collection_info.points_count > 0
        except Exception:
            # Collection doesn't exist, create it
            logger.info(f"📋 Creating collection '{config.collection_name}'...")
            client.create_collection(
                collection_name=config.collection_name,
                vectors_config=VectorParams(size=3072, distance=Distance.COSINE)  # text-embedding-3-large dimensions
            )
            return False
            
    except Exception as e:
        logger.error(f"❌ Error with Qdrant collection: {e}")
        return False

def process_pdf_documents(config: Config) -> bool:
    """Process PDF documents and add to vector store"""
    try:
        from langchain_community.document_loaders import PyPDFLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_openai import OpenAIEmbeddings
        from qdrant_client import QdrantClient
        from qdrant_client.models import PointStruct
        import uuid
        
        # Initialize components
        client = QdrantClient(host=config.qdrant_host, port=config.qdrant_port)
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
        
        # Upload all points to Qdrant
        if all_points:
            logger.info(f"📤 Uploading {len(all_points)} document chunks to Qdrant...")
            client.upsert(
                collection_name=config.collection_name,
                points=all_points
            )
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
        if create_qdrant_collection(config):
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