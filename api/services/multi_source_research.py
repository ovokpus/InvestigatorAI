"""Enhanced Multi-Source Research Service for InvestigatorAI

This module implements sophisticated concurrent research capabilities inspired by the
Open Deep Research notebook pattern, enabling multi-source data gathering with 
advanced source processing and deduplication.
"""

import asyncio
import json
import logging
import os
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

import requests
from langsmith import traceable

from ..core.config import Settings

logger = logging.getLogger(__name__)


class SearchAPI(Enum):
    """Supported search APIs"""
    TAVILY = "tavily"
    ARXIV = "arxiv"
    PUBMED = "pubmed"
    EXA = "exa"
    PERPLEXITY = "perplexity"


@dataclass
class SearchQuery:
    """Individual search query object"""
    search_query: str
    source: Optional[str] = None


@dataclass
class SearchResult:
    """Standardized search result format"""
    title: str
    url: str
    content: str
    score: float = 0.0
    raw_content: Optional[str] = None
    source: str = ""
    query: str = ""


@dataclass
class SearchResponse:
    """Search response containing multiple results"""
    query: str
    source: str
    results: List[SearchResult] = field(default_factory=list)
    follow_up_questions: Optional[List[str]] = None
    answer: Optional[str] = None
    images: List[str] = field(default_factory=list)
    error: Optional[str] = None


