"""Domain-Specific Research Agents

This module provides specialized research agents tailored for different domains,
particularly financial crime investigation, academic research, and regulatory compliance.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langsmith import traceable

from .multi_source_research import MultiSourceResearchService, SearchResponse
from .iterative_research import IterativeResearchAgent, ResearchSection, ResearchPlan, ResearchPlanner
from ..core.config import Settings

logger = logging.getLogger(__name__)


@dataclass
class EntityInvestigationResult:
    """Result from entity investigation"""
    entity_name: str
    entity_type: str
    risk_level: str
    findings: List[str]
    sources: List[str]
    compliance_issues: List[str]
    recommendations: List[str]
    investigation_date: datetime
    confidence_score: float = 0.0


@dataclass
class AcademicResearchResult:
    """Result from academic research"""
    topic: str
    papers_found: int
    key_findings: List[str]
    methodologies: List[str]
    future_research: List[str]
    citations: List[str]
    research_gaps: List[str]


class BaseSpecializedAgent(ABC):
    """Base class for specialized research agents"""
    
    def __init__(self, llm: ChatOpenAI, research_service: MultiSourceResearchService, 
                 settings: Settings):
        self.llm = llm
        self.research_service = research_service
        self.settings = settings
        self.iterative_agent = IterativeResearchAgent(llm, research_service, settings)
        
    @abstractmethod
    async def conduct_specialized_research(self, **kwargs) -> Dict[str, Any]:
        """Conduct domain-specific research"""
        pass


class FinancialResearchAgent(BaseSpecializedAgent):
    """Specialized agent for financial crime investigation and AML research"""
    
    def __init__(self, llm: ChatOpenAI, research_service: MultiSourceResearchService, 
                 settings: Settings):
        super().__init__(llm, research_service, settings)
        
        # Specialized sources for financial research
        self.financial_sources = ["tavily", "arxiv"]  # Could add specialized financial DBs
        
        # High-risk indicators from your existing system
        self.high_risk_countries = ['UAE', 'IRAN', 'RUSSIA', 'CHINA', 'AFGHANISTAN', 'SYRIA']
        
        logger.info("💰 Initialized FinancialResearchAgent")
    
    @traceable
    async def research_entity(self, entity_name: str, entity_type: str = "company",
                            investigation_context: str = "") -> EntityInvestigationResult:
        """Research financial entity with comprehensive AML/compliance focus"""
        logger.info(f"🔍 Investigating entity: {entity_name} (type: {entity_type})")
        
        # Generate specialized financial queries
        queries = await self._generate_financial_queries(entity_name, entity_type, investigation_context)
        
        # Conduct multi-source search
        search_responses = await self.research_service.search_multiple_sources(
            queries, self.financial_sources
        )
        
        # Analyze findings with financial crime focus
        analysis = await self._analyze_financial_findings(entity_name, entity_type, search_responses)
        
        # Assess compliance risks
        compliance_assessment = await self._assess_compliance_risks(entity_name, analysis)
        
        return EntityInvestigationResult(
            entity_name=entity_name,
            entity_type=entity_type,
            risk_level=analysis.get("risk_level", "UNKNOWN"),
            findings=analysis.get("findings", []),
            sources=analysis.get("sources", []),
            compliance_issues=compliance_assessment.get("issues", []),
            recommendations=compliance_assessment.get("recommendations", []),
            investigation_date=datetime.now(),
            confidence_score=analysis.get("confidence_score", 0.0)
        )
    
    async def _generate_financial_queries(self, entity_name: str, entity_type: str,
                                        context: str = "") -> List[str]:
        """Generate specialized queries for financial entity research"""
        query_prompt = f"""
        Generate 4-5 specialized search queries for investigating this financial entity:
        
        Entity: {entity_name}
        Type: {entity_type}
        Context: {context}
        
        Focus on:
        1. Sanctions screening and OFAC listings
        2. AML/compliance violations and penalties
        3. Regulatory enforcement actions
        4. Beneficial ownership and corporate structure
        5. Suspicious activity reports or investigations
        6. International correspondent banking relationships
        7. High-risk jurisdiction connections
        
        Return specific, targeted queries that would reveal compliance risks.
        Format: One query per line.
        """
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a financial crimes investigator."),
                HumanMessage(content=query_prompt)
            ])
            
            queries = [q.strip() for q in response.content.split('\n') if q.strip()]
            
            # Add standard financial crime queries
            standard_queries = [
                f'"{entity_name}" OFAC sanctions screening',
                f'"{entity_name}" AML compliance violations',
                f'"{entity_name}" FinCEN enforcement',
                f'"{entity_name}" suspicious activity reports',
                f'"{entity_name}" beneficial ownership'
            ]
            
            # Combine and deduplicate
            all_queries = list(set(queries + standard_queries))[:6]
            
            logger.info(f"🔍 Generated {len(all_queries)} financial research queries")
            return all_queries
            
        except Exception as e:
            logger.error(f"❌ Query generation failed: {e}")
            return [f'"{entity_name}" financial crime investigation']
    
    async def _analyze_financial_findings(self, entity_name: str, entity_type: str,
                                        search_responses: List[SearchResponse]) -> Dict[str, Any]:
        """Analyze search results with financial crime expertise"""
        
        # Format sources for analysis
        formatted_sources = self.research_service.deduplicate_and_format_sources(
            search_responses, max_tokens_per_source=2000
        )
        
        analysis_prompt = f"""
        Analyze these search results for financial crime risks regarding: {entity_name}
        
        Sources:
        {formatted_sources}
        
        Provide comprehensive analysis covering:
        
        1. RISK LEVEL ASSESSMENT (HIGH/MEDIUM/LOW):
        - Overall risk classification with justification
        
        2. KEY FINDINGS:
        - Sanctions or enforcement actions
        - Regulatory violations or penalties
        - Suspicious activity indicators
        - High-risk jurisdiction connections
        - Beneficial ownership concerns
        
        3. RISK FACTORS:
        - Specific compliance red flags
        - Transaction pattern concerns
        - Geographic risk factors
        - Industry-specific risks
        
        4. CONFIDENCE ASSESSMENT:
        - Reliability of sources (0.0-1.0 score)
        - Information gaps or limitations
        
        Respond in JSON format:
        {{
            "risk_level": "HIGH/MEDIUM/LOW",
            "findings": ["finding1", "finding2"],
            "risk_factors": ["factor1", "factor2"],
            "sources": ["source1", "source2"],
            "confidence_score": 0.0-1.0,
            "analysis_summary": "text"
        }}
        """
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a senior AML compliance analyst."),
                HumanMessage(content=analysis_prompt)
            ])
            
            analysis = json.loads(response.content)
            logger.info(f"✅ Financial analysis completed - Risk: {analysis.get('risk_level', 'UNKNOWN')}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Financial analysis failed: {e}")
            return {
                "risk_level": "UNKNOWN",
                "findings": [f"Analysis error: {str(e)}"],
                "confidence_score": 0.0
            }
    
    async def _assess_compliance_risks(self, entity_name: str, 
                                     analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess specific compliance obligations and recommendations"""
        
        compliance_prompt = f"""
        Based on this financial risk analysis for {entity_name}, determine:
        
        Analysis Summary: {analysis.get('analysis_summary', '')}
        Risk Level: {analysis.get('risk_level', 'UNKNOWN')}
        Key Findings: {analysis.get('findings', [])}
        
        Provide specific compliance guidance:
        
        1. COMPLIANCE ISSUES:
        - SAR filing requirements
        - Enhanced due diligence needs
        - Transaction monitoring obligations
        - Regulatory reporting requirements
        
        2. RECOMMENDATIONS:
        - Immediate actions required
        - Risk mitigation strategies
        - Ongoing monitoring requirements
        - Documentation needs
        
        Respond in JSON format:
        {{
            "issues": ["issue1", "issue2"],
            "recommendations": ["rec1", "rec2"],
            "required_actions": ["action1", "action2"],
            "monitoring_requirements": ["req1", "req2"]
        }}
        """
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a compliance officer providing regulatory guidance."),
                HumanMessage(content=compliance_prompt)
            ])
            
            assessment = json.loads(response.content)
            logger.info(f"✅ Compliance assessment completed")
            return assessment
            
        except Exception as e:
            logger.error(f"❌ Compliance assessment failed: {e}")
            return {
                "issues": [f"Assessment error: {str(e)}"],
                "recommendations": ["Conduct manual compliance review"]
            }
    
    @traceable
    async def conduct_specialized_research(self, investigation_request: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct comprehensive financial investigation"""
        logger.info("🏦 Starting specialized financial research")
        
        # Extract investigation parameters
        entity_name = investigation_request.get("entity_name", "")
        entity_type = investigation_request.get("entity_type", "company")
        context = investigation_request.get("context", "")
        
        # Conduct entity investigation
        investigation_result = await self.research_entity(entity_name, entity_type, context)
        
        # Additional financial context research if needed
        if investigation_request.get("include_market_analysis", False):
            market_analysis = await self._research_market_context(entity_name, entity_type)
            investigation_result.findings.extend(market_analysis.get("findings", []))
        
        return {
            "type": "financial_investigation",
            "result": investigation_result,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _research_market_context(self, entity_name: str, entity_type: str) -> Dict[str, Any]:
        """Research market and industry context"""
        queries = [
            f'"{entity_name}" market analysis financial performance',
            f'"{entity_name}" industry peers comparison',
            f'"{entity_name}" financial statements SEC filings'
        ]
        
        search_responses = await self.research_service.search_multiple_sources(
            queries, ["tavily"]
        )
        
        return {
            "findings": [f"Market research completed for {entity_name}"],
            "sources": [resp.source for resp in search_responses]
        }


class AcademicResearchAgent(BaseSpecializedAgent):
    """Specialized agent for academic and scientific research"""
    
    def __init__(self, llm: ChatOpenAI, research_service: MultiSourceResearchService, 
                 settings: Settings):
        super().__init__(llm, research_service, settings)
        
        # Specialized sources for academic research
        self.academic_sources = ["arxiv", "tavily"]  # Could add PubMed, Google Scholar
        
        logger.info("🎓 Initialized AcademicResearchAgent")
    
    @traceable
    async def research_academic_topic(self, topic: str, field: str = "general",
                                    research_depth: str = "comprehensive") -> AcademicResearchResult:
        """Conduct comprehensive academic research on a topic"""
        logger.info(f"📚 Researching academic topic: {topic} (field: {field})")
        
        # Generate academic-focused queries
        queries = await self._generate_academic_queries(topic, field)
        
        # Search academic sources
        search_responses = await self.research_service.search_multiple_sources(
            queries, self.academic_sources
        )
        
        # Analyze academic findings
        analysis = await self._analyze_academic_findings(topic, field, search_responses)
        
        return AcademicResearchResult(
            topic=topic,
            papers_found=analysis.get("papers_found", 0),
            key_findings=analysis.get("key_findings", []),
            methodologies=analysis.get("methodologies", []),
            future_research=analysis.get("future_research", []),
            citations=analysis.get("citations", []),
            research_gaps=analysis.get("research_gaps", [])
        )
    
    async def _generate_academic_queries(self, topic: str, field: str) -> List[str]:
        """Generate academic-focused research queries"""
        query_prompt = f"""
        Generate 4-5 academic research queries for this topic:
        
        Topic: {topic}
        Field: {field}
        
        Focus on:
        1. Recent research papers and publications
        2. Methodological approaches and frameworks
        3. Current state of the art
        4. Research gaps and future directions
        5. Key researchers and institutions
        
        Generate specific queries suitable for academic databases.
        Format: One query per line.
        """
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are an academic research specialist."),
                HumanMessage(content=query_prompt)
            ])
            
            queries = [q.strip() for q in response.content.split('\n') if q.strip()]
            
            logger.info(f"📖 Generated {len(queries)} academic research queries")
            return queries[:5]
            
        except Exception as e:
            logger.error(f"❌ Academic query generation failed: {e}")
            return [f"{topic} {field} research"]
    
    async def _analyze_academic_findings(self, topic: str, field: str,
                                       search_responses: List[SearchResponse]) -> Dict[str, Any]:
        """Analyze academic search results"""
        
        formatted_sources = self.research_service.deduplicate_and_format_sources(
            search_responses, max_tokens_per_source=3000
        )
        
        analysis_prompt = f"""
        Analyze these academic sources for comprehensive research on: {topic}
        
        Sources:
        {formatted_sources}
        
        Provide analysis covering:
        
        1. KEY FINDINGS:
        - Main research conclusions
        - Significant discoveries or insights
        - Consensus and controversies
        
        2. METHODOLOGIES:
        - Research approaches used
        - Experimental designs
        - Analytical techniques
        
        3. RESEARCH GAPS:
        - Identified limitations
        - Areas needing further research
        - Methodological gaps
        
        4. FUTURE DIRECTIONS:
        - Recommended research directions
        - Emerging trends
        - Potential applications
        
        Respond in JSON format:
        {{
            "papers_found": number,
            "key_findings": ["finding1", "finding2"],
            "methodologies": ["method1", "method2"],
            "research_gaps": ["gap1", "gap2"],
            "future_research": ["direction1", "direction2"],
            "citations": ["citation1", "citation2"]
        }}
        """
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a senior academic researcher."),
                HumanMessage(content=analysis_prompt)
            ])
            
            analysis = json.loads(response.content)
            logger.info(f"✅ Academic analysis completed - {analysis.get('papers_found', 0)} papers found")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Academic analysis failed: {e}")
            return {
                "papers_found": 0,
                "key_findings": [f"Analysis error: {str(e)}"]
            }
    
    @traceable
    async def conduct_specialized_research(self, research_request: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct comprehensive academic research"""
        logger.info("🎓 Starting specialized academic research")
        
        topic = research_request.get("topic", "")
        field = research_request.get("field", "general")
        depth = research_request.get("depth", "comprehensive")
        
        # Conduct academic research
        research_result = await self.research_academic_topic(topic, field, depth)
        
        return {
            "type": "academic_research",
            "result": research_result,
            "timestamp": datetime.now().isoformat()
        }


class EnhancedInvestigatorAI:
    """Enhanced investigator combining specialized agents with advanced research capabilities"""
    
    def __init__(self, llm: ChatOpenAI, research_service: MultiSourceResearchService,
                 settings: Settings):
        self.llm = llm
        self.research_service = research_service
        self.settings = settings
        
        # Initialize specialized agents
        self.financial_agent = FinancialResearchAgent(llm, research_service, settings)
        self.academic_agent = AcademicResearchAgent(llm, research_service, settings)
        self.iterative_agent = IterativeResearchAgent(llm, research_service, settings)
        self.research_planner = ResearchPlanner(llm)
        
        logger.info("🚀 Initialized EnhancedInvestigatorAI with specialized agents")
    
    @traceable
    async def investigate_with_domain_expertise(self, investigation_request: Dict[str, Any]) -> Dict[str, Any]:
        """Route investigation to appropriate specialized agent"""
        investigation_type = investigation_request.get("type", "general")
        
        if investigation_type == "financial":
            return await self.financial_agent.conduct_specialized_research(investigation_request)
        elif investigation_type == "academic":
            return await self.academic_agent.conduct_specialized_research(investigation_request)
        else:
            # Use general iterative research for other types
            topic = investigation_request.get("topic", "")
            research_plan = await self.research_planner.generate_research_plan(topic)
            
            sections = await self.iterative_agent.research_multiple_sections(
                topic, research_plan.sections
            )
            
            return {
                "type": "general_research",
                "result": {
                    "topic": topic,
                    "sections": sections,
                    "plan": research_plan
                },
                "timestamp": datetime.now().isoformat()
            }
