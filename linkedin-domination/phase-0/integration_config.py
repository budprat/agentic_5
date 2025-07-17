"""
ABOUTME: Integration configuration system for LinkedIn domination platform
ABOUTME: Manages API configurations, rate limits, and integration layer setup
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import yaml
from pathlib import Path
import asyncio
import aiohttp
import time
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationType(Enum):
    LINKEDIN_API = "linkedin_api"
    OPENAI_API = "openai_api"
    ELEVENLABS_API = "elevenlabs_api"
    FAL_AI_API = "fal_ai_api"
    BRIGHTDATA_API = "brightdata_api"
    PUPPETEER_CONFIG = "puppeteer_config"
    PLAYWRIGHT_CONFIG = "playwright_config"
    N8N_CONFIG = "n8n_config"
    WEBHOOK_CONFIG = "webhook_config"

@dataclass
class APIConfiguration:
    integration_type: IntegrationType
    api_key: str
    base_url: str
    rate_limit_rpm: int  # requests per minute
    rate_limit_rph: int  # requests per hour
    timeout: int
    retry_attempts: int
    retry_delay: int
    headers: Dict[str, str]
    endpoints: Dict[str, str]
    authentication_method: str
    last_request_time: Optional[datetime] = None
    current_usage: int = 0
    
@dataclass
class ContentRules:
    brand_voice: str
    tone_guidelines: List[str]
    content_standards: List[str]
    compliance_requirements: List[str]
    psychological_triggers: List[str]
    forbidden_topics: List[str]
    character_limits: Dict[str, int]
    hashtag_rules: Dict[str, Any]

@dataclass
class AlgorithmWeights:
    early_engagement: float
    dwell_time: float
    completion_rate: float
    creator_mode: float
    consistency: float
    last_updated: datetime
    adjustment_history: List[Dict[str, Any]]

class IntegrationConfigManager:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "/Users/mac/Agents/agentic_5/linkedin-domination/config"
        self.config_file = f"{self.config_path}/integration_config.yaml"
        self.secrets_file = f"{self.config_path}/secrets.yaml"
        self.api_configs = {}
        self.content_rules = None
        self.algorithm_weights = None
        self.rate_limiters = {}
        self.init_config_directory()
        
    def init_config_directory(self):
        """Initialize configuration directory structure"""
        Path(self.config_path).mkdir(parents=True, exist_ok=True)
        Path(f"{self.config_path}/api-keys").mkdir(parents=True, exist_ok=True)
        Path(f"{self.config_path}/environment-configs").mkdir(parents=True, exist_ok=True)
        Path(f"{self.config_path}/webhook-configs").mkdir(parents=True, exist_ok=True)
        
    async def initialize_all_integrations(self) -> Dict[str, Any]:
        """Initialize all integration configurations"""
        logger.info("Initializing all integration configurations...")
        
        # Initialize API configurations
        await self._init_linkedin_api_config()
        await self._init_openai_api_config()
        await self._init_elevenlabs_api_config()
        await self._init_fal_ai_config()
        await self._init_brightdata_config()
        await self._init_automation_configs()
        
        # Initialize content rules
        self._init_content_rules()
        
        # Initialize algorithm weights
        self._init_algorithm_weights()
        
        # Save configurations
        self._save_configurations()
        
        # Validate all configurations
        validation_results = await self._validate_all_configurations()
        
        return {
            'status': 'initialized',
            'configurations': list(self.api_configs.keys()),
            'validation_results': validation_results,
            'config_path': self.config_path
        }
    
    async def _init_linkedin_api_config(self):
        """Initialize LinkedIn API configuration"""
        linkedin_config = APIConfiguration(
            integration_type=IntegrationType.LINKEDIN_API,
            api_key=os.getenv('LINKEDIN_API_KEY', ''),
            base_url='https://api.linkedin.com/v2',
            rate_limit_rpm=100,
            rate_limit_rph=1000,
            timeout=30,
            retry_attempts=3,
            retry_delay=2,
            headers={
                'Authorization': f'Bearer {os.getenv("LINKEDIN_API_KEY", "")}',
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0'
            },
            endpoints={
                'people': '/people/(id:{person-id})',
                'shares': '/shares',
                'ugcPosts': '/ugcPosts',
                'articles': '/articles',
                'organizationAcls': '/organizationAcls?q=roleAssignee',
                'socialActions': '/socialActions/{shareUrn}/comments',
                'analytics': '/organizationalEntityShareStatistics'
            },
            authentication_method='oauth2'
        )
        
        self.api_configs[IntegrationType.LINKEDIN_API] = linkedin_config
        self.rate_limiters[IntegrationType.LINKEDIN_API] = RateLimiter(
            linkedin_config.rate_limit_rpm,
            linkedin_config.rate_limit_rph
        )
    
    async def _init_openai_api_config(self):
        """Initialize OpenAI API configuration"""
        openai_config = APIConfiguration(
            integration_type=IntegrationType.OPENAI_API,
            api_key=os.getenv('OPENAI_API_KEY', ''),
            base_url='https://api.openai.com/v1',
            rate_limit_rpm=3000,
            rate_limit_rph=10000,
            timeout=60,
            retry_attempts=3,
            retry_delay=1,
            headers={
                'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY", "")}',
                'Content-Type': 'application/json'
            },
            endpoints={
                'chat_completions': '/chat/completions',
                'embeddings': '/embeddings',
                'moderations': '/moderations',
                'images': '/images/generations',
                'audio': '/audio/speech'
            },
            authentication_method='bearer_token'
        )
        
        self.api_configs[IntegrationType.OPENAI_API] = openai_config
        self.rate_limiters[IntegrationType.OPENAI_API] = RateLimiter(
            openai_config.rate_limit_rpm,
            openai_config.rate_limit_rph
        )
    
    async def _init_elevenlabs_api_config(self):
        """Initialize ElevenLabs API configuration"""
        elevenlabs_config = APIConfiguration(
            integration_type=IntegrationType.ELEVENLABS_API,
            api_key=os.getenv('ELEVENLABS_API_KEY', ''),
            base_url='https://api.elevenlabs.io/v1',
            rate_limit_rpm=120,
            rate_limit_rph=1000,
            timeout=30,
            retry_attempts=3,
            retry_delay=2,
            headers={
                'xi-api-key': os.getenv('ELEVENLABS_API_KEY', ''),
                'Content-Type': 'application/json'
            },
            endpoints={
                'text_to_speech': '/text-to-speech/{voice_id}',
                'voices': '/voices',
                'voice_settings': '/voices/{voice_id}/settings',
                'user': '/user',
                'history': '/history'
            },
            authentication_method='api_key'
        )
        
        self.api_configs[IntegrationType.ELEVENLABS_API] = elevenlabs_config
        self.rate_limiters[IntegrationType.ELEVENLABS_API] = RateLimiter(
            elevenlabs_config.rate_limit_rpm,
            elevenlabs_config.rate_limit_rph
        )
    
    async def _init_fal_ai_config(self):
        """Initialize Fal.ai API configuration"""
        fal_ai_config = APIConfiguration(
            integration_type=IntegrationType.FAL_AI_API,
            api_key=os.getenv('FAL_AI_API_KEY', ''),
            base_url='https://fal.run/fal-ai',
            rate_limit_rpm=60,
            rate_limit_rph=500,
            timeout=120,
            retry_attempts=3,
            retry_delay=3,
            headers={
                'Authorization': f'Key {os.getenv("FAL_AI_API_KEY", "")}',
                'Content-Type': 'application/json'
            },
            endpoints={
                'text_to_image': '/fast-sdxl',
                'image_to_image': '/lcm-sd15-i2i',
                'face_to_sticker': '/face-to-sticker',
                'remove_background': '/birefnet',
                'upscale': '/real-esrgan'
            },
            authentication_method='api_key'
        )
        
        self.api_configs[IntegrationType.FAL_AI_API] = fal_ai_config
        self.rate_limiters[IntegrationType.FAL_AI_API] = RateLimiter(
            fal_ai_config.rate_limit_rpm,
            fal_ai_config.rate_limit_rph
        )
    
    async def _init_brightdata_config(self):
        """Initialize Brightdata API configuration"""
        brightdata_config = APIConfiguration(
            integration_type=IntegrationType.BRIGHTDATA_API,
            api_key=os.getenv('BRIGHTDATA_API_KEY', ''),
            base_url='https://api.brightdata.com/datasets/v3',
            rate_limit_rpm=100,
            rate_limit_rph=1000,
            timeout=60,
            retry_attempts=3,
            retry_delay=2,
            headers={
                'Authorization': f'Bearer {os.getenv("BRIGHTDATA_API_KEY", "")}',
                'Content-Type': 'application/json'
            },
            endpoints={
                'trigger': '/trigger',
                'snapshot': '/snapshot/{snapshot_id}',
                'datasets': '/datasets',
                'download': '/download/{snapshot_id}'
            },
            authentication_method='bearer_token'
        )
        
        self.api_configs[IntegrationType.BRIGHTDATA_API] = brightdata_config
        self.rate_limiters[IntegrationType.BRIGHTDATA_API] = RateLimiter(
            brightdata_config.rate_limit_rpm,
            brightdata_config.rate_limit_rph
        )
    
    async def _init_automation_configs(self):
        """Initialize automation tool configurations"""
        # Puppeteer configuration
        puppeteer_config = {
            'headless': True,
            'viewport': {'width': 1920, 'height': 1080},
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'timeout': 30000,
            'wait_for_selector_timeout': 10000,
            'navigation_timeout': 30000,
            'anti_detection': {
                'stealth_mode': True,
                'randomize_viewport': True,
                'proxy_rotation': True
            },
            'selectors': {
                'linkedin_login': '#username',
                'linkedin_password': '#password',
                'linkedin_login_button': 'button[type="submit"]',
                'linkedin_post_button': 'button[data-control-name="share_post"]',
                'linkedin_post_textarea': 'div[data-placeholder="Start a post..."]'
            }
        }
        
        # Playwright configuration
        playwright_config = {
            'browser_type': 'chromium',
            'headless': True,
            'viewport': {'width': 1920, 'height': 1080},
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'timeout': 30000,
            'navigation_timeout': 30000,
            'context_options': {
                'ignore_https_errors': True,
                'java_script_enabled': True
            }
        }
        
        # N8N configuration
        n8n_config = {
            'base_url': os.getenv('N8N_BASE_URL', 'http://localhost:5678'),
            'api_key': os.getenv('N8N_API_KEY', ''),
            'webhook_url': os.getenv('N8N_WEBHOOK_URL', ''),
            'workflows': {
                'content_publishing': 'linkedin_content_publisher',
                'engagement_monitoring': 'linkedin_engagement_monitor',
                'analytics_collection': 'linkedin_analytics_collector'
            }
        }
        
        # Store configurations
        self.api_configs['puppeteer'] = puppeteer_config
        self.api_configs['playwright'] = playwright_config
        self.api_configs['n8n'] = n8n_config
    
    def _init_content_rules(self):
        """Initialize content rules and guidelines"""
        self.content_rules = ContentRules(
            brand_voice="Professional, authoritative, yet approachable. Thought leader in the industry with practical insights.",
            tone_guidelines=[
                "Confident but not arrogant",
                "Helpful and educational",
                "Authentic and personal when appropriate",
                "Data-driven and evidence-based",
                "Optimistic and solution-focused"
            ],
            content_standards=[
                "Always provide value to the reader",
                "Include actionable insights or takeaways",
                "Use clear, concise language",
                "Support claims with data or examples",
                "Maintain professional standards"
            ],
            compliance_requirements=[
                "Follow FTC guidelines for sponsored content",
                "Disclose any financial relationships",
                "Respect intellectual property rights",
                "Avoid misleading or false claims",
                "Maintain LinkedIn community standards"
            ],
            psychological_triggers=[
                "Curiosity gaps in headlines",
                "Social proof through testimonials",
                "Urgency through time-sensitive information",
                "Authority through expertise demonstration",
                "Reciprocity through valuable free content"
            ],
            forbidden_topics=[
                "Political partisanship",
                "Religious controversies",
                "Personal attacks or negativity",
                "Unsubstantiated medical claims",
                "Controversial social issues"
            ],
            character_limits={
                'linkedin_post': 3000,
                'linkedin_headline': 120,
                'linkedin_summary': 2000,
                'twitter_post': 280,
                'meta_description': 160
            },
            hashtag_rules={
                'max_per_post': 5,
                'preferred_types': ['industry', 'topic', 'branded'],
                'research_required': True,
                'trending_weight': 0.3
            }
        )
    
    def _init_algorithm_weights(self):
        """Initialize algorithm weights with dynamic adjustment capability"""
        self.algorithm_weights = AlgorithmWeights(
            early_engagement=0.35,
            dwell_time=0.25,
            completion_rate=0.20,
            creator_mode=0.10,
            consistency=0.10,
            last_updated=datetime.now(),
            adjustment_history=[]
        )
    
    def _save_configurations(self):
        """Save all configurations to files"""
        # Save main configuration
        config_data = {
            'api_configurations': {
                integration_type.name: asdict(config) if hasattr(config, '__dict__') else config 
                for integration_type, config in self.api_configs.items()
                if isinstance(integration_type, IntegrationType)
            },
            'automation_configs': {
                key: config for key, config in self.api_configs.items()
                if not isinstance(key, IntegrationType)
            },
            'content_rules': asdict(self.content_rules) if self.content_rules else None,
            'algorithm_weights': asdict(self.algorithm_weights) if self.algorithm_weights else None,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)
        
        # Save environment template
        env_template = self._generate_env_template()
        with open(f"{self.config_path}/env.example", 'w') as f:
            f.write(env_template)
    
    def _generate_env_template(self) -> str:
        """Generate environment variables template"""
        template = """# LinkedIn Content Domination - Environment Variables

