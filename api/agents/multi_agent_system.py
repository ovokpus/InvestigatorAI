"""Multi-agent system for fraud investigation using LangGraph"""
import uuid
from datetime import datetime
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langgraph.graph import END, StateGraph

from ..models.schemas import FraudInvestigationState
from ..agents.tools import (
    REGULATORY_TOOLS, EVIDENCE_TOOLS, COMPLIANCE_TOOLS, REPORT_TOOLS,
    initialize_tools
)
from ..services.external_apis import ExternalAPIService

class FraudInvestigationSystem:
    """Multi-agent fraud investigation system using LangGraph"""
    
    def __init__(self, llm: ChatOpenAI, external_api_service: ExternalAPIService):
        self.llm = llm
        self.external_api_service = external_api_service
        
        # Initialize tools with dependencies
        initialize_tools(external_api_service)
        
        # Create agents
        self.agents = self._create_agents()
        
        # Build workflow
        self.investigation_graph = self._build_workflow()
    
    def _create_agent(self, llm: ChatOpenAI, tools: list, system_prompt: str) -> AgentExecutor:
        """Create a function calling agent"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_functions_agent(llm, tools, prompt)
        return AgentExecutor(agent=agent, tools=tools, verbose=False)
    
    def _create_agents(self) -> Dict[str, AgentExecutor]:
        """Create all specialist agents"""
        agents = {}
        
        # Regulatory Research Agent
        agents['regulatory_research'] = self._create_agent(
            llm=self.llm,
            tools=REGULATORY_TOOLS,
            system_prompt="""You are a Regulatory Research Agent specializing in financial fraud investigation.
            Research relevant regulations, compliance requirements, and fraud patterns.
            Use tools to search regulatory documents, research papers, and web intelligence.
            Provide comprehensive analysis of regulatory requirements and fraud indicators."""
        )
        
        # Evidence Collection Agent
        agents['evidence_collection'] = self._create_agent(
            llm=self.llm,
            tools=EVIDENCE_TOOLS,
            system_prompt="""You are an Evidence Collection Agent specializing in transaction analysis.
            Collect and analyze evidence related to suspicious transactions.
            Use tools to calculate risk scores, get exchange rates, and gather intelligence.
            Focus on quantitative analysis and risk assessment."""
        )
        
        # Compliance Check Agent
        agents['compliance_check'] = self._create_agent(
            llm=self.llm,
            tools=COMPLIANCE_TOOLS,
            system_prompt="""You are a Compliance Check Agent specializing in regulatory compliance.
            Determine filing requirements and compliance obligations.
            Use tools to check SAR/CTR requirements and regulatory obligations.
            Ensure all compliance requirements are identified and documented."""
        )
        
        # Report Generation Agent
        agents['report_generation'] = self._create_agent(
            llm=self.llm,
            tools=REPORT_TOOLS,
            system_prompt="""You are a Report Generation Agent specializing in investigation reports.
            Synthesize findings and generate comprehensive investigation reports.
            Create detailed reports with findings, recommendations, and compliance requirements.
            Ensure reports are professional and include all relevant investigation details."""
        )
        
        return agents
    
    def create_investigation_state(self, transaction_details: Dict[str, Any]) -> FraudInvestigationState:
        """Create initial state for fraud investigation"""
        investigation_id = f"INV_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:4]}"
        
        initial_message = HumanMessage(
            content=f"""Investigate this transaction:
            
            Transaction Details:
            - Amount: ${transaction_details['amount']:,} {transaction_details['currency']}
            - Description: {transaction_details['description']}
            - Customer: {transaction_details['customer_name']}
            - Account Type: {transaction_details['account_type']}
            - Customer Risk Rating: {transaction_details['customer_risk_rating']}
            - Destination Country: {transaction_details['country_to']}
            - Timestamp: {transaction_details['timestamp']}
            
            Please conduct a comprehensive fraud investigation including:
            1. Regulatory compliance assessment
            2. Risk score calculation and evidence collection
            3. Filing requirement determination
            4. Investigation report generation
            """,
            name="system"
        )
        
        return FraudInvestigationState(
            messages=[initial_message],
            investigation_id=investigation_id,
            transaction_details=transaction_details,
            agents_completed=[],
            investigation_status="in_progress",
            final_decision="pending",
            next="regulatory_research"
        )
    
    def get_next_agent(self, state: FraudInvestigationState) -> str:
        """Determine next agent to route to"""
        agents_completed = state["agents_completed"]
        required_agents = ["regulatory_research", "evidence_collection", "compliance_check", "report_generation"]
        
        for agent in required_agents:
            if agent not in agents_completed:
                return agent
        
        return "FINISH"
    
    def update_agent_completion(self, state: FraudInvestigationState, agent_name: str) -> dict:
        """Return immutable state updates for LangGraph"""
        agents_completed = state["agents_completed"].copy()
        if agent_name not in agents_completed:
            agents_completed.append(agent_name)
        
        required_agents = ["regulatory_research", "evidence_collection", "compliance_check", "report_generation"]
        all_completed = all(agent in agents_completed for agent in required_agents)
        
        state_update = {"agents_completed": agents_completed}
        
        if all_completed:
            state_update.update({
                "investigation_status": "completed",
                "final_decision": "investigation_complete"
            })
        
        return state_update
    
    def agent_node(self, state: FraudInvestigationState, agent_name: str):
        """Agent node that returns proper LangGraph state updates"""
        agent = self.agents[agent_name]
        agent_input = {"messages": state["messages"]}
        result = agent.invoke(agent_input)
        
        state_updates = self.update_agent_completion(state, agent_name)
        new_message = HumanMessage(content=result["output"], name=agent_name)
        updated_messages = state["messages"] + [new_message]
        
        return {
            **state_updates,
            "messages": updated_messages
        }
    
    def supervisor_node(self, state: FraudInvestigationState):
        """Supervisor node with immutable state updates"""
        next_agent = self.get_next_agent(state)
        
        if next_agent == "FINISH":
            completion_message = HumanMessage(
                content="Investigation completed. All specialist agents have finished their analysis.", 
                name="supervisor"
            )
            return {
                "next": "FINISH",
                "investigation_status": "completed",
                "messages": state["messages"] + [completion_message]
            }
        else:
            routing_message = HumanMessage(
                content=f"Routing investigation to {next_agent} agent for specialized analysis.", 
                name="supervisor"
            )
            return {
                "next": next_agent,
                "messages": state["messages"] + [routing_message]
            }
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(FraudInvestigationState)
        
        # Add nodes
        workflow.add_node("supervisor", self.supervisor_node)
        workflow.add_node("regulatory_research", lambda state: self.agent_node(state, "regulatory_research"))
        workflow.add_node("evidence_collection", lambda state: self.agent_node(state, "evidence_collection"))
        workflow.add_node("compliance_check", lambda state: self.agent_node(state, "compliance_check"))
        workflow.add_node("report_generation", lambda state: self.agent_node(state, "report_generation"))
        
        # Set up routing
        workflow.add_edge("regulatory_research", "supervisor")
        workflow.add_edge("evidence_collection", "supervisor")
        workflow.add_edge("compliance_check", "supervisor")
        workflow.add_edge("report_generation", "supervisor")
        
        def route_to_agent(state: FraudInvestigationState):
            next_agent = state.get("next", "")
            
            if next_agent == "FINISH":
                return END
            elif next_agent in ["regulatory_research", "evidence_collection", "compliance_check", "report_generation"]:
                return next_agent
            else:
                return "supervisor"
        
        workflow.add_conditional_edges(
            "supervisor",
            route_to_agent,
            {
                "regulatory_research": "regulatory_research",
                "evidence_collection": "evidence_collection", 
                "compliance_check": "compliance_check",
                "report_generation": "report_generation",
                END: END
            }
        )
        
        workflow.set_entry_point("supervisor")
        return workflow.compile()
    
    def investigate_fraud(self, transaction_details: Dict[str, Any]) -> Dict[str, Any]:
        """Run a fraud investigation using the LangGraph multi-agent system"""
        try:
            # Create investigation state
            investigation_state = self.create_investigation_state(transaction_details)
            
            # Run the investigation workflow
            final_state = self.investigation_graph.invoke(investigation_state)
            
            # Calculate summary metrics
            agents_completed = len(final_state.get("agents_completed", []))
            total_messages = len(final_state.get("messages", []))
            all_agents_finished = agents_completed >= 4
            
            # Return investigation results
            return {
                "investigation_id": final_state.get("investigation_id", "Unknown"),
                "status": final_state.get("investigation_status", "Unknown"),
                "final_decision": final_state.get("final_decision", "Pending"),
                "agents_completed": agents_completed,
                "total_messages": total_messages,
                "transaction_details": transaction_details,
                "all_agents_finished": all_agents_finished,
                "full_results": final_state
            }
            
        except Exception as e:
            return {
                "investigation_id": "ERROR",
                "status": "failed",
                "final_decision": "error",
                "agents_completed": 0,
                "total_messages": 0,
                "transaction_details": transaction_details,
                "all_agents_finished": False,
                "error": str(e)
            }