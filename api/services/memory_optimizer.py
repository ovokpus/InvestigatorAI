"""Memory Optimization Service

This service provides memory management capabilities for long-running investigations,
preventing memory leaks and optimizing resource usage.
"""

import gc
import logging
import sys
import psutil
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MemoryMetrics:
    """Memory usage metrics"""
    total_memory_mb: float
    used_memory_mb: float
    available_memory_mb: float
    cpu_percent: float
    process_memory_mb: float
    timestamp: datetime


class MemoryOptimizer:
    """Service for optimizing memory usage during investigations"""
    
    def __init__(self, max_memory_mb: int = 1024):
        self.max_memory_mb = max_memory_mb
        self.cleanup_threshold = 0.8  # Clean up when 80% memory used
        self.large_content_threshold = 50000  # 50KB+ content gets truncated
        
        logger.info(f"🧠 Memory Optimizer initialized - Max memory: {max_memory_mb}MB")
    
    def get_memory_metrics(self) -> MemoryMetrics:
        """Get current memory usage metrics"""
        try:
            # System memory
            memory = psutil.virtual_memory()
            
            # Process memory
            process = psutil.Process(os.getpid())
            process_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            return MemoryMetrics(
                total_memory_mb=memory.total / 1024 / 1024,
                used_memory_mb=memory.used / 1024 / 1024, 
                available_memory_mb=memory.available / 1024 / 1024,
                cpu_percent=psutil.cpu_percent(),
                process_memory_mb=process_memory,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.warning(f"⚠️ Failed to get memory metrics: {e}")
            return MemoryMetrics(0, 0, 0, 0, 0, datetime.now())
    
    def should_cleanup(self) -> bool:
        """Check if memory cleanup is needed"""
        metrics = self.get_memory_metrics()
        
        # Check if process is using too much memory
        if metrics.process_memory_mb > self.max_memory_mb:
            logger.warning(f"🚨 Process memory ({metrics.process_memory_mb:.1f}MB) exceeds limit ({self.max_memory_mb}MB)")
            return True
        
        # Check if system memory is low
        memory_usage_ratio = metrics.used_memory_mb / metrics.total_memory_mb
        if memory_usage_ratio > self.cleanup_threshold:
            logger.warning(f"🚨 System memory usage ({memory_usage_ratio:.1%}) exceeds threshold ({self.cleanup_threshold:.1%})")
            return True
        
        return False
    
    def cleanup_investigation_data(self, investigation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean up investigation data to reduce memory usage"""
        logger.info("🧹 Starting investigation data cleanup")
        
        cleaned_data = {}
        total_saved_bytes = 0
        
        for key, value in investigation_data.items():
            if isinstance(value, str):
                # Truncate large strings
                if len(value) > self.large_content_threshold:
                    original_size = len(value)
                    truncated = value[:self.large_content_threshold] + f"... [TRUNCATED: {original_size - self.large_content_threshold} chars removed for memory optimization]"
                    cleaned_data[key] = truncated
                    total_saved_bytes += original_size - len(truncated)
                    logger.debug(f"   📝 Truncated {key}: {original_size} → {len(truncated)} chars")
                else:
                    cleaned_data[key] = value
                    
            elif isinstance(value, dict):
                # Recursively clean nested dictionaries
                cleaned_data[key] = self.cleanup_investigation_data(value)
                
            elif isinstance(value, list):
                # Clean lists but limit size
                if len(value) > 100:  # Limit lists to 100 items
                    cleaned_data[key] = value[:100]
                    logger.debug(f"   📋 Truncated list {key}: {len(value)} → 100 items")
                else:
                    cleaned_data[key] = value
                    
            else:
                # Keep other data types as-is
                cleaned_data[key] = value
        
        if total_saved_bytes > 0:
            logger.info(f"✅ Memory cleanup completed - Saved {total_saved_bytes / 1024:.1f}KB")
        
        return cleaned_data
    
    def cleanup_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean up message list to reduce memory usage"""
        logger.info(f"📨 Cleaning up {len(messages)} messages")
        
        cleaned_messages = []
        total_content_size = 0
        
        for msg in messages:
            if isinstance(msg, dict):
                cleaned_msg = msg.copy()
                
                # Truncate large message content
                if "content" in cleaned_msg and isinstance(cleaned_msg["content"], str):
                    content = cleaned_msg["content"]
                    total_content_size += len(content)
                    
                    if len(content) > self.large_content_threshold:
                        cleaned_msg["content"] = content[:self.large_content_threshold] + "... [TRUNCATED for memory]"
                
                # Remove unnecessary metadata
                for key in ["raw_content", "full_results", "intermediate_steps"]:
                    if key in cleaned_msg:
                        del cleaned_msg[key]
                
                cleaned_messages.append(cleaned_msg)
            else:
                cleaned_messages.append(msg)
        
        logger.info(f"✅ Message cleanup completed - Total content: {total_content_size / 1024:.1f}KB")
        return cleaned_messages
    
    def force_garbage_collection(self):
        """Force garbage collection to free memory"""
        logger.info("🗑️ Forcing garbage collection")
        
        # Get memory before cleanup
        before_metrics = self.get_memory_metrics()
        
        # Force garbage collection
        collected = gc.collect()
        
        # Get memory after cleanup  
        after_metrics = self.get_memory_metrics()
        memory_freed = before_metrics.process_memory_mb - after_metrics.process_memory_mb
        
        logger.info(f"✅ Garbage collection completed")
        logger.info(f"   🗑️ Objects collected: {collected}")
        logger.info(f"   💾 Memory freed: {memory_freed:.1f}MB")
        logger.info(f"   📊 Process memory: {after_metrics.process_memory_mb:.1f}MB")
    
    def optimize_response_for_client(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize response data before sending to client"""
        logger.info("📤 Optimizing response for client")
        
        optimized = {}
        
        for key, value in response_data.items():
            if key == "full_results" and isinstance(value, dict):
                # Drastically reduce full_results size
                optimized[key] = {
                    "summary": "Investigation completed successfully",
                    "agents_completed": value.get("agents_completed", []),
                    "investigation_status": value.get("investigation_status", "completed"),
                    "message_count": len(value.get("messages", [])),
                    "note": "Full results truncated for performance - check logs for details"
                }
                
            elif key == "ragas_validated_messages":
                # Limit message history sent to client
                if isinstance(value, list) and len(value) > 10:
                    optimized[key] = value[-10:]  # Last 10 messages only
                else:
                    optimized[key] = value
                    
            else:
                optimized[key] = value
        
        # Calculate size reduction
        original_size = len(str(response_data))
        optimized_size = len(str(optimized))
        reduction_percent = (1 - optimized_size / original_size) * 100
        
        logger.info(f"✅ Response optimized: {original_size} → {optimized_size} chars ({reduction_percent:.1f}% reduction)")
        
        return optimized
    
    def log_memory_status(self, context: str = ""):
        """Log current memory status"""
        metrics = self.get_memory_metrics()
        
        logger.info(f"📊 Memory Status {context}")
        logger.info(f"   💾 Process Memory: {metrics.process_memory_mb:.1f}MB")
        logger.info(f"   🖥️ System Memory: {metrics.used_memory_mb:.1f}MB / {metrics.total_memory_mb:.1f}MB ({metrics.used_memory_mb/metrics.total_memory_mb:.1%})")
        logger.info(f"   🔋 CPU Usage: {metrics.cpu_percent:.1f}%")
        
        if self.should_cleanup():
            logger.warning("⚠️ Memory cleanup recommended")
    
    def create_memory_efficient_state(self, investigation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create memory-efficient version of investigation state"""
        logger.info("🎯 Creating memory-efficient investigation state")
        
        # Start with memory cleanup
        cleaned_data = self.cleanup_investigation_data(investigation_data)
        
        # Force garbage collection if needed
        if self.should_cleanup():
            self.force_garbage_collection()
        
        # Create lightweight state
        efficient_state = {
            "summary": {
                "investigation_id": cleaned_data.get("investigation_id", "unknown"),
                "status": cleaned_data.get("investigation_status", "unknown"),
                "completion_time": datetime.now().isoformat(),
                "memory_optimized": True
            },
            "results": {
                "risk_analysis": cleaned_data.get("risk_analysis", {}),
                "compliance_requirements": cleaned_data.get("compliance_requirements", []),
                "key_findings": cleaned_data.get("key_findings", [])
            },
            "performance": {
                "parallel_execution_time": cleaned_data.get("parallel_execution_time", 0),
                "memory_metrics": self.get_memory_metrics()
            }
        }
        
        logger.info("✅ Memory-efficient state created")
        return efficient_state


# Global memory optimizer instance
_memory_optimizer = None

def get_memory_optimizer() -> MemoryOptimizer:
    """Get global memory optimizer instance"""
    global _memory_optimizer
    if _memory_optimizer is None:
        _memory_optimizer = MemoryOptimizer()
    return _memory_optimizer
