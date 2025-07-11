#!/usr/bin/env python3
# ABOUTME: Simple test runner for when pytest is not available
# ABOUTME: Runs basic tests to verify the boilerplate framework structure

import sys
import os
import asyncio
import traceback

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all main modules can be imported"""
    print("Testing imports...")
    modules_to_test = [
        'a2a_mcp.common.a2a_protocol',
        'a2a_mcp.common.base_agent',
        'a2a_mcp.common.quality_framework',
        'a2a_mcp.common.standardized_agent_base',
        'a2a_mcp.agents.example_domain.master_oracle',
        'a2a_mcp.agents.example_domain.domain_specialist',
        'a2a_mcp.agents.example_domain.service_agent',
        'a2a_mcp.agents.examples.search_agent',
        'a2a_mcp.agents.examples.summarization_agent',
        'a2a_mcp.agents.examples.data_validation_agent',
    ]
    
    failed = []
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✓ {module_name}")
        except Exception as e:
            print(f"✗ {module_name}: {e}")
            failed.append(module_name)
    
    return len(failed) == 0


async def test_agent_creation():
    """Test that agents can be created"""
    print("\nTesting agent creation...")
    
    try:
        from a2a_mcp.agents.example_domain.master_oracle import MasterOracleAgent
        from a2a_mcp.agents.example_domain.domain_specialist import ResearchSpecialistAgent
        from a2a_mcp.agents.example_domain.service_agent import ServiceAgent
        from a2a_mcp.agents.examples import SearchAgent, SummarizationAgent, DataValidationAgent
        
        # Create instances
        agents = [
            MasterOracleAgent(),
            ResearchSpecialistAgent(),
            ServiceAgent(),
            SearchAgent(),
            SummarizationAgent(),
            DataValidationAgent()
        ]
        
        for agent in agents:
            print(f"✓ Created {agent.__class__.__name__}")
        
        return True
    except Exception as e:
        print(f"✗ Agent creation failed: {e}")
        traceback.print_exc()
        return False


async def test_protocol_basics():
    """Test basic A2A protocol functionality"""
    print("\nTesting A2A protocol...")
    
    try:
        from a2a_mcp.common.a2a_protocol import A2AProtocolClient
        
        # Create protocol client
        client = A2AProtocolClient()
        print("✓ Created A2A protocol client")
        
        # Test message creation
        message = {
            "jsonrpc": "2.0",
            "method": "test",
            "params": {"data": "test"},
            "id": "test-1"
        }
        print("✓ Created test message")
        
        return True
    except Exception as e:
        print(f"✗ Protocol test failed: {e}")
        traceback.print_exc()
        return False


async def test_quality_framework():
    """Test quality framework basics"""
    print("\nTesting quality framework...")
    
    try:
        from a2a_mcp.common.quality_framework import QualityThresholdFramework
        
        # Create framework instance
        qf = QualityThresholdFramework()
        print("✓ Created quality framework")
        
        # Test validation
        result = await qf.validate_response(
            {"result": "test", "confidence": 0.95},
            {"min_confidence_score": 0.8}
        )
        print(f"✓ Validation result: {result}")
        
        return True
    except Exception as e:
        print(f"✗ Quality framework test failed: {e}")
        traceback.print_exc()
        return False


async def test_example_agents():
    """Test example agent functionality"""
    print("\nTesting example agents...")
    
    try:
        from a2a_mcp.agents.examples import DataValidationAgent
        
        agent = DataValidationAgent()
        
        # Test with valid JSON
        json_data = '{"id": "123", "type": "test", "data": {"key": "value"}}'
        results = []
        async for result in agent._execute_agent_logic(f"Validate: {json_data}"):
            results.append(result)
        
        if results and results[0]["is_task_complete"]:
            print("✓ Data validation agent processed valid JSON")
        else:
            print("✗ Data validation agent failed to process JSON")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Example agent test failed: {e}")
        traceback.print_exc()
        return False


async def run_tests():
    """Run all tests"""
    print("=" * 50)
    print("Running A2A-MCP Framework Tests")
    print("=" * 50)
    
    results = []
    
    # Run sync tests
    results.append(test_imports())
    
    # Run async tests
    results.append(await test_agent_creation())
    results.append(await test_protocol_basics())
    results.append(await test_quality_framework())
    results.append(await test_example_agents())
    
    # Summary
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ All tests passed! ({passed}/{total})")
        return 0
    else:
        print(f"✗ Some tests failed! ({passed}/{total} passed)")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_tests())
    sys.exit(exit_code)