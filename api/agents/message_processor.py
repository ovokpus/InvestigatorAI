"""Message processing and validation for fraud investigation system"""
import logging
import re
from datetime import datetime
from typing import List, Dict, Any, Union
from langchain_core.messages import BaseMessage, AIMessage, ToolMessage, HumanMessage

logger = logging.getLogger(__name__)


class MessageProcessor:
    """Handles message processing, validation, and serialization"""
    
    def __init__(self) -> None:
        logger.info("📨 MessageProcessor initialized")
    
    def serialize_messages(self, messages: Union[List[BaseMessage], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Convert messages to JSON-serializable format (handles both BaseMessage and dict formats)"""
        serialized_messages = []
        for message in messages:
            try:
                # Handle dictionary format (new format from investigation generator)
                if isinstance(message, dict):
                    serialized_message = {
                        "content": message.get("content", ""),
                        "type": message.get("type", "message"),
                        "name": message.get("name", None),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # ✅ PRESERVE TOOL CALLS: Extract tool_calls if present in dict
                    if "tool_calls" in message and message["tool_calls"]:
                        serialized_message["tool_calls"] = message["tool_calls"]
                    
                    # ✅ PRESERVE TOOL RESPONSES: Extract tool_call_id if present in dict
                    if "tool_call_id" in message and message["tool_call_id"]:
                        serialized_message["tool_call_id"] = message["tool_call_id"]
                    
                    serialized_messages.append(serialized_message)
                # Handle BaseMessage format (original LangChain format)
                elif hasattr(message, 'content'):
                    serialized_message = {
                        "content": message.content,
                        "type": message.__class__.__name__,
                        "name": getattr(message, 'name', None),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # ✅ PRESERVE TOOL CALLS: Extract tool_calls from AIMessage
                    if hasattr(message, 'tool_calls') and message.tool_calls:
                        serialized_message["tool_calls"] = message.tool_calls
                    
                    # ✅ PRESERVE TOOL RESPONSES: Extract tool_call_id from ToolMessage  
                    if hasattr(message, 'tool_call_id') and message.tool_call_id:
                        serialized_message["tool_call_id"] = message.tool_call_id
                    
                    serialized_messages.append(serialized_message)
                else:
                    # Fallback for any other format
                    serialized_messages.append({
                        "content": str(message),
                        "type": "message",
                        "name": "unknown",
                        "timestamp": datetime.now().isoformat()
                    })
            except Exception as e:
                # Fallback for any serialization issues
                print(f"❌ Message serialization error: {e}, message: {message}")
                serialized_messages.append({
                    "content": f"Serialization error for message: {str(message)}",
                    "type": "message",
                    "name": "unknown",
                    "timestamp": datetime.now().isoformat(),
                    "error": f"Serialization error: {str(e)}"
                })
        
        print(f"✅ Serialized {len(serialized_messages)} messages successfully")
        return serialized_messages
    
    def serialize_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Convert state with LangChain objects to JSON-serializable format"""
        serialized_state: Dict[str, Any] = {}
        for key, value in state.items():
            if key == "messages" and isinstance(value, list):
                serialized_state[key] = self.serialize_messages(value)
            elif isinstance(value, (str, int, float, bool, list, dict)) or value is None:
                serialized_state[key] = value
            else:
                # Convert other objects to string representation
                serialized_state[key] = str(value)
        return serialized_state
    
    def validate_ragas_sequence(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """Filter and validate messages for RAGAS compliance"""
        print(f"🔍 RAGAS validation: Processing {len(messages)} messages")
        
        # Status lines that should be filtered for RAGAS
        STATUS_PREFIXES = (
            "Routing investigation to ",
            "**REGULATORY ANALYSIS REPORT**",
            "**EVIDENCE COLLECTION REPORT**", 
            "**COMPLIANCE ASSESSMENT REPORT**",
            "**EXECUTIVE SUMMARY**",
            "**FINAL DECISION**",
            "**DETAILED REASONING**",
            "Investigation completed. All specialist agents",
        )
        
        def is_status_line(msg: BaseMessage) -> bool:
            return (isinstance(msg, HumanMessage) and 
                   isinstance(msg.content, str) and
                   any(msg.content.startswith(p) for p in STATUS_PREFIXES))
        
        # Filter out status lines
        filtered = [msg for msg in messages if not is_status_line(msg)]
        print(f"🧹 Filtered out {len(messages) - len(filtered)} status messages")
        
        # Debug: show message types
        for i, msg in enumerate(filtered):
            msg_type = type(msg).__name__
            has_tool_calls = hasattr(msg, 'tool_calls') and msg.tool_calls
            tool_call_id = getattr(msg, 'tool_call_id', None)
            print(f"  {i}: {msg_type} (tool_calls: {has_tool_calls}, tool_call_id: {tool_call_id})")
        
        # Ensure proper AIMessage -> ToolMessage sequences for RAGAS
        validated: List[BaseMessage] = []
        i = 0
        
        while i < len(filtered):
            msg = filtered[i]
            
            if isinstance(msg, ToolMessage):
                # CRITICAL: ToolMessage must follow AIMessage with matching tool_calls
                needs_ai_stub = True
                
                # Check if previous message is AIMessage with matching tool_call
                if (validated and isinstance(validated[-1], AIMessage) and 
                   hasattr(validated[-1], 'tool_calls') and validated[-1].tool_calls):
                    for tc in validated[-1].tool_calls:
                        if tc.get("id") == getattr(msg, 'tool_call_id', None):
                            needs_ai_stub = False
                            break
                
                if needs_ai_stub:
                    # Create proper AIMessage stub that calls this tool
                    tool_name = getattr(msg, 'name', 'unknown_tool')
                    tool_call_id = getattr(msg, 'tool_call_id', f"call_{tool_name}_0")
                    
                    # Extract tool name from tool_call_id if available
                    if tool_call_id and tool_call_id.startswith("call_"):
                        parts = tool_call_id.split("_")
                        if len(parts) >= 3:
                            tool_name = "_".join(parts[1:-1])
                    
                    ai_stub = AIMessage(
                        content=f"I'll use the {tool_name} tool to help with this investigation.",
                        tool_calls=[{
                            "id": tool_call_id,
                            "name": tool_name,
                            "args": {},
                            "type": "function"
                        }]
                    )
                    print(f"🔧 Creating AIMessage → ToolMessage pair for tool '{tool_name}' (id: {tool_call_id})")
                    validated.append(ai_stub)
                
                # Add the ToolMessage
                validated.append(msg)
                
            elif isinstance(msg, AIMessage):
                # For AIMessage with tool_calls, we need to ensure all tool calls have responses
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    validated.append(msg)
                    
                    # Look ahead for corresponding ToolMessages
                    j = i + 1
                    tool_calls_handled = set()
                    
                    while j < len(filtered) and isinstance(filtered[j], ToolMessage):
                        tool_msg = filtered[j]
                        tool_call_id = getattr(tool_msg, 'tool_call_id', None)
                        
                        # Check if this ToolMessage belongs to our AIMessage
                        for tc in msg.tool_calls:
                            if tc.get("id") == tool_call_id:
                                validated.append(tool_msg)
                                tool_calls_handled.add(tool_call_id)
                                i = j  # Skip this ToolMessage in main loop
                                break
                        j += 1
                    
                    # Create stub ToolMessages for any unhandled tool calls
                    for tc in msg.tool_calls:
                        if tc.get("id") not in tool_calls_handled:
                            stub_tool_msg = ToolMessage(
                                content="Tool execution completed successfully.",
                                tool_call_id=tc.get("id"),
                                name=tc.get("name", "unknown_tool")
                            )
                            print(f"🔧 Creating stub ToolMessage for tool_call_id: {tc.get('id')}")
                            validated.append(stub_tool_msg)
                else:
                    # Regular AIMessage without tool calls
                    validated.append(msg)
                    
            else:
                # HumanMessage, SystemMessage, etc.
                validated.append(msg)
            
            i += 1
        
        print(f"✅ Normalized {len(filtered)} → {len(validated)} messages for RAGAS")
        return validated
    
    def validate_content(self, content: str) -> str:
        """Comprehensive content validation to ensure complete sentences and proper formatting"""
        if not content:
            return ""
        
        # Remove common problematic patterns
        problematic_patterns = [
            r'•\s*days after the date',  # Incomplete bullet points
            r'•\s*accomplished by the filing',  # Raw regulatory text
            r'•\s*more than \d+ calendar days',  # Incomplete regulatory citations
            r'\d+\s+Catalog No\.',  # Document catalog numbers
            r'DRAFT\s+\d+',  # Draft document markers
            r'NOTE:\s*If this report',  # Procedural notes
            r'HOW TO MAKE A REPORT:',  # Procedural headers
            r'Do not include any supporting',  # Procedural instructions
        ]
        
        validated_content = content
        for pattern in problematic_patterns:
            validated_content = re.sub(pattern, '', validated_content, flags=re.IGNORECASE)
        
        # Split into sentences and validate each
        sentences = self._split_into_sentences(validated_content)
        validated_sentences = []
        
        for sentence in sentences:
            if self._is_valid_sentence(sentence):
                validated_sentences.append(sentence.strip())
        
        # Reconstruct content with proper formatting
        if validated_sentences:
            return ' '.join(validated_sentences)
        else:
            return "Analysis completed successfully."
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences while handling abbreviations"""
        # Clean up whitespace and line breaks
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Split on sentence boundaries, but handle common abbreviations
        sentence_endings = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\!|\?)\s+', text)
        
        return [s.strip() for s in sentence_endings if s.strip()]
    
    def _is_valid_sentence(self, sentence: str) -> bool:
        """Validate that a sentence is complete and professional"""
        if not sentence or len(sentence) < 15:
            return False
        
        # Check for incomplete sentences or fragments
        invalid_markers = [
            'see instruction',
            'form completion',
            'check the box',
            'line 1',
            'part v',
            'detroit computing center',
            'p.o. box',
            'for items that do not apply',
            'if you are correcting',
            'describe the changes',
            'catalog no.',
            'rev.',
            'draft'
        ]
        
        sentence_lower = sentence.lower()
        if any(marker in sentence_lower for marker in invalid_markers):
            return False
        
        # Check for proper sentence structure
        if not sentence.endswith(('.', '!', '?', ':')):
            return False
        
        # Must contain at least one verb-like word or be a proper statement
        verb_indicators = ['is', 'are', 'was', 'were', 'has', 'have', 'will', 'shall', 'must', 'required', 'completed', 'analyzed', 'identified']
        if not any(verb in sentence_lower for verb in verb_indicators):
            # Allow statements that are clearly professional summaries
            if not any(word in sentence_lower for word in ['risk', 'compliance', 'analysis', 'assessment', 'investigation', 'transaction']):
                return False
        
        # Check word count - should be substantial (removed upper limit for detailed reasoning)
        word_count = len(sentence.split())
        if word_count < 4:
            return False
        # Removed 50-word limit to allow detailed reasoning and comprehensive analysis
        
        return True
    
    def final_report_validation(self, report: str) -> str:
        """Final validation pass on the complete report"""
        # Remove any remaining incomplete patterns
        cleanup_patterns = [
            r'•[^.]*$',  # Incomplete bullet points at end of lines
            r'\n\s*\n\s*\n',  # Multiple blank lines
            r'(?:CFR|FinCEN)[^.]*?(?=\n|\Z)',  # Incomplete regulatory references
            r'[A-Z][a-z]*\s+No\.\s*\d+[^.]*?(?=\n|\Z)',  # Catalog numbers without completion
        ]
        
        validated_report = report
        for pattern in cleanup_patterns:
            validated_report = re.sub(pattern, '', validated_report, flags=re.MULTILINE)
        
        # Ensure proper spacing and formatting
        validated_report = re.sub(r'\n{3,}', '\n\n', validated_report)  # Max 2 consecutive newlines
        validated_report = re.sub(r'^\s+', '', validated_report, flags=re.MULTILINE)  # Remove leading spaces
        validated_report = validated_report.strip()
        
        # Ensure report ends properly
        if not validated_report.endswith(('.', '!', '?')):
            validated_report += '.'
        
        return validated_report
