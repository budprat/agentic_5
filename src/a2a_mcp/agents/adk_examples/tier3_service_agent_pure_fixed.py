# ABOUTME: Pure ADK implementation of Tier 3 Service Agent with tool integration - Fixed version
# ABOUTME: Demonstrates tool-enabled agents for specific service delivery tasks using only Google ADK

import logging
import json
from typing import List, Dict, Any, Optional, Callable
from google.adk.agents import Agent
from google.adk.tools import code_execution, google_search
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams

logger = logging.getLogger(__name__)


class GroundingServiceAgent:
    """
    Tier 3 Service Agent with Google Search capabilities.
    Pure ADK implementation for information retrieval tasks.
    """
    
    def __init__(self):
        self.agent_name = "GroundingServiceAgent"
        self.description = "Information retrieval agent with search capabilities"
        self.instructions = """
        You are an information retrieval specialist with access to Google Search.
        Your responsibilities include:
        - Finding current information on topics
        - Researching facts and data
        - Providing up-to-date information
        - Verifying information accuracy
        
        Use the google_search tool to find relevant information and provide
        comprehensive, accurate responses based on search results.
        """
        
        # Create agent with google_search tool
        self.adk_agent = Agent(
            name=self.agent_name,
            model="gemini-2.0-flash",
            description=self.description,
            instruction=self.instructions,
            tools=[google_search]  # Using the built-in google_search tool
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute grounding/search tasks."""
        query = context.get('query', '')
        session = context.get('session')
        
        if not query:
            return {"error": "No query provided"}
        
        # For this pure implementation, we'll return a simple response
        # In a full implementation, you'd use the Runner pattern
        return {
            "result": f"Search agent ready to search for: {query}",
            "agent": self.agent_name,
            "tools": ["google_search"]
        }


class DataProcessingServiceAgentPure:
    """
    Tier 3 Data Processing Service Agent.
    Pure ADK implementation without StandardizedAgentBase dependencies.
    
    Executes data processing tasks using built-in and custom tools.
    Demonstrates tool integration and service-level operations.
    """
    
    def __init__(self, mcp_server_url: Optional[str] = None):
        self.agent_name = "DataProcessingServiceAgent"
        self.description = "Executes data processing and transformation tasks"
        self.instructions = """
        You are a data processing specialist responsible for:
        - Data validation and cleaning
        - Format transformation (JSON, CSV, XML)
        - Data aggregation and summarization
        - Statistical analysis
        - Data quality checks
        
        Use available tools to efficiently process data while maintaining
        accuracy and data integrity. Always validate inputs and outputs.
        """
        self.mcp_server_url = mcp_server_url
        self.adk_agent = None
        self.tools = []
        
    def _create_custom_tools(self) -> List[Dict[str, Any]]:
        """Create custom data processing tools."""
        
        def validate_json(data: str, schema: str) -> Dict[str, Any]:
            """Validate JSON data against a schema."""
            try:
                import jsonschema
                data_obj = json.loads(data)
                schema_obj = json.loads(schema)
                jsonschema.validate(data_obj, schema_obj)
                return {"valid": True, "message": "Data validates against schema"}
            except Exception as e:
                return {"valid": False, "message": str(e)}
                
        def transform_data_format(data: str, from_format: str, to_format: str) -> str:
            """Transform data between formats (JSON, CSV, XML)."""
            try:
                if from_format == "json" and to_format == "csv":
                    import pandas as pd
                    df = pd.DataFrame(json.loads(data))
                    return df.to_csv(index=False)
                elif from_format == "csv" and to_format == "json":
                    import pandas as pd
                    import io
                    df = pd.read_csv(io.StringIO(data))
                    return df.to_json(orient='records')
                else:
                    return f"Transformation from {from_format} to {to_format} not supported"
            except Exception as e:
                return f"Transformation error: {str(e)}"
                
        def aggregate_data(data: str, group_by: str, aggregation: str) -> str:
            """Aggregate data based on grouping and aggregation function."""
            try:
                import pandas as pd
                df = pd.DataFrame(json.loads(data))
                
                if aggregation == "sum":
                    result = df.groupby(group_by).sum()
                elif aggregation == "mean":
                    result = df.groupby(group_by).mean()
                elif aggregation == "count":
                    result = df.groupby(group_by).count()
                else:
                    return f"Unsupported aggregation: {aggregation}"
                    
                return result.to_json()
            except Exception as e:
                return f"Aggregation error: {str(e)}"
        
        return [
            {
                "name": "validate_json",
                "description": "Validate JSON data against a schema",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "string", "description": "JSON data to validate"},
                        "schema": {"type": "string", "description": "JSON schema"}
                    },
                    "required": ["data", "schema"]
                },
                "function": validate_json
            },
            {
                "name": "transform_data_format",
                "description": "Transform data between formats",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "string", "description": "Data to transform"},
                        "from_format": {"type": "string", "enum": ["json", "csv", "xml"]},
                        "to_format": {"type": "string", "enum": ["json", "csv", "xml"]}
                    },
                    "required": ["data", "from_format", "to_format"]
                },
                "function": transform_data_format
            },
            {
                "name": "aggregate_data",
                "description": "Aggregate data using grouping and aggregation functions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "string", "description": "JSON data to aggregate"},
                        "group_by": {"type": "string", "description": "Field to group by"},
                        "aggregation": {"type": "string", "enum": ["sum", "mean", "count"]}
                    },
                    "required": ["data", "group_by", "aggregation"]
                },
                "function": aggregate_data
            }
        ]
        
    async def init_agent(self):
        """Initialize service agent with MCP and custom tools."""
        # Create custom tools
        self.custom_tools = self._create_custom_tools()
        
        # Initialize MCP tools if server URL provided
        if self.mcp_server_url:
            try:
                mcp_params = SseConnectionParams(url=self.mcp_server_url)
                mcp_toolset = MCPToolset(sse_params=mcp_params)
                await mcp_toolset.init_tools()
                self.tools = mcp_toolset.get_tools()
                logger.info(f"Initialized {len(self.tools)} MCP tools")
            except Exception as e:
                logger.warning(f"Failed to initialize MCP tools: {e}")
                self.tools = []
        
        # Combine tools - Note: Only ONE built-in tool allowed
        all_tools = [code_execution] + self.custom_tools + self.tools
        
        self.adk_agent = Agent(
            name=self.agent_name,
            model="gemini-2.0-flash",
            description=self.description,
            instruction=self.instructions,
            tools=all_tools
        )
        
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data processing tasks."""
        data = context.get('data', [])
        
        # For this pure implementation, we'll return a simple response
        return {
            "result": f"Data processing agent ready to process {len(data)} items",
            "agent": self.agent_name,
            "tools": ["code_execution"] + [t["name"] for t in self.custom_tools]
        }


class CustomToolServiceAgent:
    """
    Service agent with custom tools demonstration.
    Shows how to create and use custom tools in ADK.
    """
    
    def __init__(self):
        self.agent_name = "CustomToolServiceAgent"
        self.description = "Agent demonstrating custom tool creation"
        self.instructions = """
        You are a service agent with custom tools for specific tasks.
        Use the available tools to help users with their requests.
        """
        
        # Create custom tools
        self.custom_tools = self._create_analysis_tools()
        
        # Create agent with custom tools
        self.adk_agent = Agent(
            name=self.agent_name,
            model="gemini-2.0-flash",
            description=self.description,
            instruction=self.instructions,
            tools=self.custom_tools
        )
    
    def _create_analysis_tools(self) -> List[Dict[str, Any]]:
        """Create custom analysis tools."""
        
        def analyze_text(text: str) -> Dict[str, Any]:
            """Analyze text for various metrics."""
            words = text.split()
            return {
                "word_count": len(words),
                "character_count": len(text),
                "sentence_count": text.count('.') + text.count('!') + text.count('?'),
                "average_word_length": sum(len(word) for word in words) / len(words) if words else 0
            }
        
        def categorize_items(items: List[str]) -> Dict[str, List[str]]:
            """Categorize items into groups."""
            categories = {
                "short": [],
                "medium": [],
                "long": []
            }
            
            for item in items:
                if len(item) < 5:
                    categories["short"].append(item)
                elif len(item) < 10:
                    categories["medium"].append(item)
                else:
                    categories["long"].append(item)
            
            return categories
        
        return [
            {
                "name": "analyze_text",
                "description": "Analyze text for various metrics",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to analyze"}
                    },
                    "required": ["text"]
                },
                "function": analyze_text
            },
            {
                "name": "categorize_items",
                "description": "Categorize items by length",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of items to categorize"
                        }
                    },
                    "required": ["items"]
                },
                "function": categorize_items
            }
        ]
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute custom tool tasks."""
        data = context.get('data', [])
        
        return {
            "result": f"Custom tool agent ready with {len(self.custom_tools)} tools",
            "agent": self.agent_name,
            "tools": [t["name"] for t in self.custom_tools]
        }


class MCPIntegrationAgent:
    """
    Service agent demonstrating MCP tool integration.
    Shows how to connect to MCP servers for extended functionality.
    """
    
    def __init__(self, mcp_server_url: Optional[str] = None):
        self.agent_name = "MCPIntegrationAgent"
        self.description = "Agent with MCP tool integration"
        self.instructions = """
        You are a service agent with access to MCP tools.
        Use the available MCP tools to help users with their requests.
        Note: MCP tools availability depends on server configuration.
        """
        self.mcp_server_url = mcp_server_url
        self.adk_agent = None
        
    async def init_agent(self):
        """Initialize agent with MCP tools."""
        tools = []
        
        # Try to initialize MCP tools
        if self.mcp_server_url:
            try:
                mcp_params = SseConnectionParams(url=self.mcp_server_url)
                mcp_toolset = MCPToolset(sse_params=mcp_params)
                await mcp_toolset.init_tools()
                tools = mcp_toolset.get_tools()
                logger.info(f"Initialized {len(tools)} MCP tools")
            except Exception as e:
                logger.warning(f"Failed to initialize MCP tools: {e}")
                tools = []
        
        # Create agent with MCP tools (or empty if none available)
        self.adk_agent = Agent(
            name=self.agent_name,
            model="gemini-2.0-flash",
            description=self.description,
            instruction=self.instructions,
            tools=tools if tools else []
        )
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP tool tasks."""
        library = context.get('library', '')
        
        # Initialize if not already done
        if not self.adk_agent:
            await self.init_agent()
        
        return {
            "result": f"MCP agent ready to help with {library}",
            "agent": self.agent_name,
            "mcp_available": bool(self.mcp_server_url)
        }


