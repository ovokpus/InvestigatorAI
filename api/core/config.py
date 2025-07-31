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
        
        # Model configurations
        self.embedding_model: str = "text-embedding-3-large"
        self.llm_model: str = "gpt-4"
        self.llm_temperature: float = 0
        
        # Vector database
        self.vector_collection_name: str = "regulatory_documents"
        
        # Document processing
        self.chunk_size: int = 1000
        self.chunk_overlap: int = 200
        self.pdf_data_path: str = "data/pdf_downloads"
        
        # Validate required API keys
        self._validate_api_keys()
    
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
        api_key=settings.openai_api_key
    )
    
    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openai_api_key
    )
    
    return llm, embeddings