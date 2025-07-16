# ABOUTME: Centralized security manager orchestrating all security features
# ABOUTME: Coordinates auth, mTLS, rate limiting, and security monitoring for the system

import logging
import os
import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum

from a2a_mcp.common.auth import JWTManager, APIKeyManager, AuthScheme
from .mtls_handler import MTLSHandler
from .rate_limiter import RateLimiter
from .security_monitor import SecurityMonitor, SecurityEvent, ThreatLevel
from .auth_service import AuthService, AuthToken, AuthResult

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security levels for different operational modes."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    HIGH_SECURITY = "high_security"


@dataclass
class SecurityConfig:
    """Security configuration for the system."""
    security_level: SecurityLevel = SecurityLevel.PRODUCTION
    
    # Authentication settings
    enable_jwt: bool = True
    enable_api_keys: bool = True
    enable_mtls: bool = True
    jwt_expiration_hours: int = 24
    api_key_rotation_days: int = 90
    
    # Rate limiting settings
    enable_rate_limiting: bool = True
    global_rate_limit: int = 1000  # requests per minute
    per_agent_rate_limit: int = 100  # requests per minute per agent
    burst_allowance: float = 1.5  # 50% burst allowance
    
    # Security monitoring settings
    enable_monitoring: bool = True
    alert_threshold: ThreatLevel = ThreatLevel.MEDIUM
    audit_retention_days: int = 90
    
    # mTLS settings
    mtls_cert_path: Optional[str] = None
    mtls_key_path: Optional[str] = None
    mtls_ca_path: Optional[str] = None
    mtls_verify_mode: str = "CERT_REQUIRED"
    
    # Additional security features
    enable_ip_whitelist: bool = False
    ip_whitelist: List[str] = field(default_factory=list)
    enable_request_signing: bool = False
    enable_encryption_at_rest: bool = True
    
    @classmethod
    def from_environment(cls) -> "SecurityConfig":
        """Create config from environment variables."""
        level = os.getenv("SECURITY_LEVEL", "production").lower()
        return cls(
            security_level=SecurityLevel(level),
            enable_jwt=os.getenv("ENABLE_JWT", "true").lower() == "true",
            enable_api_keys=os.getenv("ENABLE_API_KEYS", "true").lower() == "true",
            enable_mtls=os.getenv("ENABLE_MTLS", "true").lower() == "true",
            jwt_expiration_hours=int(os.getenv("JWT_EXPIRATION_HOURS", "24")),
            api_key_rotation_days=int(os.getenv("API_KEY_ROTATION_DAYS", "90")),
            enable_rate_limiting=os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true",
            global_rate_limit=int(os.getenv("GLOBAL_RATE_LIMIT", "1000")),
            per_agent_rate_limit=int(os.getenv("PER_AGENT_RATE_LIMIT", "100")),
            enable_monitoring=os.getenv("ENABLE_SECURITY_MONITORING", "true").lower() == "true",
            mtls_cert_path=os.getenv("MTLS_CERT_PATH"),
            mtls_key_path=os.getenv("MTLS_KEY_PATH"),
            mtls_ca_path=os.getenv("MTLS_CA_PATH"),
        )


