# ABOUTME: Configurable quality threshold framework for multi-agent validation
# ABOUTME: Supports domain-specific quality metrics with unified validation interface

import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class QualityDomain(Enum):
    """Quality domains for different agent types."""
    BUSINESS = "business"           # Solopreneur/business-focused agents
    ACADEMIC = "academic"           # Research/academic-focused agents
    SERVICE = "service"             # Service/tool-focused agents
    GENERIC = "generic"             # General-purpose agents


@dataclass
class QualityThreshold:
    """Individual quality threshold configuration."""
    name: str
    min_value: float
    max_value: float = 1.0
    weight: float = 1.0
    description: str = ""
    required: bool = True


@dataclass
class QualityResult:
    """Result of quality validation."""
    passed: bool
    score: float
    threshold_results: Dict[str, bool]
    issues: List[str]
    metadata: Dict[str, Any]


class QualityThresholdFramework:
    """
    Configurable quality threshold framework supporting multiple domains.
    
    Provides unified quality validation interface with domain-specific
    threshold configurations for different agent types.
    """

    # Default threshold configurations by domain
    DEFAULT_THRESHOLDS = {
        QualityDomain.BUSINESS: {
            "confidence_score": QualityThreshold(
                name="confidence_score",
                min_value=0.75,
                description="Business decision confidence threshold"
            ),
            "technical_feasibility": QualityThreshold(
                name="technical_feasibility",
                min_value=0.8,
                description="Technical implementation feasibility"
            ),
            "personal_sustainability": QualityThreshold(
                name="personal_sustainability",
                min_value=0.7,
                description="Personal sustainability and energy management"
            ),
            "risk_tolerance": QualityThreshold(
                name="risk_tolerance",
                min_value=0.6,
                max_value=0.8,
                description="Acceptable risk level for business decisions"
            )
        },
        
        QualityDomain.ACADEMIC: {
            "research_confidence": QualityThreshold(
                name="research_confidence",
                min_value=0.7,
                description="Research findings confidence threshold"
            ),
            "domain_coverage": QualityThreshold(
                name="domain_coverage",
                min_value=2.0,
                max_value=10.0,
                description="Minimum number of domains contributing insights"
            ),
            "evidence_quality": QualityThreshold(
                name="evidence_quality",
                min_value=0.75,
                description="Quality of supporting evidence"
            ),
            "bias_detection": QualityThreshold(
                name="bias_detection",
                min_value=0.6,
                description="Bias detection and mitigation threshold"
            ),
            "methodological_rigor": QualityThreshold(
                name="methodological_rigor",
                min_value=0.7,
                description="Research methodology quality"
            )
        },
        
        QualityDomain.SERVICE: {
            "service_reliability": QualityThreshold(
                name="service_reliability",
                min_value=0.95,
                description="Service reliability and availability"
            ),
            "response_accuracy": QualityThreshold(
                name="response_accuracy",
                min_value=0.8,
                description="Accuracy of service responses"
            ),
            "user_satisfaction": QualityThreshold(
                name="user_satisfaction",
                min_value=0.75,
                description="User satisfaction with service quality"
            )
        },
        
        QualityDomain.GENERIC: {
            "overall_quality": QualityThreshold(
                name="overall_quality",
                min_value=0.7,
                description="General quality threshold"
            ),
            "completeness": QualityThreshold(
                name="completeness",
                min_value=0.8,
                description="Response completeness"
            )
        }
    }

    def __init__(
        self,
        config: Dict[str, Any],
        domain: QualityDomain = QualityDomain.GENERIC
    ):
        """
        Initialize quality framework with configuration.
        
        Args:
            config: Quality configuration dictionary
            domain: Quality domain for default thresholds
        """
        self.domain = domain
        self.enabled = config.get("enabled", True)
        self.strict_mode = config.get("strict_mode", False)
        
        # Load thresholds
        self.thresholds = self._load_thresholds(config)
        
        # Validation settings
        self.fail_fast = config.get("fail_fast", False)
        self.log_results = config.get("log_results", True)
        
        logger.info(f"Quality framework initialized for domain {domain.value} with {len(self.thresholds)} thresholds")

    def _load_thresholds(self, config: Dict[str, Any]) -> Dict[str, QualityThreshold]:
        """Load quality thresholds from configuration."""
        thresholds = {}
        
        # Start with domain defaults
        if self.domain in self.DEFAULT_THRESHOLDS:
            thresholds.update(self.DEFAULT_THRESHOLDS[self.domain])
        
        # Override with custom thresholds from config
        custom_thresholds = config.get("thresholds", {})
        for name, threshold_config in custom_thresholds.items():
            if isinstance(threshold_config, dict):
                thresholds[name] = QualityThreshold(
                    name=name,
                    min_value=threshold_config.get("min_value", 0.0),
                    max_value=threshold_config.get("max_value", 1.0),
                    weight=threshold_config.get("weight", 1.0),
                    description=threshold_config.get("description", ""),
                    required=threshold_config.get("required", True)
                )
            elif isinstance(threshold_config, (int, float)):
                # Simple threshold value
                thresholds[name] = QualityThreshold(
                    name=name,
                    min_value=float(threshold_config),
                    description=f"Custom threshold for {name}"
                )
        
        return thresholds

    async def validate_response(
        self,
        response_content: Any,
        original_query: str = ""
    ) -> Dict[str, Any]:
        """
        Validate response against quality thresholds.
        
        Args:
            response_content: Response content to validate
            original_query: Original query for context
            
        Returns:
            Quality validation result
        """
        if not self.enabled:
            return {
                "quality_approved": True,
                "quality_score": 1.0,
                "threshold_results": {},
                "quality_issues": [],
                "metadata": {"framework_enabled": False}
            }

        try:
            # Extract quality metrics from response
            quality_metrics = await self._extract_quality_metrics(response_content)
            
            # Validate against thresholds
            validation_results = {}
            quality_issues = []
            weighted_scores = []
            
            for threshold_name, threshold in self.thresholds.items():
                if threshold_name in quality_metrics:
                    metric_value = quality_metrics[threshold_name]
                    passed = self._check_threshold(metric_value, threshold)
                    validation_results[threshold_name] = passed
                    
                    if not passed:
                        quality_issues.append(f"{threshold_name}_not_met")
                        if self.fail_fast:
                            break
                    
                    # Calculate weighted score contribution
                    if isinstance(metric_value, (int, float)):
                        normalized_score = min(metric_value / threshold.max_value, 1.0)
                        weighted_scores.append(normalized_score * threshold.weight)
                elif threshold.required:
                    validation_results[threshold_name] = False
                    quality_issues.append(f"{threshold_name}_missing")
                    if self.fail_fast:
                        break

            # Calculate overall quality score
            overall_score = (
                sum(weighted_scores) / sum(t.weight for t in self.thresholds.values())
                if weighted_scores and self.thresholds else 1.0
            )
            
            # Determine if quality approved
            quality_approved = len(quality_issues) == 0
            
            result = {
                "quality_approved": quality_approved,
                "quality_score": round(overall_score, 3),
                "threshold_results": validation_results,
                "quality_issues": quality_issues,
                "metadata": {
                    "domain": self.domain.value,
                    "thresholds_checked": len(validation_results),
                    "metrics_extracted": len(quality_metrics),
                    "validation_timestamp": datetime.now().isoformat()
                }
            }
            
            if self.log_results:
                if quality_approved:
                    logger.info(f"Quality validation passed (score: {overall_score:.3f})")
                else:
                    logger.warning(f"Quality validation failed: {quality_issues}")
            
            return result
            
        except Exception as e:
            logger.error(f"Quality validation error: {e}")
            return {
                "quality_approved": not self.strict_mode,  # Fail open unless strict mode
                "quality_score": 0.0,
                "threshold_results": {},
                "quality_issues": [f"validation_error: {str(e)}"],
                "metadata": {"validation_error": str(e)}
            }

    def _check_threshold(self, value: Union[int, float, str], threshold: QualityThreshold) -> bool:
        """Check if value meets threshold requirement."""
        try:
            if isinstance(value, str):
                # Handle string-based thresholds (e.g., "high", "medium", "low")
                return self._validate_categorical_threshold(value, threshold)
            
            if isinstance(value, (int, float)):
                return threshold.min_value <= value <= threshold.max_value
            
            # For other types, assume they pass (could be expanded)
            return True
            
        except Exception as e:
            logger.error(f"Threshold check error for {threshold.name}: {e}")
            return False

    def _validate_categorical_threshold(self, value: str, threshold: QualityThreshold) -> bool:
        """Validate categorical (string) thresholds."""
        value_lower = value.lower()
        
        # Common categorical mappings
        quality_mappings = {
            "high": 0.8,
            "medium": 0.5,
            "low": 0.2,
            "excellent": 0.9,
            "good": 0.7,
            "fair": 0.5,
            "poor": 0.3
        }
        
        if value_lower in quality_mappings:
            numeric_value = quality_mappings[value_lower]
            return threshold.min_value <= numeric_value <= threshold.max_value
        
        # If not in mapping, assume it passes (lenient for unknown categories)
        return True

    async def _extract_quality_metrics(self, response_content: Any) -> Dict[str, Union[int, float, str]]:
        """
        Extract quality metrics from response content.
        
        Args:
            response_content: Response content to analyze
            
        Returns:
            Dictionary of extracted quality metrics
        """
        metrics = {}
        
        if isinstance(response_content, dict):
            # Direct metric extraction
            for key, value in response_content.items():
                if key in ["confidence_score", "research_confidence"]:
                    metrics["confidence_score"] = self._safe_numeric_extract(value)
                elif key in ["technical_assessment", "feasibility_score"]:
                    if isinstance(value, dict) and "feasibility_score" in value:
                        metrics["technical_feasibility"] = self._safe_numeric_extract(value["feasibility_score"]) / 100
                elif key in ["personal_optimization", "sustainability_score"]:
                    if isinstance(value, dict) and "sustainability_score" in value:
                        metrics["personal_sustainability"] = self._safe_numeric_extract(value["sustainability_score"]) / 100
                elif key in ["quality_assessment", "evidence_strength"]:
                    if isinstance(value, dict):
                        if "evidence_strength" in value:
                            metrics["evidence_quality"] = self._safe_numeric_extract(value["evidence_strength"]) / 100
                        if "methodological_rigor" in value:
                            metrics["methodological_rigor"] = self._safe_numeric_extract(value["methodological_rigor"]) / 100
                elif key == "domain_coverage":
                    if isinstance(value, (int, str)):
                        try:
                            metrics["domain_coverage"] = float(value)
                        except (ValueError, TypeError):
                            pass
            
            # Look for nested quality indicators
            if "quality_assessment" in response_content:
                qa = response_content["quality_assessment"]
                if isinstance(qa, dict):
                    for qa_key, qa_value in qa.items():
                        if qa_key not in metrics:
                            metrics[qa_key] = self._safe_numeric_extract(qa_value)
        
        return metrics

    def _safe_numeric_extract(self, value: Any) -> float:
        """Safely extract numeric value from various input types."""
        try:
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                # Try to parse as float
                return float(value)
            else:
                return 0.0
        except (ValueError, TypeError):
            return 0.0

    def is_enabled(self) -> bool:
        """Check if quality framework is enabled."""
        return self.enabled

    def get_threshold_config(self) -> Dict[str, Any]:
        """Get current threshold configuration."""
        return {
            "domain": self.domain.value,
            "enabled": self.enabled,
            "strict_mode": self.strict_mode,
            "thresholds": {
                name: {
                    "min_value": threshold.min_value,
                    "max_value": threshold.max_value,
                    "weight": threshold.weight,
                    "description": threshold.description,
                    "required": threshold.required
                }
                for name, threshold in self.thresholds.items()
            }
        }

    def update_threshold(
        self,
        threshold_name: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        weight: Optional[float] = None
    ):
        """Update an existing threshold configuration."""
        if threshold_name in self.thresholds:
            threshold = self.thresholds[threshold_name]
            if min_value is not None:
                threshold.min_value = min_value
            if max_value is not None:
                threshold.max_value = max_value
            if weight is not None:
                threshold.weight = weight
            
            logger.info(f"Updated threshold {threshold_name}")
        else:
            logger.warning(f"Threshold {threshold_name} not found")


def create_quality_framework(
    agent_type: str,
    custom_config: Optional[Dict[str, Any]] = None
) -> QualityThresholdFramework:
    """
    Factory function to create quality framework for specific agent types.
    
    Args:
        agent_type: Type of agent (business, academic, service, generic)
        custom_config: Optional custom configuration
        
    Returns:
        Configured quality framework
    """
    # Map agent types to domains
    domain_mapping = {
        "business": QualityDomain.BUSINESS,
        "solopreneur": QualityDomain.BUSINESS,
        "academic": QualityDomain.ACADEMIC,
        "research": QualityDomain.ACADEMIC,
        "nexus": QualityDomain.ACADEMIC,
        "service": QualityDomain.SERVICE,
        "travel": QualityDomain.SERVICE,
        "generic": QualityDomain.GENERIC
    }
    
    domain = domain_mapping.get(agent_type.lower(), QualityDomain.GENERIC)
    config = custom_config or {}
    
    return QualityThresholdFramework(config, domain)