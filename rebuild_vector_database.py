#!/usr/bin/env python3
"""
Rebuild vector database with procedural text filtering
"""
import os
import sys
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def rebuild_vector_database():
    """Rebuild the vector database with filtered documents"""
    print("🔄 REBUILDING VECTOR DATABASE WITH PROCEDURAL TEXT FILTERING")
    print("=" * 60)
    
    try:
        from api.core.config import get_settings
        from api.services.document_processor import DocumentProcessor
        from api.services.vector_store import VectorStoreManager
        from langchain_openai import OpenAIEmbeddings
        
        # Get settings
        settings = get_settings()
        print(f"📁 PDF Directory: {settings.pdf_data_path}")
        print(f"🗄️  Vector Collection: {settings.vector_collection_name}")
        
        # Initialize embeddings with configured model
        embeddings = OpenAIEmbeddings(model=settings.embedding_model)
        print(f"✅ OpenAI embeddings initialized with model: {settings.embedding_model}")
        
        # Initialize document processor with filtering
        doc_processor = DocumentProcessor(embeddings, settings)
        print("✅ Document processor initialized with procedural text filtering")
        
        # Process all PDFs with new filtering
        pdf_dir = Path(settings.pdf_data_path)
        if not pdf_dir.exists():
            print(f"❌ PDF directory not found: {pdf_dir}")
            return False
            
        pdf_files = list(pdf_dir.glob("*.pdf"))
        print(f"📚 Found {len(pdf_files)} PDF files to process")
        
        all_documents = []
        for pdf_file in pdf_files:
            print(f"\n📖 Processing: {pdf_file.name}")
            try:
                documents = doc_processor.process_single_pdf(str(pdf_file))
                all_documents.extend(documents)
                print(f"   ✅ Generated {len(documents)} filtered chunks")
            except Exception as e:
                print(f"   ❌ Error processing {pdf_file.name}: {e}")
                continue
        
        print(f"\n📊 TOTAL: {len(all_documents)} document chunks generated (after filtering)")
        
        if not all_documents:
            print("❌ No documents processed successfully")
            return False
        
        # Convert to LangChain documents
        from langchain_core.documents import Document
        langchain_docs = []
        for doc_data in all_documents:
            doc = Document(
                page_content=doc_data['page_content'],
                metadata=doc_data['metadata']
            )
            langchain_docs.append(doc)
        
        print(f"✅ Converted to {len(langchain_docs)} LangChain documents")
        
        # Force recreate vector store to apply filtering
        print("\n🗄️  RECREATING VECTOR DATABASE...")
        vector_service = VectorStoreManager.initialize(embeddings, settings, doc_processor)
        
        # Delete existing collection first to handle dimension mismatch
        try:
            vector_service.qdrant_client.delete_collection(collection_name=settings.vector_collection_name)
            print(f"🗑️  Deleted existing collection: {settings.vector_collection_name}")
        except Exception as e:
            print(f"ℹ️  Collection deletion: {e}")
        
        # Initialize with new filtered documents
        success = vector_service.initialize_from_documents(langchain_docs)
        
        if success:
            print("✅ Vector database successfully rebuilt with filtered documents!")
            print("🎉 Procedural text chunks have been eliminated")
            return True
        else:
            print("❌ Failed to rebuild vector database")
            return False
            
    except Exception as e:
        print(f"❌ Error rebuilding vector database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting vector database rebuild...")
    
    # Run the rebuild
    success = asyncio.run(rebuild_vector_database())
    
    if success:
        print("\n🎉 SUCCESS! Vector database rebuilt with procedural text filtering")
        print("💡 Investigation reports should now be coherent without raw fragments")
    else:
        print("\n❌ FAILED! Vector database rebuild unsuccessful")
        sys.exit(1)