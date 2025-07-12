# ABOUTME: Tests for quality validation framework
# ABOUTME: Covers quality metrics, validation rules, and reporting

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import json

from a2a_mcp.core.quality import (
    QualityFramework, QualityMetric, QualityReport, QualityIssue,
    QualityLevel, ValidationRule, MetricType
)
from a2a_mcp.core.protocol import A2AMessage, MessageType


class TestQualityMetric:
    """Test suite for QualityMetric functionality"""
    
    def test_metric_creation(self):
        """Test creating quality metrics"""
        metric = QualityMetric(
            name="accuracy",
            value=0.95,
            threshold=0.90,
            metric_type=MetricType.PERCENTAGE
        )
        
        assert metric.name == "accuracy"
        assert metric.value == 0.95
        assert metric.threshold == 0.90
        assert metric.passed is True
        assert metric.metric_type == MetricType.PERCENTAGE
    
    def test_metric_failure(self):
        """Test metric failure when below threshold"""
        metric = QualityMetric(
            name="completeness",
            value=0.75,
            threshold=0.80,
            metric_type=MetricType.PERCENTAGE
        )
        
        assert metric.passed is False
        assert metric.value < metric.threshold
    
    def test_metric_types(self):
        """Test different metric types"""
        # Count metric
        count_metric = QualityMetric(
            name="error_count",
            value=2,
            threshold=5,
            metric_type=MetricType.COUNT,
            inverse=True  # Lower is better
        )
        assert count_metric.passed is True
        
        # Score metric
        score_metric = QualityMetric(
            name="quality_score",
            value=8.5,
            threshold=7.0,
            metric_type=MetricType.SCORE
        )
        assert score_metric.passed is True
        
        # Boolean metric
        bool_metric = QualityMetric(
            name="has_documentation",
            value=1.0,
            threshold=1.0,
            metric_type=MetricType.BOOLEAN
        )
        assert bool_metric.passed is True


class TestQualityReport:
    """Test suite for QualityReport functionality"""
    
    def test_report_creation(self):
        """Test creating quality reports"""
        metrics = [
            QualityMetric("accuracy", 0.95, 0.90),
            QualityMetric("completeness", 0.88, 0.85),
            QualityMetric("response_time", 0.5, 1.0)
        ]
        
        report = QualityReport(
            agent_id="test-agent-001",
            timestamp=datetime.now(),
            metrics=metrics,
            metadata={"test_run": "unit_test"}
        )
        
        assert report.agent_id == "test-agent-001"
        assert len(report.metrics) == 3
        assert report.passed is True
        assert report.overall_score > 0.8
    
    def test_report_with_failures(self):
        """Test report with failing metrics"""
        metrics = [
            QualityMetric("accuracy", 0.95, 0.90),
            QualityMetric("completeness", 0.70, 0.85),  # Failing
            QualityMetric("validity", 0.60, 0.80)  # Failing
        ]
        
        issues = [
            QualityIssue(
                level=QualityLevel.ERROR,
                metric="completeness",
                message="Data completeness below threshold",
                details={"missing_fields": ["field1", "field2"]}
            ),
            QualityIssue(
                level=QualityLevel.WARNING,
                metric="validity",
                message="Validation warnings found",
                details={"warnings": 3}
            )
        ]
        
        report = QualityReport(
            agent_id="test-agent-001",
            timestamp=datetime.now(),
            metrics=metrics,
            issues=issues
        )
        
        assert report.passed is False
        assert len(report.issues) == 2
        assert report.has_errors is True
        assert report.error_count == 1
        assert report.warning_count == 1
    
    def test_report_serialization(self):
        """Test report serialization to dict"""
        metrics = [QualityMetric("test_metric", 0.9, 0.8)]
        report = QualityReport(
            agent_id="test-agent",
            timestamp=datetime.now(),
            metrics=metrics
        )
        
        report_dict = report.to_dict()
        
        assert "agent_id" in report_dict
        assert "timestamp" in report_dict
        assert "metrics" in report_dict
        assert "passed" in report_dict
        assert "overall_score" in report_dict
        assert len(report_dict["metrics"]) == 1


