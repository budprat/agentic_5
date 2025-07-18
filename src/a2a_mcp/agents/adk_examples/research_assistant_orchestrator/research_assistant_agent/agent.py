"""
ABOUTME: Main Research Orchestrator Agent using Google ADK with advanced patterns
ABOUTME: Coordinates sub-agents for comprehensive research analysis
"""

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

from .sub_agents.literature_review_agent import literature_review_agent
from .callbacks import research_progress_callback, save_research_state_callback
from .prompts import RESEARCH_ORCHESTRATOR_PROMPT

# Load environment variables
load_dotenv()


# Future agents placeholder (to be implemented)
class PlaceholderAgent:
    """Placeholder for future agents"""
    def __init__(self, name):
        self.name = name


# Create placeholder agents for future implementation
patent_analyzer_agent = PlaceholderAgent("patent_analyzer_agent")
experiment_designer_agent = PlaceholderAgent("experiment_designer_agent")
data_synthesis_agent = PlaceholderAgent("data_synthesis_agent")
hypothesis_generator_agent = PlaceholderAgent("hypothesis_generator_agent")
grant_writer_agent = PlaceholderAgent("grant_writer_agent")
collaboration_finder_agent = PlaceholderAgent("collaboration_finder_agent")
publication_assistant_agent = PlaceholderAgent("publication_assistant_agent")


# Create Research Orchestrator with advanced patterns
research_orchestrator = LlmAgent(
    name="research_orchestrator",
    model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
    instruction=RESEARCH_ORCHESTRATOR_PROMPT,
    description="""Master research orchestrator that coordinates specialized agents for:
    - Literature review and analysis
    - Patent landscape mapping (coming soon)
    - Experiment design (coming soon)
    - Data synthesis (coming soon)
    - Hypothesis generation (coming soon)
    - Grant writing (coming soon)
    - Collaboration finding (coming soon)
    - Publication assistance (coming soon)
    
    Currently operational: Literature Review Agent
    """,
    sub_agents=[
        # Currently active agent
        literature_review_agent,
        
        # Future implementation - commented out for now
        # ParallelAgent(
        #     name="parallel_search",
        #     sub_agents=[
        #         literature_review_agent,
        #         patent_analyzer_agent,
        #     ],
        #     description="Parallel search across literature and patents"
        # ),
        # SequentialAgent(
        #     name="research_pipeline",
        #     sub_agents=[
        #         data_synthesis_agent,
        #         hypothesis_generator_agent,
        #         experiment_designer_agent,
        #     ],
        #     description="Sequential research development pipeline"
        # ),
    ],
    tools=[
        # Research Dashboard MCP (placeholder for future)
        # MCPToolset(
        #     connection_params=StdioServerParameters(
        #         command="npx",
        #         args=["-y", "@research/dashboard-mcp-server"],
        #         env={
        #             "DASHBOARD_URL": os.getenv("RESEARCH_DASHBOARD_URL", ""),
        #             "API_KEY": os.getenv("DASHBOARD_API_KEY", "")
        #         },
        #     )
        # ),
    ],
    before_agent_callback=research_progress_callback,
    after_agent_callback=save_research_state_callback,
)