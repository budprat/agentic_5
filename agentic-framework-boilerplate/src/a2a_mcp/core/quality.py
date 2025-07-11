# ABOUTME: Quality validation framework for the A2A MCP system
# ABOUTME: Provides metrics, reporting, and validation capabilities

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional, Callable
import statistics

from a2a_mcp.common.utils import logger, utc_now


class QualityLevel(Enum):
    """Severity levels for quality issues"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class MetricType(Enum):
    """Types of quality metrics"""
    PERCENTAGE = "PERCENTAGE"
    COUNT = "COUNT"
    SCORE = "SCORE"
    TIME = "TIME"
    BOOLEAN = "BOOLEAN"


@dataclass
class QualityMetric:
    """Individual quality metric"""
    name: str
    value: float
    threshold: float
    metric_type: MetricType = MetricType.PERCENTAGE
    passed: bool = field(init=False)
    inverse: bool = False  # If True, lower values are better
    
    def __post_init__(self):
        """Calculate if metric passed after initialization"""
        if self.inverse:
            self.passed = self.value <= self.threshold
        else:
            self.passed = self.value >= self.threshold


@dataclass
class QualityIssue:
    """Represents a quality issue found during validation"""
    level: QualityLevel
    metric: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=utc_now)


@dataclass
class QualityReport:
    """Complete quality assessment report"""
    agent_id: str
    timestamp: datetime
    metrics: List[QualityMetric]
    issues: List[QualityIssue] = field(default_factory=list)
    passed: bool = field(init=False)
    overall_score: float = field(init=False)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Calculate overall status after initialization"""
        # Report passes if all metrics pass and no ERROR/CRITICAL issues
        metric_pass = all(m.passed for m in self.metrics)
        no_critical_issues = not any(
            i.level in [QualityLevel.ERROR, QualityLevel.CRITICAL]
            for i in self.issues
        )
        self.passed = metric_pass and no_critical_issues
        
        # Calculate overall score
        if self.metrics:
            # Normalize metrics to 0-1 range
            scores = []
            for metric in self.metrics:
                if metric.metric_type == MetricType.PERCENTAGE:
                    scores.append(metric.value)
                elif metric.metric_type == MetricType.BOOLEAN:
                    scores.append(1.0 if metric.value else 0.0)
                else:
                    # For other types, use pass/fail as 1.0/0.0
                    scores.append(1.0 if metric.passed else 0.0)
            
            self.overall_score = statistics.mean(scores) if scores else 0.0
        else:
            self.overall_score = 1.0 if self.passed else 0.0
    
    @property
    def has_errors(self) -> bool:
        """Check if report has any errors"""
        return any(i.level == QualityLevel.ERROR for i in self.issues)
    
    @property
    def has_warnings(self) -> bool:
        """Check if report has any warnings"""
        return any(i.level == QualityLevel.WARNING for i in self.issues)
    
    @property
    def has_critical(self) -> bool:
        """Check if report has any critical issues"""
        return any(i.level == QualityLevel.CRITICAL for i in self.issues)
    
    @property
    def error_count(self) -> int:
        """Count of error-level issues"""
        return sum(1 for i in self.issues if i.level == QualityLevel.ERROR)
    
    @property
    def warning_count(self) -> int:
        """Count of warning-level issues"""
        return sum(1 for i in self.issues if i.level == QualityLevel.WARNING)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary"""
        return {
            "agent_id": self.agent_id,
            "timestamp": self.timestamp.isoformat(),
            "passed": self.passed,
            "overall_score": self.overall_score,
            "metrics": [
                {
                    "name": m.name,
                    "value": m.value,
                    "threshold": m.threshold,
                    "passed": m.passed,
                    "type": m.metric_type.value
                }
                for m in self.metrics
            ],
            "issues": [
                {
                    "level": i.level.value,
                    "metric": i.metric,
                    "message": i.message,
                    "details": i.details,
                    "timestamp": i.timestamp.isoformat()
                }
                for i in self.issues
            ],
            "metadata": self.metadata,
            "summary": {
                "error_count": self.error_count,
                "warning_count": self.warning_count,
                "has_critical": self.has_critical
            }
        }


@dataclass
class ValidationRule:
    """Rule for validating data"""
    name: str
    validator: Callable[[Any, Optional[Dict[str, Any]]], bool]
    error_message: str
    level: QualityLevel = QualityLevel.ERROR
    
    def validate(self, data: Any, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Validate data against this rule
        
        Args:
            data: Data to validate
            context: Optional context for validation
            
        Returns:
            True if validation passes
        """
        try:
            return self.validator(data, context) if context else self.validator(data)
        except Exception as e:
            logger.error(f"Validation rule {self.name} failed: {e}")
            return False


