# ABOUTME: Enhanced generic planner agent with master orchestrator capabilities
# ABOUTME: Framework V2.0 compliant planner using LangGraph with sophisticated planning features

# type: ignore

import logging
import os
from datetime import datetime

from collections.abc import AsyncIterable
from typing import Any, Literal, Optional, Dict, List

from a2a_mcp.common import prompts
from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.types import GenericTaskList
from a2a_mcp.common.utils import init_api_key
from a2a_mcp.common.quality_framework import QualityThresholdFramework, QualityDomain
from langchain_core.messages import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field


memory = MemorySaver()
logger = logging.getLogger(__name__)


class EnhancedPlannerResponseFormat(BaseModel):
    """Enhanced response format for sophisticated domain planning."""

    status: Literal['planning', 'input_required', 'completed', 'error'] = 'planning'
    analysis: str = Field(description="Analysis of the user request and planning approach")
    question: Optional[str] = Field(description='Input needed from the user if status is input_required', default=None)
    content: Optional[GenericTaskList] = Field(description='Generated task list when planning is completed', default=None)
    coordination_strategy: str = Field(description="Recommended execution strategy (sequential/parallel/hybrid)", default="sequential")
    domains_required: List[str] = Field(description="Domain specialists that would be helpful", default_factory=list)
    quality_score: Optional[float] = Field(description="Quality assessment of the plan (0-1)", default=None)
    confidence: Literal['high', 'medium', 'low'] = Field(description="Confidence in the plan quality", default='medium')
    dependencies_identified: bool = Field(description="Whether task dependencies were analyzed", default=False)


