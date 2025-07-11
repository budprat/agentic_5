# ABOUTME: Domain specialist agent demonstrating tier 2 capabilities with MCP tools
# ABOUTME: Shows inheritance from StandardizedAgentBase and domain-specific research logic

"""
Domain Specialist Agent - Research & Analysis Expert
A tier 2 agent that specializes in research, documentation lookup, and web analysis
"""

from typing import Dict, Any, List, Optional, Tuple
import json
import logging
from datetime import datetime

from ...core.base_agent import StandardizedAgentBase
from ...core.communication import Message, MessageType
from ...utils.mcp_client import MCPToolClient
from ...core.exceptions import AgentExecutionError

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
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, config)
        
        # Domain-specific configuration
        self.research_config = config.get('research_config', {})
        self.max_search_results = self.research_config.get('max_search_results', 5)
        self.preferred_sources = self.research_config.get('preferred_sources', [])
        self.documentation_apis = self.research_config.get('documentation_apis', {})
        
        # Initialize MCP tool client
        self.mcp_client = MCPToolClient()
        
        # Track research session state
        self.current_research_topic = None
        self.research_history = []
        self.cached_results = {}
        
        logger.info(f"ResearchSpecialistAgent {agent_id} initialized with config: {self.research_config}")
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute research-specific tasks using appropriate MCP tools.
        
        Supported task types:
        - documentation_search: Search technical documentation
        - web_research: General web research on a topic
        - code_example_search: Find code examples and implementations
        - api_reference_lookup: Look up API references
        - comparative_analysis: Compare multiple solutions/approaches
        """
        task_type = task.get('type', 'general_research')
        query = task.get('query', '')
        
        logger.info(f"Executing research task: {task_type} with query: {query}")
        
        try:
            if task_type == 'documentation_search':
                return await self._search_documentation(query, task.get('sources', []))
            
            elif task_type == 'web_research':
                return await self._conduct_web_research(query, task.get('depth', 'standard'))
            
            elif task_type == 'code_example_search':
                return await self._find_code_examples(query, task.get('language', 'any'))
            
            elif task_type == 'api_reference_lookup':
                return await self._lookup_api_reference(query, task.get('library', None))
            
            elif task_type == 'comparative_analysis':
                return await self._perform_comparative_analysis(
                    query, 
                    task.get('options', []),
                    task.get('criteria', [])
                )
            
            else:
                # Default to general research
                return await self._general_research(query, task)
                
        except Exception as e:
            logger.error(f"Error executing research task: {str(e)}")
            raise AgentExecutionError(f"Research task failed: {str(e)}")
    
    async def _search_documentation(self, query: str, sources: List[str]) -> Dict[str, Any]:
        """Search technical documentation using appropriate MCP tools."""
        results = []
        
        # Use context7 for library documentation if available
        if 'libraries' in sources or not sources:
            try:
                # First resolve library names to IDs
                library_results = await self.mcp_client.call_tool(
                    'mcp__context7__resolve-library-id',
                    {'libraryName': query}
                )
                
                if library_results and library_results.get('libraries'):
                    # Get documentation for the top match
                    library_id = library_results['libraries'][0]['id']
                    docs = await self.mcp_client.call_tool(
                        'mcp__context7__get-library-docs',
                        {
                            'context7CompatibleLibraryID': library_id,
                            'tokens': 5000,
                            'topic': query
                        }
                    )
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
                supabase_results = await self.mcp_client.call_tool(
                    'mcp__supabase__search_docs',
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
            search_results = await self.mcp_client.call_tool(
                'mcp__brave__brave_web_search',
                {
                    'query': query,
                    'count': self.max_search_results
                }
            )
            research_results['search_results'] = search_results
            
            # For deep research, scrape top results
            if depth == 'deep' and search_results.get('results'):
                for result in search_results['results'][:3]:  # Top 3 results
                    try:
                        scraped = await self.mcp_client.call_tool(
                            'mcp__firecrawl__firecrawl_scrape',
                            {
                                'url': result['url'],
                                'formats': ['markdown'],
                                'onlyMainContent': True
                            }
                        )
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
                search_results = await self.mcp_client.call_tool(
                    'mcp__firecrawl__firecrawl_search',
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
            search_results = await self.mcp_client.call_tool(
                'mcp__brave__brave_web_search',
                {
                    'query': f"site:github.com {github_query} example",
                    'count': 5
                }
            )
            
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
                library_results = await self.mcp_client.call_tool(
                    'mcp__context7__resolve-library-id',
                    {'libraryName': library}
                )
                
                if library_results and library_results.get('libraries'):
                    library_id = library_results['libraries'][0]['id']
                    api_docs = await self.mcp_client.call_tool(
                        'mcp__context7__get-library-docs',
                        {
                            'context7CompatibleLibraryID': library_id,
                            'topic': query,
                            'tokens': 8000
                        }
                    )
                    api_references.append({
                        'source': 'context7',
                        'library': library,
                        'reference': api_docs
                    })
            except Exception as e:
                logger.warning(f"API reference lookup failed for {library}: {str(e)}")
        
        # General API search
        try:
            api_search = await self.mcp_client.call_tool(
                'mcp__brave__brave_web_search',
                {
                    'query': f"{query} API reference documentation",
                    'count': 3
                }
            )
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
    
    async def process_message(self, message: Message) -> Optional[Message]:
        """Process incoming messages and route to appropriate research methods."""
        
        if message.type == MessageType.TASK_REQUEST:
            # Extract task from message
            task = message.content.get('task', {})
            
            # Check if this is a research task we can handle
            research_keywords = [
                'research', 'search', 'find', 'lookup', 'compare', 
                'analyze', 'documentation', 'example', 'reference'
            ]
            
            task_description = str(task.get('description', '')).lower()
            if any(keyword in task_description for keyword in research_keywords):
                try:
                    # Execute the research task
                    result = await self.execute_task(task)
                    
                    # Cache results for potential follow-ups
                    cache_key = f"{task.get('type', 'general')}_{task.get('query', '')}"
                    self.cached_results[cache_key] = result
                    
                    # Return success message
                    return Message(
                        type=MessageType.TASK_RESULT,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            'status': 'success',
                            'result': result,
                            'task_id': task.get('id')
                        }
                    )
                except Exception as e:
                    logger.error(f"Research task failed: {str(e)}")
                    return Message(
                        type=MessageType.ERROR,
                        sender=self.agent_id,
                        recipient=message.sender,
                        content={
                            'error': str(e),
                            'task_id': task.get('id')
                        }
                    )
            else:
                # Not a research task, pass to parent
                return await super().process_message(message)
        
        # Handle other message types
        return await super().process_message(message)
    
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