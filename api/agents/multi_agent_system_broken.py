"""Streamlined multi-agent system for fraud investigation using modular components"""
import uuid
import logging
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List, AsyncGenerator
import openai
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage, ToolMessage

from ..models.schemas import FraudInvestigationState
from ..services.external_apis import ExternalAPIService
from ..services.memory_optimizer import get_memory_optimizer
from .agent_factory import AgentFactory
from .workflow_builder import WorkflowBuilder
from .message_serializer import MessageSerializer
from .report_generator import ReportGenerator

logger = logging.getLogger(__name__)

# LangSmith monitoring
try:
    from langsmith import traceable
    LANGSMITH_AVAILABLE = True
except ImportError:
    def traceable(name: str = "", tags: List[str] = None):
        def decorator(func):
        return func
        return decorator
    LANGSMITH_AVAILABLE = False

class FraudInvestigationSystem:
    """Streamlined multi-agent fraud investigation system using modular components"""
    
    def __init__(self, llm: ChatOpenAI, external_api_service: ExternalAPIService):
        logger.info("🚀 Initializing Modular FraudInvestigationSystem")
        
        self.llm = llm
        self.external_api_service = external_api_service
        
        # Initialize modular components
        self.agent_factory = AgentFactory(llm)
        self.workflow_builder = WorkflowBuilder(self)
        self.message_serializer = MessageSerializer()
        self.report_generator = ReportGenerator()
        
        # Create agents using factory
        self.agents = self.agent_factory.create_all_agents()
        logger.info(f"✅ Created {len(self.agents)} agents: {list(self.agents.keys())}")
        
        # Build workflow using builder
        self.investigation_graph = self.workflow_builder.build_workflow()
        logger.info("✅ Workflow graph built successfully")
        
        logger.info("✅ Modular FraudInvestigationSystem initialization complete")
    
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
    
    # Delegate routing methods to workflow builder
    def get_next_agents(self, state: FraudInvestigationState) -> List[str]:
        return self.workflow_builder.get_next_agents(state)
    
    def get_next_agent(self, state: FraudInvestigationState) -> str:
        return self.workflow_builder.get_next_agent(state)
    
    # Agent node methods (simplified)
    async def regulatory_research_node(self, state: FraudInvestigationState) -> Dict[str, Any]:
        return await self._execute_agent_tool(state, "regulatory_research")
    
    async def evidence_collection_node(self, state: FraudInvestigationState) -> Dict[str, Any]:
        return await self._execute_agent_tool(state, "evidence_collection")
    
    async def compliance_check_node(self, state: FraudInvestigationState) -> Dict[str, Any]:
        return await self._execute_agent_tool(state, "compliance_check")
    
    async def report_generation_node(self, state: FraudInvestigationState) -> Dict[str, Any]:
        return await self._execute_agent_tool(state, "report_generation")
    
    async def detailed_reasoning_node(self, state: FraudInvestigationState) -> Dict[str, Any]:
        return await self._execute_agent_tool(state, "detailed_reasoning")
    
    async def _execute_agent_tool(self, state: FraudInvestigationState, agent_name: str) -> Dict[str, Any]:
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
        
        # 🔧 CRITICAL: Filter messages to remove incomplete tool call sequences
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
                    logger.debug(f"🔧 Filtering incomplete tool call sequence from {msg.name if hasattr(msg, 'name') else 'unknown'}")
            else:
                filtered_messages.append(msg)
        
        # Execute the agent with filtered messages (without current supervisor tool call)
        agent = self.agents[agent_name]
        
        # Special handling for detailed reasoning agent
        if agent_name == "detailed_reasoning":
            investigation_summary = self.report_generator.generate_investigation_summary_for_reasoning(dict(state))
            reasoning_message = HumanMessage(
                content=f"""Analyze this complete investigation and provide detailed reasoning for the decision:

{investigation_summary}

Provide clear, coherent reasoning in under 1000 words that explains WHY this decision was reached.""",
                name="investigation_summary"
            )
            agent_input = {"messages": [reasoning_message]}
        else:
            agent_input = {"messages": filtered_messages}  # Use filtered messages!
            
        result = agent.invoke(agent_input)
        
        # 🎯 EXPOSE ACTUAL TOOL CALLS FOR RAGAS
        new_messages = []
        
        # Get intermediate steps (these contain the actual tool calls)
        intermediate_steps = result.get("intermediate_steps", [])
        
        if intermediate_steps:
            logger.debug(f"🔧 Agent {agent_name}: Processing {len(intermediate_steps)} actual tool executions")
            
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
                    logger.debug(f"   ✅ Exposed tool call: {tool_name} -> {len(str(observation))} chars response")
        
        # If no intermediate steps, fall back to previous behavior
        if not new_messages:
            logger.debug(f"⚠️ No intermediate steps found for {agent_name}, using fallback")
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
            logger.debug(f"🎯 Sequence: supervisor call -> response -> {len(new_messages)} detailed tool messages")
        else:
            # Fallback: just add the new messages
            final_messages = state["messages"] + new_messages
        
        # Update agents completed
        agents_completed = state.get("agents_completed", []).copy()
        if agent_name not in agents_completed:
            agents_completed.append(agent_name)
        
        return {
            "messages": final_messages,
            "agents_completed": agents_completed,
            "next": "supervisor"
        }
    
    def supervisor_node(self, state: FraudInvestigationState) -> Dict[str, Any]:
        """Supervisor node that makes routing decisions"""
        # Check completion status
        agents_completed = state.get("agents_completed", [])
        required_agents = ["regulatory_research", "evidence_collection", "compliance_check", "report_generation", "detailed_reasoning"]
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
        
        # Use enhanced routing logic
        next_agents = self.get_next_agents(state)
        
        if next_agents == ["FINISH"]:
            return {"next": "FINISH", "investigation_status": "completed"}
        
        # Create tool call for the next agent
        next_agent = next_agents[0]
        tool_call = {
            "name": next_agent,
            "args": {"transaction_data": state["transaction_details"]},
            "id": f"call_{next_agent}_{len(state['messages'])}",
            "type": "tool_call"
        }
        
        # Create descriptive message
        if len(next_agents) > 1:
            content_msg = f"🚀 Enhanced routing: Starting with {next_agent.replace('_', ' ')} (parallel: {len(next_agents)-1} more agents)"
        else:
            content_msg = f"Initiating {next_agent.replace('_', ' ')} analysis..."
        
        supervisor_message = AIMessage(
            content=content_msg,
            tool_calls=[tool_call],
            name="supervisor"
        )
        
        return {
            "next": next_agent,
            "messages": state["messages"] + [supervisor_message]
        }
    
    def generate_final_decision_with_report(self, messages: List[Dict]) -> Dict[str, str]:
        """Generate final decision and comprehensive report from agent messages"""
        logger.info("🔍 generate_final_decision_with_report called")
        
        try:
            # Extract key insights from each agent
            agent_insights = {}
            detailed_reasoning = ""
            
            for message in messages:
                agent_name = message.get("name", "unknown")
                content = message.get("content", "")
                
                # Extract detailed reasoning from the reasoning agent
                if agent_name == "detailed_reasoning":
                    if "✅ Detailed Reasoning completed:" in content:
                        parts = content.split("✅ Detailed Reasoning completed:", 1)
                        if len(parts) > 1:
                            reasoning_content = parts[1]
                            if "' name='" in reasoning_content:
                                reasoning_content = reasoning_content.split("' name='")[0]
                            detailed_reasoning = reasoning_content.strip().strip('"')
                        else:
                            detailed_reasoning = content
                    else:
                        detailed_reasoning = content
                    
                    # Also add to agent_insights for counting
                    insights = self.report_generator.extract_key_insights(content, agent_name)
                    agent_insights[agent_name] = insights
                else:
                    # Extract insights for other agents
                    insights = self.report_generator.extract_key_insights(content, agent_name)
                    agent_insights[agent_name] = insights
                    
            # Generate final decision and report
            decision, comprehensive_report = self.report_generator.synthesize_decision_and_report(agent_insights)
            
            # Insert detailed reasoning into the report
            if detailed_reasoning:
                reasoning_section = "\n\n" + "="*80 + "\n"
                reasoning_section += "                           DETAILED REASONING\n"
                reasoning_section += "="*80 + "\n\n"
                reasoning_section += detailed_reasoning + "\n\n"
                reasoning_section += "="*80 + "\n"
                reasoning_section += "                         ADDITIONAL DATA\n"
                reasoning_section += "="*80
                
                if "ADDITIONAL DATA" in comprehensive_report:
                    comprehensive_report = comprehensive_report.replace(
                        "="*80 + "\n                         ADDITIONAL DATA\n" + "="*80,
                        reasoning_section
                    )
                else:
                    comprehensive_report += reasoning_section
            
            return {
                "decision": decision,
                "report": comprehensive_report,
                "detailed_reasoning": detailed_reasoning
            }
            
        except Exception as e:
            logger.error(f"❌ Error in generate_final_decision_with_report: {str(e)}")
            raise
    
    @traceable(name="investigate_fraud_multi_agent", tags=["investigation", "multi-agent", "fraud"])
    def investigate_fraud(self, transaction_details: Dict[str, Any]) -> Dict[str, Any]:
        """Run a fraud investigation using the LangGraph multi-agent system"""
        investigation_id = transaction_details.get("investigation_id", f"INV_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        logger.info(f"🔍 Multi-Agent Investigation STARTED - ID: {investigation_id}")
        start_time = datetime.now()
        
        try:
            # Create investigation state
            investigation_state = self.create_investigation_state(transaction_details)
            
            # Run the investigation workflow
            workflow_start = datetime.now()
            final_state = self.investigation_graph.invoke(investigation_state)
            workflow_end = datetime.now()
            
            # Calculate metrics
            agents_completed_list = final_state.get("agents_completed", [])
            unique_agents = list(set(agents_completed_list))
            agents_completed = len(unique_agents)
            total_messages = len(final_state.get("messages", []))
            all_agents_finished = agents_completed >= 5
            
            # Generate final decision if needed
            if all_agents_finished and not final_state.get("investigation_report"):
                messages_as_dicts = [
                    {"name": getattr(msg, 'name', 'unknown'), "content": msg.content}
                    for msg in final_state.get("messages", [])
                    if hasattr(msg, 'content')
                ]
                final_decision_result = self.generate_final_decision_with_report(messages_as_dicts)
                final_state["final_decision"] = final_decision_result["decision"]
                final_state["investigation_report"] = final_decision_result["report"]
                final_state["detailed_reasoning"] = final_decision_result.get("detailed_reasoning", "")
            
            total_duration = (datetime.now() - start_time).total_seconds()
            workflow_duration = (workflow_end - workflow_start).total_seconds()
            
            logger.info(f"✅ Multi-Agent Investigation COMPLETED - ID: {investigation_id}")
            logger.info(f"   🤖 Agent Executions: {len(agents_completed_list)} times")
            logger.info(f"   🎯 Unique Agents: {len(unique_agents)}/5")
            
            return {
                "investigation_id": final_state.get("investigation_id", investigation_id),
                "status": final_state.get("investigation_status", "Unknown"),
                "final_decision": final_state.get("final_decision", "Pending"),
                "investigation_report": final_state.get("investigation_report", "Report not available"),
                "detailed_reasoning": final_state.get("detailed_reasoning", ""),
                "agents_completed": agents_completed,
                "total_messages": total_messages,
                "transaction_details": transaction_details,
                "all_agents_finished": all_agents_finished,
                "full_results": self.message_serializer.serialize_state(final_state),
                "ragas_validated_messages": self.message_serializer.validate_ragas_sequence(final_state.get("messages", [])),
                "performance": {
                    "total_duration_s": total_duration,
                    "workflow_duration_s": workflow_duration
                }
            }
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Multi-Agent Investigation FAILED - ID: {investigation_id}: {str(e)}")
            
            return {
                "investigation_id": f"ERROR_{investigation_id}",
                "status": "failed", 
                "final_decision": f"error - {str(e)}",
                "agents_completed": 0,
                "total_messages": 0,
                "transaction_details": transaction_details,
                "all_agents_finished": False,
                "error": str(e),
                "performance": {"total_duration_s": duration, "workflow_duration_s": 0}
            }
    
    @traceable(name="investigate_fraud_stream_multi_agent", tags=["investigation", "multi-agent", "fraud", "stream"])
    async def investigate_fraud_stream(self, transaction_details: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream real-time progress of LangGraph fraud investigation workflow"""
        investigation_id = transaction_details.get("investigation_id", f"STREAM_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        logger.info(f"🚀 STREAMING Investigation: {investigation_id}")
        
        try:
            memory_optimizer = get_memory_optimizer()
            investigation_state = self.create_investigation_state(transaction_details)
            
            yield {"type": "progress", "step": "starting", "agent": "system", "message": "Initializing fraud investigation...", "progress": 0}
            yield {"type": "progress", "step": "setup", "agent": "system", "message": "LangGraph workflow initialized", "progress": 5}
            
            # Execute workflow with streaming
            workflow_start = datetime.now()
            step_count = 0
            current_state = investigation_state
            
            # Main workflow loop
            while True:
                step_count += 1
                base_progress = min(10 + (step_count * 15), 90)
                
                yield {"type": "progress", "step": "workflow_step", "agent": "supervisor", 
                      "message": f"LangGraph step {step_count}: Supervisor routing...", "progress": base_progress}
                
                # Get next agents
                next_agents = self.get_next_agents(current_state)
                
                if next_agents == ["FINISH"] or "FINISH" in next_agents:
                    break
                
                # Execute supervisor
                supervisor_result = self.supervisor_node(current_state)
                if "messages" in supervisor_result:
                    current_state["messages"] = supervisor_result["messages"]
                if "next" in supervisor_result:
                    current_state["next"] = supervisor_result["next"]
                
                # Execute agents (parallel or sequential)
                if len(next_agents) > 1:
                    # Parallel execution
                    yield {"type": "progress", "step": "parallel_start", "agent": "supervisor",
                          "message": f"🚀 Starting parallel execution of {len(next_agents)} agents", "progress": base_progress}
                    
                    # Execute all agents in parallel
                    tasks = []
                    for agent_name in next_agents:
                        if agent_name == "regulatory_research":
                            tasks.append(self.regulatory_research_node(current_state))
                        elif agent_name == "evidence_collection":
                            tasks.append(self.evidence_collection_node(current_state))
                        elif agent_name == "compliance_check":
                            tasks.append(self.compliance_check_node(current_state))
                        elif agent_name == "report_generation":
                            tasks.append(self.report_generation_node(current_state))
                        elif agent_name == "detailed_reasoning":
                            tasks.append(self.detailed_reasoning_node(current_state))
                    
                    parallel_results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Process parallel results
                    for i, (agent_name, result) in enumerate(zip(next_agents, parallel_results)):
                        if isinstance(result, Exception):
                            logger.error(f"❌ Agent {agent_name} failed: {result}")
                            continue
                        
                        if isinstance(result, dict):
                            # Merge state carefully for parallel execution
                            if "messages" in result:
                                current_state["messages"] = result["messages"]
                            if "agents_completed" in result:
                                existing = current_state.get("agents_completed", [])
                                new_agents = result["agents_completed"]
                                current_state["agents_completed"] = list(set(existing + new_agents))
                        
                        yield {"type": "progress", "step": "agent_complete", "agent": agent_name,
                              "message": f"✅ {agent_name.replace('_', ' ').title()} completed",
                              "progress": base_progress + 5 + (i * 2),
                              "completed_agents": len(current_state.get("agents_completed", []))}
                else:
                    # Sequential execution
                    agent_name = next_agents[0]
                    yield {"type": "progress", "step": "agent_start", "agent": agent_name,
                          "message": f"🤖 Executing {agent_name.replace('_', ' ').title()} agent",
                          "progress": base_progress + 5}
                    
                    # Execute single agent
                    if agent_name == "regulatory_research":
                        agent_result = await self.regulatory_research_node(current_state)
                    elif agent_name == "evidence_collection":
                        agent_result = await self.evidence_collection_node(current_state)
                    elif agent_name == "compliance_check":
                        agent_result = await self.compliance_check_node(current_state)
                    elif agent_name == "report_generation":
                        agent_result = await self.report_generation_node(current_state)
                    elif agent_name == "detailed_reasoning":
                        agent_result = await self.detailed_reasoning_node(current_state)
                    else:
                        continue
                    
                    # Update state
                    if "messages" in agent_result:
                        current_state["messages"] = agent_result["messages"]
                    if "agents_completed" in agent_result:
                        existing = current_state.get("agents_completed", [])
                        new_agents = agent_result["agents_completed"]
                        current_state["agents_completed"] = list(set(existing + new_agents))
                    
                    yield {"type": "progress", "step": "agent_complete", "agent": agent_name,
                          "message": f"✅ {agent_name.replace('_', ' ').title()} completed",
                          "progress": base_progress + 10,
                          "completed_agents": len(current_state.get("agents_completed", []))}
                
                if step_count > 10:
                    break
            
            # Generate final result
            workflow_end = datetime.now()
            workflow_duration = (workflow_end - workflow_start).total_seconds()
            
            yield {"type": "progress", "step": "compilation_start", "agent": "system",
                  "message": "Compiling final investigation results...", "progress": 95}
            
            # Generate final decision
            messages_as_dicts = [
                {"name": getattr(msg, 'name', 'unknown'), "content": msg.content}
                for msg in current_state.get("messages", [])
                if hasattr(msg, 'content')
            ]
            
            final_decision_result = self.generate_final_decision_with_report(messages_as_dicts)
            
            # Create final result with proper agent counting
            unique_agents = list(set(current_state.get("agents_completed", [])))
            
            final_result = {
                "investigation_id": investigation_id,
                "status": "completed",
                "final_decision": final_decision_result.get("decision", "Investigation completed"),
                "investigation_report": final_decision_result.get("report", "Report generated"),
                "detailed_reasoning": final_decision_result.get("detailed_reasoning", ""),
                "agents_completed": len(unique_agents),  # Use unique count
                "agent_list": unique_agents,  # Use unique list
                "total_messages": len(current_state.get("messages", [])),
                "transaction_details": transaction_details,
                "all_agents_finished": True,
                "workflow_type": "streaming_langgraph_modular",
                "full_results": self.message_serializer.serialize_state(dict(current_state)),
                "ragas_validated_messages": self.message_serializer.serialize_messages(
                    self.message_serializer.validate_ragas_sequence(current_state.get("messages", []))
                ),
                "enhanced_data": {
                    "real_agent_execution": True,
                    "modular_architecture": True,
                    "workflow_duration": workflow_duration,
                    "steps_executed": step_count
                }
            }
            
            # Test JSON serialization safety
            try:
                json.dumps(final_result, default=str)
                logger.info("✅ Final result JSON serialization test passed")
            except Exception as e:
                logger.error(f"❌ JSON serialization failed: {e}")
                # Create minimal safe result
                final_result = {
                    "investigation_id": investigation_id,
                        "status": "completed",
                    "final_decision": "Investigation completed with serialization issues",
                    "error": f"Serialization failed: {str(e)}"
                }
            
            logger.info(f"✅ Modular Investigation completed! Unique agents: {len(unique_agents)}/5")
            
            yield {
                "type": "complete",
                "step": "complete",
                "agent": "system",
                "message": f"Investigation completed: {len(unique_agents)} unique agents executed",
                "progress": 100,
                "result": final_result
            }
            
            memory_optimizer.log_memory_status("(Streaming Investigation Complete)")
            
        except Exception as e:
            logger.error(f"❌ Streaming Investigation failed: {str(e)}")
            
            yield {
                "type": "error",
                "step": "error",
                "agent": "system",
                "message": f"Investigation failed: {str(e)}",
                "progress": 100,
                "error": True
            }
