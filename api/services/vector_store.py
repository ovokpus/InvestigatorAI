"""Vector database service using Qdrant"""
from typing import List, Optional
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from ..core.config import Settings
from ..services.document_processor import DocumentProcessor
from ..models.schemas import VectorSearchResult, DocumentMetadata

class VectorStoreService:
    """Service for managing vector database operations"""
    
    def __init__(self, embeddings: OpenAIEmbeddings, settings: Settings):
        self.embeddings = embeddings
        self.settings = settings
        self.vector_store: Optional[QdrantVectorStore] = None
        self.is_initialized = False
    
    def initialize_from_documents(self, documents: List[Document]) -> bool:
        """Initialize vector store from processed documents"""
        try:
            print("🗄️ Setting up Qdrant vector database...")
            
            # Create vector store using QdrantVectorStore.from_documents
            self.vector_store = QdrantVectorStore.from_documents(
                documents=documents,
                embedding=self.embeddings,
                location=":memory:",  # In-memory for development
                collection_name=self.settings.vector_collection_name
            )
            
            self.is_initialized = True
            print(f"✅ Vector database created with {len(documents)} document chunks")
            
            # Test the vector store
            self._test_vector_store()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize vector store: {e}")
            return False
    
    def _test_vector_store(self) -> None:
        """Test the vector store with a sample query"""
        if not self.vector_store:
            return
        
        test_query = "suspicious activity report requirements"
        test_results = self.vector_store.similarity_search(test_query, k=3)
        
        print(f"\n🧪 Test search for '{test_query}':")
        for i, result in enumerate(test_results, 1):
            filename = result.metadata.get('filename', 'Unknown')
            category = result.metadata.get('content_category', 'unknown')
            preview = result.page_content[:100] + "..." if len(result.page_content) > 100 else result.page_content
            print(f"   {i}. {filename} ({category})")
            print(f"      {preview}")
    
    def search(self, query: str, k: int = 5) -> List[VectorSearchResult]:
        """Search the vector database"""
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        try:
            results = self.vector_store.similarity_search(query, k=k)
            
            search_results = []
            for result in results:
                metadata = DocumentMetadata(
                    filename=result.metadata.get('filename', 'Unknown'),
                    content_category=result.metadata.get('content_category', 'unknown'),
                    source_type=result.metadata.get('source_type', 'unknown'),
                    document_type=result.metadata.get('document_type', 'unknown'),
                    last_updated=result.metadata.get('last_updated')
                )
                
                search_results.append(VectorSearchResult(
                    content=result.page_content,
                    metadata=metadata
                ))
            
            return search_results
            
        except Exception as e:
            print(f"❌ Vector search failed: {e}")
            return []
    
    def search_with_scores(self, query: str, k: int = 5) -> List[VectorSearchResult]:
        """Search the vector database with similarity scores"""
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            
            search_results = []
            for result, score in results:
                metadata = DocumentMetadata(
                    filename=result.metadata.get('filename', 'Unknown'),
                    content_category=result.metadata.get('content_category', 'unknown'),
                    source_type=result.metadata.get('source_type', 'unknown'),
                    document_type=result.metadata.get('document_type', 'unknown'),
                    last_updated=result.metadata.get('last_updated')
                )
                
                search_results.append(VectorSearchResult(
                    content=result.page_content,
                    metadata=metadata,
                    similarity_score=score
                ))
            
            return search_results
            
        except Exception as e:
            print(f"❌ Vector search with scores failed: {e}")
            return []

class VectorStoreManager:
    """Singleton manager for vector store service"""
    
    _instance: Optional[VectorStoreService] = None
    
    @classmethod
    def initialize(cls, embeddings: OpenAIEmbeddings, settings: Settings, document_processor: DocumentProcessor) -> VectorStoreService:
        """Initialize the vector store manager"""
        if cls._instance is None:
            cls._instance = VectorStoreService(embeddings, settings)
            
            # Process documents and initialize vector store
            documents = document_processor.process_all_pdfs()
            if documents:
                langchain_docs = document_processor.get_langchain_documents()
                cls._instance.initialize_from_documents(langchain_docs)
            else:
                print("❌ No documents available for vector store initialization")
        
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> Optional[VectorStoreService]:
        """Get the vector store service instance"""
        return cls._instance