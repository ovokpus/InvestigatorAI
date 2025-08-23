"""Research State Management with Checkpointing

This module provides persistent state management for research operations,
enabling resumption of interrupted research and tracking of investigation progress.
"""

import asyncio
import json
import logging
import os
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

from .iterative_research import ResearchPlan, ResearchSection, ResearchFeedback

logger = logging.getLogger(__name__)


class ResearchStatus(Enum):
    """Research investigation status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ResearchCheckpoint:
    """Research checkpoint for state persistence"""
    research_id: str
    topic: str
    status: ResearchStatus
    plan: Optional[ResearchPlan] = None
    completed_sections: List[ResearchSection] = None
    current_section_index: int = 0
    total_sections: int = 0
    progress_percentage: float = 0.0
    created_at: datetime = None
    updated_at: datetime = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.completed_sections is None:
            self.completed_sections = []
        if self.metadata is None:
            self.metadata = {}


class ResearchStateManager:
    """Manage research state with persistent checkpointing"""
    
    def __init__(self, checkpoint_dir: str = "research_checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
        
        # In-memory cache for active research
        self._active_research: Dict[str, ResearchCheckpoint] = {}
        
        logger.info(f"🗃️ Initialized ResearchStateManager (checkpoint_dir: {self.checkpoint_dir})")
    
    def _get_checkpoint_path(self, research_id: str) -> Path:
        """Get file path for research checkpoint"""
        return self.checkpoint_dir / f"{research_id}.json"
    
    async def create_research_session(self, topic: str, plan: Optional[ResearchPlan] = None,
                                    metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new research session with unique ID"""
        research_id = f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(topic) % 10000:04d}"
        
        checkpoint = ResearchCheckpoint(
            research_id=research_id,
            topic=topic,
            status=ResearchStatus.PENDING,
            plan=plan,
            total_sections=len(plan.sections) if plan else 0,
            metadata=metadata or {}
        )
        
        # Save to cache and disk
        self._active_research[research_id] = checkpoint
        await self.save_checkpoint(checkpoint)
        
        logger.info(f"📝 Created research session: {research_id} for topic: {topic}")
        return research_id
    
    async def save_checkpoint(self, checkpoint: ResearchCheckpoint):
        """Save research checkpoint to disk"""
        checkpoint.updated_at = datetime.now()
        
        try:
            # Convert to serializable format
            checkpoint_data = asdict(checkpoint)
            
            # Handle datetime serialization
            for key, value in checkpoint_data.items():
                if isinstance(value, datetime):
                    checkpoint_data[key] = value.isoformat()
                elif key == "status":
                    checkpoint_data[key] = value.value if hasattr(value, 'value') else str(value)
            
            # Handle nested objects
            if checkpoint_data.get("plan"):
                plan_data = checkpoint_data["plan"]
                if hasattr(plan_data, '__dict__'):
                    checkpoint_data["plan"] = asdict(plan_data)
                if plan_data.get("created_at"):
                    checkpoint_data["plan"]["created_at"] = plan_data["created_at"].isoformat()
            
            checkpoint_path = self._get_checkpoint_path(checkpoint.research_id)
            
            # Write atomically using temporary file
            temp_path = checkpoint_path.with_suffix('.tmp')
            with open(temp_path, 'w') as f:
                json.dump(checkpoint_data, f, indent=2, default=str)
            
            temp_path.rename(checkpoint_path)
            
            # Update cache
            self._active_research[checkpoint.research_id] = checkpoint
            
            logger.debug(f"💾 Saved checkpoint for research: {checkpoint.research_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save checkpoint for {checkpoint.research_id}: {e}")
            raise
    
    async def load_checkpoint(self, research_id: str) -> Optional[ResearchCheckpoint]:
        """Load research checkpoint from disk"""
        # Check cache first
        if research_id in self._active_research:
            return self._active_research[research_id]
        
        checkpoint_path = self._get_checkpoint_path(research_id)
        
        if not checkpoint_path.exists():
            logger.warning(f"⚠️ No checkpoint found for research: {research_id}")
            return None
        
        try:
            with open(checkpoint_path, 'r') as f:
                data = json.load(f)
            
            # Convert datetime strings back to datetime objects
            if data.get("created_at"):
                data["created_at"] = datetime.fromisoformat(data["created_at"])
            if data.get("updated_at"):
                data["updated_at"] = datetime.fromisoformat(data["updated_at"])
            
            # Handle status enum
            if data.get("status"):
                data["status"] = ResearchStatus(data["status"])
            
            # Reconstruct nested objects
            if data.get("plan"):
                from .iterative_research import ResearchPlan, ResearchSection
                plan_data = data["plan"]
                
                if plan_data.get("created_at"):
                    plan_data["created_at"] = datetime.fromisoformat(plan_data["created_at"])
                
                sections = []
                for section_data in plan_data.get("sections", []):
                    section = ResearchSection(**section_data)
                    sections.append(section)
                
                plan_data["sections"] = sections
                data["plan"] = ResearchPlan(**plan_data)
            
            # Reconstruct completed sections
            if data.get("completed_sections"):
                from .iterative_research import ResearchSection
                completed_sections = []
                for section_data in data["completed_sections"]:
                    section = ResearchSection(**section_data)
                    completed_sections.append(section)
                data["completed_sections"] = completed_sections
            
            checkpoint = ResearchCheckpoint(**data)
            
            # Cache the loaded checkpoint
            self._active_research[research_id] = checkpoint
            
            logger.info(f"📂 Loaded checkpoint for research: {research_id}")
            return checkpoint
            
        except Exception as e:
            logger.error(f"❌ Failed to load checkpoint for {research_id}: {e}")
            return None
    
    async def update_research_progress(self, research_id: str, 
                                     completed_section: Optional[ResearchSection] = None,
                                     status: Optional[ResearchStatus] = None,
                                     error_message: Optional[str] = None):
        """Update research progress and save checkpoint"""
        checkpoint = await self.load_checkpoint(research_id)
        
        if not checkpoint:
            logger.error(f"❌ Cannot update progress - checkpoint not found: {research_id}")
            return
        
        # Update status
        if status:
            checkpoint.status = status
        
        # Add completed section
        if completed_section:
            checkpoint.completed_sections.append(completed_section)
            checkpoint.current_section_index = len(checkpoint.completed_sections)
            
            # Calculate progress percentage
            if checkpoint.total_sections > 0:
                checkpoint.progress_percentage = (len(checkpoint.completed_sections) / checkpoint.total_sections) * 100
        
        # Update error message
        if error_message:
            checkpoint.error_message = error_message
            checkpoint.status = ResearchStatus.FAILED
        
        # Auto-complete if all sections done
        if (checkpoint.plan and 
            len(checkpoint.completed_sections) >= len([s for s in checkpoint.plan.sections if s.research]) and
            checkpoint.status != ResearchStatus.FAILED):
            checkpoint.status = ResearchStatus.COMPLETED
            checkpoint.progress_percentage = 100.0
        
        await self.save_checkpoint(checkpoint)
        logger.info(f"📊 Updated progress for {research_id}: {checkpoint.progress_percentage:.1f}%")
    
    async def resume_research(self, research_id: str) -> Optional[ResearchCheckpoint]:
        """Resume interrupted research session"""
        checkpoint = await self.load_checkpoint(research_id)
        
        if not checkpoint:
            logger.error(f"❌ Cannot resume - research not found: {research_id}")
            return None
        
        if checkpoint.status == ResearchStatus.COMPLETED:
            logger.info(f"✅ Research already completed: {research_id}")
            return checkpoint
        
        if checkpoint.status == ResearchStatus.FAILED:
            logger.warning(f"⚠️ Resuming failed research: {research_id}")
        
        # Mark as in progress
        checkpoint.status = ResearchStatus.IN_PROGRESS
        await self.save_checkpoint(checkpoint)
        
        logger.info(f"🔄 Resumed research session: {research_id}")
        return checkpoint
    
    async def cancel_research(self, research_id: str):
        """Cancel an ongoing research session"""
        checkpoint = await self.load_checkpoint(research_id)
        
        if checkpoint:
            checkpoint.status = ResearchStatus.CANCELLED
            await self.save_checkpoint(checkpoint)
            logger.info(f"🛑 Cancelled research session: {research_id}")
    
    async def get_research_status(self, research_id: str) -> Dict[str, Any]:
        """Get current status of research session"""
        checkpoint = await self.load_checkpoint(research_id)
        
        if not checkpoint:
            return {"error": f"Research session not found: {research_id}"}
        
        return {
            "research_id": checkpoint.research_id,
            "topic": checkpoint.topic,
            "status": checkpoint.status.value,
            "progress_percentage": checkpoint.progress_percentage,
            "completed_sections": len(checkpoint.completed_sections),
            "total_sections": checkpoint.total_sections,
            "created_at": checkpoint.created_at.isoformat(),
            "updated_at": checkpoint.updated_at.isoformat(),
            "error_message": checkpoint.error_message
        }
    
    async def list_research_sessions(self, limit: int = 20, 
                                   status_filter: Optional[ResearchStatus] = None) -> List[Dict[str, Any]]:
        """List recent research sessions"""
        sessions = []
        
        # Get all checkpoint files
        checkpoint_files = list(self.checkpoint_dir.glob("*.json"))
        checkpoint_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        for checkpoint_file in checkpoint_files[:limit]:
            try:
                research_id = checkpoint_file.stem
                checkpoint = await self.load_checkpoint(research_id)
                
                if checkpoint and (not status_filter or checkpoint.status == status_filter):
                    session_info = {
                        "research_id": checkpoint.research_id,
                        "topic": checkpoint.topic,
                        "status": checkpoint.status.value,
                        "progress_percentage": checkpoint.progress_percentage,
                        "created_at": checkpoint.created_at.isoformat(),
                        "updated_at": checkpoint.updated_at.isoformat()
                    }
                    sessions.append(session_info)
                    
            except Exception as e:
                logger.error(f"❌ Error loading session from {checkpoint_file}: {e}")
                continue
        
        return sessions
    
    async def cleanup_old_checkpoints(self, days_old: int = 30):
        """Clean up old checkpoint files"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        cleaned_count = 0
        
        for checkpoint_file in self.checkpoint_dir.glob("*.json"):
            try:
                file_mtime = datetime.fromtimestamp(checkpoint_file.stat().st_mtime)
                
                if file_mtime < cutoff_date:
                    # Load checkpoint to check if it's completed or can be safely deleted
                    research_id = checkpoint_file.stem
                    checkpoint = await self.load_checkpoint(research_id)
                    
                    if (checkpoint and 
                        checkpoint.status in [ResearchStatus.COMPLETED, ResearchStatus.FAILED, ResearchStatus.CANCELLED]):
                        checkpoint_file.unlink()
                        
                        # Remove from cache
                        if research_id in self._active_research:
                            del self._active_research[research_id]
                        
                        cleaned_count += 1
                        logger.debug(f"🗑️ Cleaned up old checkpoint: {research_id}")
                        
            except Exception as e:
                logger.error(f"❌ Error cleaning up {checkpoint_file}: {e}")
                continue
        
        logger.info(f"🧹 Cleaned up {cleaned_count} old research checkpoints")
        return cleaned_count
