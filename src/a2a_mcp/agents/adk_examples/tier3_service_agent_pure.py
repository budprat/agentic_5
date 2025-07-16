# ABOUTME: Pure ADK implementation of Tier 3 Service Agent with tool integration
# ABOUTME: Demonstrates tool-enabled agents for specific service delivery tasks using only Google ADK

import logging
import json
from typing import List, Dict, Any, Optional, Callable
from google.adk.agents import Agent
from google.adk.tools import code_execution, grounding
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams

logger = logging.getLogger(__name__)


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
        
        def validate_json_schema(data: str, schema: str) -> Dict[str, Any]:
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
                    return f"Aggregation {aggregation} not supported"
                    
                return result.to_json()
            except Exception as e:
                return f"Aggregation error: {str(e)}"
        
        # Return tool definitions
        return [
            {
                "name": "validate_json_schema",
                "description": "Validate JSON data against a JSON schema",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data": {"type": "string", "description": "JSON data to validate"},
                        "schema": {"type": "string", "description": "JSON schema"}
                    },
                    "required": ["data", "schema"]
                },
                "function": validate_json_schema
            },
            {
                "name": "transform_data_format",
                "description": "Transform data between formats (JSON, CSV, XML)",
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
        """Initialize service agent with tools."""
        logger.info(f"Initializing {self.agent_name}")
        
        # Create custom tools
        custom_tools = self._create_custom_tools()
        
        # Load MCP tools if server URL provided
        mcp_tools = []
        if self.mcp_server_url:
            try:
                logger.info(f"Loading MCP tools from: {self.mcp_server_url}")
                mcp_tools = await MCPToolset(
                    connection_params=SseConnectionParams(url=self.mcp_server_url)
                ).get_tools()
                logger.info(f"Loaded {len(mcp_tools)} MCP tools")
            except Exception as e:
                logger.warning(f"Failed to load MCP tools: {e}")
        
        # Combine all tools (note: only ONE built-in tool allowed)
        self.tools = [code_execution] + custom_tools + mcp_tools
        
        self.adk_agent = Agent(
            name=self.agent_name,
            model="gemini-2.0-flash",
            instruction=self.instructions,
            tools=self.tools
        )
        
        logger.info(f"{self.agent_name}: Initialized with {len(self.tools)} tools")
        
    async def process_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data processing task."""
        try:
            # Build processing request
            processing_request = f"""
            Execute the following data processing task:
            
            Task Type: {task.get('type', 'unknown')}
            Data: {task.get('data', 'No data provided')}
            Requirements: {task.get('requirements', 'No specific requirements')}
            
            Use appropriate tools to complete the task and return results.
            """
            
            # Execute task
            result = await self.adk_agent.run(processing_request)
            
            return {
                'success': True,
                'task_type': task.get('type'),
                'result': result,
                'agent': self.agent_name
            }
            
        except Exception as e:
            logger.error(f"Data processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'task_type': task.get('type'),
                'agent': self.agent_name
            }


class APIIntegrationServiceAgentPure:
    """
    Tier 3 API Integration Service Agent.
    Pure ADK implementation.
    
    Handles external API integrations and web service interactions.
    """
    
    def __init__(self):
        self.agent_name = "APIIntegrationServiceAgent"
        self.description = "Manages API integrations and external service calls"
        self.instructions = """
        You are an API integration specialist responsible for:
        - Making HTTP requests to external APIs
        - Handling authentication (API keys, OAuth, etc.)
        - Parsing and transforming API responses
        - Error handling and retry logic
        - Rate limiting and quota management
        
        Ensure secure and efficient API interactions while handling
        errors gracefully and providing meaningful responses.
        """
        self.adk_agent = None
        
    def _create_api_tools(self) -> List[Dict[str, Any]]:
        """Create API integration tools."""
        
        async def make_api_request(
            method: str, url: str, headers: Dict = None, 
            data: Dict = None, params: Dict = None
        ) -> Dict[str, Any]:
            """Make HTTP API request."""
            import aiohttp
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method=method.upper(),
                        url=url,
                        headers=headers or {},
                        json=data,
                        params=params
                    ) as response:
                        return {
                            "status_code": response.status,
                            "headers": dict(response.headers),
                            "body": await response.text(),
                            "success": 200 <= response.status < 300
                        }
            except Exception as e:
                return {
                    "error": str(e),
                    "success": False
                }
                
        def parse_api_response(response: str, format: str = "json") -> Any:
            """Parse API response in various formats."""
            try:
                if format == "json":
                    return json.loads(response)
                elif format == "xml":
                    import xml.etree.ElementTree as ET
                    return ET.fromstring(response)
                else:
                    return response
            except Exception as e:
                return {"error": f"Parse error: {str(e)}"}
                
        return [
            {
                "name": "make_api_request",
                "description": "Make HTTP request to external API",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
                        "url": {"type": "string", "description": "API endpoint URL"},
                        "headers": {"type": "object", "description": "Request headers"},
                        "data": {"type": "object", "description": "Request body data"},
                        "params": {"type": "object", "description": "Query parameters"}
                    },
                    "required": ["method", "url"]
                },
                "function": make_api_request
            },
            {
                "name": "parse_api_response",
                "description": "Parse API response data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "response": {"type": "string", "description": "Response data to parse"},
                        "format": {"type": "string", "enum": ["json", "xml", "text"]}
                    },
                    "required": ["response"]
                },
                "function": parse_api_response
            }
        ]
        
    async def init_agent(self):
        """Initialize API integration agent."""
        logger.info(f"Initializing {self.agent_name}")
        
        # Create API tools
        api_tools = self._create_api_tools()
        
        # Use grounding tool for web research
        all_tools = [grounding] + api_tools
        
        self.adk_agent = Agent(
            name=self.agent_name,
            model="gemini-2.0-flash",
            instruction=self.instructions,
            tools=all_tools
        )
        
        logger.info(f"{self.agent_name}: Initialized with {len(all_tools)} tools")
        
    async def integrate_api(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API integration task."""
        try:
            integration_request = f"""
            Execute the following API integration task:
            
            API: {request.get('api_name', 'unknown')}
            Endpoint: {request.get('endpoint', 'not specified')}
            Method: {request.get('method', 'GET')}
            Requirements: {request.get('requirements', 'Standard API call')}
            
            Use the appropriate tools to make the API call and process the response.
            """
            
            result = await self.adk_agent.run(integration_request)
            
            return {
                'success': True,
                'api_name': request.get('api_name'),
                'result': result,
                'agent': self.agent_name
            }
            
        except Exception as e:
            logger.error(f"API integration failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'api_name': request.get('api_name'),
                'agent': self.agent_name
            }


class ComputationServiceAgentPure:
    """
    Tier 3 Computation Service Agent.
    Pure ADK implementation.
    
    Performs complex calculations and numerical operations.
    Uses code_execution tool for dynamic computation.
    """
    
    def __init__(self):
        self.agent_name = "ComputationServiceAgent"
        self.description = "Executes computational and analytical tasks"
        self.instructions = """
        You are a computation specialist capable of:
        - Statistical analysis
        - Mathematical calculations
        - Data modeling
        - Algorithmic operations
        - Numerical simulations
        
        Use the code execution tool to perform complex calculations
        and return accurate results with appropriate precision.
        """
        self.adk_agent = None
        
    async def init_agent(self):
        """Initialize computation agent with code execution capability."""
        logger.info(f"Initializing {self.agent_name}")
        
        # Use code_execution as the primary tool
        self.adk_agent = Agent(
            name=self.agent_name,
            model="gemini-2.0-flash",
            instruction=self.instructions,
            tools=[code_execution]
        )
        
        logger.info(f"{self.agent_name}: Initialized with code execution capability")
        
    async def compute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute computation task."""
        try:
            computation_request = f"""
            Execute the following computational task:
            
            Type: {task.get('computation_type', 'general')}
            Data: {task.get('data', 'No data provided')}
            Formula/Algorithm: {task.get('algorithm', 'Use appropriate method')}
            Requirements: {task.get('requirements', 'Compute and return results')}
            
            Use code execution to perform the calculation and return results.
            """
            
            result = await self.adk_agent.run(computation_request)
            
            return {
                'success': True,
                'computation_type': task.get('computation_type'),
                'result': result,
                'agent': self.agent_name
            }
            
        except Exception as e:
            logger.error(f"Computation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'computation_type': task.get('computation_type'),
                'agent': self.agent_name
            }


# Service Coordinator
class ServiceCoordinatorPure:
    """
    Coordinates multiple Tier 3 service agents for complex operations.
    Pure ADK implementation.
    """
    
    def __init__(self, mcp_server_url: Optional[str] = None):
        self.agent_name = "ServiceCoordinator"
        self.description = "Coordinates multiple service agents"
        self.service_agents = {}
        self.mcp_server_url = mcp_server_url
        
    async def init_agent(self):
        """Initialize coordinator and service agents."""
        logger.info(f"Initializing {self.agent_name}")
        
        # Initialize all service agents
        self.service_agents = {
            'data_processing': DataProcessingServiceAgentPure(self.mcp_server_url),
            'api_integration': APIIntegrationServiceAgentPure(),
            'computation': ComputationServiceAgentPure()
        }
        
        # Initialize each service agent
        for name, agent in self.service_agents.items():
            logger.info(f"Initializing service: {name}")
            await agent.init_agent()
            
        logger.info(f"{self.agent_name}: Initialized with {len(self.service_agents)} service agents")
            
    async def execute_service_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route task to appropriate service agent."""
        service_type = task.get('service_type', '').lower()
        
        if service_type in self.service_agents:
            agent = self.service_agents[service_type]
            
            if service_type == 'data_processing':
                return await agent.process_data(task)
            elif service_type == 'api_integration':
                return await agent.integrate_api(task)
            elif service_type == 'computation':
                return await agent.compute(task)
                
        return {
            'success': False,
            'error': f"Unknown service type: {service_type}"
        }


# Example usage
async def main():
    """Demonstrate service agent usage."""
    # Data processing example
    data_agent = DataProcessingServiceAgentPure()
    await data_agent.init_agent()
    
    # Process data task
    processing_task = {
        'type': 'transform',
        'data': json.dumps([
            {'name': 'Alice', 'age': 30, 'department': 'Engineering'},
            {'name': 'Bob', 'age': 25, 'department': 'Sales'},
            {'name': 'Charlie', 'age': 35, 'department': 'Engineering'}
        ]),
        'requirements': 'Transform JSON to CSV format and calculate average age by department'
    }
    
    result = await data_agent.process_data(processing_task)
    print(f"Processing result: {result['success']}")
    if result['success']:
        print(f"Result: {result['result']}")
    
    # Computation example
    compute_agent = ComputationServiceAgentPure()
    await compute_agent.init_agent()
    
    computation_task = {
        'computation_type': 'statistics',
        'data': '[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]',
        'algorithm': 'Calculate mean, median, mode, and standard deviation',
        'requirements': 'Return statistical summary'
    }
    
    compute_result = await compute_agent.compute(computation_task)
    print(f"\nComputation result: {compute_result['success']}")
    if compute_result['success']:
        print(f"Result: {compute_result['result']}")
    
    # Service coordination example
    coordinator = ServiceCoordinatorPure()
    await coordinator.init_agent()
    
    # Multi-service task
    complex_task = {
        'service_type': 'data_processing',
        'type': 'aggregate',
        'data': processing_task['data'],
        'requirements': 'Group by department and calculate statistics'
    }
    
    coord_result = await coordinator.execute_service_task(complex_task)
    print(f"\nCoordination result: {coord_result}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())