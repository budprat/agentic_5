# ABOUTME: Example data validation agent showing quality framework usage
# ABOUTME: Demonstrates validation patterns and structured data processing

"""
Data Validation Agent Example

An agent that validates data structures and ensures quality standards.
Shows advanced usage of the quality framework.
"""

from typing import Dict, Any, AsyncIterable, Optional, List
import json
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase


class DataValidationAgent(StandardizedAgentBase):
    """
    Example agent that performs data validation and quality checks.
    
    Demonstrates:
    - Custom validation rules
    - Quality framework integration
    - Structured error reporting
    - Schema validation patterns
    """
    
    def __init__(self):
        super().__init__(
            agent_name="data_validation_agent",
            description="Data validation and quality assurance agent",
            instructions="""You are a data validation specialist. Your tasks include:
            1. Validating data against schemas
            2. Checking data quality and completeness
            3. Identifying anomalies and issues
            4. Providing detailed validation reports""",
            quality_config={
                "domain": "SERVICE",  # Service domain for technical validation
                "min_confidence_score": 0.9,
                "required_validations": ["structure", "completeness", "consistency"]
            }
        )
        
        # Define validation rules
        self.validation_rules = {
            "required_fields": ["id", "type", "data"],
            "type_checks": {
                "id": (str, int),
                "type": str,
                "data": dict
            }
        }
    
    async def _execute_agent_logic(self, prompt: str) -> AsyncIterable[Dict[str, Any]]:
        """Execute validation logic"""
        # Parse input as JSON data to validate
        try:
            # Try to extract JSON from the prompt
            if "{" in prompt and "}" in prompt:
                json_start = prompt.find("{")
                json_end = prompt.rfind("}") + 1
                json_str = prompt[json_start:json_end]
                data = json.loads(json_str)
            else:
                yield {
                    "is_task_complete": True,
                    "require_user_input": True,
                    "content": "Please provide JSON data to validate. Format: {\"id\": ..., \"type\": ..., \"data\": {...}}"
                }
                return
                
        except json.JSONDecodeError as e:
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": f"Invalid JSON format: {str(e)}"
            }
            return
        
        # Perform validation
        validation_report = await self._validate_data(data)
        
        # Format report
        report_text = self._format_validation_report(validation_report)
        
        yield {
            "is_task_complete": True,
            "require_user_input": False,
            "content": report_text
        }
    
    async def _validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against rules"""
        issues = []
        warnings = []
        
        # Check required fields
        for field in self.validation_rules["required_fields"]:
            if field not in data:
                issues.append(f"Missing required field: '{field}'")
        
        # Check types
        for field, expected_types in self.validation_rules["type_checks"].items():
            if field in data:
                if not isinstance(data[field], expected_types):
                    issues.append(f"Field '{field}' has incorrect type. Expected {expected_types}, got {type(data[field])}")
        
        # Additional checks
        if "data" in data and isinstance(data["data"], dict):
            if not data["data"]:
                warnings.append("Data field is empty")
            if len(data["data"]) > 100:
                warnings.append("Data field contains many keys (>100)")
        
        # Calculate validation score
        total_checks = len(self.validation_rules["required_fields"]) + len(self.validation_rules["type_checks"])
        passed_checks = total_checks - len(issues)
        score = passed_checks / total_checks if total_checks > 0 else 0
        
        return {
            "valid": len(issues) == 0,
            "score": score,
            "issues": issues,
            "warnings": warnings,
            "data_summary": {
                "fields": list(data.keys()),
                "size": len(str(data))
            }
        }
    
    def _format_validation_report(self, report: Dict[str, Any]) -> str:
        """Format validation report for output"""
        lines = ["## Data Validation Report\n"]
        
        # Status
        status = "✅ VALID" if report["valid"] else "❌ INVALID"
        lines.append(f"**Status:** {status}")
        lines.append(f"**Score:** {report['score']:.2%}\n")
        
        # Issues
        if report["issues"]:
            lines.append("### Issues")
            for issue in report["issues"]:
                lines.append(f"- {issue}")
            lines.append("")
        
        # Warnings
        if report["warnings"]:
            lines.append("### Warnings")
            for warning in report["warnings"]:
                lines.append(f"- {warning}")
            lines.append("")
        
        # Summary
        lines.append("### Data Summary")
        lines.append(f"- Fields: {', '.join(report['data_summary']['fields'])}")
        lines.append(f"- Size: {report['data_summary']['size']} bytes")
        
        return "\n".join(lines)
    
    def get_agent_temperature(self) -> Optional[float]:
        """Very low temperature for consistent validation"""
        return 0.1
    
    def get_response_mime_type(self) -> Optional[str]:
        return "text/markdown"