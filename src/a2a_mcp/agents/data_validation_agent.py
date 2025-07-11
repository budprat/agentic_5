# ABOUTME: Example DataValidationAgent implementation for the A2A MCP framework
# ABOUTME: Demonstrates data validation and quality assurance capabilities

import asyncio
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

from a2a_mcp.core.agent import Agent, AgentCapability
from a2a_mcp.core.protocol import A2AMessage, MessageType, MessageStatus
from a2a_mcp.core.quality import (
    QualityFramework, QualityReport, QualityMetric,
    QualityIssue, QualityLevel, ValidationRule
)
from a2a_mcp.common.utils import logger, generate_id


class DataValidationAgent(Agent):
    """
    Example agent that performs data validation and quality checks
    """
    
    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            agent_type="data_validation",
            capabilities={
                AgentCapability.VALIDATION,
                AgentCapability.QUALITY_ASSURANCE
            },
            metadata={
                "version": "1.0.0",
                "description": "Data validation and quality assurance agent"
            }
        )
        
        # Initialize quality framework
        self.quality_framework = QualityFramework(agent_id=agent_id)
        self._setup_validation_rules()
    
    def _setup_validation_rules(self):
        """Set up common validation rules"""
        # Add some default validation rules
        self.quality_framework.add_rule(ValidationRule(
            name="non_empty_data",
            validator=lambda data: bool(data),
            error_message="Data cannot be empty"
        ))
    
    async def process_request(self, message: A2AMessage) -> A2AMessage:
        """Process incoming validation requests"""
        try:
            action = message.content.get("action")
            
            if action == "validate":
                return await self._handle_validate_request(message)
            elif action == "quality_check":
                return await self._handle_quality_check(message)
            elif action == "get_capabilities":
                return await self._handle_capability_query(message)
            else:
                return self._create_error_response(
                    message,
                    f"Unknown action: {action}"
                )
        
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return self._create_error_response(message, str(e))
    
    async def _handle_validate_request(self, message: A2AMessage) -> A2AMessage:
        """Handle data validation requests"""
        data = message.content.get("data")
        schema = message.content.get("schema", {})
        
        if data is None:
            return self._create_error_response(
                message,
                "Data field is required for validation"
            )
        
        # Perform validation
        validation_result = await self._validate_data(data, schema)
        
        # Create response
        return A2AMessage(
            message_id=generate_id("msg"),
            sender_id=self.agent_id,
            receiver_id=message.sender_id,
            message_type=MessageType.RESPONSE,
            content={
                "valid": validation_result["valid"],
                "errors": validation_result["errors"],
                "validation_report": validation_result["report"]
            },
            correlation_id=message.message_id,
            status=MessageStatus.COMPLETED
        )
    
    async def _handle_quality_check(self, message: A2AMessage) -> A2AMessage:
        """Handle quality check requests"""
        data = message.content.get("data")
        checks = message.content.get("checks", ["completeness", "consistency"])
        
        if data is None:
            return self._create_error_response(
                message,
                "Data field is required for quality check"
            )
        
        # Perform quality check
        report = await self.quality_framework.validate(data)
        
        # Create response
        return A2AMessage(
            message_id=generate_id("msg"),
            sender_id=self.agent_id,
            receiver_id=message.sender_id,
            message_type=MessageType.RESPONSE,
            content={
                "quality_report": report.to_dict()
            },
            correlation_id=message.message_id,
            status=MessageStatus.COMPLETED
        )
    
    async def _handle_capability_query(self, message: A2AMessage) -> A2AMessage:
        """Handle capability query requests"""
        capabilities = [cap.value for cap in self.capabilities]
        
        return A2AMessage(
            message_id=generate_id("msg"),
            sender_id=self.agent_id,
            receiver_id=message.sender_id,
            message_type=MessageType.RESPONSE,
            content={
                "capabilities": capabilities,
                "agent_type": self.agent_type,
                "metadata": self.metadata
            },
            correlation_id=message.message_id,
            status=MessageStatus.COMPLETED
        )
    
    async def _validate_data(
        self,
        data: Any,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate data against schema
        """
        # Simulate processing delay
        await asyncio.sleep(0.2)
        
        errors = []
        
        # Validate against schema if provided
        if isinstance(data, dict) and schema:
            for field_name, field_rules in schema.items():
                field_value = data.get(field_name)
                
                # Check required fields
                if field_rules.get("required", False) and field_value is None:
                    errors.append(f"Required field '{field_name}' is missing")
                    continue
                
                if field_value is not None:
                    # Type validation
                    expected_type = field_rules.get("type")
                    if expected_type:
                        if not self._check_type(field_value, expected_type):
                            errors.append(
                                f"Field '{field_name}' has invalid type. "
                                f"Expected {expected_type}"
                            )
                    
                    # Range validation for numbers
                    if expected_type in ["integer", "number"]:
                        min_val = field_rules.get("min")
                        max_val = field_rules.get("max")
                        
                        if min_val is not None and field_value < min_val:
                            errors.append(
                                f"Field '{field_name}' value {field_value} "
                                f"is below minimum {min_val}"
                            )
                        
                        if max_val is not None and field_value > max_val:
                            errors.append(
                                f"Field '{field_name}' value {field_value} "
                                f"exceeds maximum {max_val}"
                            )
                    
                    # String validation
                    if expected_type == "string":
                        pattern = field_rules.get("pattern")
                        if pattern and not re.match(pattern, str(field_value)):
                            errors.append(
                                f"Field '{field_name}' does not match "
                                f"required pattern"
                            )
                        
                        min_length = field_rules.get("min_length")
                        if min_length and len(str(field_value)) < min_length:
                            errors.append(
                                f"Field '{field_name}' is too short "
                                f"(minimum {min_length} characters)"
                            )
        
        # Create validation report
        valid = len(errors) == 0
        report = {
            "timestamp": datetime.now().isoformat(),
            "data_type": type(data).__name__,
            "validation_passed": valid,
            "error_count": len(errors),
            "errors": errors
        }
        
        return {
            "valid": valid,
            "errors": errors,
            "report": report
        }
    
    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type"""
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        expected = type_map.get(expected_type)
        if expected:
            return isinstance(value, expected)
        
        return True
    
    def _create_error_response(
        self,
        original_message: A2AMessage,
        error: str
    ) -> A2AMessage:
        """Create an error response message"""
        return A2AMessage(
            message_id=generate_id("msg"),
            sender_id=self.agent_id,
            receiver_id=original_message.sender_id,
            message_type=MessageType.RESPONSE,
            content={"error": error},
            correlation_id=original_message.message_id,
            status=MessageStatus.FAILED
        )