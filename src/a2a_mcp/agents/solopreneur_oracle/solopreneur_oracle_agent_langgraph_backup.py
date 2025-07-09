"""
Solopreneur Oracle Agent - Master orchestrator with LangGraph integration.
Uses sophisticated multi-agent handoffs and parallel execution.
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Literal, Optional
from datetime import datetime
from collections.abc import AsyncIterable

from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import init_api_key
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command
from langgraph.prebuilt import create_react_agent, InjectedState
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from google import genai
import networkx as nx

logger = logging.getLogger(__name__)

# Domain specialist handoff tools
def create_handoff_tool(*, agent_name: str, description: str = None):
    """Create a handoff tool following LangGraph patterns."""
    from langchain_core.tools import tool
    
    name = f"transfer_to_{agent_name}"
    description = description or f"Transfer to {agent_name} specialist"
    
    @tool(name, description=description)
    def handoff_tool(
        state: InjectedState,
        tool_call_id: str,
    ) -> Command:
        tool_message = {
            "role": "tool",
            "content": f"Successfully transferred to {agent_name}",
            "name": name,
            "tool_call_id": tool_call_id,
        }
        return Command(
            goto=agent_name,
            update={"messages": state["messages"] + [tool_message]},
            graph=Command.PARENT,
        )
    return handoff_tool

# Master synthesis prompt
ORACLE_SYNTHESIS_PROMPT = """
You are the Solopreneur Oracle, a master AI orchestrator for developers and entrepreneurs.
You coordinate multiple domain specialists to provide comprehensive, actionable insights.

Current Analysis Context:
{context}

Domain Intelligence Gathered:
{intelligence_data}

Quality Thresholds:
- Minimum confidence: {min_confidence}
- Technical feasibility: {tech_feasibility}
- Personal sustainability: {personal_sustainability}

Your task is to synthesize all domain intelligence into a cohesive strategy that balances:
1. Technical excellence and innovation opportunities
2. Personal energy and cognitive optimization
3. Learning efficiency and skill development
4. Workflow automation and productivity

