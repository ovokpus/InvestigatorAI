"""
Comprehensive logging configuration for InvestigatorAI API
Provides structured logging with different levels and formatters
"""

import logging
import logging.config
import sys
from datetime import datetime
from typing import Dict, Any
import json
import os
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        if hasattr(record, 'investigation_id'):
            log_entry["investigation_id"] = record.investigation_id
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        if hasattr(record, 'duration_ms'):
            log_entry["duration_ms"] = record.duration_ms
        
        return json.dumps(log_entry)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors"""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Create formatted message
        formatted = f"{color}[{timestamp}] {record.levelname:8} {record.name:20} | {record.getMessage()}{reset}"
        
        # Add location info for debug level
        if record.levelno == logging.DEBUG:
            formatted += f" ({record.filename}:{record.lineno})"
        
        return formatted


def setup_logging(
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_file_path: str = "logs/investigator_ai.log",
    json_logging: bool = False,
    enable_performance_logging: bool = True
) -> None:
    """
    Setup comprehensive logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file
        log_file_path: Path to log file
        json_logging: Whether to use JSON formatting for file logs
        enable_performance_logging: Whether to enable performance logging
    """
    
    # Create logs directory if it doesn't exist
    if log_to_file:
        log_dir = Path(log_file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(ColoredFormatter())
    root_logger.addHandler(console_handler)
    
    # File handler if enabled
    if log_to_file:
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        
        if json_logging:
            file_handler.setFormatter(JSONFormatter())
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s | %(filename)s:%(lineno)d'
            )
            file_handler.setFormatter(file_formatter)
        
        root_logger.addHandler(file_handler)
    
    # Performance logger if enabled
    if enable_performance_logging:
        perf_logger = logging.getLogger('performance')
        perf_handler = logging.FileHandler('logs/performance.log', encoding='utf-8')
        perf_handler.setFormatter(JSONFormatter())
        perf_logger.addHandler(perf_handler)
        perf_logger.setLevel(logging.INFO)
        perf_logger.propagate = False  # Don't propagate to root logger
    
    # Set specific logger levels
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('langchain').setLevel(logging.INFO)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {log_level}, File: {log_to_file}, JSON: {json_logging}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name"""
    return logging.getLogger(name)


def log_performance(logger: logging.Logger, operation: str, duration_ms: float, **kwargs) -> None:
    """Log performance metrics"""
    perf_logger = logging.getLogger('performance')
    perf_logger.info(
        f"Performance: {operation}",
        extra={
            'operation': operation,
            'duration_ms': duration_ms,
            **kwargs
        }
    )


def log_investigation_event(
    logger: logging.Logger, 
    event: str, 
    investigation_id: str, 
    **kwargs
) -> None:
    """Log investigation-specific events"""
    logger.info(
        f"Investigation Event: {event}",
        extra={
            'investigation_id': investigation_id,
            'event': event,
            **kwargs
        }
    )


def log_api_request(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    request_id: str = None,
    **kwargs
) -> None:
    """Log API request details"""
    logger.info(
        f"{method} {path} - {status_code} ({duration_ms:.2f}ms)",
        extra={
            'method': method,
            'path': path,
            'status_code': status_code,
            'duration_ms': duration_ms,
            'request_id': request_id,
            **kwargs
        }
    )