class SecurityManager:
    """
    Centralized security manager for the video generation system.
    
    Provides comprehensive security features including:
    - Multi-factor authentication (JWT, API keys, mTLS)
    - Rate limiting and DDoS protection
    - Security monitoring and threat detection
    - Audit logging and compliance reporting
    - IP whitelisting and request validation
    """
    
    def __init__(self, config: Optional[SecurityConfig] = None):
        """Initialize security manager with configuration."""
        self.config = config or SecurityConfig.from_environment()
        
        # Initialize security components
        self.auth_service = AuthService(
            enable_jwt=self.config.enable_jwt,
            enable_api_keys=self.config.enable_api_keys,
            jwt_expiration_hours=self.config.jwt_expiration_hours
        )
        
        self.mtls_handler = MTLSHandler(
            cert_path=self.config.mtls_cert_path,
            key_path=self.config.mtls_key_path,
            ca_path=self.config.mtls_ca_path,
            verify_mode=self.config.mtls_verify_mode
        ) if self.config.enable_mtls else None
        
        self.rate_limiter = RateLimiter(
            global_limit=self.config.global_rate_limit,
            per_identity_limit=self.config.per_agent_rate_limit,
            burst_allowance=self.config.burst_allowance
        ) if self.config.enable_rate_limiting else None
        
        self.security_monitor = SecurityMonitor(
            alert_threshold=self.config.alert_threshold,
            audit_retention_days=self.config.audit_retention_days
        ) if self.config.enable_monitoring else None
        
        # Security middleware chain
        self._middleware_chain: List[Callable] = []
        self._build_middleware_chain()
        
        logger.info(f"Security manager initialized with level: {self.config.security_level.value}")
    
    def _build_middleware_chain(self):
        """Build the security middleware chain based on configuration."""
        # Order matters: IP check -> Rate limit -> mTLS -> Auth -> Monitoring
        
        if self.config.enable_ip_whitelist:
            self._middleware_chain.append(self._check_ip_whitelist)
        
        if self.config.enable_rate_limiting:
            self._middleware_chain.append(self._check_rate_limit)
        
        if self.config.enable_mtls:
            self._middleware_chain.append(self._verify_mtls)
        
        # Authentication is always required
        self._middleware_chain.append(self._authenticate_request)
        
        if self.config.enable_monitoring:
            self._middleware_chain.append(self._monitor_request)
    
    async def validate_request(
        self,
        request_data: Dict[str, Any],
        headers: Dict[str, str],
        client_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate an incoming request through the security chain.
        
        Args:
            request_data: The request payload
            headers: HTTP headers
            client_info: Client information (IP, cert info, etc.)
            
        Returns:
            Security context with validated identity and permissions
            
        Raises:
            SecurityException: If any security check fails
        """
        security_context = {
            "request_id": headers.get("X-Request-ID", self._generate_request_id()),
            "timestamp": datetime.now(timezone.utc),
            "client_info": client_info,
            "headers": headers,
            "checks_passed": []
        }
        
        # Run through middleware chain
        for middleware in self._middleware_chain:
            try:
                security_context = await middleware(
                    request_data, headers, client_info, security_context
                )
                security_context["checks_passed"].append(middleware.__name__)
            except Exception as e:
                logger.error(f"Security check failed in {middleware.__name__}: {e}")
                if self.security_monitor:
                    await self.security_monitor.log_security_event(
                        SecurityEvent(
                            event_type="security_check_failed",
                            threat_level=ThreatLevel.HIGH,
                            source_ip=client_info.get("ip", "unknown"),
                            description=f"Failed {middleware.__name__}: {str(e)}",
                            metadata={
                                "middleware": middleware.__name__,
                                "request_id": security_context["request_id"]
                            }
                        )
                    )
                raise SecurityException(f"Security validation failed: {str(e)}")
        
        logger.info(f"Request {security_context['request_id']} passed all security checks")
        return security_context
    
    async def _check_ip_whitelist(
        self, request_data: Dict, headers: Dict, client_info: Dict, context: Dict
    ) -> Dict:
        """Check if client IP is in whitelist."""
        client_ip = client_info.get("ip", "")
        
        if client_ip not in self.config.ip_whitelist:
            raise SecurityException(f"IP {client_ip} not in whitelist")
        
        context["ip_whitelisted"] = True
        return context
    
    async def _check_rate_limit(
        self, request_data: Dict, headers: Dict, client_info: Dict, context: Dict
    ) -> Dict:
        """Check rate limits."""
        # Use authenticated identity if available, otherwise use IP
        identity = context.get("authenticated_identity", client_info.get("ip", "unknown"))
        
        allowed = await self.rate_limiter.check_rate_limit(identity)
        
        if not allowed:
            raise SecurityException(f"Rate limit exceeded for {identity}")
        
        # Add rate limit headers
        limits = await self.rate_limiter.get_rate_limit_info(identity)
        context["rate_limit_info"] = limits
        
        return context
    
    async def _verify_mtls(
        self, request_data: Dict, headers: Dict, client_info: Dict, context: Dict
    ) -> Dict:
        """Verify mTLS certificate."""
        cert_data = client_info.get("client_cert")
        
        if not cert_data:
            raise SecurityException("No client certificate provided")
        
        # Verify certificate
        cert_info = await self.mtls_handler.verify_certificate(cert_data)
        
        if not cert_info["valid"]:
            raise SecurityException(f"Invalid certificate: {cert_info.get('error', 'Unknown error')}")
        
        context["mtls_verified"] = True
        context["cert_subject"] = cert_info.get("subject")
        context["cert_fingerprint"] = cert_info.get("fingerprint")
        
        return context
    
    async def _authenticate_request(
        self, request_data: Dict, headers: Dict, client_info: Dict, context: Dict
    ) -> Dict:
        """Authenticate the request."""
        # Try different auth methods in order of preference
        auth_result = None
        
        # 1. Try JWT token
        if self.config.enable_jwt:
            auth_header = headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]
                auth_result = await self.auth_service.validate_jwt(token)
        
        # 2. Try API key
        if not auth_result and self.config.enable_api_keys:
            api_key = headers.get("X-API-Key") or request_data.get("api_key")
            if api_key:
                auth_result = await self.auth_service.validate_api_key(api_key)
        
        # 3. Try mTLS certificate authentication
        if not auth_result and context.get("mtls_verified"):
            cert_subject = context.get("cert_subject", "")
            auth_result = await self.auth_service.validate_certificate(cert_subject)
        
        if not auth_result or not auth_result.authenticated:
            raise SecurityException("Authentication failed")
        
        context["authenticated"] = True
        context["authenticated_identity"] = auth_result.identity
        context["permissions"] = auth_result.permissions
        context["auth_method"] = auth_result.auth_method
        
        return context
    
    async def _monitor_request(
        self, request_data: Dict, headers: Dict, client_info: Dict, context: Dict
    ) -> Dict:
        """Monitor request for security threats."""
        # Log the successful request
        await self.security_monitor.log_security_event(
            SecurityEvent(
                event_type="authenticated_request",
                threat_level=ThreatLevel.INFO,
                source_ip=client_info.get("ip", "unknown"),
                authenticated_identity=context.get("authenticated_identity"),
                description="Successful authenticated request",
                metadata={
                    "request_id": context["request_id"],
                    "auth_method": context.get("auth_method"),
                    "checks_passed": context.get("checks_passed", [])
                }
            )
        )
        
        # Check for suspicious patterns
        threat_indicators = await self.security_monitor.analyze_request_patterns(
            client_info.get("ip"),
            context.get("authenticated_identity"),
            request_data
        )
        
        if threat_indicators:
            context["threat_indicators"] = threat_indicators
            
            # Determine threat level
            max_threat = max(
                indicator.get("threat_level", ThreatLevel.LOW)
                for indicator in threat_indicators
            )
            
            if max_threat.value >= self.config.alert_threshold.value:
                await self._handle_security_alert(context, threat_indicators)
        
        return context
    
    async def _handle_security_alert(
        self, context: Dict, threat_indicators: List[Dict]
    ):
        """Handle security alerts based on threat level."""
        logger.warning(f"Security alert triggered for request {context['request_id']}")
        
        # Log high-priority event
        await self.security_monitor.log_security_event(
            SecurityEvent(
                event_type="security_alert",
                threat_level=ThreatLevel.HIGH,
                source_ip=context.get("client_info", {}).get("ip", "unknown"),
                authenticated_identity=context.get("authenticated_identity"),
                description="Multiple threat indicators detected",
                metadata={
                    "request_id": context["request_id"],
                    "threat_indicators": threat_indicators
                }
            )
        )
        
        # In high security mode, we might want to block the request
        if self.config.security_level == SecurityLevel.HIGH_SECURITY:
            raise SecurityException("Request blocked due to security concerns")
    
    async def rotate_credentials(self):
        """Rotate security credentials based on policy."""
        logger.info("Starting credential rotation")
        
        # Rotate API keys older than configured days
        rotated_keys = await self.auth_service.rotate_old_api_keys(
            self.config.api_key_rotation_days
        )
        
        if rotated_keys:
            logger.info(f"Rotated {len(rotated_keys)} API keys")
            
            # Log rotation event
            if self.security_monitor:
                await self.security_monitor.log_security_event(
                    SecurityEvent(
                        event_type="credential_rotation",
                        threat_level=ThreatLevel.INFO,
                        description=f"Rotated {len(rotated_keys)} API keys",
                        metadata={"rotated_keys": rotated_keys}
                    )
                )
    
    async def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report."""
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "security_level": self.config.security_level.value,
            "configuration": {
                "jwt_enabled": self.config.enable_jwt,
                "api_keys_enabled": self.config.enable_api_keys,
                "mtls_enabled": self.config.enable_mtls,
                "rate_limiting_enabled": self.config.enable_rate_limiting,
                "monitoring_enabled": self.config.enable_monitoring
            }
        }
        
        # Get statistics from components
        if self.auth_service:
            report["authentication"] = await self.auth_service.get_statistics()
        
        if self.rate_limiter:
            report["rate_limiting"] = await self.rate_limiter.get_statistics()
        
        if self.security_monitor:
            report["security_events"] = await self.security_monitor.get_event_summary()
            report["threat_analysis"] = await self.security_monitor.get_threat_analysis()
        
        if self.mtls_handler:
            report["mtls"] = await self.mtls_handler.get_certificate_statistics()
        
        return report
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID."""
        import uuid
        return str(uuid.uuid4())
    
    async def shutdown(self):
        """Gracefully shutdown security components."""
        logger.info("Shutting down security manager")
        
        # Save any pending audit logs
        if self.security_monitor:
            await self.security_monitor.flush_audit_logs()
        
        # Clean up rate limiter
        if self.rate_limiter:
            await self.rate_limiter.cleanup()
        
        logger.info("Security manager shutdown complete")


class SecurityException(Exception):
    """Security-related exception."""
    pass