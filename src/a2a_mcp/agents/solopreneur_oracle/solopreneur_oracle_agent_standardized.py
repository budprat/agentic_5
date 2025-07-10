"""
ABOUTME: Standardized Solopreneur Oracle Agent using Google ADK + LangGraph pattern
ABOUTME: Features task decomposition, unified MCP tools, and quality thresholds
"""

import logging
import json
import asyncio
from collections.abc import AsyncIterable
from typing import Dict, Any, List, Literal
from datetime import datetime

from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.agent_runner import AgentRunner
from a2a_mcp.common.utils import get_mcp_server_config, init_api_key
from a2a_mcp.common.types import TaskList

# Google ADK imports
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams
from google.genai import types as genai_types

# LangGraph imports
from langchain_core.messages import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
memory = MemorySaver()

# Task Decomposition Response Format
class TaskDecompositionFormat(BaseModel):
    """Response format for task decomposition."""
    
    status: Literal['planning', 'ready', 'error'] = 'planning'
    analysis: str = Field(description="Analysis of the user request")
    tasks: TaskList = Field(description="Decomposed tasks for domain oracles")
    coordination_strategy: str = Field(description="How tasks will be coordinated")
    quality_requirements: Dict[str, float] = Field(description="Quality thresholds for each domain")

# Synthesis Response Format  
class SynthesisFormat(BaseModel):
    """Response format for intelligence synthesis."""
    
    executive_summary: str = Field(description="Brief 2-3 sentence summary")
    confidence_score: float = Field(description="Overall confidence 0.0-1.0")
    technical_assessment: Dict[str, Any] = Field(description="Technical feasibility analysis")
    personal_optimization: Dict[str, Any] = Field(description="Personal productivity insights")
    strategic_insights: List[Dict[str, Any]] = Field(description="Key findings from domains")
    integration_opportunities: Dict[str, Any] = Field(description="Synergy opportunities")
    action_plan: Dict[str, Any] = Field(description="Structured action plan")
    risk_assessment: Dict[str, Any] = Field(description="Risk analysis and mitigation")