# LinkedIn API Configuration
LINKEDIN_API_KEY=your_linkedin_api_key_here
LINKEDIN_CLIENT_ID=your_linkedin_client_id_here
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret_here

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_ORGANIZATION=your_openai_org_id_here

# ElevenLabs API Configuration
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Fal.ai API Configuration
FAL_AI_API_KEY=your_fal_ai_api_key_here

# Brightdata API Configuration
BRIGHTDATA_API_KEY=your_brightdata_api_key_here
BRIGHTDATA_PROXY_HOST=your_brightdata_proxy_host
BRIGHTDATA_PROXY_PORT=your_brightdata_proxy_port
BRIGHTDATA_PROXY_USERNAME=your_brightdata_proxy_username
BRIGHTDATA_PROXY_PASSWORD=your_brightdata_proxy_password

# N8N Configuration
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=your_n8n_api_key_here
N8N_WEBHOOK_URL=your_n8n_webhook_url_here

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/linkedin_domination
REDIS_URL=redis://localhost:6379

# Webhook Configuration
WEBHOOK_SECRET=your_webhook_secret_here
WEBHOOK_BASE_URL=https://your-domain.com/webhooks

# Security Configuration
JWT_SECRET=your_jwt_secret_here
ENCRYPTION_KEY=your_encryption_key_here

