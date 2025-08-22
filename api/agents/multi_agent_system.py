"""Multi-agent system for fraud investigation using LangGraph - Modular Implementation"""

# Backward compatibility import - delegates to new modular system
from .fraud_investigation_system import FraudInvestigationSystem

# Re-export for backward compatibility
__all__ = ['FraudInvestigationSystem']