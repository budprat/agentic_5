# ABOUTME: Domain specialist agent demonstrating tier 2 capabilities with MCP tools
# ABOUTME: Shows inheritance from StandardizedAgentBase and domain-specific research logic

"""
Domain Specialist Agent - Research & Analysis Expert
A tier 2 agent that specializes in research, documentation lookup, and web analysis
"""

from typing import Dict, Any, List, Optional, AsyncIterable
import json
import logging
from datetime import datetime
import asyncio

from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.a2a_protocol import A2AProtocolClient

logger = logging.getLogger(__name__)


class ResearchSpecialistAgent(StandardizedAgentBase):
    """
    A domain specialist agent focused on research and analysis tasks.
    
    This agent demonstrates:
    - Tier 2 specialization with specific domain knowledge
    - Integration with multiple MCP tools for research
    - Complex decision-making based on task requirements
    - Structured output formatting for research results
    """
    
    def __init__(self, agent_id: str = "research_specialist", config: Optional[Dict[str, Any]] = None):
        config = config or {}
        
        # Define research specialist instructions
        instructions = """
        You are a Research Specialist agent with deep expertise in conducting thorough research and analysis.
        Your capabilities include:
        1. Searching technical documentation and APIs
        2. Conducting web research on various topics
        3. Finding code examples and implementations
        4. Performing comparative analysis between options
        
        Use your MCP tools effectively to gather comprehensive information.
        Present findings in a clear, structured format with proper citations.
        Maintain objectivity and highlight both pros and cons when relevant.
        """
        
        super().__init__(
            agent_name=agent_id,
            description="Research Specialist - Expert in documentation, web research, and comparative analysis",
            instructions=instructions,
            quality_config={
                "min_confidence_score": 0.7,
                "require_sources": True,
                "max_response_length": 10000
            },
            mcp_tools_enabled=True
        )
        
        # Domain-specific configuration
        self.research_config = config.get('research_config', {})
        self.max_search_results = self.research_config.get('max_search_results', 5)
        self.preferred_sources = self.research_config.get('preferred_sources', [])
        self.documentation_apis = self.research_config.get('documentation_apis', {})
        
        # Track research session state
        self.current_research_topic = None
        self.research_history = []
        self.cached_results = {}
        
        logger.info(f"ResearchSpecialistAgent {agent_id} initialized")
    
    def _analyze_query(self, query: str) -> str:
        """Analyze query to determine research type."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['documentation', 'docs', 'api docs']):
            return 'documentation_search'
        elif any(word in query_lower for word in ['code', 'example', 'implementation', 'snippet']):
            return 'code_example_search'
        elif any(word in query_lower for word in ['api', 'reference', 'method', 'function']):
            return 'api_reference_lookup'
        elif any(word in query_lower for word in ['compare', 'versus', 'vs', 'comparison', 'differences']):
            return 'comparative_analysis'
        elif any(word in query_lower for word in ['research', 'find', 'search', 'information']):
            return 'web_research'
        else:
            return 'general_research'
    
    def _extract_comparison_options(self, query: str) -> List[str]:
        """Extract comparison options from query."""
        # Simple extraction - in production, use NLP
        options = []
        
        # Look for patterns like "X vs Y" or "compare X and Y"
        import re
        vs_pattern = r'(\w+)\s+(?:vs\.?|versus)\s+(\w+)'
        compare_pattern = r'compare\s+(\w+)\s+and\s+(\w+)'
        
        vs_match = re.search(vs_pattern, query, re.IGNORECASE)
        if vs_match:
            options.extend([vs_match.group(1), vs_match.group(2)])
        
        compare_match = re.search(compare_pattern, query, re.IGNORECASE)
        if compare_match:
            options.extend([compare_match.group(1), compare_match.group(2)])
        
        # Remove duplicates
        return list(set(options)) if options else ['option1', 'option2']
    
    async def _execute_agent_logic(
        self, query: str, context_id: str, task_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        """
        Execute research-specific logic based on query analysis.
        """
        # Analyze query to determine research type
        research_type = self._analyze_query(query)
        
        # Update current topic
        self.current_research_topic = query
        
        # Yield initial status
        yield {
            "is_task_complete": False,
            "require_user_input": False,
            "content": f"Analyzing research request: {research_type}..."
        }
        
        try:
            # Initialize agent if needed (for MCP tools)
            if not self.agent:
                await self.init_agent()
            
            # Execute research based on type
            if research_type == 'documentation_search':
                result = await self._search_documentation(query, [])
            elif research_type == 'web_research':
                result = await self._conduct_web_research(query, 'standard')
            elif research_type == 'code_example_search':
                result = await self._find_code_examples(query, 'any')
            elif research_type == 'api_reference_lookup':
                result = await self._lookup_api_reference(query, None)
            elif research_type == 'comparative_analysis':
                # Extract options from query
                options = self._extract_comparison_options(query)
                result = await self._perform_comparative_analysis(query, options, [])
            else:
                # Default to general research
                result = await self._general_research(query, {})
            
            # Cache the result
            cache_key = f"{research_type}_{query[:50]}"
            self.cached_results[cache_key] = result
            
            # Yield final result
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": result
            }
            
        except Exception as e:
            logger.error(f"Research error: {str(e)}")
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": {
                    "error": f"Research task failed: {str(e)}",
                    "research_type": research_type,
                    "query": query
                }
            }
    
    async def _search_documentation(self, query: str, sources: List[str]) -> Dict[str, Any]:
        """Search technical documentation using appropriate MCP tools."""
        results = []
        
        # Use context7 for library documentation if available
        if 'libraries' in sources or not sources:
            try:
                # Use the agent's tools to resolve library names
                if self.agent and self.tools:
                    # Find the context7 resolve tool
                    resolve_tool = next((t for t in self.tools if t.name == 'mcp__context7__resolve-library-id'), None)
                    if resolve_tool:
                        library_results = await self.agent.run_tool(
                            resolve_tool,
                            {'libraryName': query}
                        )
                    else:
                        library_results = None
                else:
                    library_results = None
                
                if library_results and library_results.get('libraries'):
                    # Get documentation for the top match
                    library_id = library_results['libraries'][0]['id']
                    # Use the get-library-docs tool
                    docs_tool = next((t for t in self.tools if t.name == 'mcp__context7__get-library-docs'), None)
                    if docs_tool:
                        docs = await self.agent.run_tool(
                            docs_tool,
                            {
                                'context7CompatibleLibraryID': library_id,
                                'tokens': 5000,
                                'topic': query
                            }
                        )
                    else:
                        docs = None
                    results.append({
                        'source': 'context7',
                        'library': library_id,
                        'content': docs
                    })
            except Exception as e:
                logger.warning(f"Context7 search failed: {str(e)}")
        
        # Use Supabase docs search if configured
        if 'supabase' in sources or 'supabase' in self.documentation_apis:
            try:
                # Use Supabase docs search tool
                supabase_tool = next((t for t in self.tools if t.name == 'mcp__supabase__search_docs'), None)
                if supabase_tool:
                    supabase_results = await self.agent.run_tool(
                        supabase_tool,
                        {
                            'graphql_query': f"""
                            query {{
                                searchDocs(query: "{query}", limit: 3) {{
                                    nodes {{
                                        title
                                        href
                                        content
                                    }}
                                }}
                            }}
                            """
                        }
                    )
                else:
                    supabase_results = None
                if supabase_results:
                    results.append({
                        'source': 'supabase_docs',
                        'results': supabase_results
                    })
            except Exception as e:
                logger.warning(f"Supabase docs search failed: {str(e)}")
        
        return {
            'task_type': 'documentation_search',
            'query': query,
            'results': results,
            'sources_searched': sources,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _conduct_web_research(self, query: str, depth: str) -> Dict[str, Any]:
        """Conduct web research using search and scraping tools."""
        research_results = {
            'search_results': [],
            'scraped_content': [],
            'key_findings': []
        }
        
        # Perform web search
        try:
            # Use Brave web search tool
            brave_tool = next((t for t in self.tools if t.name == 'mcp__brave__brave_web_search'), None)
            if brave_tool:
                search_results = await self.agent.run_tool(
                    brave_tool,
                    {
                        'query': query,
                        'count': self.max_search_results
                    }
                )
            else:
                search_results = None
            research_results['search_results'] = search_results
            
            # For deep research, scrape top results
            if depth == 'deep' and search_results.get('results'):
                for result in search_results['results'][:3]:  # Top 3 results
                    try:
                        # Use Firecrawl scrape tool
                        scrape_tool = next((t for t in self.tools if t.name == 'mcp__firecrawl__firecrawl_scrape'), None)
                        if scrape_tool:
                            scraped = await self.agent.run_tool(
                                scrape_tool,
                                {
                                    'url': result['url'],
                                    'formats': ['markdown'],
                                    'onlyMainContent': True
                                }
                            )
                        else:
                            scraped = None
                        research_results['scraped_content'].append({
                            'url': result['url'],
                            'title': result.get('title', ''),
                            'content': scraped
                        })
                    except Exception as e:
                        logger.warning(f"Failed to scrape {result['url']}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Web search failed: {str(e)}")
            # Fallback to firecrawl search
            try:
                firecrawl_search_tool = next((t for t in self.tools if t.name == 'mcp__firecrawl__firecrawl_search'), None)
                if firecrawl_search_tool:
                    search_results = await self.agent.run_tool(
                        firecrawl_search_tool,
                        {
                            'query': query,
                            'limit': self.max_search_results
                        }
                    )
                    research_results['search_results'] = search_results
            except Exception as e2:
                logger.error(f"Fallback search also failed: {str(e2)}")
        
        # Extract key findings
        research_results['key_findings'] = self._extract_key_findings(research_results)
        
        return {
            'task_type': 'web_research',
            'query': query,
            'depth': depth,
            'results': research_results,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _find_code_examples(self, query: str, language: str) -> Dict[str, Any]:
        """Find code examples using GitHub and documentation sources."""
        code_examples = []
        
        # Search GitHub repositories
        github_query = f"{query} language:{language}" if language != 'any' else query
        
        try:
            # Use web search for GitHub
            brave_tool = next((t for t in self.tools if t.name == 'mcp__brave__brave_web_search'), None)
            if brave_tool:
                search_results = await self.agent.run_tool(
                    brave_tool,
                    {
                        'query': f"site:github.com {github_query} example",
                        'count': 5
                    }
                )
            else:
                search_results = {'results': []}
            
            # Extract and process GitHub links
            for result in search_results.get('results', []):
                if 'github.com' in result.get('url', ''):
                    code_examples.append({
                        'source': 'github',
                        'url': result['url'],
                        'title': result.get('title', ''),
                        'description': result.get('description', '')
                    })
        except Exception as e:
            logger.warning(f"GitHub search failed: {str(e)}")
        
        return {
            'task_type': 'code_example_search',
            'query': query,
            'language': language,
            'examples': code_examples,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _lookup_api_reference(self, query: str, library: Optional[str]) -> Dict[str, Any]:
        """Look up API references for specific libraries or general APIs."""
        api_references = []
        
        if library:
            # Try context7 for specific library
            try:
                resolve_tool = next((t for t in self.tools if t.name == 'mcp__context7__resolve-library-id'), None)
                if resolve_tool:
                    library_results = await self.agent.run_tool(
                        resolve_tool,
                        {'libraryName': library}
                    )
                else:
                    library_results = None
                
                if library_results and library_results.get('libraries'):
                    library_id = library_results['libraries'][0]['id']
                    docs_tool = next((t for t in self.tools if t.name == 'mcp__context7__get-library-docs'), None)
                    if docs_tool:
                        api_docs = await self.agent.run_tool(
                            docs_tool,
                            {
                                'context7CompatibleLibraryID': library_id,
                                'topic': query,
                                'tokens': 8000
                            }
                        )
                    else:
                        api_docs = None
                    api_references.append({
                        'source': 'context7',
                        'library': library,
                        'reference': api_docs
                    })
            except Exception as e:
                logger.warning(f"API reference lookup failed for {library}: {str(e)}")
        
        # General API search
        try:
            brave_tool = next((t for t in self.tools if t.name == 'mcp__brave__brave_web_search'), None)
            if brave_tool:
                api_search = await self.agent.run_tool(
                    brave_tool,
                    {
                        'query': f"{query} API reference documentation",
                        'count': 3
                    }
                )
            else:
                api_search = {'results': []}
            for result in api_search.get('results', []):
                api_references.append({
                    'source': 'web',
                    'url': result['url'],
                    'title': result.get('title', ''),
                    'snippet': result.get('description', '')
                })
        except Exception as e:
            logger.warning(f"General API search failed: {str(e)}")
        
        return {
            'task_type': 'api_reference_lookup',
            'query': query,
            'library': library,
            'references': api_references,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _perform_comparative_analysis(
        self, 
        topic: str, 
        options: List[str], 
        criteria: List[str]
    ) -> Dict[str, Any]:
        """Perform comparative analysis between multiple options."""
        analysis_results = {
            'topic': topic,
            'options': {},
            'comparison_matrix': {},
            'recommendations': []
        }
        
        # Research each option
        for option in options:
            option_query = f"{topic} {option}"
            research = await self._conduct_web_research(option_query, 'standard')
            analysis_results['options'][option] = {
                'research': research,
                'scores': {}
            }
        
        # Analyze based on criteria
        for criterion in criteria:
            analysis_results['comparison_matrix'][criterion] = {}
            for option in options:
                # Simple scoring based on mention frequency
                score = self._calculate_criterion_score(
                    analysis_results['options'][option]['research'],
                    criterion
                )
                analysis_results['comparison_matrix'][criterion][option] = score
                analysis_results['options'][option]['scores'][criterion] = score
        
        # Generate recommendations
        analysis_results['recommendations'] = self._generate_recommendations(
            analysis_results['comparison_matrix'],
            options,
            criteria
        )
        
        return {
            'task_type': 'comparative_analysis',
            'results': analysis_results,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _general_research(self, query: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback general research method."""
        # Combine multiple research methods
        results = {
            'web_search': await self._conduct_web_research(query, 'standard'),
            'documentation': await self._search_documentation(query, [])
        }
        
        # If code-related query detected, add code examples
        code_keywords = ['example', 'implementation', 'code', 'function', 'class', 'method']
        if any(keyword in query.lower() for keyword in code_keywords):
            results['code_examples'] = await self._find_code_examples(query, 'any')
        
        return {
            'task_type': 'general_research',
            'query': query,
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _extract_key_findings(self, research_results: Dict[str, Any]) -> List[str]:
        """Extract key findings from research results."""
        findings = []
        
        # Extract from search results
        for result in research_results.get('search_results', {}).get('results', [])[:3]:
            if result.get('description'):
                findings.append(f"- {result['description']}")
        
        # Extract from scraped content (would need NLP in production)
        for scraped in research_results.get('scraped_content', []):
            # Simple extraction - take first meaningful paragraph
            content = scraped.get('content', {}).get('content', '')
            if content:
                # Find first paragraph with substantial content
                paragraphs = content.split('\n\n')
                for para in paragraphs:
                    if len(para) > 100 and not para.startswith('#'):
                        findings.append(f"- From {scraped['title']}: {para[:200]}...")
                        break
        
        return findings[:5]  # Limit to top 5 findings
    
    def _calculate_criterion_score(
        self, 
        research_data: Dict[str, Any], 
        criterion: str
    ) -> float:
        """Calculate a score for how well an option meets a criterion."""
        # Simple implementation - count mentions
        score = 0.0
        criterion_lower = criterion.lower()
        
        # Check search results
        for result in research_data.get('search_results', {}).get('results', []):
            text = f"{result.get('title', '')} {result.get('description', '')}".lower()
            score += text.count(criterion_lower) * 0.5
        
        # Check scraped content
        for scraped in research_data.get('scraped_content', []):
            content = scraped.get('content', {}).get('content', '').lower()
            score += content.count(criterion_lower) * 0.1
        
        # Normalize to 0-10 scale
        return min(10.0, score)
    
    def _generate_recommendations(
        self, 
        comparison_matrix: Dict[str, Dict[str, float]], 
        options: List[str],
        criteria: List[str]
    ) -> List[str]:
        """Generate recommendations based on comparative analysis."""
        recommendations = []
        
        # Calculate overall scores
        overall_scores = {}
        for option in options:
            total = sum(
                comparison_matrix[criterion].get(option, 0) 
                for criterion in criteria
            )
            overall_scores[option] = total / len(criteria) if criteria else 0
        
        # Sort by score
        sorted_options = sorted(
            overall_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Generate recommendations
        if sorted_options:
            best_option = sorted_options[0][0]
            best_score = sorted_options[0][1]
            
            recommendations.append(
                f"Based on the analysis, **{best_option}** appears to be the best choice "
                f"with an average score of {best_score:.1f}/10 across all criteria."
            )
            
            # Identify strengths
            strengths = []
            for criterion in criteria:
                if comparison_matrix[criterion].get(best_option, 0) >= 7:
                    strengths.append(criterion)
            
            if strengths:
                recommendations.append(
                    f"{best_option} particularly excels in: {', '.join(strengths)}"
                )
            
            # Note alternatives
            if len(sorted_options) > 1:
                second_best = sorted_options[1][0]
                recommendations.append(
                    f"Consider {second_best} as an alternative, especially if "
                    f"your specific use case differs from the general criteria."
                )
        
        return recommendations
    
    def get_agent_temperature(self) -> float:
        """Use moderate temperature for research tasks."""
        return 0.5
    
    def get_response_mime_type(self) -> str:
        """Return structured JSON for research results."""
        return "application/json"
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return the research capabilities of this agent."""
        return {
            'agent_type': 'domain_specialist',
            'domain': 'research_and_analysis',
            'tier': 2,
            'capabilities': [
                'documentation_search',
                'web_research',
                'code_example_search',
                'api_reference_lookup',
                'comparative_analysis'
            ],
            'mcp_tools_used': [
                'context7',
                'brave_search',
                'firecrawl',
                'supabase_docs'
            ],
            'specializations': {
                'technical_documentation': True,
                'code_examples': True,
                'api_references': True,
                'comparative_analysis': True,
                'web_scraping': True
            },
            'performance_metrics': {
                'max_concurrent_searches': 5,
                'cache_enabled': True,
                'average_response_time': '2-5 seconds'
            }
        }


# Example usage and configuration
if __name__ == "__main__":
    # Example configuration for the research specialist
    config = {
        'research_config': {
            'max_search_results': 10,
            'preferred_sources': ['github', 'official_docs', 'stackoverflow'],
            'documentation_apis': {
                'supabase': True,
                'context7': True
            }
        },
        'mcp_config': {
            'timeout': 30,
            'retry_attempts': 3
        }
    }
    
    # Example of how this agent would be instantiated
    research_agent = ResearchSpecialistAgent('research_specialist_01', config)
    
    # Example task that could be sent to this agent
    example_task = {
        'type': 'comparative_analysis',
        'query': 'JavaScript frameworks',
        'options': ['React', 'Vue', 'Angular', 'Svelte'],
        'criteria': ['performance', 'learning curve', 'community support', 'ecosystem']
    }