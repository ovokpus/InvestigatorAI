"""Configuration management for InvestigatorAI"""
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

# Load environment variables
load_dotenv()

class Settings:
    """Application settings"""
    
    def __init__(self):
        # API Keys
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
        self.tavily_search_api_key: str = os.getenv("TAVILY_SEARCH_API_KEY", "")
        self.exchange_rate_api_key: str = os.getenv("EXCHANGE_RATE_API_KEY", "")
        self.langsmith_api_key: str = os.getenv("LANGSMITH_API_KEY", "")
        
        # Model configurations
        self.embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
        self.llm_model: str = os.getenv("LLM_MODEL", "gpt-4o")
        self.llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0"))
        self.llm_max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "15000"))  # Configurable via env var
        
        # Redis Cache Configuration
        self.redis_host: str = os.getenv("REDIS_HOST", "localhost")
        self.redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_db: int = int(os.getenv("REDIS_DB", "0"))
        self.redis_password: str = os.getenv("REDIS_PASSWORD", "")
        self.cache_enabled: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"
        
        # Qdrant Vector Database Configuration
        self.qdrant_host: str = os.getenv("QDRANT_HOST", "localhost")
        self.qdrant_port: int = int(os.getenv("QDRANT_PORT", "6333"))
        self.qdrant_grpc_port: int = int(os.getenv("QDRANT_GRPC_PORT", "6334"))
        self.qdrant_api_key: str = os.getenv("QDRANT_API_KEY", "")
        self.vector_collection_name: str = os.getenv("VECTOR_COLLECTION_NAME", "regulatory_documents")
        
        # Document processing
        self.chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
        self.chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))
        self.pdf_data_path: str = os.getenv("PDF_DATA_PATH", "data/pdf_downloads")
        
        # Performance settings
        self.max_concurrent_requests: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
        self.request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
        
        # Retrieval optimization settings
        self.default_retrieval_method: str = os.getenv("DEFAULT_RETRIEVAL_METHOD", "auto")  # auto, bm25, dense
        self.enable_performance_logging: bool = os.getenv("ENABLE_PERFORMANCE_LOGGING", "true").lower() == "true"
        self.bm25_enabled: bool = os.getenv("BM25_ENABLED", "true").lower() == "true"
        
        # LangSmith monitoring settings
        self.langsmith_project: str = os.getenv("LANGSMITH_PROJECT", "InvestigatorAI-Production")
        self.langsmith_tracing: bool = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
        self.langsmith_endpoint: str = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
        
        # Validate required API keys
        self._validate_api_keys()
        
        # Initialize LangSmith if configured
        self._setup_langsmith()
    
    def _validate_api_keys(self) -> None:
        """Validate that required API keys are present"""
        required_keys = {
            'OPENAI_API_KEY': self.openai_api_key,
            'TAVILY_SEARCH_API_KEY': self.tavily_search_api_key,
        }
        
        missing_keys = [key for key, value in required_keys.items() if not value]
        
        if missing_keys:
            raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")
    
    @property
    def api_keys_available(self) -> bool:
        """Check if all required API keys are available"""
        return bool(self.openai_api_key and self.tavily_search_api_key)
    
    @property
    def langsmith_available(self) -> bool:
        """Check if LangSmith is configured and available"""
        return bool(self.langsmith_api_key and self.langsmith_tracing)
    
    def _setup_langsmith(self) -> None:
        """Set up LangSmith environment variables if configured"""
        if self.langsmith_available:
            os.environ["LANGSMITH_API_KEY"] = self.langsmith_api_key
            os.environ["LANGSMITH_PROJECT"] = self.langsmith_project
            os.environ["LANGSMITH_TRACING"] = str(self.langsmith_tracing).lower()
            os.environ["LANGSMITH_ENDPOINT"] = self.langsmith_endpoint
            # Also set legacy LangChain project for compatibility
            os.environ["LANGCHAIN_PROJECT"] = self.langsmith_project

def get_settings() -> Settings:
    """Get application settings"""
    return Settings()

def initialize_llm_components(settings: Settings) -> tuple[ChatOpenAI, OpenAIEmbeddings]:
    """Initialize LLM and embedding models"""
    if not settings.api_keys_available:
        raise ValueError("Cannot initialize LLM components - API keys missing")
    
    llm = ChatOpenAI(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        api_key=settings.openai_api_key
    )
    
    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openai_api_key
    )
    
    return llm, embeddings