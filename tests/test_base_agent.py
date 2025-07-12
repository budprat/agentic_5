# ABOUTME: Tests for BaseAgent abstract class and its implementations
# ABOUTME: Validates agent lifecycle, message handling, and protocol compliance

import pytest
from unittest.mock import Mock, patch, AsyncMock
from abc import ABC
import asyncio
from typing import Dict, Any, List

from a2a_mcp.common.base_agent import BaseAgent


class TestBaseAgent:
    """Test suite for BaseAgent abstract class"""
    
    def test_base_agent_is_abstract(self):
        """Test that BaseAgent cannot be instantiated directly"""
        with pytest.raises(TypeError):
            # Should fail because BaseAgent is abstract
            BaseAgent(agent_id="test", name="Test", description="Test agent")
    
    def test_concrete_agent_implementation(self):
        """Test creating a concrete implementation of BaseAgent"""
        class ConcreteAgent(BaseAgent):
            async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
                return {"status": "processed", "request": request}
            
            async def validate_request(self, request: Dict[str, Any]) -> bool:
                return "action" in request
            
            async def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
                return {"error": str(error), "context": context}
        
        # Should succeed with concrete implementation
        agent = ConcreteAgent(
            agent_id="concrete-001",
            name="Concrete Agent",
            description="A concrete implementation",
            capabilities=["test", "demo"]
        )
        
        assert agent.agent_id == "concrete-001"
        assert agent.name == "Concrete Agent"
        assert "test" in agent.capabilities
        assert "demo" in agent.capabilities
    
    @pytest.mark.asyncio
    async def test_agent_request_processing(self):
        """Test agent processes requests correctly"""
        class TestAgent(BaseAgent):
            async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
                action = request.get("action")
                if action == "echo":
                    return {"result": request.get("message", "")}
                elif action == "add":
                    numbers = request.get("numbers", [])
                    return {"result": sum(numbers)}
                else:
                    return {"error": "Unknown action"}
            
            async def validate_request(self, request: Dict[str, Any]) -> bool:
                return "action" in request
            
            async def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
                return {"error": str(error), "context": context}
        
        agent = TestAgent(
            agent_id="test-001",
            name="Test Agent",
            description="Agent for testing"
        )
        
        # Test echo action
        echo_response = await agent.process_request({
            "action": "echo",
            "message": "Hello, World!"
        })
        assert echo_response["result"] == "Hello, World!"
        
        # Test add action
        add_response = await agent.process_request({
            "action": "add",
            "numbers": [1, 2, 3, 4, 5]
        })
        assert add_response["result"] == 15
        
        # Test unknown action
        unknown_response = await agent.process_request({
            "action": "unknown"
        })
        assert "error" in unknown_response
    
    @pytest.mark.asyncio
    async def test_agent_request_validation(self):
        """Test agent validates requests before processing"""
        class ValidatingAgent(BaseAgent):
            async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
                # Should only be called if validation passes
                return {"processed": True}
            
            async def validate_request(self, request: Dict[str, Any]) -> bool:
                # Requires both 'action' and 'data' fields
                return "action" in request and "data" in request
            
            async def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
                return {"error": str(error)}
        
        agent = ValidatingAgent(
            agent_id="validator-001",
            name="Validating Agent",
            description="Agent with validation"
        )
        
        # Test valid request
        valid_request = {"action": "test", "data": {"value": 123}}
        is_valid = await agent.validate_request(valid_request)
        assert is_valid is True
        
        # Test invalid request (missing data)
        invalid_request = {"action": "test"}
        is_valid = await agent.validate_request(invalid_request)
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_agent_error_handling(self):
        """Test agent handles errors appropriately"""
        class ErrorHandlingAgent(BaseAgent):
            async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
                if request.get("trigger_error"):
                    raise ValueError("Intentional error for testing")
                return {"success": True}
            
            async def validate_request(self, request: Dict[str, Any]) -> bool:
                return True
            
            async def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
                return {
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                    "request": context.get("request", {})
                }
        
        agent = ErrorHandlingAgent(
            agent_id="error-handler-001",
            name="Error Handling Agent",
            description="Agent that handles errors"
        )
        
        # Test error handling
        error_context = {"request": {"trigger_error": True}}
        error_response = await agent.handle_error(
            ValueError("Test error"),
            error_context
        )
        
        assert error_response["error_type"] == "ValueError"
        assert error_response["error_message"] == "Test error"
        assert error_response["request"]["trigger_error"] is True
    
    def test_agent_metadata(self):
        """Test agent metadata and properties"""
        class MetadataAgent(BaseAgent):
            async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
                return {"processed": True}
            
            async def validate_request(self, request: Dict[str, Any]) -> bool:
                return True
            
            async def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
                return {"error": str(error)}
        
        metadata = {
            "version": "1.0.0",
            "author": "Test Suite",
            "tags": ["test", "example"]
        }
        
        agent = MetadataAgent(
            agent_id="metadata-001",
            name="Metadata Agent",
            description="Agent with metadata",
            metadata=metadata
        )
        
        assert agent.metadata["version"] == "1.0.0"
        assert agent.metadata["author"] == "Test Suite"
        assert "test" in agent.metadata["tags"]
    
    @pytest.mark.asyncio
    async def test_agent_lifecycle(self):
        """Test agent lifecycle methods (if implemented)"""
        class LifecycleAgent(BaseAgent):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.initialized = False
                self.shutdown = False
            
            async def initialize(self):
                """Initialize agent resources"""
                self.initialized = True
                return True
            
            async def shutdown(self):
                """Cleanup agent resources"""
                self.shutdown = True
                return True
            
            async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
                if not self.initialized:
                    return {"error": "Agent not initialized"}
                return {"status": "ok"}
            
            async def validate_request(self, request: Dict[str, Any]) -> bool:
                return True
            
            async def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
                return {"error": str(error)}
        
        agent = LifecycleAgent(
            agent_id="lifecycle-001",
            name="Lifecycle Agent",
            description="Agent with lifecycle methods"
        )
        
        # Test initialization
        assert agent.initialized is False
        await agent.initialize()
        assert agent.initialized is True
        
        # Test processing after initialization
        response = await agent.process_request({"test": "data"})
        assert response["status"] == "ok"
        
        # Test shutdown
        assert agent.shutdown is False
        await agent.shutdown()
        assert agent.shutdown is True


