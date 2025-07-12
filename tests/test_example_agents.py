# ABOUTME: Tests for example agents to verify they work correctly
# ABOUTME: Demonstrates testing patterns for StandardizedAgentBase agents

"""
Tests for Example Agents

Verifies that the example agents can be created and function properly.
"""

import pytest
import asyncio
from typing import List, Dict, Any

from a2a_mcp.agents.examples import SearchAgent, SummarizationAgent, DataValidationAgent


class TestExampleAgents:
    """Test suite for example agents"""
    
    def test_search_agent_creation(self):
        """Test that SearchAgent can be created"""
        agent = SearchAgent()
        assert agent.agent_name == "search_agent"
        assert agent.description == "Web search and information retrieval agent"
        assert agent.get_agent_temperature() == 0.3
    
    def test_summarization_agent_creation(self):
        """Test that SummarizationAgent can be created"""
        agent = SummarizationAgent()
        assert agent.agent_name == "summarization_agent"
        assert agent.description == "Text summarization and processing agent"
        assert agent.get_agent_temperature() == 0.5
    
    def test_data_validation_agent_creation(self):
        """Test that DataValidationAgent can be created"""
        agent = DataValidationAgent()
        assert agent.agent_name == "data_validation_agent"
        assert agent.description == "Data validation and quality assurance agent"
        assert agent.get_agent_temperature() == 0.1
    
    @pytest.mark.asyncio
    async def test_search_agent_empty_query(self):
        """Test SearchAgent with empty query"""
        agent = SearchAgent()
        
        # Collect results
        results = []
        async for result in agent._execute_agent_logic(""):
            results.append(result)
        
        assert len(results) == 1
        assert results[0]["is_task_complete"] is True
        assert "provide a search query" in results[0]["content"].lower()
    
    @pytest.mark.asyncio
    async def test_summarization_agent_short_text(self):
        """Test SummarizationAgent with text too short"""
        agent = SummarizationAgent()
        
        # Collect results
        results = []
        async for result in agent._execute_agent_logic("Short text"):
            results.append(result)
        
        assert len(results) == 1
        assert results[0]["require_user_input"] is True
        assert "at least 50 characters" in results[0]["content"]
    
    @pytest.mark.asyncio
    async def test_data_validation_agent_invalid_json(self):
        """Test DataValidationAgent with invalid JSON"""
        agent = DataValidationAgent()
        
        # Collect results
        results = []
        async for result in agent._execute_agent_logic("not json"):
            results.append(result)
        
        assert len(results) == 1
        assert results[0]["is_task_complete"] is True
        assert "provide JSON data" in results[0]["content"]
    
    @pytest.mark.asyncio
    async def test_data_validation_agent_valid_json(self):
        """Test DataValidationAgent with valid JSON"""
        agent = DataValidationAgent()
        
        json_data = '{"id": "123", "type": "test", "data": {"key": "value"}}'
        
        # Collect results
        results = []
        async for result in agent._execute_agent_logic(f"Validate this: {json_data}"):
            results.append(result)
        
        assert len(results) == 1
        assert results[0]["is_task_complete"] is True
        assert "✅ VALID" in results[0]["content"] or "valid" in results[0]["content"].lower()
    
    def test_all_agents_have_quality_config(self):
        """Test that all agents have quality configuration"""
        agents = [SearchAgent(), SummarizationAgent(), DataValidationAgent()]
        
        for agent in agents:
            assert hasattr(agent, 'quality_config')
            assert 'domain' in agent.quality_config
            assert 'min_confidence_score' in agent.quality_config


if __name__ == "__main__":
    # Run tests without pytest
    test = TestExampleAgents()
    
    # Run sync tests
    print("Testing agent creation...")
    test.test_search_agent_creation()
    test.test_summarization_agent_creation()
    test.test_data_validation_agent_creation()
    test.test_all_agents_have_quality_config()
    print("✓ All creation tests passed")
    
    # Run async tests
    print("\nTesting agent logic...")
    asyncio.run(test.test_search_agent_empty_query())
    print("✓ Search agent empty query test passed")
    
    asyncio.run(test.test_summarization_agent_short_text())
    print("✓ Summarization agent short text test passed")
    
    asyncio.run(test.test_data_validation_agent_invalid_json())
    print("✓ Data validation invalid JSON test passed")
    
    asyncio.run(test.test_data_validation_agent_valid_json())
    print("✓ Data validation valid JSON test passed")
    
    print("\n✅ All tests passed!")