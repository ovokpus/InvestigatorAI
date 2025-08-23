"""
Logging middleware for FastAPI to track requests and responses
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
from api.utils.logging_config import get_logger, log_api_request


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses"""
    
    def __init__(self, app, exclude_paths: list = None):
        super().__init__(app)
        self.logger = get_logger(__name__)
        self.exclude_paths = exclude_paths or ["/health", "/docs", "/openapi.json", "/favicon.ico"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details"""
        
        # Skip logging for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # Generate request ID
        request_id = str(uuid.uuid4())[:8]
        
        # Start timing
        start_time = time.time()
        
        # Log incoming request
        self.logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra={
                'request_id': request_id,
                'method': request.method,
                'path': request.url.path,
                'query_params': str(request.query_params),
                'client_ip': request.client.host if request.client else 'unknown',
                'user_agent': request.headers.get('user-agent', 'unknown')
            }
        )
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response
            log_api_request(
                self.logger,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                request_id=request_id
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Calculate duration for error case
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            self.logger.error(
                f"Request failed: {request.method} {request.url.path} - {str(e)}",
                extra={
                    'request_id': request_id,
                    'method': request.method,
                    'path': request.url.path,
                    'duration_ms': duration_ms,
                    'error': str(e)
                },
                exc_info=True
            )
            
            raise


class StreamingLoggingMiddleware(BaseHTTPMiddleware):
    """Special middleware for streaming responses"""
    
    def __init__(self, app):
        super().__init__(app)
        self.logger = get_logger(__name__)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle streaming responses with proper logging"""
        
        # Only handle streaming endpoints
        if not request.url.path.endswith('/stream'):
            return await call_next(request)
        
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        
        self.logger.info(
            f"Starting streaming request: {request.method} {request.url.path}",
            extra={'request_id': request_id}
        )
        
        try:
            response = await call_next(request)
            
            if isinstance(response, StreamingResponse):
                # Wrap the streaming response to log completion
                original_stream = response.body_iterator
                
                async def logged_stream():
                    chunk_count = 0
                    try:
                        async for chunk in original_stream:
                            chunk_count += 1
                            yield chunk
                        
                        duration_ms = (time.time() - start_time) * 1000
                        self.logger.info(
                            f"Streaming completed: {chunk_count} chunks in {duration_ms:.2f}ms",
                            extra={
                                'request_id': request_id,
                                'chunk_count': chunk_count,
                                'duration_ms': duration_ms
                            }
                        )
                    except Exception as e:
                        self.logger.error(
                            f"Streaming failed: {str(e)}",
                            extra={'request_id': request_id},
                            exc_info=True
                        )
                        raise
                
                response.body_iterator = logged_stream()
            
            response.headers["X-Request-ID"] = request_id
            return response
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.error(
                f"Streaming request failed: {str(e)}",
                extra={
                    'request_id': request_id,
                    'duration_ms': duration_ms
                },
                exc_info=True
            )
            raise