class TestValidationRule:
    """Test suite for ValidationRule functionality"""
    
    def test_simple_validation_rule(self):
        """Test simple validation rules"""
        # Required field rule
        rule = ValidationRule(
            name="required_field",
            validator=lambda data: "required_key" in data,
            error_message="Missing required field: required_key"
        )
        
        assert rule.validate({"required_key": "value"}) is True
        assert rule.validate({"other_key": "value"}) is False
    
    def test_complex_validation_rule(self):
        """Test complex validation rules"""
        # Range validation
        def validate_range(data):
            value = data.get("value", 0)
            return 0 <= value <= 100
        
        rule = ValidationRule(
            name="value_range",
            validator=validate_range,
            error_message="Value must be between 0 and 100",
            level=QualityLevel.ERROR
        )
        
        assert rule.validate({"value": 50}) is True
        assert rule.validate({"value": 150}) is False
        assert rule.validate({"value": -10}) is False
    
    def test_validation_rule_with_context(self):
        """Test validation rules with context"""
        def validate_consistency(data, context=None):
            if context and "expected_sum" in context:
                actual_sum = sum(data.get("values", []))
                return actual_sum == context["expected_sum"]
            return True
        
        rule = ValidationRule(
            name="sum_consistency",
            validator=validate_consistency,
            error_message="Sum of values doesn't match expected"
        )
        
        data = {"values": [10, 20, 30]}
        assert rule.validate(data, context={"expected_sum": 60}) is True
        assert rule.validate(data, context={"expected_sum": 50}) is False


class TestQualityFramework:
    """Test suite for QualityFramework functionality"""
    
    @pytest.fixture
    def framework(self):
        """Create QualityFramework instance for testing"""
        return QualityFramework(agent_id="test-agent-001")
    
    def test_framework_initialization(self, framework):
        """Test framework initialization"""
        assert framework.agent_id == "test-agent-001"
        assert len(framework.rules) == 0
        assert len(framework.metrics_config) > 0  # Should have default metrics
    
    def test_add_validation_rules(self, framework):
        """Test adding validation rules to framework"""
        rule1 = ValidationRule(
            name="has_content",
            validator=lambda data: bool(data.get("content")),
            error_message="Content is required"
        )
        
        rule2 = ValidationRule(
            name="valid_status",
            validator=lambda data: data.get("status") in ["success", "pending", "failed"],
            error_message="Invalid status value"
        )
        
        framework.add_rule(rule1)
        framework.add_rule(rule2)
        
        assert len(framework.rules) == 2
        assert "has_content" in [r.name for r in framework.rules]
    
    @pytest.mark.asyncio
    async def test_validate_data(self, framework):
        """Test data validation"""
        # Add rules
        framework.add_rule(ValidationRule(
            name="required_fields",
            validator=lambda d: all(k in d for k in ["id", "type", "data"]),
            error_message="Missing required fields"
        ))
        
        framework.add_rule(ValidationRule(
            name="valid_type",
            validator=lambda d: d.get("type") in ["A", "B", "C"],
            error_message="Invalid type"
        ))
        
        # Test valid data
        valid_data = {
            "id": "123",
            "type": "A",
            "data": {"test": "value"}
        }
        
        report = await framework.validate(valid_data)
        assert report.passed is True
        assert len(report.issues) == 0
        
        # Test invalid data
        invalid_data = {
            "id": "456",
            "type": "X",  # Invalid type
            # Missing 'data' field
        }
        
        report = await framework.validate(invalid_data)
        assert report.passed is False
        assert len(report.issues) >= 2
    
    @pytest.mark.asyncio
    async def test_validate_message(self, framework):
        """Test A2A message validation"""
        # Add message-specific rules
        framework.add_rule(ValidationRule(
            name="valid_message_content",
            validator=lambda d: isinstance(d.get("content"), dict),
            error_message="Message content must be a dictionary"
        ))
        
        # Valid message
        valid_msg = A2AMessage(
            message_id="msg-001",
            sender_id="sender",
            receiver_id="receiver",
            message_type=MessageType.REQUEST,
            content={"action": "test"}
        )
        
        report = await framework.validate_message(valid_msg)
        assert report.passed is True
        
        # Invalid message (content is not dict)
        invalid_msg = A2AMessage(
            message_id="msg-002",
            sender_id="sender",
            receiver_id="receiver",
            message_type=MessageType.REQUEST,
            content="invalid_content"  # Should be dict
        )
        
        report = await framework.validate_message(invalid_msg)
        assert report.passed is False
    
    @pytest.mark.asyncio
    async def test_custom_metrics(self, framework):
        """Test custom metric calculation"""
        # Add custom metric calculator
        def calculate_data_quality(data):
            # Simple quality score based on data completeness
            total_fields = 5
            present_fields = len([k for k in ["id", "name", "type", "value", "timestamp"] if k in data])
            return present_fields / total_fields
        
        framework.add_metric_calculator("data_quality", calculate_data_quality, threshold=0.8)
        
        # Test with complete data
        complete_data = {
            "id": "123",
            "name": "Test",
            "type": "A",
            "value": 100,
            "timestamp": datetime.now().isoformat()
        }
        
        report = await framework.validate(complete_data)
        quality_metric = next((m for m in report.metrics if m.name == "data_quality"), None)
        assert quality_metric is not None
        assert quality_metric.value == 1.0
        assert quality_metric.passed is True
        
        # Test with incomplete data
        incomplete_data = {
            "id": "456",
            "name": "Test2"
            # Missing type, value, timestamp
        }
        
        report = await framework.validate(incomplete_data)
        quality_metric = next((m for m in report.metrics if m.name == "data_quality"), None)
        assert quality_metric.value == 0.4
        assert quality_metric.passed is False
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, framework):
        """Test performance metric tracking"""
        # Simulate message processing with timing
        start_time = datetime.now()
        
        # Simulate some processing
        await asyncio.sleep(0.1)  # 100ms
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Add performance metric
        framework.add_metric_calculator(
            "response_time",
            lambda d: processing_time,
            threshold=0.5,  # 500ms threshold
            metric_type=MetricType.TIME
        )
        
        report = await framework.validate({})
        perf_metric = next((m for m in report.metrics if m.name == "response_time"), None)
        assert perf_metric is not None
        assert 0.09 < perf_metric.value < 0.15  # Around 100ms
        assert perf_metric.passed is True