class MultiSourceResearchService:
    """Enhanced research service supporting multiple concurrent data sources"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        logger.info("🔬 Initializing MultiSourceResearchService")
        
        # API parameters for different sources
        self.search_api_params = {
            "tavily": [],
            "arxiv": ["max_results", "get_full_documents", "load_all_available_meta"],
            "pubmed": ["top_k_results", "email", "api_key", "doc_content_chars_max"],
            "exa": ["max_characters", "num_results", "include_domains", "exclude_domains", "subpages"],
            "perplexity": []
        }
        
    def get_search_params(self, search_api: str, search_api_config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Filter configuration to include only valid parameters for specific search API"""
        accepted_params = self.search_api_params.get(search_api, [])
        
        if not search_api_config:
            return {}
            
        return {k: v for k, v in search_api_config.items() if k in accepted_params}
    
    @traceable
    async def search_tavily_async(self, search_queries: List[str], **kwargs) -> List[SearchResponse]:
        """Asynchronous Tavily search with concurrent processing"""
        logger.info(f"🌐 Starting Tavily async search for {len(search_queries)} queries")
        
        if not self.settings.tavily_search_api_key:
            logger.warning("❌ Tavily API key not available")
            return [SearchResponse(query=q, source="tavily", error="API key not available") for q in search_queries]
        
        search_responses = []
        
        async def search_single_query(query: str) -> SearchResponse:
            """Search single query with Tavily"""
            try:
                url = "https://api.tavily.com/search"
                payload = {
                    "api_key": self.settings.tavily_search_api_key,
                    "query": query,
                    "max_results": kwargs.get("max_results", 5),
                    "search_depth": "basic",
                    "include_raw_content": kwargs.get("include_raw_content", True),
                    "topic": "general"
                }
                
                # Use aiohttp for async requests
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload, timeout=30) as response:
                        if response.status == 200:
                            data = await response.json()
                            results = []
                            
                            for result_data in data.get('results', []):
                                result = SearchResult(
                                    title=result_data.get('title', 'No title'),
                                    url=result_data.get('url', ''),
                                    content=result_data.get('content', ''),
                                    score=result_data.get('score', 0.0),
                                    raw_content=result_data.get('raw_content'),
                                    source="tavily",
                                    query=query
                                )
                                results.append(result)
                            
                            return SearchResponse(
                                query=query,
                                source="tavily",
                                results=results,
                                follow_up_questions=data.get('follow_up_questions'),
                                answer=data.get('answer'),
                                images=data.get('images', [])
                            )
                        else:
                            error_msg = f"Tavily API error: {response.status}"
                            logger.error(error_msg)
                            return SearchResponse(query=query, source="tavily", error=error_msg)
                            
            except Exception as e:
                error_msg = f"Tavily search failed: {str(e)}"
                logger.error(f"❌ {error_msg}")
                return SearchResponse(query=query, source="tavily", error=error_msg)
        
        # Execute all searches concurrently
        tasks = [search_single_query(query) for query in search_queries]
        search_responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_responses = []
        for i, response in enumerate(search_responses):
            if isinstance(response, Exception):
                logger.error(f"Search task failed: {response}")
                processed_responses.append(
                    SearchResponse(query=search_queries[i], source="tavily", error=str(response))
                )
            else:
                processed_responses.append(response)
        
        logger.info(f"✅ Tavily async search completed - {len(processed_responses)} responses")
        return processed_responses
    
    @traceable
    async def search_arxiv_async(self, search_queries: List[str], 
                                load_max_docs: int = 5, 
                                get_full_documents: bool = True,
                                load_all_available_meta: bool = True) -> List[SearchResponse]:
        """Asynchronous arXiv search"""
        logger.info(f"📚 Starting arXiv async search for {len(search_queries)} queries")
        
        async def search_single_query(query: str) -> SearchResponse:
            """Search single query on arXiv"""
            try:
                encoded_query = urllib.parse.quote_plus(query)
                url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results={load_max_docs}"
                
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=30) as response:
                        if response.status == 200:
                            content = await response.text()
                            root = ET.fromstring(content)
                            
                            entries = root.findall('{http://www.w3.org/2005/Atom}entry')
                            results = []
                            
                            for i, entry in enumerate(entries):
                                title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
                                summary_elem = entry.find('{http://www.w3.org/2005/Atom}summary')
                                id_elem = entry.find('{http://www.w3.org/2005/Atom}id')
                                
                                title = title_elem.text.strip() if title_elem is not None else "No title"
                                summary = summary_elem.text.strip() if summary_elem is not None else "No summary"
                                entry_id = id_elem.text.strip() if id_elem is not None else ""
                                
                                # Extract authors
                                authors = []
                                for author in entry.findall('{http://www.w3.org/2005/Atom}author'):
                                    name_elem = author.find('{http://www.w3.org/2005/Atom}name')
                                    if name_elem is not None:
                                        authors.append(name_elem.text)
                                
                                # Format content with metadata
                                content_parts = [f"Summary: {summary}"]
                                if authors:
                                    content_parts.append(f"Authors: {', '.join(authors)}")
                                
                                published_elem = entry.find('{http://www.w3.org/2005/Atom}published')
                                if published_elem is not None:
                                    content_parts.append(f"Published: {published_elem.text}")
                                
                                content = "\n".join(content_parts)
                                
                                result = SearchResult(
                                    title=title,
                                    url=entry_id,
                                    content=content,
                                    score=1.0 - (i * 0.1),  # Decreasing relevance score
                                    raw_content=summary if get_full_documents else None,
                                    source="arxiv",
                                    query=query
                                )
                                results.append(result)
                            
                            return SearchResponse(query=query, source="arxiv", results=results)
                        else:
                            error_msg = f"arXiv API error: {response.status}"
                            return SearchResponse(query=query, source="arxiv", error=error_msg)
                            
            except Exception as e:
                error_msg = f"arXiv search failed: {str(e)}"
                logger.error(f"❌ {error_msg}")
                return SearchResponse(query=query, source="arxiv", error=error_msg)
        
        # Add delay between requests to respect arXiv rate limits
        responses = []
        for i, query in enumerate(search_queries):
            if i > 0:
                await asyncio.sleep(3.0)  # 3 second delay between requests
            
            response = await search_single_query(query)
            responses.append(response)
        
        logger.info(f"✅ arXiv async search completed - {len(responses)} responses")
        return responses
    
    async def search_multiple_sources(self, queries: List[str], 
                                    sources: List[str] = ["tavily", "arxiv"],
                                    search_config: Optional[Dict[str, Any]] = None) -> List[SearchResponse]:
        """Search multiple sources concurrently"""
        logger.info(f"🔍 Multi-source search: {len(queries)} queries across {sources}")
        
        all_responses = []
        search_tasks = []
        
        for source in sources:
            # Get filtered parameters for this source
            source_config = search_config or {}
            filtered_params = self.get_search_params(source, source_config)
            
            if source == "tavily":
                task = self.search_tavily_async(queries, **filtered_params)
            elif source == "arxiv":
                task = self.search_arxiv_async(queries, **filtered_params)
            else:
                logger.warning(f"⚠️ Unsupported source: {source}")
                continue
                
            search_tasks.append(task)
        
        # Execute all source searches concurrently
        if search_tasks:
            results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Source search failed: {result}")
                else:
                    all_responses.extend(result)
        
        logger.info(f"✅ Multi-source search completed - {len(all_responses)} total responses")
        return all_responses
    
    def deduplicate_and_format_sources(self, search_responses: List[SearchResponse], 
                                     max_tokens_per_source: int = 5000,
                                     include_raw_content: bool = True) -> str:
        """Deduplicate results and format into readable text"""
        logger.info(f"📝 Processing {len(search_responses)} search responses for deduplication")
        
        # Collect all results from all responses
        all_results = []
        for response in search_responses:
            all_results.extend(response.results)
        
        # Deduplicate by URL
        unique_sources = {}
        for result in all_results:
            if result.url not in unique_sources:
                unique_sources[result.url] = result
        
        logger.info(f"🔗 Deduplicated to {len(unique_sources)} unique sources")
        
        # Format output
        formatted_text = "Sources:\n\n"
        for i, (url, source) in enumerate(unique_sources.items(), 1):
            formatted_text += f"Source {source.title}:\n===\n"
            formatted_text += f"URL: {source.url}\n===\n"
            formatted_text += f"Most relevant content from source: {source.content}\n===\n"
            
            if include_raw_content and source.raw_content:
                # Using rough estimate of 4 characters per token
                char_limit = max_tokens_per_source * 4
                raw_content = source.raw_content or ""
                
                if len(raw_content) > char_limit:
                    raw_content = raw_content[:char_limit] + "... [truncated]"
                    
                formatted_text += f"Full source content limited to {max_tokens_per_source} tokens: {raw_content}\n\n"
            else:
                formatted_text += "\n"
        
        logger.info(f"✅ Formatted {len(unique_sources)} sources into text")
        return formatted_text.strip()
