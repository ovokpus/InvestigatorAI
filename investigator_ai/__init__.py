"""InvestigatorAI - Multi-agent fraud investigation system"""

__version__ = "0.1.0"
__author__ = "InvestigatorAI Team"

# Main exports for the package
from api.agents.multi_agent_system import FraudInvestigationSystem
from api.services.unified_investigation import UnifiedInvestigationService

__all__ = [
    "FraudInvestigationSystem",
    "UnifiedInvestigationService",
]
