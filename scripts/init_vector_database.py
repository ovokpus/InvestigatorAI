#!/usr/bin/env python3
"""
Document Vector Database Initialization Service

This service runs after Qdrant starts and before the API starts.
It processes all regulatory documents and loads them into the vector database.
This separates document processing from API startup for faster API availability.
"""

import os
import sys
import time
import logging
from pathlib import Path

# Add the api directory to the Python path
sys.path.append('/app')

from api.core.config import get_settings
from api.services.document_processor import DocumentProcessor
from api.services.vector_store import VectorStoreService
from langchain_openai import OpenAIEmbeddings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def wait_for_qdrant(host: str, port: int, max_retries: int = 30) -> bool:
    """Wait for Qdrant to be ready"""
    import requests
    
    for attempt in range(max_retries):
        try:
            response = requests.get(f"http://{host}:{port}/", timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ Qdrant is ready at {host}:{port}")
                return True
        except Exception as e:
            logger.info(f"⏳ Waiting for Qdrant... (attempt {attempt + 1}/{max_retries})")
            time.sleep(2)
    
    logger.error(f"❌ Qdrant not ready after {max_retries} attempts")
    return False

def check_collection_exists(settings) -> bool:
    """Check if vector collection already exists with documents"""
    try:
        from qdrant_client import QdrantClient
        
        client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            timeout=10
        )
        
        # Check if collection exists
        try:
            collection_info = client.get_collection(settings.vector_collection_name)
            points_count = collection_info.points_count
            
            if points_count > 0:
                logger.info(f"✅ Collection '{settings.vector_collection_name}' exists with {points_count} documents")
                return True
            else:
                logger.info(f"📋 Collection '{settings.vector_collection_name}' exists but is empty")
                return False
                
        except Exception:
            logger.info(f"📋 Collection '{settings.vector_collection_name}' does not exist")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error checking collection: {e}")
        return False

def initialize_vector_database():
    """Initialize the vector database with regulatory documents"""
    logger.info("🚀 Starting Document Vector Database Initialization")
    logger.info("=" * 60)
    
    try:
        # Load settings
        settings = get_settings()
        logger.info(f"📁 PDF Directory: {settings.pdf_data_path}")
        logger.info(f"🗄️  Vector Collection: {settings.vector_collection_name}")
        logger.info(f"🤖 Embedding Model: {settings.embedding_model}")
        
        # Wait for Qdrant to be ready
        if not wait_for_qdrant(settings.qdrant_host, settings.qdrant_port):
            return False
        
        # Check if collection already exists with documents
        if check_collection_exists(settings):
            logger.info("✅ Vector database already initialized - skipping document processing")
            return True
        
        # Initialize embeddings with configured model
        logger.info("🔧 Initializing embeddings...")
        embeddings = OpenAIEmbeddings(model=settings.embedding_model)
        logger.info(f"✅ Embeddings initialized with model: {settings.embedding_model}")
        
        # Initialize document processor
        logger.info("📚 Initializing document processor...")
        doc_processor = DocumentProcessor(embeddings, settings)
        logger.info("✅ Document processor initialized with procedural text filtering")
        
        # Check for PDF files
        pdf_dir = Path(settings.pdf_data_path)
        if not pdf_dir.exists():
            logger.error(f"❌ PDF directory not found: {pdf_dir}")
            return False
            
        pdf_files = list(pdf_dir.glob("*.pdf"))
        if not pdf_files:
            logger.error(f"❌ No PDF files found in {pdf_dir}")
            return False
            
        logger.info(f"📄 Found {len(pdf_files)} PDF files to process")
        
        # Process all documents
        logger.info("🔄 Processing regulatory documents...")
        all_documents = doc_processor.process_all_pdfs()
        
        if not all_documents:
            logger.error("❌ No documents processed successfully")
            return False
            
        logger.info(f"✅ Processed {len(all_documents)} document chunks")
        
        # Initialize vector store
        logger.info("🗄️  Initializing vector store...")
        vector_service = VectorStoreService(embeddings, settings)
        
        # Convert to LangChain documents
        langchain_docs = doc_processor.get_langchain_documents()
        
        # Initialize vector store with documents
        success = vector_service.initialize_from_documents(langchain_docs)
        
        if success:
            logger.info("🎉 SUCCESS! Vector database initialized with regulatory documents")
            logger.info(f"📊 Total document chunks: {len(langchain_docs)}")
            logger.info("🚀 API can now start quickly without document processing delay")
            return True
        else:
            logger.error("❌ Failed to initialize vector store")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error initializing vector database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("🔧 Document Vector Database Initialization Service")
    logger.info("🎯 Purpose: Pre-load documents to speed up API startup")
    
    success = initialize_vector_database()
    
    if success:
        logger.info("✅ INITIALIZATION COMPLETE - API can start quickly now!")
        sys.exit(0)
    else:
        logger.error("❌ INITIALIZATION FAILED")
        sys.exit(1)