"""Authentication middleware and utilities for A2A agents."""

import os
import jwt
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone
from functools import wraps
import secrets
from pydantic import BaseModel, Field
from starlette.authentication import AuthenticationBackend, AuthCredentials, SimpleUser
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class AuthScheme(BaseModel):
    """Authentication scheme definition."""
    type: str = Field(..., description="Authentication type: bearer, apiKey")
    scheme: Optional[str] = Field(None, description="Scheme name for bearer auth")
    bearerFormat: Optional[str] = Field(None, description="Format of bearer token (e.g., JWT)")
    in_location: Optional[str] = Field(None, alias="in", description="Location for API key: header, query")
    name: Optional[str] = Field(None, description="Name of the header or query parameter")


class JWTConfig(BaseModel):
    """JWT configuration."""
    secret_key: str = Field(default_factory=lambda: os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32)))
    algorithm: str = "HS256"
    expiration_hours: int = 24


class APIKeyManager:
    """Manages API keys for agent authentication."""
    
    def __init__(self):
        # In production, these would be stored in a database
        self._api_keys: Dict[str, Dict[str, Any]] = {}
        self._load_from_env()
    
    def _load_from_env(self):
        """Load API keys from environment variables."""
        # Example: AGENT_API_KEYS=key1:agent1:read,write;key2:agent2:read
        keys_config = os.getenv("AGENT_API_KEYS", "")
        if keys_config:
            for key_info in keys_config.split(";"):
                if key_info:
                    parts = key_info.split(":")
                    if len(parts) >= 3:
                        key, agent_name, permissions = parts[0], parts[1], parts[2].split(",")
                        self._api_keys[key] = {
                            "agent_name": agent_name,
                            "permissions": permissions
                        }
    
    def validate_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate an API key and return associated metadata."""
        return self._api_keys.get(api_key)
    
    def generate_key(self, agent_name: str, permissions: List[str]) -> str:
        """Generate a new API key for an agent."""
        api_key = f"ak_{secrets.token_urlsafe(32)}"
        self._api_keys[api_key] = {
            "agent_name": agent_name,
            "permissions": permissions,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        return api_key


class JWTManager:
    """Manages JWT tokens for agent authentication."""
    
    def __init__(self, config: JWTConfig = None):
        self.config = config or JWTConfig()
    
    def generate_token(self, agent_name: str, permissions: List[str]) -> str:
        """Generate a JWT token for an agent."""
        payload = {
            "agent_name": agent_name,
            "permissions": permissions,
            "exp": datetime.now(timezone.utc) + timedelta(hours=self.config.expiration_hours),
            "iat": datetime.now(timezone.utc),
            "iss": "a2a-mcp-framework"
        }
        return jwt.encode(payload, self.config.secret_key, algorithm=self.config.algorithm)
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate a JWT token and return the payload."""
        try:
            payload = jwt.decode(
                token, 
                self.config.secret_key, 
                algorithms=[self.config.algorithm],
                options={"verify_exp": True}
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None


class A2AAuthBackend(AuthenticationBackend):
    """Starlette authentication backend for A2A agents."""
    
    def __init__(self, auth_schemes: List[AuthScheme]):
        self.auth_schemes = {scheme.type: scheme for scheme in auth_schemes}
        self.jwt_manager = JWTManager()
        self.api_key_manager = APIKeyManager()
    
    async def authenticate(self, request: Request):
        """Authenticate the request based on configured schemes."""
        # Try Bearer token authentication
        if "bearer" in self.auth_schemes:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]
                payload = self.jwt_manager.validate_token(token)
                if payload:
                    return AuthCredentials(["authenticated"] + payload.get("permissions", [])), SimpleUser(payload["agent_name"])
        
        # Try API key authentication
        if "apiKey" in self.auth_schemes:
            scheme = self.auth_schemes["apiKey"]
            api_key = None
            
            if scheme.in_location == "header":
                api_key = request.headers.get(scheme.name, "")
            elif scheme.in_location == "query":
                api_key = request.query_params.get(scheme.name, "")
            
            if api_key:
                key_info = self.api_key_manager.validate_key(api_key)
                if key_info:
                    return AuthCredentials(["authenticated"] + key_info.get("permissions", [])), SimpleUser(key_info["agent_name"])
        
        return None


def create_auth_middleware(auth_schemes: List[AuthScheme]) -> AuthenticationMiddleware:
    """Create authentication middleware for Starlette apps."""
    backend = A2AAuthBackend(auth_schemes)
    return AuthenticationMiddleware(backend=backend)


def require_auth(permissions: List[str] = None):
    """Decorator to require authentication and specific permissions."""
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            if not hasattr(request, "user") or not request.user.is_authenticated:
                return JSONResponse(
                    {"error": "Authentication required"},
                    status_code=401,
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            if permissions:
                user_permissions = request.auth.scopes if hasattr(request, "auth") else []
                if not all(perm in user_permissions for perm in permissions):
                    return JSONResponse(
                        {"error": "Insufficient permissions"},
                        status_code=403
                    )
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


def generate_default_keys():
    """Generate default API keys for testing (remove in production)."""
    manager = APIKeyManager()
    
    # Generate keys for each agent
    agents = [
        ("orchestrator", ["read", "write", "execute"]),
        ("planner", ["read", "execute"]),
        ("air_ticketing", ["read", "execute"]),
        ("hotel_booking", ["read", "execute"]),
        ("car_rental", ["read", "execute"])
    ]
    
    print("\n=== Generated API Keys for Testing ===")
    for agent_name, permissions in agents:
        key = manager.generate_key(agent_name, permissions)
        print(f"{agent_name}: {key}")
    print("=====================================\n")
    
    # Also generate a JWT token for testing
    jwt_manager = JWTManager()
    test_token = jwt_manager.generate_token("test_client", ["read", "write", "execute"])
    print(f"Test JWT Token: {test_token}\n")


if __name__ == "__main__":
    # Generate test keys when module is run directly
    generate_default_keys()