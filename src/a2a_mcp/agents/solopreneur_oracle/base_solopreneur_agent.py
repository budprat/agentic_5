"""Base class for all solopreneur agents following framework pattern."""

import logging
from typing import Dict, Any, List, Optional
from collections.abc import AsyncIterable
import json
import asyncio

from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import init_api_key
from google import genai
from a2a_mcp.mcp.client import MCPToolset, SseConnectionParams
from a2a_mcp.common.utils import get_mcp_server_config

logger = logging.getLogger(__name__)

class UnifiedSolopreneurAgent(BaseAgent):
    """
    Framework-compliant base class for all solopreneur agents.
    Follows the proven TravelAgent pattern for specialization.
    """
    
    def __init__(
        self, 
        agent_name: str, 
        description: str, 
        instructions: str,
        port: int
    ):
        init_api_key()
        super().__init__(
            agent_name=agent_name,
            description=description,
            content_types=['text', 'text/plain', 'application/json']
        )
        
        self.instructions = instructions
        self.port = port
        self.tier = self._determine_tier(port)
        self.mcp_tools = None
        self.client = None
        
    def _determine_tier(self, port: int) -> int:
        """Determine agent tier based on port number."""
        if port == 10901:
            return 1  # Master Oracle
        elif 10902 <= port <= 10906:
            return 2  # Domain Specialists
        elif 10910 <= port <= 10959:
            return 3  # Intelligence Modules
        else:
            return 0  # Unknown
    
    async def init_mcp_tools(self):
        """Initialize MCP tools for database and external service access."""
        if not self.mcp_tools:
            config = get_mcp_server_config()
            self.mcp_tools = await MCPToolset(
                connection_params=SseConnectionParams(url=config.url)
            ).get_tools()
            logger.info(f"{self.agent_name} initialized {len(self.mcp_tools)} MCP tools")
    
    async def init_genai_client(self):
        """Initialize Google Generative AI client."""
        if not self.client:
            self.client = genai.Client()
            
    async def stream(
        self, 
        query: str, 
        context_id: str, 
        task_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        """Stream implementation following framework patterns."""
        logger.info(f"{self.agent_name} (Tier {self.tier}) processing: {query}")
        
        # Initialize tools and client
        await self.init_mcp_tools()
        await self.init_genai_client()
        
        # Tier-specific processing
        if self.tier == 1:
            # Master Oracle coordinates other agents
            async for chunk in self._master_oracle_stream(query, context_id, task_id):
                yield chunk
        elif self.tier == 2:
            # Domain Specialists coordinate modules
            async for chunk in self._domain_specialist_stream(query, context_id, task_id):
                yield chunk
        elif self.tier == 3:
            # Intelligence Modules provide specific analysis
            async for chunk in self._intelligence_module_stream(query, context_id, task_id):
                yield chunk
                
    async def _master_oracle_stream(self, query, context_id, task_id):
        """Master Oracle coordination logic."""
        yield {
            'is_task_complete': False,
            'require_user_input': False,
            'content': f'{self.agent_name}: Orchestrating multi-tier analysis...'
        }
        
        # Analyze query to determine required domain specialists
        domains_needed = await self._analyze_query_domains(query)
        
        yield {
            'is_task_complete': False,
            'require_user_input': False,
            'content': f'{self.agent_name}: Identified {len(domains_needed)} domains for analysis: {", ".join(domains_needed)}'
        }
        
        # Coordinate with domain specialists (simulation for now)
        domain_results = {}
        for domain in domains_needed:
            yield {
                'is_task_complete': False,
                'require_user_input': False,
                'content': f'{self.agent_name}: Consulting {domain} specialist...'
            }
            # In full implementation, this would make actual A2A calls
            domain_results[domain] = await self._simulate_domain_analysis(domain, query)
        
        # Synthesize results
        synthesis = await self._synthesize_results(domain_results, query)
        
        yield {
            'is_task_complete': True,
            'require_user_input': False,
            'response_type': 'data',
            'content': synthesis
        }
        
    async def _domain_specialist_stream(self, query, context_id, task_id):
        """Domain Specialist coordination logic."""
        yield {
            'is_task_complete': False,
            'require_user_input': False,
            'content': f'{self.agent_name}: Analyzing domain-specific requirements...'
        }
        
        # Determine which intelligence modules to activate
        modules_needed = await self._analyze_required_modules(query)
        
        yield {
            'is_task_complete': False,
            'require_user_input': False,
            'content': f'{self.agent_name}: Activating {len(modules_needed)} intelligence modules...'
        }
        
        # Coordinate intelligence modules (simulation)
        module_results = {}
        for module in modules_needed:
            module_results[module] = await self._simulate_module_analysis(module, query)
            
        # Domain-specific synthesis
        domain_synthesis = await self._domain_synthesis(module_results, query)
        
        yield {
            'is_task_complete': True,
            'require_user_input': False,
            'response_type': 'data',
            'content': domain_synthesis
        }
        
    async def _intelligence_module_stream(self, query, context_id, task_id):
        """Intelligence Module analysis logic."""
        yield {
            'is_task_complete': False,
            'require_user_input': False,
            'content': f'{self.agent_name}: Performing specialized analysis...'
        }
        
        # Use MCP tools for data access
        tool_results = await self._execute_relevant_tools(query)
        
        # Generate specialized analysis
        prompt = f"""
        {self.instructions}
        
        Query: {query}
        Tool Results: {json.dumps(tool_results, indent=2)}
        
        Provide specialized analysis in JSON format.
        """
        
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        )
        
        analysis = json.loads(response.text)
        
        yield {
            'is_task_complete': True,
            'require_user_input': False,
            'response_type': 'data',
            'content': analysis
        }
    
    async def _analyze_query_domains(self, query: str) -> List[str]:
        """Analyze query to determine required domains."""
        query_lower = query.lower()
        domains = []
        
        if any(word in query_lower for word in ["code", "architecture", "ai", "research", "tech"]):
            domains.append("Technical Intelligence")
        if any(word in query_lower for word in ["knowledge", "graph", "information", "data"]):
            domains.append("Knowledge Management")
        if any(word in query_lower for word in ["energy", "focus", "productivity", "schedule"]):
            domains.append("Personal Optimization")
        if any(word in query_lower for word in ["learn", "skill", "development", "education"]):
            domains.append("Learning Enhancement")
        if len(domains) > 1:
            domains.append("Integration Synthesis")
            
        return domains if domains else ["Technical Intelligence", "Personal Optimization"]
    
    async def _analyze_required_modules(self, query: str) -> List[str]:
        """Determine which intelligence modules are needed."""
        # This would be more sophisticated in full implementation
        modules = []
        query_lower = query.lower()
        
        # Map keywords to modules based on agent's domain
        if "Technical Intelligence" in self.agent_name:
            if "research" in query_lower:
                modules.append("AI Research Analyzer")
            if "architecture" in query_lower:
                modules.append("Code Architecture Evaluator")
            if "stack" in query_lower:
                modules.append("Tech Stack Optimizer")
        elif "Personal Optimization" in self.agent_name:
            if "energy" in query_lower:
                modules.append("Energy Pattern Analyzer")
            if "focus" in query_lower:
                modules.append("Focus State Monitor")
            if "schedule" in query_lower:
                modules.append("Circadian Optimizer")
                
        return modules if modules else ["General Analysis Module"]
    
    async def _execute_relevant_tools(self, query: str) -> Dict[str, Any]:
        """Execute relevant MCP tools based on query."""
        results = {}
        
        # Determine which tools to use based on tier and query
        if self.tier == 3:  # Intelligence modules use specific tools
            if "energy" in query.lower():
                # Use energy pattern analysis tool
                for tool in self.mcp_tools:
                    if tool.name == "analyze_energy_patterns":
                        try:
                            result = await tool.run({"user_id": "default"})
                            results["energy_patterns"] = result
                        except Exception as e:
                            logger.error(f"Tool execution error: {e}")
            elif "research" in query.lower():
                # Use research monitoring tool
                for tool in self.mcp_tools:
                    if tool.name == "monitor_technical_trends":
                        try:
                            result = await tool.run({"research_areas": ["ai", "machine learning"]})
                            results["technical_trends"] = result
                        except Exception as e:
                            logger.error(f"Tool execution error: {e}")
                            
        return results
    
    async def _simulate_domain_analysis(self, domain: str, query: str) -> Dict[str, Any]:
        """Simulate domain specialist analysis (placeholder for A2A calls)."""
        return {
            "domain": domain,
            "confidence": 0.85,
            "key_insights": [f"{domain} insight 1", f"{domain} insight 2"],
            "recommendations": [f"{domain} recommendation"]
        }
    
    async def _simulate_module_analysis(self, module: str, query: str) -> Dict[str, Any]:
        """Simulate intelligence module analysis (placeholder for A2A calls)."""
        return {
            "module": module,
            "analysis_type": "specialized",
            "findings": [f"{module} finding 1", f"{module} finding 2"],
            "confidence": 0.9
        }
    
    async def _synthesize_results(self, results: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Synthesize results from multiple domains."""
        prompt = f"""
        As the Solopreneur Oracle Master, synthesize the following domain analyses:
        
        Query: {query}
        Domain Results: {json.dumps(results, indent=2)}
        
        Provide comprehensive synthesis in JSON format with:
        - executive_summary
        - key_recommendations
        - action_plan
        - risk_assessment
        """
        
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        )
        
        return json.loads(response.text)
    
    async def _domain_synthesis(self, results: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Domain-specific synthesis of module results."""
        return {
            "domain": self.agent_name,
            "synthesis": "Domain-specific insights",
            "module_results": results,
            "confidence": 0.88
        }