Provide your synthesis in this structured format:
{
    "executive_summary": "2-3 sentence overview of key insights and recommendations",
    "confidence_score": 0.85,
    "domain_synthesis": {
        "technical": {
            "key_findings": ["finding1", "finding2"],
            "opportunities": ["opportunity1", "opportunity2"],
            "risks": ["risk1", "risk2"],
            "priority_actions": ["action1", "action2"]
        },
        "personal": {
            "energy_insights": "current energy state and optimization potential",
            "cognitive_load_assessment": "current vs optimal cognitive load",
            "sustainability_score": 0.75,
            "optimization_strategies": ["strategy1", "strategy2"]
        },
        "learning": {
            "skill_gaps": ["gap1", "gap2"],
            "learning_velocity": "current learning speed assessment",
            "recommended_focus": ["skill1", "skill2"],
            "resources": ["resource1", "resource2"]
        },
        "workflow": {
            "bottlenecks": ["bottleneck1", "bottleneck2"],
            "automation_opportunities": ["opportunity1", "opportunity2"],
            "tool_recommendations": ["tool1", "tool2"],
            "efficiency_gains": "estimated productivity improvement"
        }
    },
    "integrated_strategy": {
        "immediate_actions": [
            {"action": "action1", "domain": "technical", "impact": "high"},
            {"action": "action2", "domain": "personal", "impact": "medium"}
        ],
        "weekly_plan": {
            "monday": {"focus": "deep work", "tasks": ["task1", "task2"]},
            "tuesday": {"focus": "learning", "tasks": ["task3", "task4"]}
        },
        "monthly_goals": ["goal1", "goal2", "goal3"],
        "success_metrics": ["metric1", "metric2"]
    },
    "risk_mitigation": {
        "identified_risks": ["risk1", "risk2"],
        "mitigation_strategies": ["strategy1", "strategy2"],
        "contingency_plans": ["plan1", "plan2"]
    },
    "next_analysis_triggers": ["trigger1", "trigger2"]
}
"""

class OracleState(MessagesState):
    """Extended state for Oracle orchestration."""
    intelligence_data: Dict[str, Any]
    active_domains: List[str]
    quality_scores: Dict[str, float]
    synthesis_complete: bool
    last_active_agent: str

class SolopreneurOracleAgent(BaseAgent):
    """
    Master Oracle agent using LangGraph for sophisticated orchestration.
    Implements parallel domain analysis with quality validation.
    """
    
    def __init__(self):
        init_api_key()
        super().__init__(
            agent_name="Solopreneur Oracle",
            description="Master AI orchestrator for developer/entrepreneur intelligence",
            content_types=["text", "text/plain", "application/json"],
        )
        
        self.quality_thresholds = {
            "min_confidence": 0.75,
            "tech_feasibility": 0.8,
            "personal_sustainability": 0.7,
            "cross_domain_coherence": 0.65
        }
        
        # Initialize LangGraph components
        self.graph = self._build_oracle_graph()
        
    def _build_oracle_graph(self) -> StateGraph:
        """Build the Oracle's LangGraph for multi-agent orchestration."""
        
        # Create domain specialist agents with handoff capabilities
        technical_handoff = create_handoff_tool(
            agent_name="technical_specialist",
            description="Transfer to Technical Intelligence specialist for AI research and tech analysis"
        )
        
        personal_handoff = create_handoff_tool(
            agent_name="personal_specialist", 
            description="Transfer to Personal Optimization specialist for energy and productivity"
        )
        
        learning_handoff = create_handoff_tool(
            agent_name="learning_specialist",
            description="Transfer to Learning Enhancement specialist for skill development"
        )
        
        workflow_handoff = create_handoff_tool(
            agent_name="workflow_specialist",
            description="Transfer to Workflow Integration specialist for automation"
        )
        
        # Initialize Oracle supervisor with all handoff tools
        oracle_tools = [
            technical_handoff,
            personal_handoff,
            learning_handoff,
            workflow_handoff
        ]
        
        oracle_supervisor = create_react_agent(
            model=genai.Client().models.get("gemini-2.0-flash"),
            tools=oracle_tools,
            prompt="""You are the Solopreneur Oracle supervisor. 
            Analyze the user's request and delegate to appropriate domain specialists.
            Always gather intelligence from multiple relevant domains before synthesis."""
        )
        
        # Define node functions
        async def oracle_supervisor_node(state: OracleState) -> Command:
            """Oracle supervisor decides which specialists to consult."""
            response = await oracle_supervisor.ainvoke(state)
            
            # Track active domains based on tool calls
            active_domains = []
            for msg in response.get("messages", []):
                if hasattr(msg, "tool_calls"):
                    for tool_call in msg.tool_calls:
                        if "technical" in tool_call["name"]:
                            active_domains.append("technical")
                        elif "personal" in tool_call["name"]:
                            active_domains.append("personal")
                        elif "learning" in tool_call["name"]:
                            active_domains.append("learning")
                        elif "workflow" in tool_call["name"]:
                            active_domains.append("workflow")
            
            update = {
                **response,
                "active_domains": active_domains,
                "last_active_agent": "oracle_supervisor"
            }
            
            # If no specialists called, go to synthesis
            if not active_domains:
                return Command(update=update, goto="synthesis")
            
            return Command(update=update)
        
        async def technical_specialist_node(state: OracleState) -> Command:
            """Technical intelligence specialist analyzes tech trends and research."""
            # Simulate technical analysis
            technical_intelligence = {
                "latest_research": ["LLM scaling laws", "Multi-agent systems"],
                "relevant_repos": ["langchain", "autogen", "crew-ai"],
                "implementation_priority": ["Multi-agent orchestration", "RAG optimization"],
                "technical_risks": ["API rate limits", "Model context limitations"]
            }
            
            state["intelligence_data"]["technical"] = technical_intelligence
            state["quality_scores"]["technical"] = 0.85
            
            return Command(
                goto="oracle_supervisor",
                update={
                    "intelligence_data": state["intelligence_data"],
                    "quality_scores": state["quality_scores"],
                    "messages": state["messages"] + [AIMessage(
                        content=f"Technical analysis complete. Found {len(technical_intelligence['latest_research'])} relevant research areas."
                    )]
                }
            )
        
        async def personal_specialist_node(state: OracleState) -> Command:
            """Personal optimization specialist analyzes energy and productivity."""
            # Simulate personal optimization analysis
            personal_intelligence = {
                "energy_pattern": "Peak performance 9-11 AM, 3-5 PM",
                "cognitive_load": "Currently at 65% capacity",
                "optimization_strategies": ["Time-blocking", "Pomodoro for learning"],
                "sustainability_score": 0.72
            }
            
            state["intelligence_data"]["personal"] = personal_intelligence
            state["quality_scores"]["personal"] = 0.78
            
            return Command(
                goto="oracle_supervisor",
                update={
                    "intelligence_data": state["intelligence_data"],
                    "quality_scores": state["quality_scores"],
                    "messages": state["messages"] + [AIMessage(
                        content="Personal optimization analysis complete. Energy patterns identified."
                    )]
                }
            )
        
        async def learning_specialist_node(state: OracleState) -> Command:
            """Learning enhancement specialist analyzes skill development."""
            # Simulate learning analysis
            learning_intelligence = {
                "skill_gaps": ["Advanced LangGraph patterns", "Distributed systems"],
                "learning_velocity": "2.3x baseline when using spaced repetition",
                "recommended_resources": ["LangGraph documentation", "System design course"],
                "optimal_learning_schedule": "45min sessions with 15min breaks"
            }
            
            state["intelligence_data"]["learning"] = learning_intelligence
            state["quality_scores"]["learning"] = 0.82
            
            return Command(
                goto="oracle_supervisor",
                update={
                    "intelligence_data": state["intelligence_data"],
                    "quality_scores": state["quality_scores"],
                    "messages": state["messages"] + [AIMessage(
                        content="Learning analysis complete. Skill development path identified."
                    )]
                }
            )
        
        async def workflow_specialist_node(state: OracleState) -> Command:
            """Workflow integration specialist analyzes automation opportunities."""
            # Simulate workflow analysis
            workflow_intelligence = {
                "automation_opportunities": ["Code review automation", "Test generation"],
                "tool_integrations": ["VS Code + Copilot", "pytest + coverage"],
                "bottlenecks": ["Manual deployment process", "Repetitive documentation"],
                "estimated_time_savings": "8 hours/week"
            }
            
            state["intelligence_data"]["workflow"] = workflow_intelligence
            state["quality_scores"]["workflow"] = 0.80
            
            return Command(
                goto="oracle_supervisor",
                update={
                    "intelligence_data": state["intelligence_data"],
                    "quality_scores": state["quality_scores"],
                    "messages": state["messages"] + [AIMessage(
                        content="Workflow analysis complete. Automation opportunities identified."
                    )]
                }
            )
        
        async def synthesis_node(state: OracleState) -> Command:
            """Synthesize all domain intelligence into coherent strategy."""
            client = genai.Client()
            
            # Generate comprehensive synthesis
            prompt = ORACLE_SYNTHESIS_PROMPT.format(
                context=json.dumps({"query": state["messages"][-1].content}),
                intelligence_data=json.dumps(state.get("intelligence_data", {})),
                min_confidence=self.quality_thresholds["min_confidence"],
                tech_feasibility=self.quality_thresholds["tech_feasibility"],
                personal_sustainability=self.quality_thresholds["personal_sustainability"]
            )
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config={"temperature": 0.1, "response_mime_type": "application/json"}
            )
            
            synthesis = json.loads(response.text)
            
            # Validate synthesis quality
            if synthesis.get("confidence_score", 0) < self.quality_thresholds["min_confidence"]:
                # Request additional analysis from specific domains
                return Command(
                    goto="oracle_supervisor",
                    update={
                        "messages": state["messages"] + [AIMessage(
                            content="Synthesis confidence below threshold. Gathering additional intelligence..."
                        )]
                    }
                )
            
            return Command(
                update={
                    "messages": state["messages"] + [AIMessage(
                        content=json.dumps(synthesis, indent=2)
                    )],
                    "synthesis_complete": True
                },
                goto=END
            )
        
        # Build the graph
        builder = StateGraph(OracleState)
        
        # Add nodes
        builder.add_node("oracle_supervisor", oracle_supervisor_node)
        builder.add_node("technical_specialist", technical_specialist_node)
        builder.add_node("personal_specialist", personal_specialist_node)
        builder.add_node("learning_specialist", learning_specialist_node)
        builder.add_node("workflow_specialist", workflow_specialist_node)
        builder.add_node("synthesis", synthesis_node)
        
        # Add edges
        builder.add_edge(START, "oracle_supervisor")
        
        # Specialists can be called from supervisor and return to it
        builder.add_edge("technical_specialist", "oracle_supervisor")
        builder.add_edge("personal_specialist", "oracle_supervisor")
        builder.add_edge("learning_specialist", "oracle_supervisor")
        builder.add_edge("workflow_specialist", "oracle_supervisor")
        
        # Supervisor can go to synthesis
        builder.add_conditional_edges(
            "oracle_supervisor",
            lambda state: "synthesis" if len(state.get("intelligence_data", {})) >= 2 else "continue",
            {
                "synthesis": "synthesis",
                "continue": END  # Placeholder, actual routing handled by handoffs
            }
        )
        
        return builder.compile()
    
    async def stream(
        self, 
        query: str, 
        context_id: str, 
        task_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        """Execute the Oracle workflow with streaming updates."""
        logger.info(f"Solopreneur Oracle analyzing: {query}")
        
        try:
            # Initialize state
            initial_state = {
                "messages": [HumanMessage(content=query)],
                "intelligence_data": {},
                "active_domains": [],
                "quality_scores": {},
                "synthesis_complete": False,
                "last_active_agent": "user"
            }
            
            # Stream execution updates
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "🔮 Solopreneur Oracle: Initiating multi-domain analysis..."
            }
            
            # Execute the graph
            config = {
                "configurable": {
                    "thread_id": context_id,
                    "checkpoint_ns": task_id
                }
            }
            
            async for event in self.graph.astream(initial_state, config):
                # Stream progress updates
                for node_name, node_output in event.items():
                    if node_name == "oracle_supervisor":
                        yield {
                            "is_task_complete": False,
                            "require_user_input": False,
                            "content": "🎯 Oracle: Coordinating domain specialists..."
                        }
                    elif "specialist" in node_name:
                        domain = node_name.split("_")[0].title()
                        yield {
                            "is_task_complete": False,
                            "require_user_input": False,
                            "content": f"🔍 {domain} Specialist: Analyzing {domain.lower()} factors..."
                        }
                    elif node_name == "synthesis":
                        yield {
                            "is_task_complete": False,
                            "require_user_input": False,
                            "content": "🧬 Oracle: Synthesizing multi-domain intelligence..."
                        }
            
            # Get final state
            final_state = await self.graph.aget_state(config)
            
            if final_state.values.get("synthesis_complete"):
                # Extract synthesis from messages
                synthesis_message = None
                for msg in reversed(final_state.values["messages"]):
                    if isinstance(msg, AIMessage) and msg.content.startswith("{"):
                        synthesis_message = msg.content
                        break
                
                if synthesis_message:
                    yield {
                        "is_task_complete": True,
                        "require_user_input": False,
                        "response_type": "data",
                        "content": json.loads(synthesis_message)
                    }
                else:
                    yield {
                        "is_task_complete": True,
                        "require_user_input": False,
                        "content": "Oracle analysis complete. Please review the recommendations above."
                    }
            else:
                yield {
                    "is_task_complete": True,
                    "require_user_input": True,
                    "content": "Oracle requires additional information. Please provide more context about your specific needs."
                }
                
        except Exception as e:
            logger.error(f"Oracle error: {e}", exc_info=True)
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": f"🚨 Oracle encountered an error: {str(e)}"
            }