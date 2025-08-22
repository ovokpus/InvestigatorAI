"""LangGraph workflow builder for fraud investigation system"""
import logging
from typing import Dict, Any, Callable
from langgraph.graph import END, StateGraph
from langchain.agents import AgentExecutor

from ..models.schemas import FraudInvestigationState

logger = logging.getLogger(__name__)


class WorkflowBuilder:
    """Builder for creating LangGraph investigation workflows"""
    
    def __init__(self, agents: Dict[str, AgentExecutor]):
        self.agents = agents
        logger.info("🔄 WorkflowBuilder initialized")
    
    def build_investigation_workflow(
        self, 
        agent_nodes: Dict[str, Callable], 
        supervisor_node: Callable
    ) -> Any:
        """Build the complete LangGraph workflow with all nodes and routing"""
        logger.info("🔄 Building LangGraph workflow...")
        
        workflow = StateGraph(FraudInvestigationState)
        
        # Add supervisor node
        workflow.add_node("supervisor", supervisor_node)
        
        # Add agent nodes
        for agent_name, node_func in agent_nodes.items():
            workflow.add_node(agent_name, node_func)
        
        # Set up routing logic
        supervisor_router = self._create_supervisor_router()
        tool_router = self._create_tool_router()
        
        # Add conditional edges from supervisor
        workflow.add_conditional_edges(
            "supervisor",
            supervisor_router,
            {
                "regulatory_research": "regulatory_research",
                "evidence_collection": "evidence_collection",
                "compliance_check": "compliance_check", 
                "report_generation": "report_generation",
                END: END
            }
        )
        
        # Add edges from each tool back to supervisor
        for agent_name in agent_nodes.keys():
            workflow.add_conditional_edges(
                agent_name, 
                tool_router, 
                {"supervisor": "supervisor", END: END}
            )
        
        workflow.set_entry_point("supervisor")
        compiled_workflow = workflow.compile()
        
        logger.info("✅ Workflow graph built successfully")
        return compiled_workflow
    
    def _create_supervisor_router(self) -> Callable[[FraudInvestigationState], str]:
        """Create routing function from supervisor to agents"""
        def route_from_supervisor(state: FraudInvestigationState) -> str:
            next_step = state.get("next", "")
            if next_step == "FINISH":
                return END
            elif next_step in ["regulatory_research", "evidence_collection", "compliance_check", "report_generation"]:
                return next_step
            else:
                return "supervisor"
        
        return route_from_supervisor
    
    def _create_tool_router(self) -> Callable[[FraudInvestigationState], str]:
        """Create routing function from tools back to supervisor"""
        def route_from_tool(state: FraudInvestigationState) -> str:
            next_step = state.get("next", "")
            if next_step == "FINISH":
                return END
            else:
                return "supervisor"
        
        return route_from_tool
