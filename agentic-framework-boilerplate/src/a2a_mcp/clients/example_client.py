# ABOUTME: Example A2A client demonstrating connection, communication, and error handling
# ABOUTME: Shows practical usage patterns for interacting with agents using the A2A protocol

"""
Example A2A Protocol Client
Demonstrates how to connect to and communicate with agents using the A2A protocol.

This module provides comprehensive examples of:
- Basic agent connection and message sending
- Error handling and retry strategies
- Response processing and data extraction
- Health checks and monitoring
- Batch operations and workflows
- Custom response processors
- Real-world usage patterns
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import the A2A protocol client and utilities
from ..common.a2a_protocol import (
    A2AProtocolClient,
    A2ACommunicationError,
    get_agent_port,
    register_agent_port
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExampleA2AClient:
    """
    Example client demonstrating A2A protocol usage patterns.
    
    This class provides practical examples of how to:
    - Connect to different types of agents
    - Handle various response formats
    - Implement error recovery
    - Process complex workflows
    """
    
    def __init__(self):
        """Initialize the example client with default A2A protocol configuration."""
        # Create A2A client with custom configuration
        self.client = A2AProtocolClient(
            default_timeout=30,  # 30 second timeout
            max_retries=3,       # Try up to 3 times
            retry_delay=1.0,     # Start with 1 second delay
            custom_port_mapping={
                # Add any custom agent mappings here
                "custom_agent": 11000,
                "test_agent": 11001
            }
        )
        
        # Track example session state
        self.session_id = f"example_{int(datetime.now().timestamp())}"
        self.results = []
        
    async def basic_message_example(self):
        """
        Example 1: Basic message sending to an agent.
        
        Shows the simplest way to send a message and receive a response.
        """
        print("\n=== Example 1: Basic Message Sending ===")
        
        try:
            # Send a simple message to the solopreneur oracle
            response = await self.client.send_message_by_name(
                agent_name="solopreneur_oracle",
                message="What are the key considerations for starting a software business?",
                metadata={
                    "session_id": self.session_id,
                    "example_type": "basic_message"
                }
            )
            
            # Process the response
            if response.get("success"):
                print(f" Response received successfully!")
                print(f"Content: {response['content'][:200]}...")  # First 200 chars
                print(f"Metadata: {response.get('metadata', {})}")
            else:
                print(f" Request failed: {response.get('content')}")
                
            return response
            
        except A2ACommunicationError as e:
            print(f" Communication error: {e}")
            return None
            
    async def error_handling_example(self):
        """
        Example 2: Comprehensive error handling patterns.
        
        Demonstrates how to handle various error scenarios gracefully.
        """
        print("\n=== Example 2: Error Handling ===")
        
        # Test 1: Handle agent not found
        try:
            print("Test 1: Non-existent agent")
            response = await self.client.send_message_by_name(
                agent_name="non_existent_agent",
                message="This should fail",
                metadata={"test": "agent_not_found"}
            )
        except ValueError as e:
            print(f" Correctly caught agent not found: {e}")
        except Exception as e:
            print(f" Unexpected error: {e}")
            
        # Test 2: Handle timeout with custom timeout
        try:
            print("\nTest 2: Custom timeout handling")
            response = await self.client.send_message(
                target_port=99999,  # Invalid port
                message="This should timeout",
                timeout=5,  # 5 second timeout
                metadata={"test": "timeout"}
            )
        except A2ACommunicationError as e:
            print(f" Correctly caught timeout/network error: {e}")
            
        # Test 3: Handle malformed response
        print("\nTest 3: Response validation")
        # This would typically be handled by the response processor
        
    async def response_processing_example(self):
        """
        Example 3: Advanced response processing patterns.
        
        Shows how to handle different response formats and extract data.
        """
        print("\n=== Example 3: Response Processing ===")
        
        # Create a custom response processor
        async def domain_specific_processor(response: Dict[str, Any]) -> Dict[str, Any]:
            """Custom processor for domain-specific responses."""
            # Check for special format
            if "result" in response and isinstance(response["result"], dict):
                result = response["result"]
                
                # Handle research results format
                if "research_data" in result:
                    return {
                        "success": True,
                        "content": {
                            "summary": result.get("summary"),
                            "sources": result.get("sources", []),
                            "confidence": result.get("confidence_score", 0.0)
                        },
                        "metadata": {
                            "processor": "domain_specific",
                            "timestamp": datetime.now().isoformat()
                        }
                    }
            
            # Fall back to default processing
            return None
        
        # Create client with custom processor
        custom_client = A2AProtocolClient(
            response_processor=domain_specific_processor
        )
        
        try:
            # Send request expecting custom format
            response = await custom_client.send_message(
                target_port=10902,  # Technical intelligence agent
                message="Research the latest trends in AI agent architectures",
                metadata={
                    "response_format": "research",
                    "include_sources": True
                }
            )
            
            print(f"Processed response: {json.dumps(response, indent=2)}")
            return response
            
        except Exception as e:
            print(f"Error in custom processing: {e}")
            return None
            
    async def health_check_example(self):
        """
        Example 4: Agent health checks and monitoring.
        
        Demonstrates how to check agent availability and health.
        """
        print("\n=== Example 4: Health Checks ===")
        
        # Single agent health check
        print("Checking single agent health...")
        health_result = await self.client.health_check(10901)  # Solopreneur oracle
        print(f"Oracle health: {health_result}")
        
        # Batch health check for multiple agents
        print("\nChecking multiple agents...")
        agents_to_check = [
            "solopreneur_oracle",
            "technical_intelligence",
            "knowledge_management"
        ]
        
        batch_results = await self.client.batch_health_check(agents_to_check)
        
        # Display results
        healthy_count = sum(1 for r in batch_results.values() if r["status"] == "healthy")
        print(f"\nHealth Check Summary:")
        print(f" Healthy agents: {healthy_count}/{len(batch_results)}")
        
        for agent_name, result in batch_results.items():
            status_icon = "" if result["status"] == "healthy" else ""
            print(f"{status_icon} {agent_name}: {result['status']}")
            
        return batch_results
        
    async def workflow_example(self):
        """
        Example 5: Complex multi-agent workflow.
        
        Shows how to coordinate multiple agents for a complex task.
        """
        print("\n=== Example 5: Multi-Agent Workflow ===")
        
        workflow_results = {}
        
        try:
            # Step 1: Get analysis from oracle
            print("Step 1: Consulting Oracle...")
            oracle_response = await self.client.send_message_by_name(
                agent_name="solopreneur_oracle",
                message="Analyze market opportunity for an AI code review tool",
                metadata={
                    "workflow_id": self.session_id,
                    "step": 1
                }
            )
            workflow_results["oracle_analysis"] = oracle_response
            
            if not oracle_response.get("success"):
                print("Oracle analysis failed, aborting workflow")
                return workflow_results
                
            # Step 2: Get technical details
            print("\nStep 2: Getting technical insights...")
            tech_response = await self.client.send_message_by_name(
                agent_name="technical_intelligence",
                message=f"Based on this market analysis: {oracle_response['content'][:500]}... "
                       f"What technical architecture would you recommend?",
                metadata={
                    "workflow_id": self.session_id,
                    "step": 2,
                    "oracle_context": True
                }
            )
            workflow_results["technical_design"] = tech_response
            
            # Step 3: Synthesize results
            print("\nStep 3: Synthesizing insights...")
            synthesis_response = await self.client.send_message_by_name(
                agent_name="integration_synthesis",
                message=f"Synthesize these insights into an action plan:\n"
                       f"Market: {oracle_response['content'][:300]}...\n"
                       f"Technical: {tech_response['content'][:300]}...",
                metadata={
                    "workflow_id": self.session_id,
                    "step": 3,
                    "final_synthesis": True
                }
            )
            workflow_results["synthesis"] = synthesis_response
            
            # Display final results
            print("\n=== Workflow Complete ===")
            print(f"Oracle Analysis: {oracle_response.get('success', False)}")
            print(f"Technical Design: {tech_response.get('success', False)}")
            print(f"Final Synthesis: {synthesis_response.get('success', False)}")
            
            return workflow_results
            
        except Exception as e:
            print(f"Workflow error at step: {e}")
            workflow_results["error"] = str(e)
            return workflow_results
            
    async def batch_operations_example(self):
        """
        Example 6: Batch operations and parallel processing.
        
        Demonstrates efficient parallel communication with multiple agents.
        """
        print("\n=== Example 6: Batch Operations ===")
        
        # Define batch queries
        queries = [
            ("solopreneur_oracle", "What are common startup mistakes?"),
            ("technical_intelligence", "What are best practices for API design?"),
            ("knowledge_management", "How to organize technical documentation?")
        ]
        
        # Execute queries in parallel
        print("Sending parallel queries to multiple agents...")
        tasks = []
        for agent_name, query in queries:
            task = self.client.send_message_by_name(
                agent_name=agent_name,
                message=query,
                metadata={
                    "batch_id": self.session_id,
                    "query_type": "batch"
                }
            )
            tasks.append((agent_name, task))
            
        # Gather results
        results = {}
        for agent_name, task in tasks:
            try:
                response = await task
                results[agent_name] = {
                    "success": response.get("success", False),
                    "preview": response.get("content", "")[:100] + "..."
                }
                print(f" {agent_name}: Received response")
            except Exception as e:
                results[agent_name] = {"success": False, "error": str(e)}
                print(f" {agent_name}: {e}")
                
        return results
        
    async def custom_headers_example(self):
        """
        Example 7: Using custom headers for authentication or routing.
        
        Shows how to add custom headers to A2A requests.
        """
        print("\n=== Example 7: Custom Headers ===")
        
        try:
            response = await self.client.send_message(
                target_port=10901,
                message="Get premium analysis features",
                metadata={"tier": "premium"},
                custom_headers={
                    "X-API-Key": "example-api-key",
                    "X-Client-ID": self.session_id,
                    "X-Priority": "high"
                }
            )
            
            print(f"Response with custom headers: {response.get('success')}")
            return response
            
        except Exception as e:
            print(f"Custom header request failed: {e}")
            return None
            
    async def get_session_statistics(self):
        """
        Example 8: Session statistics and monitoring.
        
        Shows how to track communication metrics.
        """
        print("\n=== Example 8: Session Statistics ===")
        
        stats = self.client.get_session_stats()
        
        print("Session Communication Statistics:")
        print(f"  Total Requests: {stats['requests_sent']}")
        print(f"  Successful: {stats['requests_successful']}")
        print(f"  Failed: {stats['requests_failed']}")
        print(f"  Success Rate: {stats['success_rate_percent']}%")
        print(f"  Total Retries: {stats['retries_performed']}")
        print(f"  Avg Retries/Request: {stats['average_retries_per_request']:.2f}")
        
        return stats


async def main():
    """
    Main function demonstrating all example patterns.
    
    Run this to see comprehensive A2A protocol usage examples.
    """
    print("=== A2A Protocol Client Examples ===")
    print(f"Starting example session at {datetime.now()}")
    
    # Initialize example client
    example_client = ExampleA2AClient()
    
    # Run all examples
    examples = [
        ("Basic Message", example_client.basic_message_example),
        ("Error Handling", example_client.error_handling_example),
        ("Response Processing", example_client.response_processing_example),
        ("Health Checks", example_client.health_check_example),
        ("Multi-Agent Workflow", example_client.workflow_example),
        ("Batch Operations", example_client.batch_operations_example),
        ("Custom Headers", example_client.custom_headers_example),
        ("Session Statistics", example_client.get_session_statistics)
    ]
    
    # Store all results
    all_results = {}
    
    for example_name, example_func in examples:
        try:
            print(f"\n{'='*60}")
            result = await example_func()
            all_results[example_name] = {"success": True, "result": result}
        except Exception as e:
            print(f"\nExample '{example_name}' failed with error: {e}")
            all_results[example_name] = {"success": False, "error": str(e)}
            
    # Final summary
    print(f"\n{'='*60}")
    print("=== Example Session Complete ===")
    successful = sum(1 for r in all_results.values() if r["success"])
    print(f"Successfully ran {successful}/{len(examples)} examples")
    
    return all_results


# Quick usage examples for common patterns
async def quick_send_message(agent_name: str, message: str) -> Optional[Dict[str, Any]]:
    """
    Quick helper for sending a single message to an agent.
    
    Args:
        agent_name: Name of the target agent
        message: Message to send
        
    Returns:
        Response dict or None if failed
    """
    client = A2AProtocolClient()
    try:
        return await client.send_message_by_name(agent_name, message)
    except Exception as e:
        logger.error(f"Failed to send message to {agent_name}: {e}")
        return None


async def quick_health_check(agent_name: str) -> bool:
    """
    Quick helper to check if an agent is healthy.
    
    Args:
        agent_name: Name of the agent to check
        
    Returns:
        True if healthy, False otherwise
    """
    client = A2AProtocolClient()
    try:
        port = get_agent_port(agent_name)
        result = await client.health_check(port)
        return result["status"] == "healthy"
    except Exception:
        return False


# Example of extending with custom agents
def setup_custom_agents():
    """Example of registering custom agents."""
    # Method 1: Register globally
    register_agent_port("my_custom_analyzer", 11100)
    register_agent_port("my_custom_processor", 11101)
    
    # Method 2: Use in client initialization
    client = A2AProtocolClient(
        custom_port_mapping={
            "experimental_agent": 11200,
            "test_orchestrator": 11201
        }
    )
    return client


if __name__ == "__main__":
    # Run all examples when script is executed directly
    asyncio.run(main())