class EnhancedGenericPlannerAgent(BaseAgent):
    """Enhanced Generic Planner Agent with master orchestrator capabilities but simple interface."""

    def __init__(
        self, 
        domain: str = "General",
        agent_name: str = None, 
        custom_prompt: Optional[str] = None,
        domain_specialists: Optional[Dict[str, str]] = None,
        enable_quality_validation: bool = True,
        enable_fallback_planning: bool = True,
        planning_mode: Literal['simple', 'sophisticated'] = 'sophisticated',
        quality_domain: QualityDomain = QualityDomain.GENERIC
    ):
        init_api_key()

        agent_name = agent_name or f"Enhanced {domain} Planner Agent"
        logger.info(f'Initializing {agent_name}')

        super().__init__(
            agent_name=agent_name,
            description=f'Advanced breakdown of {domain.lower()} user requests into executable tasks with quality validation',
            content_types=['text', 'text/plain'],
        )

        self.domain = domain
        self.domain_specialists = domain_specialists or {}
        self.enable_quality_validation = enable_quality_validation
        self.enable_fallback_planning = enable_fallback_planning
        self.planning_mode = planning_mode
        
        # Initialize quality framework if enabled
        self.quality_framework = None
        if enable_quality_validation:
            self.quality_framework = QualityThresholdFramework()
            self.quality_framework.configure_domain(quality_domain)

        self.model = ChatGoogleGenerativeAI(
            model=os.getenv('GEMINI_MODEL', 'gemini-2.0-flash'), 
            temperature=0.1  # Slightly higher for more creative planning
        )

        # Enhanced planning instructions
        if custom_prompt:
            planning_prompt = custom_prompt
        elif self.planning_mode == 'sophisticated':
            planning_prompt = self._get_enhanced_planning_prompt()
        else:
            planning_prompt = prompts.GENERIC_PLANNER_COT_INSTRUCTIONS

        # Initialize primary planner
        self.graph = None
        self._init_planner(planning_prompt)
        
        # Health and diagnostics
        self.planning_history = []
        self.failure_count = 0
        self.last_health_check = None

    def _init_planner(self, planning_prompt: str):
        """Initialize LangGraph planner with enhanced error handling."""
        try:
            self.graph = create_react_agent(
                self.model,
                checkpointer=memory,
                prompt=planning_prompt,
                response_format=EnhancedPlannerResponseFormat,
                tools=[],
            )
            logger.info(f"Enhanced planner initialized for {self.domain}")
            
        except Exception as e:
            logger.error(f"Failed to initialize enhanced planner for {self.domain}: {e}")
            if self.enable_fallback_planning:
                self._init_fallback_planner()
            else:
                raise

    def _init_fallback_planner(self):
        """Initialize simple fallback planner when main planner fails."""
        try:
            logger.warning(f"Initializing fallback planner for {self.domain}")
            # Use simpler prompt for fallback
            fallback_prompt = prompts.GENERIC_PLANNER_COT_INSTRUCTIONS
            
            self.graph = create_react_agent(
                self.model,
                checkpointer=memory,
                prompt=fallback_prompt,
                response_format=EnhancedPlannerResponseFormat,
                tools=[],
            )
            logger.info(f"Fallback planner initialized for {self.domain}")
            
        except Exception as e:
            logger.error(f"Complete planner initialization failure for {self.domain}: {e}")
            self.graph = None  # Will trigger manual fallback in methods

    def _get_enhanced_planning_prompt(self) -> str:
        """Get enhanced planning prompt with domain specialists awareness."""
        specialist_list = ""
        if self.domain_specialists:
            specialist_list = '\n'.join([f"- {key}: {desc}" for key, desc in self.domain_specialists.items()])
            specialist_context = f"""
Available Domain Specialists:
{specialist_list}

When creating tasks, consider which specialists would be best suited for each task.
"""
        else:
            specialist_context = "No specific domain specialists configured. Create general task assignments."

        return f"""
You are an Enhanced {self.domain} Task Planner with sophisticated planning capabilities.

Your role is to analyze user requests and create comprehensive, high-quality execution plans.

{specialist_context}

ENHANCED PLANNING PROCESS:
1. **Domain Analysis**: Identify the specific {self.domain.lower()} context and requirements
2. **Requirement Extraction**: Extract all explicit and implicit requirements
3. **Task Decomposition**: Break down into logical, executable tasks
4. **Dependency Analysis**: Identify task dependencies and prerequisites
5. **Coordination Strategy**: Determine optimal execution approach (sequential/parallel/hybrid)
6. **Quality Assessment**: Evaluate plan completeness and feasibility
7. **Specialist Assignment**: Recommend appropriate domain specialists for each task

QUALITY STANDARDS:
- Tasks must be specific, measurable, and actionable
- Dependencies must be clearly identified
- Execution strategy must be optimized for efficiency
- Plan must be comprehensive yet practical

RESPONSE REQUIREMENTS:
- Provide thorough analysis of the request
- Create detailed task breakdown with clear descriptions
- Identify coordination strategy and domain specialists needed
- Assess plan quality and confidence level
- Ask clarifying questions if critical information is missing

ADVANCED CAPABILITIES:
- Dependency Analysis: Identify task dependencies and critical path
- Quality Assessment: Score plan completeness and feasibility (0-1 scale)
- Coordination Strategy: Recommend optimal execution approach
- Specialist Assignment: Match tasks to appropriate domain specialists
- Risk Assessment: Identify potential blockers and mitigation strategies

Focus on creating enterprise-grade plans that are both comprehensive and executable.
        """

    def _get_generic_planning_prompt(self) -> str:
        """Get generic planning prompt that works for any domain."""
        return f"""
You are a {self.domain} Task Planner. Your role is to analyze user requests and break them down into clear, executable tasks.

Instructions:
1. Analyze the user's request thoroughly
2. Identify the key components and requirements
3. Break down the request into specific, actionable tasks
4. Ensure tasks are ordered logically with clear dependencies
5. Assign appropriate status to each task (pending, in_progress, completed, etc.)
6. Consider the domain context: {self.domain.lower()}

If you need more information from the user to create a comprehensive plan, ask specific questions.
Always provide a complete task list when you have sufficient information.
        """

    def invoke(self, query, sessionId) -> str:
        """Invoke enhanced planner with quality validation and health monitoring."""
        config = {'configurable': {'thread_id': sessionId}}
        
        try:
            # Record planning attempt
            self.planning_history.append({
                'timestamp': datetime.now(),
                'query': query,
                'session_id': sessionId,
                'mode': self.planning_mode
            })
            
            # Execute planning
            if self.graph:
                result = self.graph.invoke({'messages': [('user', query)]}, config)
                response = self.get_agent_response(config)
                
                # Quality validation if enabled
                if self.enable_quality_validation and self.quality_framework:
                    self._validate_plan_quality(response, query)
                
                return response
            else:
                return self._manual_fallback_planning(query)
                
        except Exception as e:
            logger.error(f"Enhanced planner invoke error: {e}")
            self.failure_count += 1
            
            if self.enable_fallback_planning:
                return self._manual_fallback_planning(query)
            else:
                return {
                    'response_type': 'text',
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': f'Planning failed: {str(e)}. Please try again.'
                }

    async def stream(
        self, query, sessionId, task_id
    ) -> AsyncIterable[dict[str, Any]]:
        """Stream enhanced planning with sophisticated progress tracking."""
        inputs = {'messages': [('user', query)]}
        config = {'configurable': {'thread_id': sessionId}}

        logger.info(
            f'Running {self.agent_name} stream for session {sessionId} {task_id} with input {query}'
        )

        try:
            # Record streaming attempt
            self.planning_history.append({
                'timestamp': datetime.now(),
                'query': query,
                'session_id': sessionId,
                'task_id': task_id,
                'mode': self.planning_mode,
                'stream': True
            })

            if self.graph:
                # Enhanced streaming with progress indicators
                step_count = 0
                for item in self.graph.stream(inputs, config, stream_mode='values'):
                    step_count += 1
                    message = item['messages'][-1]
                    
                    if isinstance(message, AIMessage):
                        # Add planning progress context
                        content = message.content
                        if self.planning_mode == 'sophisticated':
                            content = f"[Step {step_count}] {content}"
                        
                        yield {
                            'response_type': 'text',
                            'is_task_complete': False,
                            'require_user_input': False,
                            'content': content,
                            'planning_step': step_count,
                            'domain': self.domain
                        }
                
                # Final response with quality validation
                final_response = self.get_agent_response(config)
                if self.enable_quality_validation and self.quality_framework:
                    self._validate_plan_quality(final_response, query)
                
                yield final_response
            else:
                # Fallback streaming
                yield {
                    'response_type': 'text',
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': 'Planning system initializing with fallback mode...'
                }
                yield self._manual_fallback_planning(query)
                
        except Exception as e:
            logger.error(f"Enhanced planner stream error: {e}")
            self.failure_count += 1
            
            yield {
                'response_type': 'text',
                'is_task_complete': False,
                'require_user_input': True,
                'content': f'Planning stream failed: {str(e)}. Please try again.'
            }

    def get_agent_response(self, config):
        current_state = self.graph.get_state(config)
        structured_response = current_state.values.get('structured_response')
        if structured_response and isinstance(
            structured_response, EnhancedPlannerResponseFormat
        ):
            if (
                structured_response.status == 'input_required'
                # and structured_response.content.tasks
            ):
                return {
                    'response_type': 'text',
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': structured_response.question,
                }
            if structured_response.status == 'error':
                return {
                    'response_type': 'text',
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': structured_response.question,
                }
            if structured_response.status == 'completed':
                return {
                    'response_type': 'data',
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': structured_response.content.model_dump(),
                }
        return {
            'response_type': 'text',
            'is_task_complete': False,
            'require_user_input': True,
            'content': 'We are unable to process your request at the moment. Please try again.',
        }

    def _validate_plan_quality(self, response: dict, query: str) -> None:
        """Validate plan quality using quality framework."""
        try:
            if response.get('response_type') == 'data' and response.get('content'):
                plan_data = response['content']
                
                # Basic quality checks
                task_count = len(plan_data.get('tasks', []))
                has_descriptions = all(
                    task.get('description', '').strip() 
                    for task in plan_data.get('tasks', [])
                )
                
                quality_score = 0.0
                if task_count > 0:
                    quality_score += 0.3
                if has_descriptions:
                    quality_score += 0.4
                if plan_data.get('coordination_strategy'):
                    quality_score += 0.3
                
                logger.info(f"Plan quality score: {quality_score:.2f} for query: {query[:50]}...")
                
        except Exception as e:
            logger.warning(f"Quality validation failed: {e}")

    def _manual_fallback_planning(self, query: str) -> dict:
        """Manual fallback when LangGraph planning fails."""
        logger.info(f"Using manual fallback planning for: {query[:50]}...")
        
        # Simple task breakdown logic
        tasks = [{
            'id': 1,
            'description': f'Analyze and plan: {query}',
            'status': 'pending',
            'agent_type': 'generic',
            'priority': 5,
            'dependencies': [],
            'estimated_duration': '30 minutes'
        }]
        
        return {
            'response_type': 'data',
            'is_task_complete': True,
            'require_user_input': False,
            'content': {
                'original_query': query,
                'domain': self.domain,
                'tasks': tasks,
                'coordination_strategy': 'sequential',
                'metadata': {
                    'complexity': 'medium',
                    'total_estimated_duration': '30 minutes',
                    'fallback_used': True
                }
            }
        }

    def get_health_status(self) -> dict:
        """Get agent health and performance metrics."""
        return {
            'agent_name': self.agent_name,
            'domain': self.domain,
            'planning_mode': self.planning_mode,
            'total_plans': len(self.planning_history),
            'failure_count': self.failure_count,
            'success_rate': (len(self.planning_history) - self.failure_count) / max(len(self.planning_history), 1),
            'quality_validation_enabled': self.enable_quality_validation,
            'fallback_planning_enabled': self.enable_fallback_planning,
            'graph_initialized': self.graph is not None,
            'domain_specialists': list(self.domain_specialists.keys()),
            'last_health_check': datetime.now().isoformat()
        }

    def get_planning_insights(self) -> dict:
        """Get insights from planning history for optimization."""
        if not self.planning_history:
            return {'insights': 'No planning history available'}
        
        recent_plans = self.planning_history[-10:]  # Last 10 plans
        
        return {
            'total_plans_analyzed': len(recent_plans),
            'domains_covered': list(set(plan.get('mode', 'unknown') for plan in recent_plans)),
            'average_planning_frequency': 'Multiple per session',
            'recommendations': [
                'Monitor quality scores for plan optimization',
                'Consider domain specialist utilization',
                'Track coordination strategy effectiveness'
            ]
        }

    def analyze_task_dependencies(self, tasks: List[dict]) -> dict:
        """Analyze task dependencies and suggest execution strategy."""
        if not tasks:
            return {'strategy': 'none', 'analysis': 'No tasks to analyze'}
        
        # Simple dependency analysis
        has_dependencies = any(task.get('dependencies', []) for task in tasks)
        task_count = len(tasks)
        
        if task_count == 1:
            strategy = 'single'
        elif has_dependencies:
            strategy = 'sequential'  # Safe default for dependencies
        elif task_count <= 3:
            strategy = 'parallel'
        else:
            strategy = 'hybrid'  # Mix of parallel and sequential
        
        return {
            'strategy': strategy,
            'task_count': task_count,
            'has_dependencies': has_dependencies,
            'analysis': f'Recommended {strategy} execution for {task_count} tasks',
            'coordination_recommendations': [
                f'Execute {strategy}ly for optimal efficiency',
                'Monitor task completion for dependencies',
                'Consider resource allocation across tasks'
            ]
        }

    def get_domain_specialist_recommendations(self, tasks: List[dict]) -> dict:
        """Recommend domain specialists for task execution."""
        recommendations = {}
        
        for task in tasks:
            task_desc = task.get('description', '').lower()
            task_id = task.get('id', 'unknown')
            
            # Simple keyword matching for specialist recommendation
            if any(keyword in task_desc for keyword in ['analyze', 'research', 'investigate']):
                recommendations[task_id] = 'analyst'
            elif any(keyword in task_desc for keyword in ['implement', 'build', 'create', 'develop']):
                recommendations[task_id] = 'implementer'
            elif any(keyword in task_desc for keyword in ['test', 'validate', 'verify']):
                recommendations[task_id] = 'validator'
            elif any(keyword in task_desc for keyword in ['coordinate', 'manage', 'oversee']):
                recommendations[task_id] = 'coordinator'
            else:
                recommendations[task_id] = 'generalist'
        
        return {
            'task_specialist_mapping': recommendations,
            'unique_specialists_needed': list(set(recommendations.values())),
            'specialist_utilization': len(set(recommendations.values())),
            'recommendations': f'Utilize {len(set(recommendations.values()))} specialist types for optimal task execution'
        }

    def enhance_task_with_metadata(self, task: dict, context: dict = None) -> dict:
        """Enhance a task with additional metadata for better execution."""
        enhanced_task = task.copy()
        
        # Add enhanced metadata
        enhanced_task.update({
            'domain': self.domain,
            'created_by': self.agent_name,
            'planning_mode': self.planning_mode,
            'enhancement_timestamp': datetime.now().isoformat(),
            'estimated_complexity': self._estimate_task_complexity(task),
            'suggested_specialist': self._suggest_task_specialist(task),
            'execution_hints': self._generate_execution_hints(task)
        })
        
        return enhanced_task

    def _estimate_task_complexity(self, task: dict) -> str:
        """Estimate task complexity based on description and metadata."""
        description = task.get('description', '')
        
        # Simple heuristic based on description length and keywords
        if len(description) > 100 or any(keyword in description.lower() for keyword in ['complex', 'integrate', 'comprehensive']):
            return 'high'
        elif len(description) > 50 or any(keyword in description.lower() for keyword in ['analyze', 'implement', 'coordinate']):
            return 'medium'
        else:
            return 'low'

    def _suggest_task_specialist(self, task: dict) -> str:
        """Suggest appropriate specialist for task execution."""
        description = task.get('description', '').lower()
        
        # Check configured domain specialists first
        for specialist_type, specialist_desc in self.domain_specialists.items():
            if any(keyword in description for keyword in specialist_desc.lower().split()):
                return specialist_type
        
        # Fallback to general specialist categories
        if any(keyword in description for keyword in ['plan', 'strategy', 'coordinate']):
            return 'planner'
        elif any(keyword in description for keyword in ['implement', 'build', 'create']):
            return 'implementer'
        elif any(keyword in description for keyword in ['analyze', 'research', 'study']):
            return 'analyst'
        else:
            return 'generalist'

    def _generate_execution_hints(self, task: dict) -> List[str]:
        """Generate execution hints for better task completion."""
        hints = []
        description = task.get('description', '').lower()
        
        if 'analyze' in description:
            hints.append('Consider multiple data sources and validation methods')
        if 'implement' in description:
            hints.append('Follow established patterns and best practices')
        if 'coordinate' in description:
            hints.append('Ensure clear communication channels with all stakeholders')
        if 'test' in description:
            hints.append('Plan for both positive and negative test scenarios')
        
        # Add domain-specific hints
        hints.append(f'Apply {self.domain.lower()} domain expertise and standards')
        
        return hints or ['Follow standard execution procedures']