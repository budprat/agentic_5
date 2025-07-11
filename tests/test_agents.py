# ABOUTME: Tests for example agents demonstrating agent behavior validation
# ABOUTME: Covers SearchAgent, SummarizationAgent, and DataValidationAgent functionality

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from datetime import datetime

from a2a_mcp.agents.search_agent import SearchAgent
from a2a_mcp.agents.summarization_agent import SummarizationAgent
from a2a_mcp.agents.data_validation_agent import DataValidationAgent
from a2a_mcp.core.agent import AgentCapability
from a2a_mcp.core.protocol import A2AMessage, MessageType, MessageStatus
from a2a_mcp.core.quality import QualityReport, QualityMetric


class TestSearchAgent:
    """Test suite for SearchAgent functionality"""
    
    @pytest.fixture
    def search_agent(self):
        """Create a SearchAgent instance for testing"""
        return SearchAgent(agent_id="test-search-001")
    
    def test_agent_initialization(self, search_agent):
        """Test SearchAgent is properly initialized"""
        assert search_agent.agent_id == "test-search-001"
        assert search_agent.agent_type == "search"
        assert AgentCapability.SEARCH in search_agent.capabilities
        assert AgentCapability.WEB_SCRAPING in search_agent.capabilities
    
    @pytest.mark.asyncio
    async def test_search_request_processing(self, search_agent):
        """Test SearchAgent processes search requests correctly"""
        # Create a search request message
        request = A2AMessage(
            message_id="msg-001",
            sender_id="requester-001",
            receiver_id="test-search-001",
            message_type=MessageType.REQUEST,
            content={
                "action": "search",
                "query": "Python testing best practices",
                "limit": 5
            },
            metadata={"priority": "high"}
        )
        
        # Mock the web search method
        with patch.object(search_agent, '_perform_web_search', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [
                {"title": "Test Result 1", "url": "http://example.com/1", "snippet": "Testing info"},
                {"title": "Test Result 2", "url": "http://example.com/2", "snippet": "More testing"}
            ]
            
            # Process the request
            response = await search_agent.process_request(request)
            
            # Verify response
            assert response.message_type == MessageType.RESPONSE
            assert response.status == MessageStatus.COMPLETED
            assert len(response.content["results"]) == 2
            assert response.content["results"][0]["title"] == "Test Result 1"
            mock_search.assert_called_once_with("Python testing best practices", 5)
    
    @pytest.mark.asyncio
    async def test_search_error_handling(self, search_agent):
        """Test SearchAgent handles errors gracefully"""
        request = A2AMessage(
            message_id="msg-002",
            sender_id="requester-001",
            receiver_id="test-search-001",
            message_type=MessageType.REQUEST,
            content={
                "action": "search",
                "query": "test query"
            }
        )
        
        # Mock search to raise an exception
        with patch.object(search_agent, '_perform_web_search', new_callable=AsyncMock) as mock_search:
            mock_search.side_effect = Exception("Search API error")
            
            # Process should handle error
            response = await search_agent.process_request(request)
            
            assert response.status == MessageStatus.FAILED
            assert "error" in response.content
            assert "Search API error" in response.content["error"]
    
    @pytest.mark.asyncio
    async def test_capability_query(self, search_agent):
        """Test SearchAgent responds to capability queries"""
        request = A2AMessage(
            message_id="msg-003",
            sender_id="requester-001",
            receiver_id="test-search-001",
            message_type=MessageType.REQUEST,
            content={"action": "get_capabilities"}
        )
        
        response = await search_agent.process_request(request)
        
        assert response.status == MessageStatus.COMPLETED
        assert "capabilities" in response.content
        assert "search" in response.content["capabilities"]
        assert "web_scraping" in response.content["capabilities"]


class TestSummarizationAgent:
    """Test suite for SummarizationAgent functionality"""
    
    @pytest.fixture
    def summarization_agent(self):
        """Create a SummarizationAgent instance for testing"""
        return SummarizationAgent(agent_id="test-summarizer-001")
    
    def test_agent_initialization(self, summarization_agent):
        """Test SummarizationAgent is properly initialized"""
        assert summarization_agent.agent_id == "test-summarizer-001"
        assert summarization_agent.agent_type == "summarization"
        assert AgentCapability.TEXT_PROCESSING in summarization_agent.capabilities
        assert AgentCapability.SUMMARIZATION in summarization_agent.capabilities
    
    @pytest.mark.asyncio
    async def test_text_summarization(self, summarization_agent):
        """Test SummarizationAgent summarizes text correctly"""
        long_text = """
        This is a long document about artificial intelligence and machine learning.
        It contains multiple paragraphs discussing various aspects of AI technology.
        The document covers topics such as neural networks, deep learning, and 
        natural language processing. There are also sections on practical applications
        and future developments in the field. This is just test content to demonstrate
        the summarization capabilities of the agent.
        """ * 3  # Make it longer
        
        request = A2AMessage(
            message_id="msg-004",
            sender_id="requester-001",
            receiver_id="test-summarizer-001",
            message_type=MessageType.REQUEST,
            content={
                "action": "summarize",
                "text": long_text,
                "max_length": 100
            }
        )
        
        response = await summarization_agent.process_request(request)
        
        assert response.status == MessageStatus.COMPLETED
        assert "summary" in response.content
        assert len(response.content["summary"]) <= 100
        assert "metrics" in response.content
        assert response.content["metrics"]["compression_ratio"] > 1.0
    
    @pytest.mark.asyncio
    async def test_invalid_summarization_request(self, summarization_agent):
        """Test SummarizationAgent handles invalid requests"""
        request = A2AMessage(
            message_id="msg-005",
            sender_id="requester-001",
            receiver_id="test-summarizer-001",
            message_type=MessageType.REQUEST,
            content={
                "action": "summarize",
                # Missing required 'text' field
                "max_length": 100
            }
        )
        
        response = await summarization_agent.process_request(request)
        
        assert response.status == MessageStatus.FAILED
        assert "error" in response.content
        assert "text" in response.content["error"].lower()


class TestDataValidationAgent:
    """Test suite for DataValidationAgent functionality"""
    
    @pytest.fixture
    def validation_agent(self):
        """Create a DataValidationAgent instance for testing"""
        return DataValidationAgent(agent_id="test-validator-001")
    
    def test_agent_initialization(self, validation_agent):
        """Test DataValidationAgent is properly initialized"""
        assert validation_agent.agent_id == "test-validator-001"
        assert validation_agent.agent_type == "data_validation"
        assert AgentCapability.VALIDATION in validation_agent.capabilities
        assert AgentCapability.QUALITY_ASSURANCE in validation_agent.capabilities
    
    @pytest.mark.asyncio
    async def test_data_validation_success(self, validation_agent):
        """Test DataValidationAgent validates correct data successfully"""
        request = A2AMessage(
            message_id="msg-006",
            sender_id="requester-001",
            receiver_id="test-validator-001",
            message_type=MessageType.REQUEST,
            content={
                "action": "validate",
                "data": {
                    "name": "John Doe",
                    "age": 30,
                    "email": "john.doe@example.com"
                },
                "schema": {
                    "name": {"type": "string", "required": True},
                    "age": {"type": "integer", "min": 0, "max": 150},
                    "email": {"type": "string", "pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"}
                }
            }
        )
        
        response = await validation_agent.process_request(request)
        
        assert response.status == MessageStatus.COMPLETED
        assert response.content["valid"] is True
        assert len(response.content["errors"]) == 0
        assert "validation_report" in response.content
    
    @pytest.mark.asyncio
    async def test_data_validation_failure(self, validation_agent):
        """Test DataValidationAgent detects invalid data"""
        request = A2AMessage(
            message_id="msg-007",
            sender_id="requester-001",
            receiver_id="test-validator-001",
            message_type=MessageType.REQUEST,
            content={
                "action": "validate",
                "data": {
                    "name": "",  # Empty name
                    "age": 200,  # Age too high
                    "email": "invalid-email"  # Invalid email format
                },
                "schema": {
                    "name": {"type": "string", "required": True, "min_length": 1},
                    "age": {"type": "integer", "min": 0, "max": 150},
                    "email": {"type": "string", "pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"}
                }
            }
        )
        
        response = await validation_agent.process_request(request)
        
        assert response.status == MessageStatus.COMPLETED
        assert response.content["valid"] is False
        assert len(response.content["errors"]) >= 3
        assert any("name" in error for error in response.content["errors"])
        assert any("age" in error for error in response.content["errors"])
        assert any("email" in error for error in response.content["errors"])
    
    @pytest.mark.asyncio
    async def test_quality_report_generation(self, validation_agent):
        """Test DataValidationAgent generates quality reports"""
        request = A2AMessage(
            message_id="msg-008",
            sender_id="requester-001",
            receiver_id="test-validator-001",
            message_type=MessageType.REQUEST,
            content={
                "action": "quality_check",
                "data": {"test": "data"},
                "checks": ["completeness", "consistency"]
            }
        )
        
        with patch.object(validation_agent.quality_framework, 'validate', new_callable=AsyncMock) as mock_validate:
            mock_report = QualityReport(
                agent_id="test-validator-001",
                timestamp=datetime.now(),
                metrics=[
                    QualityMetric(name="completeness", value=1.0, threshold=0.8, passed=True),
                    QualityMetric(name="consistency", value=0.95, threshold=0.9, passed=True)
                ],
                passed=True,
                issues=[]
            )
            mock_validate.return_value = mock_report
            
            response = await validation_agent.process_request(request)
            
            assert response.status == MessageStatus.COMPLETED
            assert "quality_report" in response.content
            assert response.content["quality_report"]["passed"] is True


class TestAgentIntegration:
    """Test suite for agent-to-agent communication"""
    
    @pytest.mark.asyncio
    async def test_search_to_summarization_workflow(self):
        """Test workflow: SearchAgent -> SummarizationAgent"""
        search_agent = SearchAgent(agent_id="search-001")
        summarization_agent = SummarizationAgent(agent_id="summarizer-001")
        
        # Mock search results
        search_results = [
            {
                "title": "AI Article 1",
                "url": "http://example.com/1",
                "snippet": "This article discusses the latest developments in AI..."
            },
            {
                "title": "AI Article 2",
                "url": "http://example.com/2",
                "snippet": "Machine learning has revolutionized many industries..."
            }
        ]
        
        # Create search request
        search_request = A2AMessage(
            message_id="workflow-001",
            sender_id="coordinator",
            receiver_id="search-001",
            message_type=MessageType.REQUEST,
            content={
                "action": "search",
                "query": "artificial intelligence",
                "limit": 2
            }
        )
        
        # Mock search response
        with patch.object(search_agent, '_perform_web_search', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = search_results
            search_response = await search_agent.process_request(search_request)
        
        # Create summarization request from search results
        combined_text = "\n".join([
            f"{r['title']}: {r['snippet']}" 
            for r in search_response.content["results"]
        ])
        
        summarize_request = A2AMessage(
            message_id="workflow-002",
            sender_id="coordinator",
            receiver_id="summarizer-001",
            message_type=MessageType.REQUEST,
            content={
                "action": "summarize",
                "text": combined_text,
                "max_length": 100
            },
            metadata={"source": "search_results"}
        )
        
        summary_response = await summarization_agent.process_request(summarize_request)
        
        assert search_response.status == MessageStatus.COMPLETED
        assert summary_response.status == MessageStatus.COMPLETED
        assert "summary" in summary_response.content
        assert len(summary_response.content["summary"]) <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])