# Monitoring Configuration
SENTRY_DSN=your_sentry_dsn_here
LOG_LEVEL=INFO
"""
        return template
    
    async def _validate_all_configurations(self) -> Dict[str, Any]:
        """Validate all API configurations"""
        validation_results = {}
        
        for integration_type, config in self.api_configs.items():
            if isinstance(integration_type, IntegrationType):
                try:
                    validation_result = await self._validate_api_config(config)
                    validation_results[integration_type.name] = validation_result
                except Exception as e:
                    validation_results[integration_type.name] = {
                        'valid': False,
                        'error': str(e)
                    }
        
        return validation_results
    
    async def _validate_api_config(self, config: APIConfiguration) -> Dict[str, Any]:
        """Validate individual API configuration"""
        if not config.api_key:
            return {
                'valid': False,
                'error': 'API key not configured'
            }
        
        try:
            # Test API connection
            async with aiohttp.ClientSession() as session:
                test_url = f"{config.base_url}/test" if config.integration_type == IntegrationType.LINKEDIN_API else config.base_url
                
                async with session.get(
                    test_url,
                    headers=config.headers,
                    timeout=aiohttp.ClientTimeout(total=config.timeout)
                ) as response:
                    if response.status in [200, 401, 403]:  # 401/403 means auth is being processed
                        return {
                            'valid': True,
                            'status_code': response.status,
                            'response_time': response.headers.get('X-Response-Time', 'N/A')
                        }
                    else:
                        return {
                            'valid': False,
                            'error': f'Unexpected status code: {response.status}'
                        }
        except Exception as e:
            return {
                'valid': False,
                'error': f'Connection test failed: {str(e)}'
            }
    
    def get_api_config(self, integration_type: IntegrationType) -> APIConfiguration:
        """Get API configuration for specific integration"""
        return self.api_configs.get(integration_type)
    
    def get_rate_limiter(self, integration_type: IntegrationType) -> 'RateLimiter':
        """Get rate limiter for specific integration"""
        return self.rate_limiters.get(integration_type)
    
    def update_algorithm_weights(self, new_weights: Dict[str, float]) -> None:
        """Update algorithm weights with history tracking"""
        if self.algorithm_weights:
            old_weights = asdict(self.algorithm_weights)
            
            # Update weights
            for key, value in new_weights.items():
                if hasattr(self.algorithm_weights, key):
                    setattr(self.algorithm_weights, key, value)
            
            # Track history
            self.algorithm_weights.adjustment_history.append({
                'timestamp': datetime.now().isoformat(),
                'old_weights': old_weights,
                'new_weights': new_weights,
                'reason': 'Manual adjustment'
            })
            
            self.algorithm_weights.last_updated = datetime.now()
            
            # Save updated configuration
            self._save_configurations()

class RateLimiter:
    def __init__(self, requests_per_minute: int, requests_per_hour: int):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_requests = []
        self.hour_requests = []
    
    async def acquire(self) -> bool:
        """Acquire rate limit permission"""
        now = datetime.now()
        
        # Clean old requests
        self.minute_requests = [req_time for req_time in self.minute_requests 
                               if now - req_time < timedelta(minutes=1)]
        self.hour_requests = [req_time for req_time in self.hour_requests 
                             if now - req_time < timedelta(hours=1)]
        
        # Check limits
        if len(self.minute_requests) >= self.requests_per_minute:
            return False
        if len(self.hour_requests) >= self.requests_per_hour:
            return False
        
        # Record request
        self.minute_requests.append(now)
        self.hour_requests.append(now)
        
        return True
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        now = datetime.now()
        
        minute_usage = len([req_time for req_time in self.minute_requests 
                           if now - req_time < timedelta(minutes=1)])
        hour_usage = len([req_time for req_time in self.hour_requests 
                         if now - req_time < timedelta(hours=1)])
        
        return {
            'minute_usage': minute_usage,
            'minute_limit': self.requests_per_minute,
            'hour_usage': hour_usage,
            'hour_limit': self.requests_per_hour,
            'minute_remaining': self.requests_per_minute - minute_usage,
            'hour_remaining': self.requests_per_hour - hour_usage
        }

# Usage example
async def main():
    config_manager = IntegrationConfigManager()
    
    # Initialize all integrations
    results = await config_manager.initialize_all_integrations()
    
    print("Integration configuration complete!")
    print(f"Status: {results['status']}")
    print(f"Configurations: {results['configurations']}")
    print(f"Validation results: {results['validation_results']}")

if __name__ == "__main__":
    asyncio.run(main())