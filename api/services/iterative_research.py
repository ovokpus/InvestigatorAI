"""Iterative Research Agent with Quality Assessment and Feedback Loops

This module implements the sophisticated iterative research pattern from the Open Deep Research
notebook, featuring quality assessment, feedback loops, and multi-iteration refinement.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Literal
from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langsmith import traceable

from .multi_source_research import MultiSourceResearchService, SearchResponse
from ..core.config import Settings

logger = logging.getLogger(__name__)


@dataclass
class ResearchSection:
    """Individual research section with metadata"""
    name: str
    description: str
    research: bool = True
    content: str = ""
    queries: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    iteration_count: int = 0
    quality_score: float = 0.0


@dataclass
class ResearchFeedback:
    """Feedback structure for quality assessment"""
    grade: Literal["pass", "fail"]
    missing_aspects: List[str] = field(default_factory=list)
    follow_up_queries: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    feedback_text: str = ""


@dataclass
class ResearchPlan:
    """Complete research plan with sections"""
    topic: str
    sections: List[ResearchSection] = field(default_factory=list)
    research_depth: int = 2
    query_count: int = 2
    created_at: datetime = field(default_factory=datetime.now)


class ResearchQualityAssessor:
    """Assess quality of research content and provide feedback"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        logger.info("🔍 Initialized ResearchQualityAssessor")
    
    @traceable
    async def grade_research_section(self, content: str, section: ResearchSection, 
                                   requirements: str = "") -> ResearchFeedback:
        """Grade research content quality and provide improvement feedback"""
        logger.info(f"📊 Grading research section: {section.name}")
        
        grading_prompt = f"""
        You are a senior research quality assessor evaluating the completeness and accuracy of research content.
        
        SECTION TO EVALUATE:
        Title: {section.name}
        Description: {section.description}
        Content: {content}
        
        REQUIREMENTS:
        {requirements or "Comprehensive coverage of the topic with accurate information from reliable sources"}
        
        EVALUATION CRITERIA:
        1. Completeness: Does the content fully address the section description?
        2. Accuracy: Is the information factually correct and up-to-date?
        3. Source Quality: Are the sources reliable and authoritative?
        4. Depth: Is the analysis sufficiently detailed for the topic?
        5. Coherence: Is the content well-structured and logical?
        
        ASSESSMENT TASK:
        Evaluate the content and provide:
        1. Grade: "pass" if content meets requirements, "fail" if insufficient
        2. Quality Score: 0.0-1.0 numeric score
        3. Missing Aspects: List specific areas that need improvement
        4. Follow-up Queries: Specific search queries to address deficiencies
        5. Feedback Text: Detailed explanation of assessment
        
        Respond in JSON format:
        {{
            "grade": "pass" or "fail",
            "quality_score": 0.0-1.0,
            "missing_aspects": ["aspect1", "aspect2"],
            "follow_up_queries": ["query1", "query2"],
            "feedback_text": "detailed feedback"
        }}
        """
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a research quality assessor."),
                HumanMessage(content=grading_prompt)
            ])
            
            # Parse the JSON response
            import json
            feedback_data = json.loads(response.content)
            
            feedback = ResearchFeedback(
                grade=feedback_data.get("grade", "fail"),
                quality_score=feedback_data.get("quality_score", 0.0),
                missing_aspects=feedback_data.get("missing_aspects", []),
                follow_up_queries=feedback_data.get("follow_up_queries", []),
                feedback_text=feedback_data.get("feedback_text", "")
            )
            
            logger.info(f"✅ Section graded: {feedback.grade} (score: {feedback.quality_score:.2f})")
            return feedback
            
        except Exception as e:
            logger.error(f"❌ Grading failed: {e}")
            return ResearchFeedback(
                grade="fail",
                quality_score=0.0,
                feedback_text=f"Grading error: {str(e)}"
            )