class StandardizedSolopreneurOracleAgent(BaseAgent):
    """Standardized Solopreneur Oracle using Google ADK + LangGraph pattern with task decomposition."""

    def __init__(self):
        init_api_key()
        
        super().__init__(
            agent_name="Solopreneur Oracle Standardized",
            description="Master AI developer/entrepreneur intelligence orchestrator with ADK+LangGraph",
            content_types=["text", "text/plain"],
        )
        
        # Standardized components
        self.adk_agent = None
        self.task_planner = None
        self.runner = None
        
        # Quality thresholds (domain-specific)
        self.quality_thresholds = {
            "business": {
                "confidence_score": 0.75,
                "technical_feasibility": 0.8,
                "personal_sustainability": 0.7
            },
            "technical": {
                "confidence_score": 0.8,
                "implementation_complexity": 0.7,
                "architecture_quality": 0.85
            },
            "personal": {
                "energy_impact": 0.7,
                "cognitive_load": 0.6,
                "sustainability_score": 0.75
            }
        }
        
        # Domain oracle mapping
        self.domain_oracles = {
            "technical_intelligence": "http://localhost:10902",
            "knowledge_management": "http://localhost:10903", 
            "personal_optimization": "http://localhost:10904",
            "learning_enhancement": "http://localhost:10905",
            "integration_synthesis": "http://localhost:10906"
        }

    async def init_agents(self):
        """Initialize Google ADK agent and LangGraph task planner."""
        if self.adk_agent and self.task_planner:
            return
            
        logger.info("Initializing standardized solopreneur oracle components")
        
        # Initialize MCP tools via ADK
        config = get_mcp_server_config()
        tools = await MCPToolset(
            connection_params=SseServerParams(url=config.url)
        ).get_tools()
        
        logger.info(f"Loaded {len(tools)} MCP tools via ADK")
        
        # Initialize Google ADK agent for execution
        generate_content_config = genai_types.GenerateContentConfig(temperature=0.1)
        
        self.adk_agent = Agent(
            name=self.agent_name,
            instruction=self._get_execution_instructions(),
            model='gemini-2.0-flash',
            disallow_transfer_to_parent=True,
            disallow_transfer_to_peers=True, 
            generate_content_config=generate_content_config,
            tools=tools,
        )
        
        # Initialize LangGraph task planner
        self.task_planner = create_react_agent(
            ChatGoogleGenerativeAI(model='gemini-2.0-flash', temperature=0.0),
            checkpointer=memory,
            prompt=self._get_planning_instructions(),
            response_format=TaskDecompositionFormat,
            tools=[],
        )
        
        self.runner = AgentRunner()
        logger.info("Standardized components initialized successfully")

    def _get_planning_instructions(self) -> str:
        """Get task decomposition instructions for LangGraph planner."""
        return """
        You are the Solopreneur Oracle Task Planner. Decompose user requests into coordinated tasks for domain specialists.
        
        Domain Oracles Available:
        - technical_intelligence: Architecture, code quality, AI/ML implementation
        - knowledge_management: Information organization, learning strategies  
        - personal_optimization: Energy, focus, productivity optimization
        - learning_enhancement: Skill development, education strategies
        - integration_synthesis: Workflow integration, automation opportunities
        
        For each request:
        1. Analyze the scope and identify relevant domains
        2. Create specific tasks for each domain oracle
        3. Define coordination strategy (parallel/sequential)
        4. Set quality requirements per domain
        5. Plan synthesis approach
        
        Focus on AI developer/entrepreneur context with technical excellence and personal sustainability.
        """

    def _get_execution_instructions(self) -> str:
        """Get execution instructions for Google ADK agent."""
        return """
        You are the Solopreneur Oracle Executor. Coordinate domain oracles and synthesize intelligence.
        
        Your role:
        1. Execute task plans from the planner
        2. Coordinate with domain oracles via A2A protocol  
        3. Monitor quality thresholds
        4. Synthesize intelligence into actionable insights
        5. Provide strategic recommendations for AI developers/entrepreneurs
        
        Quality Standards:
        - Technical solutions must be implementable and scalable
        - Personal recommendations must consider energy/sustainability
        - Integration opportunities should reduce cognitive load
        - All recommendations need clear success metrics
        
        Use available MCP tools for enhanced capabilities.
        """

    async def stream(self, query: str, context_id: str, task_id: str) -> AsyncIterable[Dict[str, Any]]:
        """Main streaming interface with task decomposition."""
        logger.info(f"Solopreneur Oracle processing: {query}")
        
        if not self.adk_agent or not self.task_planner:
            await self.init_agents()
            
        try:
            # Phase 1: Task Decomposition via LangGraph
            yield {
                'is_task_complete': False,
                'require_user_input': False,
                'content': "🎯 Decomposing request into specialized tasks..."
            }
            
            task_plan = await self._decompose_tasks(query, context_id)
            
            yield {
                'is_task_complete': False,
                'require_user_input': False,
                'content': f"📋 Created {len(task_plan.tasks.tasks)} specialized tasks"
            }
            
            # Phase 2: Execute tasks via ADK agent with domain coordination
            yield {
                'is_task_complete': False,
                'require_user_input': False,
                'content': "⚡ Coordinating domain oracles..."
            }
            
            intelligence_data = await self._execute_domain_coordination(task_plan, context_id)
            
            # Phase 3: Intelligence synthesis via ADK agent
            yield {
                'is_task_complete': False,
                'require_user_input': False,
                'content': "🔬 Synthesizing intelligence..."
            }
            
            synthesis_query = self._build_synthesis_query(query, task_plan, intelligence_data)
            
            async for chunk in self.runner.run_stream(self.adk_agent, synthesis_query, context_id):
                if isinstance(chunk, dict) and chunk.get('type') == 'final_result':
                    response = chunk['response']
                    yield self.get_agent_response(response)
                else:
                    yield {
                        'is_task_complete': False,
                        'require_user_input': False,
                        'content': "🔄 Processing synthesis...",
                    }
                    
        except Exception as e:
            logger.error(f"Error in solopreneur oracle: {e}")
            yield {
                'is_task_complete': True,
                'require_user_input': False,
                'content': f"❌ Error: {str(e)}",
            }

    async def _decompose_tasks(self, query: str, context_id: str) -> TaskDecompositionFormat:
        """Decompose user request into domain-specific tasks via LangGraph."""
        inputs = {'messages': [('user', f"Decompose this solopreneur request: {query}")]}
        config = {'configurable': {'thread_id': context_id}}
        
        # Run LangGraph planner
        for item in self.task_planner.stream(inputs, config, stream_mode='values'):
            message = item['messages'][-1]
            if isinstance(message, AIMessage):
                continue
                
        # Get structured task plan
        current_state = self.task_planner.get_state(config)
        task_plan = current_state.values.get('structured_response')
        
        if not task_plan or not isinstance(task_plan, TaskDecompositionFormat):
            # Fallback plan if decomposition fails
            logger.warning("Task decomposition failed, using fallback plan")
            return TaskDecompositionFormat(
                status='ready',
                analysis=f"General analysis needed for: {query}",
                tasks=TaskList(tasks=[
                    {"task_id": "tech_analysis", "description": f"Technical analysis of: {query}", "domain": "technical_intelligence"},
                    {"task_id": "personal_analysis", "description": f"Personal optimization for: {query}", "domain": "personal_optimization"}
                ]),
                coordination_strategy="parallel",
                quality_requirements=self.quality_thresholds["business"]
            )
            
        return task_plan

    async def _execute_domain_coordination(self, task_plan: TaskDecompositionFormat, context_id: str) -> Dict[str, Any]:
        """Execute domain oracle coordination via A2A protocol."""
        intelligence_data = {}
        
        # Group tasks by domain for parallel execution
        domain_tasks = {}
        for task in task_plan.tasks.tasks:
            domain = task.get('domain', 'technical_intelligence')
            if domain not in domain_tasks:
                domain_tasks[domain] = []
            domain_tasks[domain].append(task)
        
        # Execute domain tasks (simplified - in production would use A2A protocol)
        for domain, tasks in domain_tasks.items():
            try:
                # Simulate domain oracle response (replace with actual A2A calls)
                intelligence_data[domain] = {
                    "tasks_completed": len(tasks),
                    "domain_analysis": f"Analysis from {domain} oracle",
                    "confidence": 0.8,
                    "recommendations": [f"Recommendation from {domain}"],
                    "timestamp": datetime.now().isoformat()
                }
                logger.info(f"Completed {len(tasks)} tasks for {domain}")
                
            except Exception as e:
                logger.error(f"Error executing {domain} tasks: {e}")
                intelligence_data[domain] = {"error": str(e)}
        
        return intelligence_data

    def _build_synthesis_query(self, original_query: str, task_plan: TaskDecompositionFormat, intelligence_data: Dict[str, Any]) -> str:
        """Build synthesis query for ADK agent."""
        return f"""
        Synthesize the following solopreneur intelligence into actionable insights:
        
        Original Query: {original_query}
        
        Task Plan Analysis: {task_plan.analysis}
        Coordination Strategy: {task_plan.coordination_strategy}
        
        Domain Intelligence:
        {json.dumps(intelligence_data, indent=2)}
        
        Quality Requirements:
        {json.dumps(task_plan.quality_requirements, indent=2)}
        
        Provide comprehensive synthesis addressing:
        1. Executive summary with confidence assessment
        2. Technical feasibility and architecture recommendations  
        3. Personal optimization strategies
        4. Strategic insights from domain analysis
        5. Integration opportunities and workflow optimizations
        6. Actionable plans with success metrics
        7. Risk assessment and mitigation strategies
        
        Format as structured JSON matching SynthesisFormat.
        """

    async def invoke(self, query: str, session_id: str) -> dict:
        """Non-streaming invoke method."""
        raise NotImplementedError("Use streaming interface for standardized agent")