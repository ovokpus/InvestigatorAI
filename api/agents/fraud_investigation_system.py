"""Modular fraud investigation system using specialized components"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, AsyncGenerator
import openai
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage, ToolMessage


from ..models.schemas import FraudInvestigationState
from ..agents.tools import initialize_tools
from ..services.external_apis import ExternalAPIService
from .agent_factory import AgentFactory
from .workflow_builder import WorkflowBuilder
from .message_processor import MessageProcessor
from .report_generator import ReportGenerator
from .streaming_handler import StreamingHandler

logger = logging.getLogger(__name__)

# LangSmith monitoring
try:
    from langsmith import traceable
    LANGSMITH_AVAILABLE = True
except ImportError:
    # Create no-op decorator if LangSmith is not installed
    LANGSMITH_AVAILABLE = False
    def traceable(func: Any) -> Any:
        return func


class FraudInvestigationSystem:
    """Modular multi-agent fraud investigation system using LangGraph"""
    
    def __init__(self, llm: ChatOpenAI, external_api_service: ExternalAPIService):
        logger.info("🚀 Initializing FraudInvestigationSystem")
        logger.info(f"   🤖 LLM Model: {llm.model_name if hasattr(llm, 'model_name') else 'Unknown'}")
        logger.info(f"   🔗 External API Service: {type(external_api_service).__name__}")
        
        self.llm = llm
        self.external_api_service = external_api_service
        
        # Initialize tools with dependencies
        logger.info("🔧 Initializing agent tools...")
        initialize_tools(external_api_service)
        logger.info("   ✅ Tools initialized successfully")
        
        # Initialize modular components
        self.agent_factory = AgentFactory(llm)
        self.message_processor = MessageProcessor()
        self.report_generator = ReportGenerator()
        self.streaming_handler = StreamingHandler(external_api_service)
        
        # Create agents using factory
        logger.info("🤖 Creating specialized agents...")
        self.agents = self.agent_factory.create_all_agents()
        logger.info(f"   ✅ Created {len(self.agents)} agents: {list(self.agents.keys())}")
        
        # Create agent node functions
        self.agent_nodes = {
            "regulatory_research": self.regulatory_research_node,
            "evidence_collection": self.evidence_collection_node,
            "compliance_check": self.compliance_check_node,
            "report_generation": self.report_generation_node
        }
        
        # Build workflow using builder
        logger.info("🔄 Building LangGraph workflow...")
        self.workflow_builder = WorkflowBuilder(self.agents)
        self.investigation_graph = self.workflow_builder.build_investigation_workflow(
            self.agent_nodes, 
            self.supervisor_node
        )
        logger.info("   ✅ Workflow graph built successfully")
        
        logger.info("✅ FraudInvestigationSystem initialization complete")
    
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
        """Determine next agent to route to - report_generation runs AFTER other three agents"""
        agents_completed = state["agents_completed"]
        
        # First three agents can run in any order
        primary_agents = ["regulatory_research", "evidence_collection", "compliance_check"]
        
        # Check if any primary agents still need to run
        for agent in primary_agents:
            if agent not in agents_completed:
                return agent
        
        # All primary agents done - now run report generation if not completed
        if "report_generation" not in agents_completed:
            return "report_generation"
        
        return "FINISH"
    
    def update_agent_completion(self, state: FraudInvestigationState, agent_name: str) -> Dict[str, Any]:
        """Return immutable state updates for LangGraph"""
        agents_completed = state["agents_completed"].copy()
        if agent_name not in agents_completed:
            agents_completed.append(agent_name)
        
        required_agents = ["regulatory_research", "evidence_collection", "compliance_check", "report_generation"]
        all_completed = all(agent in agents_completed for agent in required_agents)
        
        state_update: Dict[str, Any] = {"agents_completed": agents_completed}
        
        if all_completed:
            # Generate a comprehensive final decision from all agent messages
            final_decision_result = self.report_generator.generate_final_decision_with_report(state["messages"])
            state_update.update({
                "investigation_status": "completed",
                "final_decision": final_decision_result["decision"],
                "investigation_report": final_decision_result["report"]
            })
        
        return state_update
    
    def supervisor_node(self, state: FraudInvestigationState) -> Dict[str, Any]:
        """Supervisor node that makes tool calls for RAGAS compliance"""
        
        # Check completion status
        agents_completed = state.get("agents_completed", [])
        required_agents = ["regulatory_research", "evidence_collection", "compliance_check", "report_generation"]
        all_completed = all(agent in agents_completed for agent in required_agents)
        
        if all_completed:
            completion_message = AIMessage(
                content="Investigation completed. All specialist agents have finished their analysis.", 
                name="supervisor"
            )
            return {
                "next": "FINISH", 
                "investigation_status": "completed",
                "messages": state["messages"] + [completion_message]
            }
        
        # Use the improved sequencing logic
        next_agent = self.get_next_agent(state)
        
        if next_agent == "FINISH":
            return {"next": "FINISH", "investigation_status": "completed"}
        
        # Create tool call for the next agent
        tool_call = {
            "name": next_agent,
            "args": {"transaction_data": state["transaction_details"]},
            "id": f"call_{next_agent}_{len(state['messages'])}",
            "type": "tool_call"
        }
        
        # Create AI message with tool call
        supervisor_message = AIMessage(
            content=f"Initiating {next_agent.replace('_', ' ')} analysis...",
            tool_calls=[tool_call],
            name="supervisor"
        )
        
        return {
            "next": next_agent,
            "messages": state["messages"] + [supervisor_message]
        }
    
    def regulatory_research_node(self, state: FraudInvestigationState) -> Dict[str, Any]:
        """Execute regulatory research agent and return ToolMessage"""
        return self._execute_agent_tool(state, "regulatory_research")
    
    def evidence_collection_node(self, state: FraudInvestigationState) -> Dict[str, Any]:
        """Execute evidence collection agent and return ToolMessage"""
        return self._execute_agent_tool(state, "evidence_collection")
    
    def compliance_check_node(self, state: FraudInvestigationState) -> Dict[str, Any]:
        """Execute compliance check agent and return ToolMessage"""
        return self._execute_agent_tool(state, "compliance_check")
    
    def report_generation_node(self, state: FraudInvestigationState) -> Dict[str, Any]:
        """Execute report generation agent and return ToolMessage"""
        return self._execute_agent_tool(state, "report_generation")
    
    def _execute_agent_tool(self, state: FraudInvestigationState, agent_name: str) -> Dict[str, Any]:
        """Execute a specific agent tool and expose actual tool calls for RAGAS evaluation"""
        # Find the corresponding tool call in the last message (supervisor's AIMessage)
        last_message = state["messages"][-1]
        tool_call_id = None
        supervisor_message = None
        
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            for tool_call in last_message.tool_calls:
                if tool_call["name"] == agent_name:
                    tool_call_id = tool_call["id"]
                    supervisor_message = last_message  # 🎯 Preserve the supervisor's AIMessage
                    break
        
        if not tool_call_id:
            tool_call_id = f"call_{agent_name}_{len(state['messages'])}"
        
        # 🔧 FIX: Filter messages to remove incomplete tool call sequences
        # BUT preserve the current supervisor message for RAGAS
        filtered_messages: List[BaseMessage] = []
        for i, msg in enumerate(state["messages"]):
            if isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls') and msg.tool_calls:
                # Skip the current supervisor message (we'll handle it separately)
                if msg == supervisor_message:
                    continue
                    
                # Check if this AIMessage has corresponding ToolMessages
                has_responses = True
                for tool_call in msg.tool_calls:
                    tc_id = tool_call.get("id")
                    # Look for ToolMessage with matching tool_call_id
                    found_response = False
                    for j in range(i+1, len(state["messages"])):
                        next_msg = state["messages"][j]
                        if isinstance(next_msg, ToolMessage) and getattr(next_msg, 'tool_call_id', None) == tc_id:
                            found_response = True
                            break
                    if not found_response:
                        has_responses = False
                        break
                
                # Only include AIMessage if all tool_calls have responses
                if has_responses:
                    filtered_messages.append(msg)
                else:
                    print(f"🔧 Filtering incomplete tool call sequence from {msg.name if hasattr(msg, 'name') else 'unknown'}")
            else:
                filtered_messages.append(msg)
        
        # Execute the agent with filtered messages (without current supervisor tool call)
        agent = self.agents[agent_name]
        agent_input = {"messages": filtered_messages}
        result = agent.invoke(agent_input)
        
        # 🎯 EXPOSE ACTUAL TOOL CALLS FOR RAGAS
        new_messages: List[BaseMessage] = []
        
        # Get intermediate steps (these contain the actual tool calls)
        intermediate_steps = result.get("intermediate_steps", [])
        
        if intermediate_steps:
            print(f"🔧 Agent {agent_name}: Processing {len(intermediate_steps)} actual tool executions")
            
            # Process each tool execution step
            for i, step in enumerate(intermediate_steps):
                if isinstance(step, tuple) and len(step) == 2:
                    agent_action, observation = step
                    
                    # Extract the actual tool call information
                    tool_name = agent_action.tool
                    tool_input = agent_action.tool_input
                    # Generate shorter ID to stay within OpenAI's 40-char limit
                    agent_short = agent_name[:3]  # reg, evi, com, rep
                    tool_short = tool_name.split('_')[-1][:8]  # last word, max 8 chars
                    actual_tool_call_id = f"call_{tool_short}_{i}_{agent_short}"
                    
                    # Create AIMessage with proper tool_calls structure for the actual tool
                    ai_message = AIMessage(
                        content=f"Using {tool_name} for {agent_name} analysis...",
                        tool_calls=[{
                            "id": actual_tool_call_id,
                            "name": tool_name,
                            "args": tool_input,
                            "type": "function"
                        }],
                        name=f"{agent_name}_executor"
                    )
                    
                    # Create ToolMessage with the observation
                    tool_message = ToolMessage(
                        content=str(observation),
                        tool_call_id=actual_tool_call_id,
                        name=tool_name
                    )
                    
                    new_messages.extend([ai_message, tool_message])
                    print(f"   ✅ Exposed tool call: {tool_name} -> {len(str(observation))} chars response")
        
        # If no intermediate steps, fall back to previous behavior
        if not new_messages:
            print(f"⚠️ No intermediate steps found for {agent_name}, using fallback")
            # Extract agent's final output
            agent_output = result.get("output", f"Analysis completed by {agent_name}")
            
            # Create ToolMessage response for the supervisor's agent call
            agent_tool_response = ToolMessage(
                content=agent_output,
                tool_call_id=tool_call_id,
                name=agent_name
            )
            new_messages = [agent_tool_response]
        
        # 🎯 BUILD FINAL MESSAGE SEQUENCE FOR RAGAS
        # Ensure proper supervisor tool call -> response sequence
        if supervisor_message:
            # Start with all previous messages except the supervisor's
            prev_messages = state["messages"][:-1]
            
            # Create supervisor response to close the agent call
            agent_output = result.get("output", f"Analysis completed by {agent_name}")
            supervisor_response = ToolMessage(
                content=f"✅ {agent_name.replace('_', ' ').title()} completed: {agent_output}",
                tool_call_id=tool_call_id,  # This closes the supervisor's tool call
                name=agent_name
            )
            
            # Build proper sequence: prev -> supervisor_call -> supervisor_response -> [detailed_tools if any]
            # Remove any duplicate supervisor response from new_messages
            detailed_tools = [msg for msg in new_messages if not (hasattr(msg, 'tool_call_id') and msg.tool_call_id == tool_call_id)]
            final_messages = prev_messages + [supervisor_message, supervisor_response] + detailed_tools
            print(f"🎯 Sequence: supervisor call -> response -> {len(new_messages)} detailed tool messages")
        else:
            # Fallback: just add the new messages
            final_messages = state["messages"] + new_messages
        
        # Update agents completed
        agents_completed = state.get("agents_completed", []).copy()
        if agent_name not in agents_completed:
            agents_completed.append(agent_name)
        
        # Check if all agents completed
        required_agents = ["regulatory_research", "evidence_collection", "compliance_check", "report_generation"]
        all_completed = all(agent in agents_completed for agent in required_agents)
        
        state_updates = {
            "messages": final_messages,
            "agents_completed": agents_completed
        }
        
        if all_completed:
            state_updates.update({
                "investigation_status": "completed",
                "next": "FINISH"
            })
        else:
            state_updates["next"] = "supervisor"
            
        return state_updates
    
    def _create_frontend_results(self, final_state: Dict[str, Any]) -> Dict[str, Any]:
        """Create frontend-optimized results with detailed agent messages"""
        # Extract detailed agent messages for frontend display
        messages = final_state.get("messages", [])
        frontend_messages = self.message_processor.extract_frontend_messages(messages)
        
        # Serialize the frontend messages
        serialized_frontend_messages = self.message_processor.serialize_messages(frontend_messages)
        
        # Create frontend-optimized results
        frontend_results = {
            "investigation_id": final_state.get("investigation_id", "Unknown"),
            "investigation_status": final_state.get("investigation_status", "completed"),
            "agents_completed": final_state.get("agents_completed", []),
            "messages": serialized_frontend_messages,  # Detailed agent messages for frontend
            "total_messages": len(messages),
            "frontend_message_count": len(frontend_messages),
            "detailed_reasoning_available": len(frontend_messages) > 0
        }
        
        print(f"🎯 Created frontend results: {len(frontend_messages)} detailed messages for display")
        return frontend_results
    
    @traceable(name="investigate_fraud_multi_agent", tags=["investigation", "multi-agent", "fraud"])
    def investigate_fraud(self, transaction_details: Dict[str, Any]) -> Dict[str, Any]:
        """Run a fraud investigation using the LangGraph multi-agent system"""
        investigation_id = transaction_details.get("investigation_id", f"INV_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        amount = transaction_details.get("amount", "N/A")
        currency = transaction_details.get("currency", "N/A")
        customer_name = transaction_details.get("customer_name", "N/A")
        country_to = transaction_details.get("country_to", "N/A")
        
        logger.info(f"🔍 Multi-Agent Investigation STARTED - ID: {investigation_id}")
        logger.info(f"   💰 Transaction: {amount} {currency}")
        logger.info(f"   👤 Customer: {customer_name}")
        logger.info(f"   🌍 Destination: {country_to}")
        
        start_time = datetime.now()
        
        try:
            # Create investigation state
            logger.info(f"📋 Creating investigation state for {investigation_id}")
            investigation_state = self.create_investigation_state(transaction_details)
            logger.debug(f"   State created with keys: {list(investigation_state.keys())}")
            
            # Run the investigation workflow
            logger.info(f"🔄 Starting LangGraph workflow for {investigation_id}")
            workflow_start = datetime.now()
            
            final_state = self.investigation_graph.invoke(investigation_state)
            
            workflow_end = datetime.now()
            workflow_duration = (workflow_end - workflow_start).total_seconds()
            
            # Calculate summary metrics
            agents_completed = len(final_state.get("agents_completed", []))
            total_messages = len(final_state.get("messages", []))
            all_agents_finished = agents_completed >= 4
            
            total_duration = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ Multi-Agent Investigation COMPLETED - ID: {investigation_id}")
            logger.info(f"   ⏱️  Total Duration: {total_duration:.2f}s (Workflow: {workflow_duration:.2f}s)")
            logger.info(f"   🤖 Agents Completed: {agents_completed}/4")
            logger.info(f"   💬 Total Messages: {total_messages}")
            logger.info(f"   🏁 All Agents Finished: {all_agents_finished}")
            logger.info(f"   📊 Final Status: {final_state.get('investigation_status', 'Unknown')}")
            logger.info(f"   ⚖️  Final Decision: {final_state.get('final_decision', 'Pending')}")
            
            if agents_completed < 4:
                logger.warning(f"⚠️  Investigation {investigation_id} completed with only {agents_completed}/4 agents")
            
            # Return investigation results
            return {
                "investigation_id": final_state.get("investigation_id", investigation_id),
                "status": final_state.get("investigation_status", "Unknown"),
                "final_decision": final_state.get("final_decision", "Pending"),
                "investigation_report": final_state.get("investigation_report", "Report not available"),
                "agents_completed": agents_completed,
                "total_messages": total_messages,
                "transaction_details": transaction_details,
                "all_agents_finished": all_agents_finished,
                "full_results": self._create_frontend_results(final_state),
                "final_report": self.message_processor.extract_final_report(final_state.get("messages", [])),
                "ragas_validated_messages": self.message_processor.validate_ragas_sequence(final_state.get("messages", [])),
                "performance": {
                    "total_duration_s": total_duration,
                    "workflow_duration_s": workflow_duration
                }
            }
            
        except openai.OpenAIError as e:
            error_type = "OpenAI API Error"
            error_message = f"AI service error: {str(e)}"
            
            if "max_tokens" in str(e).lower():
                error_type = "Token Limit Error"
                error_message = "Investigation analysis too complex. Please try with simpler transaction details or contact support for assistance."
            elif "rate limit" in str(e).lower():
                error_type = "Rate Limit Error"
                error_message = "AI service temporarily busy. Please wait a moment and try again."
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Multi-Agent Investigation FAILED - ID: {investigation_id}")
            logger.error(f"   🚨 Error Type: {error_type}")
            logger.error(f"   💥 Error Message: {error_message}")
            logger.error(f"   ⏱️  Duration before failure: {duration:.2f}s")
            
            return {
                "investigation_id": f"ERROR_{investigation_id}_{datetime.now().strftime('%H%M%S')}",
                "status": "failed",
                "final_decision": "error - " + error_message,
                "agents_completed": 0,
                "total_messages": 0,
                "transaction_details": transaction_details,
                "all_agents_finished": False,
                "error": error_message,
                "error_type": error_type,
                "performance": {
                    "total_duration_s": duration,
                    "workflow_duration_s": 0
                }
            }
            
        except Exception as e:
            error_type = "General Error"
            error_message = str(e)
            
            if "max_tokens" in error_message.lower() or "token limit" in error_message.lower():
                error_type = "Token Limit Error"
                error_message = "Investigation analysis exceeded maximum length. Please try with a shorter transaction description."
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Multi-Agent Investigation FAILED - ID: {investigation_id}")
            logger.error(f"   🚨 Error Type: {error_type}")
            logger.error(f"   💥 Error Details: {error_message}")
            logger.error(f"   ⏱️  Duration before failure: {duration:.2f}s")
            logger.exception(f"   🔍 Full exception details:")
            
            return {
                "investigation_id": f"ERROR_{investigation_id}_{datetime.now().strftime('%H%M%S')}",
                "status": "failed", 
                "final_decision": "error - " + error_message,
                "agents_completed": 0,
                "total_messages": 0,
                "transaction_details": transaction_details,
                "all_agents_finished": False,
                "error": error_message,
                "error_type": error_type,
                "performance": {
                    "total_duration_s": duration,
                    "workflow_duration_s": 0
                }
            }
    
    async def investigate_fraud_stream(self, transaction_details: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream a fraud investigation using the REAL LangGraph workflow with detailed reasoning"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        # Create investigation state
        investigation_state = self.create_investigation_state(transaction_details)
        
        # Yield initial progress
        yield {
            "type": "progress",
            "step": "setup",
            "agent": "system", 
            "message": "Initializing LangGraph multi-agent investigation...",
            "progress": 5
        }
        
        # Run the actual LangGraph workflow in a thread to avoid blocking
        def run_langgraph_workflow():
            return self.investigation_graph.invoke(investigation_state)
        
        # Execute workflow with progress simulation
        with ThreadPoolExecutor() as executor:
            # Start the workflow
            future = executor.submit(run_langgraph_workflow)
            
            # Simulate progress while workflow runs
            progress_steps = [
                (10, "supervisor", "Starting agent coordination..."),
                (20, "regulatory_research", "Analyzing regulatory requirements..."),
                (35, "evidence_collection", "Collecting evidence and calculating risk..."),
                (50, "compliance_check", "Checking compliance requirements..."),
                (70, "report_generation", "Generating detailed reasoning and final report..."),
                (90, "system", "Finalizing investigation results...")
            ]
            
            step_duration = 8.0  # seconds per step
            for progress, agent, message in progress_steps:
                # Check if workflow is done
                if future.done():
                    break
                    
                yield {
                    "type": "progress",
                    "step": "agent_execution",
                    "agent": agent,
                    "message": message,
                    "progress": progress
                }
                
                # Wait for step duration or until workflow completes
                try:
                    final_state = future.result(timeout=step_duration)
                    break  # Workflow completed
                except:
                    continue  # Keep waiting
            
            # Get final results (wait if needed)
            if not future.done():
                yield {
                    "type": "progress", 
                    "step": "finalizing",
                    "agent": "system",
                    "message": "Completing final analysis...",
                    "progress": 95
                }
                final_state = future.result()  # Wait for completion
            else:
                final_state = future.result()
        
        # Extract detailed reasoning for frontend
        frontend_results = self._create_frontend_results(final_state)
        
        # Generate final decision
        final_decision_result = self.report_generator.generate_final_decision_with_report(final_state.get("messages", []))
        
        # Create completion result with detailed reasoning
        completion_result = {
            "investigation_id": final_state.get("investigation_id", "Unknown"),
            "status": final_state.get("investigation_status", "completed"),
            "final_decision": final_decision_result["decision"],
            "investigation_report": final_decision_result["report"],
            "agents_completed": len(final_state.get("agents_completed", [])),
            "total_messages": len(final_state.get("messages", [])),
            "transaction_details": transaction_details,
            "all_agents_finished": True,
            "full_results": frontend_results,  # Contains detailed reasoning for frontend
            "final_report": frontend_results.get("final_report", ""),  # Comprehensive final report for prominent display
            "detailed_reasoning_available": frontend_results.get("detailed_reasoning_available", False),
            "final_report_available": frontend_results.get("final_report_available", False)
        }
        
        yield {
            "type": "complete",
            "step": "complete",
            "agent": "system",
            "message": "Investigation completed with detailed reasoning",
            "progress": 100,
            "result": completion_result
        }