class APIIntegrationServiceAgentPure:
    """
    Tier 3 API Integration Service Agent.
    Handles external API integrations and data fetching.
    """
    
    def __init__(self):
        self.agent_name = "APIIntegrationServiceAgent"
        self.description = "Handles external API integrations"
        self.instructions = """
        You are an API integration specialist responsible for:
        - Making HTTP requests to external APIs
        - Handling authentication and authorization
        - Parsing API responses
        - Error handling and retries
        - Data transformation from API responses
        
        Note: In this demo, we simulate API calls. In production,
        you would use actual HTTP libraries or MCP tools.
        """
        
        # Create agent with code execution for API simulation
        self.adk_agent = Agent(
            name=self.agent_name,
            model="gemini-2.0-flash",
            description=self.description,
            instruction=self.instructions,
            tools=[code_execution]
        )
        
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API integration tasks."""
        endpoint = context.get('endpoint', '')
        method = context.get('method', 'GET')
        
        return {
            "result": f"API agent ready to {method} {endpoint}",
            "agent": self.agent_name,
            "capabilities": ["REST API", "GraphQL", "WebSocket"]
        }


class ComputationServiceAgentPure:
    """
    Tier 3 Computation Service Agent.
    Performs mathematical and statistical computations.
    """
    
    def __init__(self):
        self.agent_name = "ComputationServiceAgent"
        self.description = "Performs complex computations"
        self.instructions = """
        You are a computation specialist responsible for:
        - Mathematical calculations
        - Statistical analysis
        - Data modeling
        - Algorithm implementation
        - Performance optimization
        
        Use the code_execution tool to perform accurate calculations
        and provide detailed results with explanations.
        """
        
        # Create agent with code execution
        self.adk_agent = Agent(
            name=self.agent_name,
            model="gemini-2.0-flash",
            description=self.description,
            instruction=self.instructions,
            tools=[code_execution]
        )
        
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute computation tasks."""
        computation_type = context.get('computation_type', 'general')
        
        return {
            "result": f"Computation agent ready for {computation_type} calculations",
            "agent": self.agent_name,
            "capabilities": ["statistics", "linear_algebra", "calculus", "optimization"]
        }


class ServiceCoordinatorPure:
    """
    Coordinates multiple service agents for complex tasks.
    Demonstrates service agent orchestration at Tier 3.
    """
    
    def __init__(self):
        self.agent_name = "ServiceCoordinator"
        self.description = "Coordinates multiple service agents"
        
        # Initialize service agents
        self.data_agent = DataProcessingServiceAgentPure()
        self.api_agent = APIIntegrationServiceAgentPure()
        self.compute_agent = ComputationServiceAgentPure()
        
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate service agents based on task requirements."""
        task_type = context.get('task_type', 'unknown')
        
        # Route to appropriate service agent
        if task_type == "data_processing":
            return await self.data_agent.execute(context)
        elif task_type == "api_integration":
            return await self.api_agent.execute(context)
        elif task_type == "computation":
            return await self.compute_agent.execute(context)
        else:
            return {
                "result": "Service coordinator ready",
                "available_services": [
                    "data_processing",
                    "api_integration",
                    "computation"
                ]
            }