class TestAgentCapabilities:
    """Test suite for agent capability management"""
    
    def test_capability_registration(self):
        """Test registering and querying agent capabilities"""
        class CapableAgent(BaseAgent):
            async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
                action = request.get("action")
                if action in self.capabilities:
                    return {"result": f"Executing {action}"}
                return {"error": f"Capability '{action}' not supported"}
            
            async def validate_request(self, request: Dict[str, Any]) -> bool:
                return "action" in request
            
            async def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
                return {"error": str(error)}
        
        agent = CapableAgent(
            agent_id="capable-001",
            name="Capable Agent",
            description="Agent with multiple capabilities",
            capabilities=["search", "summarize", "analyze"]
        )
        
        assert len(agent.capabilities) == 3
        assert "search" in agent.capabilities
        assert "summarize" in agent.capabilities
        assert "analyze" in agent.capabilities
        assert "translate" not in agent.capabilities
    
    def test_dynamic_capability_updates(self):
        """Test dynamically updating agent capabilities"""
        class DynamicAgent(BaseAgent):
            def add_capability(self, capability: str):
                """Add a new capability"""
                if capability not in self.capabilities:
                    self.capabilities.append(capability)
            
            def remove_capability(self, capability: str):
                """Remove a capability"""
                if capability in self.capabilities:
                    self.capabilities.remove(capability)
            
            async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
                return {"capabilities": self.capabilities}
            
            async def validate_request(self, request: Dict[str, Any]) -> bool:
                return True
            
            async def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
                return {"error": str(error)}
        
        agent = DynamicAgent(
            agent_id="dynamic-001",
            name="Dynamic Agent",
            description="Agent with dynamic capabilities",
            capabilities=["basic"]
        )
        
        # Test initial capabilities
        assert len(agent.capabilities) == 1
        assert "basic" in agent.capabilities
        
        # Add capabilities
        agent.add_capability("advanced")
        agent.add_capability("expert")
        assert len(agent.capabilities) == 3
        assert "advanced" in agent.capabilities
        assert "expert" in agent.capabilities
        
        # Remove capability
        agent.remove_capability("basic")
        assert len(agent.capabilities) == 2
        assert "basic" not in agent.capabilities


if __name__ == "__main__":
    pytest.main([__file__, "-v"])