"""Vector database service using Qdrant with BM25 optimization"""
from typing import List, Optional
import time
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from qdrant_client import QdrantClient
from qdrant_client.http import models

# LangSmith monitoring
try:
    from langsmith import traceable
    LANGSMITH_AVAILABLE = True
except ImportError:
    # Create no-op decorator if LangSmith is not installed
    def traceable(func):
        return func
    LANGSMITH_AVAILABLE = False

from ..core.config import Settings
from ..services.document_processor import DocumentProcessor
from ..services.cache_service import get_cache_service
from ..models.schemas import VectorSearchResult, DocumentMetadata

class VectorStoreService:
    """Service for managing vector database operations"""
    
    def __init__(self, embeddings: OpenAIEmbeddings, settings: Settings):
        self.embeddings = embeddings
        self.settings = settings
        self.vector_store: Optional[QdrantVectorStore] = None
        self.qdrant_client: Optional[QdrantClient] = None
        self.bm25_retriever: Optional[BM25Retriever] = None
        self.documents: List[Document] = []  # Store for BM25 initialization
        self.cache_service = get_cache_service()
        self.is_initialized = False
        self._setup_qdrant_client()
    
    def _setup_qdrant_client(self):
        """Setup Qdrant client for containerized deployment"""
        try:
            self.qdrant_client = QdrantClient(
                host=self.settings.qdrant_host,
                port=self.settings.qdrant_port,
                api_key=self.settings.qdrant_api_key if self.settings.qdrant_api_key else None,
                timeout=30
            )
            # Test connection
            collections = self.qdrant_client.get_collections()
            print(f"✅ Connected to Qdrant at {self.settings.qdrant_host}:{self.settings.qdrant_port}")
            print(f"📋 Available collections: {len(collections.collections)}")
        except Exception as e:
            print(f"⚠️ Qdrant connection failed: {e}")
            self.qdrant_client = None
    
    def initialize_from_documents(self, documents: List[Document]) -> bool:
        """Initialize vector store and BM25 retriever from processed documents"""
        try:
            print("🗄️ Setting up Qdrant vector database and BM25 retriever...")
            
            if not self.qdrant_client:
                print("❌ Qdrant client not available")
                return False
            
            # Store documents for BM25 retriever
            self.documents = documents
            
            # Check if collection already exists
            try:
                collection_info = self.qdrant_client.get_collection(self.settings.vector_collection_name)
                print(f"📋 Collection '{self.settings.vector_collection_name}' already exists with {collection_info.points_count} points")
                
                # Create vector store using existing collection
                self.vector_store = QdrantVectorStore(
                    client=self.qdrant_client,
                    collection_name=self.settings.vector_collection_name,
                    embeddings=self.embeddings
                )
                
            except Exception:
                # Collection doesn't exist, create it
                print(f"📋 Creating new collection '{self.settings.vector_collection_name}'")
                
                # Create vector store using containerized Qdrant
                self.vector_store = QdrantVectorStore.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    url=f"http://{self.settings.qdrant_host}:{self.settings.qdrant_port}",
                    collection_name=self.settings.vector_collection_name,
                    force_recreate=False  # Don't recreate if exists
                )
                
                print(f"✅ Vector database created with {len(documents)} document chunks")
            
            # Initialize BM25 retriever for fast sparse search (if enabled)
            if self.settings.bm25_enabled:
                print("🚀 Initializing BM25 retriever for optimized search...")
                self.bm25_retriever = BM25Retriever.from_documents(documents)
                self.bm25_retriever.k = 5  # Default k value
                print(f"✅ BM25 retriever initialized with {len(documents)} documents")
            else:
                print("ℹ️ BM25 retriever disabled in configuration, using dense search only")
            
            self.is_initialized = True
            
            # Test retrievers
            self._test_vector_store()
            if self.settings.bm25_enabled:
                self._test_bm25_retriever()
            
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
        
        print(f"\n🧪 Dense Vector Test for '{test_query}':")
        for i, result in enumerate(test_results, 1):
            filename = result.metadata.get('filename', 'Unknown')
            category = result.metadata.get('content_category', 'unknown')
            preview = result.page_content[:100] + "..." if len(result.page_content) > 100 else result.page_content
            print(f"   {i}. {filename} ({category})")
            print(f"      {preview}")
    
    def _test_bm25_retriever(self) -> None:
        """Test the BM25 retriever with a sample query"""
        if not self.bm25_retriever:
            return
        
        test_query = "suspicious activity report requirements"
        test_results = self.bm25_retriever.get_relevant_documents(test_query)
        
        print(f"\n🚀 BM25 Sparse Test for '{test_query}':")
        for i, result in enumerate(test_results[:3], 1):  # Limit to 3 for comparison
            filename = result.metadata.get('filename', 'Unknown')
            category = result.metadata.get('content_category', 'unknown')
            preview = result.page_content[:100] + "..." if len(result.page_content) > 100 else result.page_content
            print(f"   {i}. {filename} ({category})")
            print(f"      {preview}")
    
    @traceable(name="vector_store_search", tags=["search", "vector", "retrieval"])
    def search(self, query: str, k: int = 5, method: str = None) -> List[VectorSearchResult]:
        """
        Optimized search using BM25 primary with dense fallback
        Based on evaluation: BM25 = 2.2ms, 0.953 RAGAS vs Dense = 551ms, 0.800 RAGAS
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        # Use configured default method if none specified
        if method is None:
            method = self.settings.default_retrieval_method
        
        # Check if BM25 is enabled in config
        if method in ["auto", "bm25"] and not self.settings.bm25_enabled:
            method = "dense"
            if self.settings.enable_performance_logging:
                print("ℹ️ BM25 disabled in config, using dense search")
        
        # Try cache first
        cache_key = f"{query}_{k}_{method}"
        cached_results = self.cache_service.get_cached_document_search(cache_key)
        if cached_results:
            return [VectorSearchResult(**result) for result in cached_results]
        
        start_time = time.time()
        search_results = []
        
        try:
            # Auto routing: BM25 primary (2.2ms, 0.953 quality) with dense fallback
            if method == "auto" or method == "bm25":
                search_results = self._bm25_search(query, k)
                
                # Fallback to dense if BM25 fails or returns insufficient results
                if not search_results and method == "auto":
                    if self.settings.enable_performance_logging:
                        print("🔄 BM25 search failed, falling back to dense vector search...")
                    search_results = self._dense_search(query, k)
                    
            elif method == "dense":
                search_results = self._dense_search(query, k)
            else:
                # Default to BM25 for unknown methods (if enabled)
                if self.settings.bm25_enabled:
                    search_results = self._bm25_search(query, k)
                else:
                    search_results = self._dense_search(query, k)
            
            # Performance logging (configurable)
            if self.settings.enable_performance_logging:
                elapsed_ms = (time.time() - start_time) * 1000
                method_used = "BM25" if (method == "auto" or method == "bm25") and search_results else "Dense"
                print(f"⚡ {method_used} search completed in {elapsed_ms:.1f}ms")
            
            # Cache results for 30 minutes
            if search_results:
                cache_data = [result.dict() for result in search_results]
                self.cache_service.cache_document_search(cache_key, cache_data, ttl=1800)
            
            return search_results
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []
    
    @traceable(name="bm25_search", tags=["search", "bm25", "sparse"])
    def _bm25_search(self, query: str, k: int) -> List[VectorSearchResult]:
        """
        BM25 sparse search - optimized for speed and quality
        Performance: 2.2ms average, 0.953 RAGAS score
        """
        if not self.bm25_retriever:
            return []
        
        try:
            # Set k for this query
            self.bm25_retriever.k = k
            results = self.bm25_retriever.get_relevant_documents(query)
            
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
            print(f"❌ BM25 search failed: {e}")
            return []
    
    @traceable(name="dense_search", tags=["search", "dense", "vector"])
    def _dense_search(self, query: str, k: int) -> List[VectorSearchResult]:
        """
        Dense vector search - fallback method
        Performance: 551ms average, 0.800 RAGAS score
        """
        if not self.vector_store:
            return []
        
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
            print(f"❌ Dense search failed: {e}")
            return []
    
    def search_with_scores(self, query: str, k: int = 5, method: str = "auto") -> List[VectorSearchResult]:
        """
        Search with similarity scores - uses dense vector search since BM25 doesn't provide scores
        For performance-critical use cases without score requirements, use search() method
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
        
        start_time = time.time()
        
        try:
            # Note: BM25 doesn't provide similarity scores, so we use dense for scored results
            if method == "auto" or method == "dense":
                results = self.vector_store.similarity_search_with_score(query, k=k)
                method_used = "Dense (scores)"
            else:
                # Fallback to regular BM25 search without scores for other methods
                bm25_results = self._bm25_search(query, k)
                if self.settings.enable_performance_logging:
                    elapsed_ms = (time.time() - start_time) * 1000
                    print(f"⚡ BM25 search (no scores) completed in {elapsed_ms:.1f}ms")
                return bm25_results
            
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
            
            # Performance logging (configurable)
            if self.settings.enable_performance_logging:
                elapsed_ms = (time.time() - start_time) * 1000
                print(f"⚡ {method_used} search completed in {elapsed_ms:.1f}ms")
            
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