class IterativeResearchAgent:
    """Advanced research agent with iterative refinement capabilities"""
    
    def __init__(self, llm: ChatOpenAI, research_service: MultiSourceResearchService, 
                 settings: Settings):
        self.llm = llm
        self.research_service = research_service
        self.settings = settings
        self.quality_assessor = ResearchQualityAssessor(llm)
        
        # Configuration from notebook patterns
        self.max_iterations = getattr(settings, 'max_research_iterations', 2)
        self.query_count = getattr(settings, 'research_queries_per_iteration', 2)
        
        logger.info(f"🧠 Initialized IterativeResearchAgent (max_iterations: {self.max_iterations})")
    
    @traceable
    async def generate_search_queries(self, topic: str, section: ResearchSection, 
                                    iteration: int = 0) -> List[str]:
        """Generate targeted search queries for a research section"""
        logger.info(f"🔍 Generating queries for section: {section.name} (iteration {iteration})")
        
        if iteration == 0:
            # Initial query generation
            query_prompt = f"""
            Generate {self.query_count} focused search queries for researching this section:
            
            Topic: {topic}
            Section: {section.name}
            Description: {section.description}
            
            The queries should:
            1. Be specific enough to find high-quality, relevant sources
            2. Cover different aspects of the section topic
            3. Target authoritative and recent information
            4. Be suitable for academic and professional sources
            
            Return only the queries, one per line.
            """
        else:
            # Follow-up query generation based on previous content
            query_prompt = f"""
            Generate {self.query_count} follow-up search queries to improve this research section:
            
            Topic: {topic}
            Section: {section.name}
            Description: {section.description}
            
            Current Content: {section.content[:500]}...
            
            The follow-up queries should:
            1. Address gaps in the current content
            2. Find more recent or authoritative sources
            3. Provide additional depth or alternative perspectives
            4. Target specific missing information
            
            Return only the queries, one per line.
            """
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a research query specialist."),
                HumanMessage(content=query_prompt)
            ])
            
            queries = [q.strip() for q in response.content.split('\n') if q.strip()]
            queries = queries[:self.query_count]  # Limit to configured count
            
            logger.info(f"✅ Generated {len(queries)} search queries")
            return queries
            
        except Exception as e:
            logger.error(f"❌ Query generation failed: {e}")
            return [f"{topic} {section.name}"]  # Fallback query
    
    @traceable
    async def write_section_content(self, topic: str, section: ResearchSection, 
                                  sources: str, iteration: int = 0) -> str:
        """Write or improve section content based on research sources"""
        logger.info(f"✍️ Writing content for section: {section.name} (iteration {iteration})")
        
        if iteration == 0:
            # Initial content writing
            writing_prompt = f"""
            Write comprehensive content for this research section based on the provided sources.
            
            Topic: {topic}
            Section: {section.name}
            Description: {section.description}
            
            Sources:
            {sources}
            
            REQUIREMENTS:
            - Write 300-500 words of high-quality content
            - Use information from the provided sources
            - Maintain professional, analytical tone
            - Include specific facts, figures, and examples
            - Structure with clear paragraphs and logical flow
            - Cite key sources where relevant
            
            Write the content now:
            """
        else:
            # Content refinement
            writing_prompt = f"""
            Improve and expand this research section content using new sources.
            
            Topic: {topic}
            Section: {section.name}
            Description: {section.description}
            
            Current Content:
            {section.content}
            
            New Sources:
            {sources}
            
            IMPROVEMENT REQUIREMENTS:
            - Integrate new information from sources
            - Address any gaps or weaknesses in current content
            - Maintain coherent structure and flow
            - Expand depth and detail where appropriate
            - Ensure accuracy and currency of information
            - Keep total length to 300-600 words
            
            Write the improved content:
            """
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a professional research writer."),
                HumanMessage(content=writing_prompt)
            ])
            
            content = response.content.strip()
            logger.info(f"✅ Generated {len(content)} characters of content")
            return content
            
        except Exception as e:
            logger.error(f"❌ Content writing failed: {e}")
            return f"Error generating content: {str(e)}"
    
    @traceable
    async def research_section_iteratively(self, topic: str, section: ResearchSection,
                                         sources: List[str] = None) -> ResearchSection:
        """Research a section with iterative refinement based on quality feedback"""
        logger.info(f"🔄 Starting iterative research for section: {section.name}")
        
        sources = sources or ["tavily", "arxiv"]
        
        for iteration in range(self.max_iterations):
            logger.info(f"📖 Research iteration {iteration + 1}/{self.max_iterations}")
            
            # Generate search queries
            queries = await self.generate_search_queries(topic, section, iteration)
            section.queries.extend(queries)
            
            # Perform multi-source search
            search_responses = await self.research_service.search_multiple_sources(
                queries, sources
            )
            
            # Format sources
            formatted_sources = self.research_service.deduplicate_and_format_sources(
                search_responses, max_tokens_per_source=1000
            )
            
            # Write/improve content
            new_content = await self.write_section_content(topic, section, formatted_sources, iteration)
            section.content = new_content
            section.iteration_count = iteration + 1
            
            # Quality assessment
            feedback = await self.quality_assessor.grade_research_section(
                section.content, section
            )
            section.quality_score = feedback.quality_score
            
            logger.info(f"📊 Quality assessment: {feedback.grade} (score: {feedback.quality_score:.2f})")
            
            # Check if we should continue iterating
            if feedback.grade == "pass" or iteration >= self.max_iterations - 1:
                logger.info(f"✅ Research completed for section: {section.name}")
                break
                
            if feedback.follow_up_queries:
                logger.info(f"🔄 Continuing with {len(feedback.follow_up_queries)} follow-up queries")
                # Use feedback queries for next iteration
                section.queries.extend(feedback.follow_up_queries[:self.query_count])
        
        return section
    
    @traceable
    async def research_multiple_sections(self, topic: str, sections: List[ResearchSection],
                                       sources: List[str] = None) -> List[ResearchSection]:
        """Research multiple sections concurrently with iterative refinement"""
        logger.info(f"🔬 Starting research for {len(sections)} sections")
        
        # Research sections that require research
        research_sections = [s for s in sections if s.research]
        non_research_sections = [s for s in sections if not s.research]
        
        if research_sections:
            # Run research for each section (could be parallelized further)
            completed_sections = []
            for section in research_sections:
                completed_section = await self.research_section_iteratively(topic, section, sources)
                completed_sections.append(completed_section)
            
            # Combine with non-research sections
            all_sections = completed_sections + non_research_sections
        else:
            all_sections = sections
        
        logger.info(f"✅ Research completed for all sections")
        return all_sections