class TestQualityAggregation:
    """Test suite for quality metric aggregation"""
    
    @pytest.mark.asyncio
    async def test_aggregate_quality_reports(self):
        """Test aggregating multiple quality reports"""
        # Create multiple reports
        reports = []
        for i in range(5):
            metrics = [
                QualityMetric("accuracy", 0.9 + i * 0.01, 0.9),
                QualityMetric("speed", 1.0 - i * 0.1, 0.5)
            ]
            report = QualityReport(
                agent_id=f"agent-{i:03d}",
                timestamp=datetime.now() - timedelta(minutes=i),
                metrics=metrics
            )
            reports.append(report)
        
        # Aggregate metrics
        aggregated = QualityFramework.aggregate_reports(reports)
        
        assert "accuracy" in aggregated
        assert "speed" in aggregated
        assert aggregated["accuracy"]["avg"] > 0.9
        assert aggregated["speed"]["min"] >= 0.5
        assert aggregated["speed"]["max"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_quality_trends(self):
        """Test quality trend analysis"""
        framework = QualityFramework(agent_id="trend-test")
        
        # Generate historical data
        historical_reports = []
        for day in range(7):
            timestamp = datetime.now() - timedelta(days=day)
            # Simulate improving accuracy over time
            accuracy = 0.80 + (6 - day) * 0.02
            metrics = [
                QualityMetric("accuracy", accuracy, 0.85),
                QualityMetric("reliability", 0.95, 0.90)
            ]
            report = QualityReport(
                agent_id="trend-test",
                timestamp=timestamp,
                metrics=metrics
            )
            historical_reports.append(report)
        
        # Analyze trends
        trends = framework.analyze_trends(historical_reports)
        
        assert "accuracy" in trends
        assert trends["accuracy"]["trend"] == "improving"
        assert trends["accuracy"]["change_rate"] > 0
        assert trends["reliability"]["trend"] == "stable"


class TestQualityEnforcement:
    """Test suite for quality enforcement and policies"""
    
    @pytest.mark.asyncio
    async def test_quality_gates(self):
        """Test quality gates that block low-quality outputs"""
        framework = QualityFramework(agent_id="gate-test")
        
        # Set up strict quality gate
        framework.add_rule(ValidationRule(
            name="min_confidence",
            validator=lambda d: d.get("confidence", 0) >= 0.95,
            error_message="Confidence too low for production",
            level=QualityLevel.CRITICAL
        ))
        
        # Test data that fails gate
        low_confidence_data = {
            "result": "some output",
            "confidence": 0.8  # Below threshold
        }
        
        report = await framework.validate(low_confidence_data)
        assert report.passed is False
        assert report.has_critical is True
        
        # Test data that passes gate
        high_confidence_data = {
            "result": "some output",
            "confidence": 0.98
        }
        
        report = await framework.validate(high_confidence_data)
        assert report.passed is True
        assert report.has_critical is False
    
    @pytest.mark.asyncio
    async def test_adaptive_thresholds(self):
        """Test adaptive threshold adjustment based on performance"""
        framework = QualityFramework(agent_id="adaptive-test")
        
        # Simulate adaptive threshold for response time
        baseline_response_time = 0.5  # 500ms
        
        def adaptive_threshold(historical_data):
            # Adjust threshold based on recent performance
            if historical_data:
                recent_avg = sum(historical_data[-10:]) / len(historical_data[-10:])
                return min(recent_avg * 1.2, baseline_response_time * 1.5)
            return baseline_response_time
        
        # Test threshold adaptation
        historical = [0.4, 0.45, 0.42, 0.38, 0.41]  # Getting faster
        new_threshold = adaptive_threshold(historical)
        assert new_threshold < baseline_response_time  # Threshold tightened
        
        historical = [0.6, 0.65, 0.7, 0.68, 0.72]  # Getting slower
        new_threshold = adaptive_threshold(historical)
        assert new_threshold > baseline_response_time  # Threshold relaxed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])