class QualityFramework:
    """
    Framework for quality validation and assessment
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.rules: List[ValidationRule] = []
        self.metrics_config: Dict[str, Dict[str, Any]] = self._default_metrics()
        self.metric_calculators: Dict[str, Callable] = {}
    
    def _default_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get default metric configurations"""
        return {
            "completeness": {
                "threshold": 0.95,
                "type": MetricType.PERCENTAGE
            },
            "accuracy": {
                "threshold": 0.90,
                "type": MetricType.PERCENTAGE
            },
            "response_time": {
                "threshold": 1.0,
                "type": MetricType.TIME,
                "inverse": True
            }
        }
    
    def add_rule(self, rule: ValidationRule) -> None:
        """Add a validation rule"""
        self.rules.append(rule)
        logger.debug(f"Added validation rule: {rule.name}")
    
    def add_metric_calculator(
        self,
        name: str,
        calculator: Callable[[Any], float],
        threshold: float,
        metric_type: MetricType = MetricType.SCORE
    ) -> None:
        """
        Add a custom metric calculator
        
        Args:
            name: Name of the metric
            calculator: Function to calculate metric value
            threshold: Threshold for the metric
            metric_type: Type of metric
        """
        self.metric_calculators[name] = calculator
        self.metrics_config[name] = {
            "threshold": threshold,
            "type": metric_type
        }
    
    async def validate(self, data: Any, context: Optional[Dict[str, Any]] = None) -> QualityReport:
        """
        Validate data and generate quality report
        
        Args:
            data: Data to validate
            context: Optional validation context
            
        Returns:
            Quality report
        """
        metrics = []
        issues = []
        
        # Run validation rules
        for rule in self.rules:
            if not rule.validate(data, context):
                issues.append(QualityIssue(
                    level=rule.level,
                    metric=rule.name,
                    message=rule.error_message,
                    details={"data_type": type(data).__name__}
                ))
        
        # Calculate metrics
        for metric_name, config in self.metrics_config.items():
            if metric_name in self.metric_calculators:
                try:
                    value = self.metric_calculators[metric_name](data)
                    metrics.append(QualityMetric(
                        name=metric_name,
                        value=value,
                        threshold=config["threshold"],
                        metric_type=config["type"],
                        inverse=config.get("inverse", False)
                    ))
                except Exception as e:
                    logger.error(f"Failed to calculate metric {metric_name}: {e}")
                    issues.append(QualityIssue(
                        level=QualityLevel.WARNING,
                        metric=metric_name,
                        message=f"Failed to calculate metric: {str(e)}"
                    ))
        
        # Create and return report
        report = QualityReport(
            agent_id=self.agent_id,
            timestamp=utc_now(),
            metrics=metrics,
            issues=issues,
            metadata={
                "data_size": len(str(data)) if data else 0,
                "rule_count": len(self.rules),
                "metric_count": len(metrics)
            }
        )
        
        logger.info(
            f"Quality validation completed",
            agent_id=self.agent_id,
            passed=report.passed,
            score=report.overall_score
        )
        
        return report
    
    async def validate_message(self, message: Any) -> QualityReport:
        """
        Validate an A2A message
        
        Args:
            message: Message to validate
            
        Returns:
            Quality report
        """
        # Convert message to dict for validation
        if hasattr(message, 'to_dict'):
            data = message.to_dict()
        else:
            data = message
        
        return await self.validate(data)
    
    @staticmethod
    def aggregate_reports(reports: List[QualityReport]) -> Dict[str, Dict[str, float]]:
        """
        Aggregate multiple quality reports
        
        Args:
            reports: List of quality reports
            
        Returns:
            Aggregated metrics
        """
        if not reports:
            return {}
        
        # Group metrics by name
        metric_groups: Dict[str, List[float]] = {}
        
        for report in reports:
            for metric in report.metrics:
                if metric.name not in metric_groups:
                    metric_groups[metric.name] = []
                metric_groups[metric.name].append(metric.value)
        
        # Calculate aggregates
        aggregated = {}
        for metric_name, values in metric_groups.items():
            aggregated[metric_name] = {
                "min": min(values),
                "max": max(values),
                "avg": statistics.mean(values),
                "median": statistics.median(values),
                "count": len(values)
            }
        
        return aggregated
    
    def analyze_trends(self, reports: List[QualityReport]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze quality trends over time
        
        Args:
            reports: List of reports ordered by time
            
        Returns:
            Trend analysis
        """
        if len(reports) < 2:
            return {}
        
        trends = {}
        
        # Group metrics by name across reports
        metric_series: Dict[str, List[tuple[datetime, float]]] = {}
        
        for report in reports:
            for metric in report.metrics:
                if metric.name not in metric_series:
                    metric_series[metric.name] = []
                metric_series[metric.name].append((report.timestamp, metric.value))
        
        # Analyze each metric series
        for metric_name, series in metric_series.items():
            if len(series) < 2:
                continue
            
            # Sort by timestamp
            series.sort(key=lambda x: x[0])
            
            # Calculate trend
            values = [v for _, v in series]
            first_half_avg = statistics.mean(values[:len(values)//2])
            second_half_avg = statistics.mean(values[len(values)//2:])
            
            change_rate = (second_half_avg - first_half_avg) / first_half_avg if first_half_avg != 0 else 0
            
            if abs(change_rate) < 0.05:
                trend = "stable"
            elif change_rate > 0:
                trend = "improving"
            else:
                trend = "declining"
            
            trends[metric_name] = {
                "trend": trend,
                "change_rate": change_rate,
                "latest_value": values[-1],
                "avg_value": statistics.mean(values)
            }
        
        return trends