class ResearchPlanner:
    """Generate structured research plans with dynamic sections"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        logger.info("📋 Initialized ResearchPlanner")
    
    @traceable
    async def generate_research_plan(self, topic: str, context: str = "") -> ResearchPlan:
        """Generate a structured research plan for a given topic"""
        logger.info(f"📋 Generating research plan for: {topic}")
        
        planning_prompt = f"""
        Create a comprehensive research plan for the following topic:
        
        Topic: {topic}
        Context: {context}
        
        Generate 3-5 research sections that provide thorough coverage of the topic.
        Each section should have:
        1. A clear, descriptive name
        2. A detailed description of what it covers
        3. Whether web research is needed (true/false)
        
        Structure the plan logically:
        - Start with introduction/overview (research: false)
        - Include 2-3 main research sections (research: true)
        - End with conclusion/summary (research: false)
        
        Respond in JSON format:
        {{
            "sections": [
                {{
                    "name": "Section Name",
                    "description": "Detailed description of section content and scope",
                    "research": true/false
                }}
            ]
        }}
        """
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a research planning specialist."),
                HumanMessage(content=planning_prompt)
            ])
            
            import json
            plan_data = json.loads(response.content)
            
            sections = []
            for section_data in plan_data.get("sections", []):
                section = ResearchSection(
                    name=section_data.get("name", "Unknown Section"),
                    description=section_data.get("description", ""),
                    research=section_data.get("research", True)
                )
                sections.append(section)
            
            plan = ResearchPlan(topic=topic, sections=sections)
            logger.info(f"✅ Generated research plan with {len(sections)} sections")
            return plan
            
        except Exception as e:
            logger.error(f"❌ Research planning failed: {e}")
            # Create a fallback basic plan
            fallback_sections = [
                ResearchSection(name="Introduction", description=f"Overview of {topic}", research=False),
                ResearchSection(name="Main Analysis", description=f"Detailed analysis of {topic}", research=True),
                ResearchSection(name="Conclusion", description=f"Summary and implications of {topic}", research=False)
            ]
            return ResearchPlan(topic=topic, sections=fallback_sections)
