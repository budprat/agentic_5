# ABOUTME: Example Tier 3 Service Agent implementation using Google ADK with MCP tools
# ABOUTME: Demonstrates tool-enabled agents for specific service delivery tasks

import logging
import json
from typing import List, Dict, Any, Optional, Callable
from google.adk.agents import Agent
from google.adk.tools import code_execution, grounding
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.quality_framework import QualityDomain

logger = logging.getLogger(__name__)


class DataProcessingServiceAgent(StandardizedAgentBase):
    """
    Tier 3 Data Processing Service Agent.
    
    Executes data processing tasks using MCP tools and custom functions.
    Demonstrates tool integration and service-level operations.
    """
    
    def __init__(self):
        super().__init__(
            agent_name="DataProcessingServiceAgent",
            description="Executes data processing and transformation tasks",
            instructions="""
            You are a data processing specialist responsible for:
            - Data validation and cleaning
            - Format transformation (JSON, CSV, XML)
            - Data aggregation and summarization
            - Statistical analysis
            - Data quality checks
            
            Use available tools to efficiently process data while maintaining
            accuracy and data integrity. Always validate inputs and outputs.
            """,
            quality_config={
                "domain": QualityDomain.SERVICE,
                "thresholds": {
                    "accuracy": 0.95,
                    "completeness": 0.90,
                    "relevance": 0.85
                }
            },
            mcp_tools_enabled=True  # Enable MCP tools for data operations
        )
        self.custom_tools = []
        
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
                    df = pd.read_csv(pd.io.common.StringIO(data))
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
        """Initialize service agent with MCP and custom tools."""
        await super().init_agent()
        
        # Create custom tools
        self.custom_tools = self._create_custom_tools()
        
        # Combine MCP tools with custom tools
        # Note: Only ONE built-in tool allowed, so we use code_execution
        all_tools = [code_execution] + self.custom_tools + self.tools
        
        self.adk_agent = Agent(
            name=self.agent_name,
            model="gemini-2.0-flash",
            instruction=self.instructions,
            tools=all_tools
        )
        
        logger.info(f"{self.agent_name}: Initialized with {len(all_tools)} tools")
        
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
                'tools_used': self._extract_tools_used(result)
            }
            
        except Exception as e:
            logger.error(f"Data processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'task_type': task.get('type')
            }
            
    def _extract_tools_used(self, result: Any) -> List[str]:
        """Extract which tools were used in processing."""
        # This would parse the result to identify tool usage
        # For now, return empty list
        return []


class APIIntegrationServiceAgent(StandardizedAgentBase):
    """
    Tier 3 API Integration Service Agent.
    
    Handles external API integrations and web service interactions.
    """
    
    def __init__(self):
        super().__init__(
            agent_name="APIIntegrationServiceAgent",
            description="Manages API integrations and external service calls",
            instructions="""
            You are an API integration specialist responsible for:
            - Making HTTP requests to external APIs
            - Handling authentication (API keys, OAuth, etc.)
            - Parsing and transforming API responses
            - Error handling and retry logic
            - Rate limiting and quota management
            
            Ensure secure and efficient API interactions while handling
            errors gracefully and providing meaningful responses.
            """,
            quality_config={
                "domain": QualityDomain.SERVICE,
                "thresholds": {
                    "accuracy": 0.90,
                    "completeness": 0.85,
                    "relevance": 0.85
                }
            }
        )
        
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


class FileOperationsServiceAgent(StandardizedAgentBase):
    """
    Tier 3 File Operations Service Agent.
    
    Handles file I/O, transformations, and management tasks.
    """
    
    def __init__(self):
        super().__init__(
            agent_name="FileOperationsServiceAgent",
            description="Manages file operations and transformations",
            instructions="""
            You are a file operations specialist handling:
            - File reading and writing
            - Format conversions
            - File compression/decompression
            - Directory operations
            - File metadata management
            
            Ensure safe file operations with proper error handling
            and validation of file paths and permissions.
            """,
            quality_config={
                "domain": QualityDomain.SERVICE,
                "thresholds": {
                    "accuracy": 0.95,
                    "completeness": 0.90,
                    "relevance": 0.85
                }
            }
        )


class ComputationServiceAgent(StandardizedAgentBase):
    """
    Tier 3 Computation Service Agent.
    
    Performs complex calculations and numerical operations.
    Uses code_execution tool for dynamic computation.
    """
    
    def __init__(self):
        super().__init__(
            agent_name="ComputationServiceAgent",
            description="Executes computational and analytical tasks",
            instructions="""
            You are a computation specialist capable of:
            - Statistical analysis
            - Mathematical calculations
            - Data modeling
            - Algorithmic operations
            - Numerical simulations
            
            Use the code execution tool to perform complex calculations
            and return accurate results with appropriate precision.
            """,
            mcp_tools_enabled=True
        )
        
    async def init_agent(self):
        """Initialize computation agent with code execution capability."""
        await super().init_agent()
        
        # Use code_execution as the built-in tool
        self.adk_agent = Agent(
            name=self.agent_name,
            model="gemini-2.0-flash",
            instruction=self.instructions,
            tools=[code_execution] + self.tools  # Combine with MCP tools
        )


# Example coordination of multiple service agents
class ServiceCoordinator(StandardizedAgentBase):
    """
    Coordinates multiple Tier 3 service agents for complex operations.
    """
    
    def __init__(self):
        super().__init__(
            agent_name="ServiceCoordinator",
            description="Coordinates multiple service agents",
            instructions="Route tasks to appropriate service agents based on requirements."
        )
        self.service_agents = {}
        
    async def init_agent(self):
        """Initialize coordinator and service agents."""
        await super().init_agent()
        
        # Initialize all service agents
        self.service_agents = {
            'data_processing': DataProcessingServiceAgent(),
            'api_integration': APIIntegrationServiceAgent(),
            'file_operations': FileOperationsServiceAgent(),
            'computation': ComputationServiceAgent()
        }
        
        # Initialize each service agent
        for agent in self.service_agents.values():
            await agent.init_agent()
            
    async def execute_service_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Route task to appropriate service agent."""
        service_type = task.get('service_type', '').lower()
        
        if service_type in self.service_agents:
            agent = self.service_agents[service_type]
            
            if service_type == 'data_processing':
                return await agent.process_data(task)
            else:
                # Generic execution for other service types
                return await agent.adk_agent.run(task.get('request', ''))
                
        return {
            'success': False,
            'error': f"Unknown service type: {service_type}"
        }


# Example usage
async def main():
    """Demonstrate service agent usage."""
    # Data processing example
    data_agent = DataProcessingServiceAgent()
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
    
    # Service coordination example
    coordinator = ServiceCoordinator()
    await coordinator.init_agent()
    
    # Multi-service task
    complex_task = {
        'service_type': 'data_processing',
        'type': 'aggregate',
        'data': processing_task['data'],
        'requirements': 'Group by department and calculate statistics'
    }
    
    coord_result = await coordinator.execute_service_task(complex_task)
    print(f"Coordination result: {coord_result}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())