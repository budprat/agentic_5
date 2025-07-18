"""
ABOUTME: Literature Review Agent using Google ADK with MCP integration
ABOUTME: Analyzes academic papers using Firecrawl, Brightdata, and Context7 MCPs
"""

import os
import json
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

from .schemas import LiteratureReviewResult
from .prompts import LITERATURE_REVIEW_PROMPT
from .tools import (
    analyze_paper_relevance,
    extract_methodology,
    build_citation_network,
    identify_research_gaps,
    generate_synthesis,
    extract_paper_metadata
)

# Load environment variables
load_dotenv()

# Create Literature Review Agent with MCP tools
literature_review_agent = LlmAgent(
    name="literature_review_agent",
    model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
    instruction=LITERATURE_REVIEW_PROMPT,
    tools=[
        # Firecrawl MCP for scraping research papers
        MCPToolset(
            connection_params=StdioServerParameters(
                command="npx",
                args=["-y", "@firecrawl/mcp-server"],
                env={"FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY")},
            )
        ),
        # Brightdata MCP for academic database searches
        MCPToolset(
            connection_params=StdioServerParameters(
                command="npx",
                args=["-y", "@brightdata/mcp-server"],
                env={"BRIGHTDATA_API_KEY": os.getenv("BRIGHTDATA_API_KEY")},
            )
        ),
        # Context7 MCP for technical documentation
        MCPToolset(
            connection_params=StdioServerParameters(
                command="npx",
                args=["-y", "@context7/mcp-server"],
                env={},  # Context7 doesn't require API key
            )
        ),
        # Custom analysis tools
        analyze_paper_relevance,
        extract_methodology,
        build_citation_network,
        identify_research_gaps,
        generate_synthesis,
        extract_paper_metadata
    ],
    output_schema=LiteratureReviewResult,
    output_key="literature_review",
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    description="""Advanced literature review agent that:
    - Searches multiple academic databases simultaneously
    - Analyzes papers for relevance and quality
    - Extracts key insights and methodologies
    - Identifies research gaps and trends
    - Builds citation networks
    - Generates comprehensive synthesis"""
)