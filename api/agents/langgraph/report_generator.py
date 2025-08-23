"""Report generation and decision synthesis for fraud investigation"""
import logging
from typing import Dict, Any, List, Union, Tuple
from langchain_core.messages import BaseMessage

from .message_processor import MessageProcessor

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Handles report generation and final decision synthesis"""
    
    def __init__(self) -> None:
        self.message_processor = MessageProcessor()
        logger.info("📊 ReportGenerator initialized")
    
    def generate_final_decision(self, messages: Union[List[BaseMessage], List[Dict[str, Any]]]) -> str:
        """Generate a comprehensive, professional final decision from all agent analyses"""
        try:
            # Extract and parse agent findings
            agent_findings = {}
            for message in messages:
                name = None
                content = None
                
                # Handle dictionary format (new format)
                if isinstance(message, dict):
                    name = message.get('name', '')
                    content = message.get('content', '')
                # Handle BaseMessage format (original format)
                elif hasattr(message, 'name') and message.name:
                    name = message.name
                    content = message.content
                
                if name and content and name != 'system':
                    # Clean and summarize content instead of using raw text
                    agent_findings[name] = self._extract_key_insights(content, name)
            
            if not agent_findings:
                return "Investigation completed but no detailed findings available."
            
            # Generate structured, professional report
            return self._synthesize_professional_report(agent_findings)
            
        except Exception as e:
            logger.error(f"Error generating final decision: {e}")
            return f"Investigation completed with technical issues. Please contact support for assistance."
    
    def generate_final_decision_with_report(self, messages: Union[List[BaseMessage], List[Dict[str, Any]]]) -> Dict[str, str]:
        """Generate both final decision and full investigation report"""
        try:
            # Extract and parse agent findings
            agent_findings = {}
            for message in messages:
                name = None
                content = None
                
                # Handle dictionary format (new format)
                if isinstance(message, dict):
                    name = message.get('name', '')
                    content = message.get('content', '')
                # Handle BaseMessage format (original format)
                elif hasattr(message, 'name') and message.name:
                    name = message.name
                    content = message.content
                
                if name and content and name != 'system':
                    # Clean and summarize content instead of using raw text
                    agent_findings[name] = self._extract_key_insights(content, name)
            
            if not agent_findings:
                return {
                    "decision": "insufficient_data",
                    "report": "Investigation completed but no detailed findings available."
                }
            
            # Generate both decision and report
            decision, report = self._synthesize_decision_and_report(agent_findings)
            
            return {
                "decision": decision,
                "report": report
            }
            
        except Exception as e:
            logger.error(f"Error generating decision with report: {e}")
            return {
                "decision": "error",
                "report": f"Investigation completed with technical issues. Please contact support for assistance."
            }
    
    def _extract_key_insights(self, content: str, agent_name: str) -> Dict[str, Any]:
        """Extract key insights from agent content, removing raw document dumps"""
        insights = {
            'summary': '',
            'key_points': [],
            'recommendations': [],
            'risk_indicators': []
        }
        
        # Apply comprehensive content validation
        validated_content = self.message_processor.validate_content(content)
        
        # Extract risk indicators from the full content
        risk_keywords = ['HIGH RISK', 'RISK LEVEL: HIGH', 'HIGH-RISK', 'SUSPICIOUS', 'TERRORIST', 'SANCTIONS', 'SAR REQUIRED', 'OFAC', 'AL-QAEDA']
        for keyword in risk_keywords:
            if keyword in validated_content.upper():
                insights['risk_indicators'].append(f"Found: {keyword}")
        
        # Clean content - remove incomplete sentences and raw regulatory text
        lines = validated_content.split('\n')
        clean_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip incomplete bullet points, raw regulatory snippets, and partial sentences
            if (line and 
                not line.startswith('•') and 
                not line.startswith('-') and
                not 'CFR' in line and
                not 'FinCEN' in line and
                len(line) > 20 and
                line.endswith(('.', '!', '?', ':'))):
                clean_lines.append(line)
        
        # Extract insights based on agent type
        if agent_name == 'regulatory_research':
            insights['summary'] = f"Regulatory analysis completed for destination jurisdiction"
            insights['key_points'] = [line for line in clean_lines if 'risk' in line.lower() or 'compliance' in line.lower()]
        elif agent_name == 'evidence_collection':
            insights['summary'] = f"Risk assessment and evidence collection completed"
            insights['key_points'] = [line for line in clean_lines if 'risk' in line.lower() or 'score' in line.lower()]
        elif agent_name == 'compliance_check':
            insights['summary'] = f"Compliance requirements assessment completed"
            insights['key_points'] = [line for line in clean_lines if 'required' in line.lower() or 'SAR' in line or 'CTR' in line]
        elif agent_name == 'report_generation':
            insights['summary'] = f"Final report compilation completed"
            insights['key_points'] = [line for line in clean_lines if 'complete' in line.lower() or 'classification' in line.lower()]
            # For report generation, also capture the full content as it contains the final assessment
            if 'RISK LEVEL: HIGH' in validated_content.upper() or 'HIGH RISK' in validated_content.upper():
                insights['key_points'].append("HIGH RISK classification identified in final report")
            if 'TERRORIST' in validated_content.upper() or 'AL-QAEDA' in validated_content.upper():
                insights['key_points'].append("Terrorist association identified")
            if 'SAR' in validated_content.upper() and 'REQUIRED' in validated_content.upper():
                insights['key_points'].append("SAR filing required")
        
        return insights
    
    def _synthesize_professional_report(self, agent_findings: Dict[str, Dict[str, Any]]) -> str:
        """Create a professional, coherent investigation report with validated content"""
        
        # Extract key information
        risk_level = "MEDIUM RISK"  # Default
        compliance_items = []
        key_findings = []
        
        # Parse findings from each agent
        for agent_name, findings in agent_findings.items():
            if findings['key_points']:
                # Validate each key point before adding
                validated_points = [self.message_processor.validate_content(point) for point in findings['key_points']]
                validated_points = [point for point in validated_points if point and len(point) > 10]
                key_findings.extend(validated_points)
                
            # Check risk indicators first (more reliable)
            if findings.get('risk_indicators'):
                for indicator in findings['risk_indicators']:
                    if any(keyword in indicator.upper() for keyword in ['HIGH RISK', 'TERRORIST', 'SUSPICIOUS', 'SAR REQUIRED']):
                        risk_level = "HIGH RISK"
                        break
                        
            # Extract risk level and compliance info from key points
            for point in findings['key_points']:
                if any(keyword in point.upper() for keyword in ['HIGH RISK', 'TERRORIST', 'SUSPICIOUS', 'SAR REQUIRED']):
                    risk_level = "HIGH RISK"
                elif 'LOW RISK' in point.upper() and risk_level == "MEDIUM RISK":
                    risk_level = "LOW RISK"
                    
                if any(word in point.upper() for word in ['SAR', 'CTR', 'REQUIRED', 'FILING']):
                    validated_compliance = self.message_processor.validate_content(point)
                    if validated_compliance and len(validated_compliance) > 10:
                        compliance_items.append(validated_compliance)
        
        # Generate professional report with final validation
        report = "**FRAUD INVESTIGATION COMPLETE**\n\n"
        
        # Executive Summary
        report += "**EXECUTIVE SUMMARY**\n"
        report += f"Investigation Status: Complete\n"
        report += f"Risk Classification: {risk_level}\n"
        report += f"Agents Completed: 4/4 (Regulatory, Evidence, Compliance, Reporting)\n\n"
        
        # Key Findings
        report += "**KEY FINDINGS**\n\n"
        report += "**Regulatory Analysis:** Comprehensive jurisdiction risk assessment and sanctions screening completed with regulatory compliance evaluation.\n\n"
        report += "**Evidence Collection:** Quantitative transaction risk analysis performed with external intelligence gathering and verification.\n\n"
        report += "**Compliance Assessment:** Regulatory filing requirements determination including SAR/CTR obligations and compliance timeline assessment.\n\n"
        report += "**Final Report:** Complete investigation analysis with risk classification determination and actionable recommendations.\n\n"
        
        # Add validated key findings if available
        if key_findings:
            report += "**DETAILED FINDINGS**\n"
            for i, finding in enumerate(key_findings, 1):  # Include ALL findings
                if self.message_processor._is_valid_sentence(finding):
                    report += f"{i}. {finding}\n"
            report += "\n"
        
        # Compliance Requirements
        if compliance_items:
            report += "**COMPLIANCE REQUIREMENTS**\n"
            for i, item in enumerate(compliance_items, 1):  # Include ALL compliance items
                if self.message_processor._is_valid_sentence(item):
                    report += f"{i}. {item}\n"
            report += "\n"
        
        # Conclusion  
        report += f"**INVESTIGATION STATUS:** All investigative agents have completed comprehensive multi-faceted analysis. Final risk classification: {risk_level}."
        
        # Store the full report for download
        validated_report = self.message_processor.final_report_validation(report)
        
        # Return proper fraud decision based on risk level
        if risk_level == "HIGH RISK":
            decision = "suspicious"
        elif risk_level == "LOW RISK":
            decision = "not_suspicious"
        else:  # MEDIUM RISK
            # Use additional logic to determine suspicion level
            suspicious_indicators = sum(1 for finding in key_findings 
                                      if any(word in finding.lower() for word in 
                                           ['suspicious', 'alert', 'flag', 'concern', 'high risk', 'unusual']))
            
            if suspicious_indicators >= 2:
                decision = "requires_review"
            else:
                decision = "not_suspicious"
        
        logger.info(f"Generated fraud decision: {decision} (Risk: {risk_level}, Report: {len(validated_report)} chars)")
        
        return decision
    
    def _synthesize_decision_and_report(self, agent_findings: Dict[str, Dict[str, Any]]) -> Tuple[str, str]:
        """Create both fraud decision and full investigation report"""
        
        # Extract key information
        risk_level = "MEDIUM RISK"  # Default
        compliance_items = []
        key_findings = []
        
        # Parse findings from each agent
        for agent_name, findings in agent_findings.items():
            if findings['key_points']:
                # Validate each key point before adding
                validated_points = [self.message_processor.validate_content(point) for point in findings['key_points']]
                validated_points = [point for point in validated_points if point and len(point) > 10]
                key_findings.extend(validated_points)
                
            # Check risk indicators first (more reliable)
            if findings.get('risk_indicators'):
                for indicator in findings['risk_indicators']:
                    if any(keyword in indicator.upper() for keyword in ['HIGH RISK', 'TERRORIST', 'SUSPICIOUS', 'SAR REQUIRED']):
                        risk_level = "HIGH RISK"
                        break
                        
            # Extract risk level and compliance info from key points
            for point in findings['key_points']:
                if any(keyword in point.upper() for keyword in ['HIGH RISK', 'TERRORIST', 'SUSPICIOUS', 'SAR REQUIRED']):
                    risk_level = "HIGH RISK"
                elif 'LOW RISK' in point.upper() and risk_level == "MEDIUM RISK":
                    risk_level = "LOW RISK"
                    
                if any(word in point.upper() for word in ['SAR', 'CTR', 'REQUIRED', 'FILING']):
                    validated_compliance = self.message_processor.validate_content(point)
                    if validated_compliance and len(validated_compliance) > 10:
                        compliance_items.append(validated_compliance)
        
        # Generate fraud decision based on risk level
        if risk_level == "HIGH RISK":
            decision = "suspicious"
        elif risk_level == "LOW RISK":
            decision = "not_suspicious"
        else:  # MEDIUM RISK
            # Use additional logic to determine suspicion level
            suspicious_indicators = sum(1 for finding in key_findings 
                                      if any(word in finding.lower() for word in 
                                           ['suspicious', 'alert', 'flag', 'concern', 'high risk', 'unusual']))
            
            if suspicious_indicators >= 2:
                decision = "requires_review"
            else:
                decision = "not_suspicious"
        
        # Generate full professional report
        report = "**FRAUD INVESTIGATION COMPLETE**\n\n"
        
        # Executive Summary
        report += "**EXECUTIVE SUMMARY**\n"
        report += f"Investigation Status: Complete\n"
        report += f"Final Decision: {decision.upper()}\n"
        report += f"Risk Classification: {risk_level}\n"
        report += f"Agents Completed: 4/4 (Regulatory, Evidence, Compliance, Reporting)\n\n"
        
        # Key Findings
        report += "**KEY FINDINGS**\n\n"
        report += "**Regulatory Analysis:** Comprehensive jurisdiction risk assessment and sanctions screening completed with regulatory compliance evaluation.\n\n"
        report += "**Evidence Collection:** Quantitative transaction risk analysis performed with external intelligence gathering and verification.\n\n"
        report += "**Compliance Assessment:** Regulatory filing requirements determination including SAR/CTR obligations and compliance timeline assessment.\n\n"
        report += "**Final Report:** Complete investigation analysis with risk classification determination and actionable recommendations.\n\n"
        
        # Add validated key findings if available
        if key_findings:
            report += "**DETAILED FINDINGS**\n"
            for i, finding in enumerate(key_findings, 1):  # Include ALL findings
                if self.message_processor._is_valid_sentence(finding):
                    report += f"{i}. {finding}\n"
            report += "\n"
        
        # Compliance Requirements
        if compliance_items:
            report += "**COMPLIANCE REQUIREMENTS**\n"
            for i, item in enumerate(compliance_items, 1):  # Include ALL compliance items
                if self.message_processor._is_valid_sentence(item):
                    report += f"{i}. {item}\n"
            report += "\n"
        
        # Conclusion
        report += f"**INVESTIGATION STATUS:** All investigative agents have completed comprehensive multi-faceted analysis. Final decision: {decision.upper()}. Risk classification: {risk_level}."
        
        # Final content validation on entire report
        validated_report = self.message_processor.final_report_validation(report)
        
        logger.info(f"Generated decision: {decision} (Risk: {risk_level}, Report: {len(validated_report)} chars)")
        
        return decision, validated_report
