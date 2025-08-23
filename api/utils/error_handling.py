"""Error Handling Utilities"""

import logging
import openai
from typing import Any

logger = logging.getLogger(__name__)

def serialize_langchain_objects(obj: Any) -> Any:
    """Custom serializer for LangChain objects"""
    from langchain_core.messages import BaseMessage, AIMessage, ToolMessage, HumanMessage, SystemMessage
    
    if isinstance(obj, BaseMessage):
        # Serialize LangChain messages to dict format
        serialized = {
            "content": obj.content,
            "type": obj.__class__.__name__,
            "name": getattr(obj, 'name', None),
        }
        
        # Preserve tool calls for AIMessage
        if hasattr(obj, 'tool_calls') and obj.tool_calls:
            serialized["tool_calls"] = obj.tool_calls
        
        # Preserve tool_call_id for ToolMessage
        if hasattr(obj, 'tool_call_id') and obj.tool_call_id:
            serialized["tool_call_id"] = obj.tool_call_id
            
        return serialized
    
    elif isinstance(obj, list):
        return [serialize_langchain_objects(item) for item in obj]
    
    elif isinstance(obj, dict):
        return {key: serialize_langchain_objects(value) for key, value in obj.items()}
    
    else:
        # Return object as-is for basic types
        return obj

def handle_openai_error(e: Exception) -> tuple[int, str]:
    """Handle OpenAI API errors gracefully"""
    if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
        status_code = e.response.status_code
        
        if status_code == 400:
            error_message = str(e)
            if "max_tokens" in error_message.lower():
                return 413, "Investigation response too long. The AI generated more content than the current token limit allows. Please try a simpler investigation or contact support."
            elif "rate limit" in error_message.lower():
                return 429, "API rate limit exceeded. Please wait a moment and try again."
            else:
                return 400, f"Invalid request to AI service: {error_message}"
        elif status_code == 401:
            return 401, "AI service authentication failed. Please check API key configuration."
        elif status_code == 429:
            return 429, "AI service rate limit exceeded. Please wait a moment and try again."
        elif status_code >= 500:
            return 503, "AI service temporarily unavailable. Please try again in a few moments."
    
    # Handle generic OpenAI errors
    error_str = str(e).lower()
    if "max_tokens" in error_str or "token limit" in error_str:
        return 413, "Investigation response too long. The AI analysis exceeded the maximum allowed length. Please try with a simpler transaction description."
    elif "rate limit" in error_str:
        return 429, "Too many requests. Please wait a moment before trying again."
    elif "api key" in error_str or "authentication" in error_str:
        return 401, "AI service authentication error. Please contact support."
    
    return 500, f"AI service error: {str(e)}"
