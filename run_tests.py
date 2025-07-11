#!/usr/bin/env python3
# ABOUTME: Simple test runner for when pytest is not available
# ABOUTME: Runs basic tests to verify the boilerplate structure

import sys
import os
import importlib
import traceback

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all main modules can be imported"""
    print("Testing imports...")
    modules_to_test = [
        # Skip the main a2a_mcp module as it imports MCP server
        # 'a2a_mcp',
        'a2a_mcp.core',
        'a2a_mcp.core.agent',
        'a2a_mcp.core.protocol',
        'a2a_mcp.core.quality',
        # Skip common as it's imported by other modules
        # 'a2a_mcp.common',
        # 'a2a_mcp.common.utils',
        'a2a_mcp.agents.search_agent',
        'a2a_mcp.agents.summarization_agent',
        'a2a_mcp.agents.data_validation_agent',
    ]
    
    failed = []
    for module_name in modules_to_test:
        try:
            importlib.import_module(module_name)
            print(f"✓ {module_name}")
        except Exception as e:
            print(f"✗ {module_name}: {e}")
            failed.append(module_name)
    
    return len(failed) == 0


def test_agent_creation():
    """Test that agents can be created"""
    print("\nTesting agent creation...")
    
    try:
        from a2a_mcp.agents.search_agent import SearchAgent
        from a2a_mcp.agents.summarization_agent import SummarizationAgent
        from a2a_mcp.agents.data_validation_agent import DataValidationAgent
        
        # Create agents
        search = SearchAgent("test-search-001")
        print(f"✓ Created SearchAgent: {search.agent_id}")
        
        summarizer = SummarizationAgent("test-summarizer-001")
        print(f"✓ Created SummarizationAgent: {summarizer.agent_id}")
        
        validator = DataValidationAgent("test-validator-001")
        print(f"✓ Created DataValidationAgent: {validator.agent_id}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to create agents: {e}")
        traceback.print_exc()
        return False


def test_protocol_basics():
    """Test basic protocol functionality"""
    print("\nTesting protocol basics...")
    
    try:
        from a2a_mcp.core.protocol import A2AMessage, MessageType, A2AProtocol
        from a2a_mcp.agents.search_agent import SearchAgent
        
        # Create protocol
        protocol = A2AProtocol()
        print("✓ Created A2AProtocol")
        
        # Create and register agent
        agent = SearchAgent("test-agent-001")
        protocol.register_agent(agent)
        print("✓ Registered agent")
        
        # Create message
        msg = A2AMessage(
            message_id="msg-001",
            sender_id="test",
            receiver_id="test-agent-001",
            message_type=MessageType.REQUEST,
            content={"action": "get_capabilities"}
        )
        print("✓ Created A2AMessage")
        
        # Test serialization
        msg_dict = msg.to_dict()
        msg2 = A2AMessage.from_dict(msg_dict)
        print("✓ Message serialization works")
        
        return True
    except Exception as e:
        print(f"✗ Protocol test failed: {e}")
        traceback.print_exc()
        return False


def test_quality_framework():
    """Test quality framework basics"""
    print("\nTesting quality framework...")
    
    try:
        from a2a_mcp.core.quality import QualityFramework, QualityMetric, MetricType
        
        # Create framework
        framework = QualityFramework("test-agent")
        print("✓ Created QualityFramework")
        
        # Create metric
        metric = QualityMetric(
            name="test_metric",
            value=0.95,
            threshold=0.90,
            metric_type=MetricType.PERCENTAGE
        )
        print(f"✓ Created QualityMetric: passed={metric.passed}")
        
        return True
    except Exception as e:
        print(f"✗ Quality framework test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("Running boilerplate tests...\n")
    
    tests = [
        test_imports,
        test_agent_creation,
        test_protocol_basics,
        test_quality_framework,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n{'='*50}")
    print(f"Test Summary: {passed}/{total} passed")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())