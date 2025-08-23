"""Vector database service using Qdrant with BM25 optimization"""
from typing import List, Optional
import time
import logging
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from qdrant_client import QdrantClient
from qdrant_client.http import models

logger = logging.getLogger(__name__)

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
        logger.info("🗄️  Initializing VectorStoreService")
        logger.info(f"   📊 Embedding Model: {type(embeddings).__name__}")
        logger.info(f"   🎯 Qdrant Host: {settings.qdrant_host}:{settings.qdrant_port}")
        logger.info(f"   📦 Collection: {settings.vector_collection_name}")
        logger.info(f"   🔍 BM25 Enabled: {settings.bm25_enabled}")
        logger.info(f"   📈 Performance Logging: {settings.enable_performance_logging}")
        
        self.embeddings = embeddings
        self.settings = settings
        self.vector_store: Optional[QdrantVectorStore] = None
        self.qdrant_client: Optional[QdrantClient] = None
        self.bm25_retriever: Optional[BM25Retriever] = None
        self.documents: List[Document] = []  # Store for BM25 initialization
        self.cache_service = get_cache_service()
        self.is_initialized = False
        
        logger.info("🔗 Setting up Qdrant client connection...")
        self._setup_qdrant_client()
        logger.info("✅ VectorStoreService initialization complete")
    
    def _setup_qdrant_client(self):
        """Setup Qdrant client for containerized deployment"""
        logger.info(f"🔗 Connecting to Qdrant database...")
        logger.info(f"   🎯 Host: {self.settings.qdrant_host}:{self.settings.qdrant_port}")
        logger.info(f"   🔐 API Key: {'✅ Set' if self.settings.qdrant_api_key else '❌ Not set'}")
        logger.info(f"   ⏰ Timeout: 30s")
        
        try:
            start_time = time.time()
            
            self.qdrant_client = QdrantClient(
                host=self.settings.qdrant_host,
                port=self.settings.qdrant_port,
                api_key=self.settings.qdrant_api_key if self.settings.qdrant_api_key else None,
                timeout=30
            )
            
            # Test connection
            logger.info("🔍 Testing Qdrant connection...")
            collections = self.qdrant_client.get_collections()
            
            connection_time = (time.time() - start_time) * 1000
            logger.info(f"✅ Connected to Qdrant successfully in {connection_time:.1f}ms")
            logger.info(f"   📋 Available collections: {len(collections.collections)}")
            
            for collection in collections.collections:
                logger.debug(f"   📦 Collection: {collection.name}")
                
        except Exception as e:
            logger.error(f"❌ Qdrant connection failed: {e}")
            logger.exception(f"   🔍 Connection error details:")
            self.qdrant_client = None
    
    def initialize_from_documents(self, documents: List[Document]) -> bool:
        """Initialize vector store and BM25 retriever from processed documents"""
        logger.info("🗄️  Initializing vector store and BM25 retriever...")
        logger.info(f"   📄 Document count: {len(documents)}")
        logger.info(f"   🔍 BM25 enabled: {self.settings.bm25_enabled}")
        
        try:
            if not self.qdrant_client:
                logger.error("❌ Qdrant client not available - cannot initialize vector store")
                return False
            
            # Store documents for BM25 retriever
            logger.info("📝 Storing documents for BM25 initialization...")
            self.documents = documents
            
            # Check if collection already exists
            logger.info(f"🔍 Checking for existing collection: {self.settings.vector_collection_name}")
            try:
                collection_info = self.qdrant_client.get_collection(self.settings.vector_collection_name)
                points_count = collection_info.points_count
                logger.info(f"📋 Collection '{self.settings.vector_collection_name}' exists with {points_count} points")
                
                # Create vector store using existing collection
                logger.info("🔗 Connecting to existing collection...")
                self.vector_store = QdrantVectorStore(
                    client=self.qdrant_client,
                    collection_name=self.settings.vector_collection_name,
                    embeddings=self.embeddings
                )
                logger.info("   ✅ Connected to existing vector store")
                
            except Exception as e:
                # Collection doesn't exist, create it
                logger.info(f"📋 Collection not found, creating new collection: {self.settings.vector_collection_name}")
                logger.debug(f"   Collection check error: {e}")
                
                # Create vector store using containerized Qdrant
                self.vector_store = QdrantVectorStore.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    url=f"http://{self.settings.qdrant_host}:{self.settings.qdrant_port}",
                    collection_name=self.settings.vector_collection_name,
                    force_recreate=False  # Don't recreate if exists
                )
                
                logger.info(f"Vector database created with {len(documents)} document chunks")
            
            # Initialize BM25 retriever for fast sparse search (if enabled)
            if self.settings.bm25_enabled:
                logger.info("Initializing BM25 retriever for optimized search...")
                self.bm25_retriever = BM25Retriever.from_documents(documents)
                self.bm25_retriever.k = 5  # Default k value
                logger.info(f"BM25 retriever initialized with {len(documents)} documents")
            else:
                logger.info("BM25 retriever disabled in configuration, using dense search only")
            
            self.is_initialized = True
            
            # Test retrievers
            self._test_vector_store()
            if self.settings.bm25_enabled:
                self._test_bm25_retriever()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
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
        query_preview = query[:50] + "..." if len(query) > 50 else query
        logger.info(f"🔍 Vector search initiated - Query: '{query_preview}', k={k}, method={method}")
        
        if not self.vector_store:
            logger.error("❌ Vector store not initialized - cannot perform search")
            raise ValueError("Vector store not initialized")
        
        # Use configured default method if none specified
        if method is None:
            method = self.settings.default_retrieval_method
            logger.debug(f"   Using default retrieval method: {method}")
        
        # Check if BM25 is enabled in config
        original_method = method
        if method in ["auto", "bm25"] and not self.settings.bm25_enabled:
            method = "dense"
            logger.warning(f"ℹ️  BM25 disabled in config, switching from '{original_method}' to 'dense' search")
        
        # Try cache first
        cache_key = f"{query}_{k}_{method}"
        logger.debug(f"🔍 Checking cache with key: {cache_key[:100]}...")
        cached_results = self.cache_service.get_cached_document_search(cache_key)
        if cached_results:
            logger.info(f"⚡ Cache HIT - Returning {len(cached_results)} cached results")
            return [VectorSearchResult(**result) for result in cached_results]
        
        logger.debug("🔍 Cache MISS - Performing fresh search")
        start_time = time.time()
        search_results = []
        method_used = None
        fallback_used = False
        
        try:
            # Auto routing: BM25 primary (2.2ms, 0.953 quality) with dense fallback
            if method == "auto" or method == "bm25":
                logger.info(f"🚀 Attempting BM25 search (target: ~2.2ms, 0.953 quality)")
                search_results = self._bm25_search(query, k)
                method_used = "BM25"
                
                # Fallback to dense if BM25 fails or returns insufficient results
                if not search_results and method == "auto":
                    logger.warning("🔄 BM25 search failed/empty, falling back to dense vector search...")
                    fallback_start = time.time()
                    search_results = self._dense_search(query, k)
                    fallback_time = (time.time() - fallback_start) * 1000
                    method_used = "Dense (fallback)"
                    fallback_used = True
                    logger.info(f"   🔄 Fallback to dense completed in {fallback_time:.1f}ms")
                    
            elif method == "dense":
                logger.info(f"🎯 Using dense vector search (expected: ~551ms)")
                search_results = self._dense_search(query, k)
                method_used = "Dense"
            else:
                # Default to BM25 for unknown methods (if enabled)
                if self.settings.bm25_enabled:
                    logger.info(f"❓ Unknown method '{method}', defaulting to BM25")
                    search_results = self._bm25_search(query, k)
                    method_used = "BM25 (default)"
                else:
                    logger.info(f"❓ Unknown method '{method}', defaulting to dense (BM25 disabled)")
                    search_results = self._dense_search(query, k)
                    method_used = "Dense (default)"
            
            # Performance logging and analysis
            elapsed_ms = (time.time() - start_time) * 1000
            result_count = len(search_results)
            
            # Log performance with context
            if self.settings.enable_performance_logging or elapsed_ms > 100:  # Always log slow searches
                performance_status = "⚡" if elapsed_ms < 10 else "🐌" if elapsed_ms > 500 else "⏱️"
                logger.info(f"{performance_status} {method_used} search completed in {elapsed_ms:.1f}ms")
                logger.info(f"   📊 Results: {result_count}/{k} requested")
                logger.info(f"   🎯 Method: {original_method} → {method_used}")
                
                if fallback_used:
                    logger.info(f"   🔄 Fallback: BM25 → Dense")
                
                # Performance analysis
                if method_used.startswith("BM25") and elapsed_ms > 10:
                    logger.warning(f"   ⚠️  BM25 slower than expected (target: ~2.2ms, actual: {elapsed_ms:.1f}ms)")
                elif method_used.startswith("Dense") and elapsed_ms > 600:
                    logger.warning(f"   ⚠️  Dense search slower than expected (baseline: ~551ms, actual: {elapsed_ms:.1f}ms)")
            
            # Cache results for 30 minutes
            if search_results:
                logger.debug(f"💾 Caching {result_count} search results (TTL: 30min)")
                cache_data = [result.dict() for result in search_results]
                self.cache_service.cache_document_search(cache_key, cache_data, ttl=1800)
            else:
                logger.warning(f"❌ No results found for query: '{query_preview}'")
            
            logger.info(f"✅ Vector search completed - {result_count} results in {elapsed_ms:.1f}ms using {method_used}")
            return search_results
            
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(f"❌ Vector search failed after {elapsed_ms:.1f}ms")
            logger.error(f"   🚨 Error: {e}")
            logger.error(f"   🔍 Query: '{query_preview}'")
            logger.error(f"   ⚙️  Method: {method}")
            logger.exception(f"   📋 Full exception details:")
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
    
    @classmethod
    def connect_existing(cls, embeddings: OpenAIEmbeddings, settings: Settings) -> Optional[VectorStoreService]:
        """Connect to existing vector store without processing documents"""
        logger.info("🔗 Connecting to existing vector store...")
        
        if cls._instance is None:
            cls._instance = VectorStoreService(embeddings, settings)
            
            try:
                # Check if collection exists
                if cls._instance.qdrant_client:
                    collection_info = cls._instance.qdrant_client.get_collection(settings.vector_collection_name)
                    points_count = collection_info.points_count
                    
                    if points_count > 0:
                        logger.info(f"✅ Found existing collection with {points_count} documents")
                        
                        # Connect to existing vector store
                        cls._instance.vector_store = QdrantVectorStore(
                            client=cls._instance.qdrant_client,
                            collection_name=settings.vector_collection_name,
                            embedding=embeddings
                        )
                        
                        # Initialize BM25 if enabled (will need documents)
                        if settings.bm25_enabled:
                            logger.info("ℹ️  BM25 retriever will be initialized on first search")
                        
                        cls._instance.is_initialized = True
                        logger.info("✅ Successfully connected to existing vector store")
                    else:
                        logger.warning("⚠️  Collection exists but is empty")
                        
                else:
                    logger.error("❌ Qdrant client not available")
                    
            except Exception as e:
                logger.warning(f"⚠️  Could not connect to existing vector store: {e}")
                logger.info("💡 This is normal if the init service hasn't run yet")
        
        return cls._instance