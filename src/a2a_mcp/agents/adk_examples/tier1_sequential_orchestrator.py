# ABOUTME: Example Tier 1 Sequential Orchestrator implementation using Google ADK
# ABOUTME: Demonstrates how to create a production-ready orchestrator agent

import logging
from typing import List, Dict, Any, Optional
from google.adk.agents import SequentialAgent, Agent
from a2a_mcp.common.standardized_agent_base import StandardizedAgentBase
from a2a_mcp.common.quality_framework import QualityDomain

logger = logging.getLogger(__name__)


class ContentCreationOrchestrator(StandardizedAgentBase):
    """
    Tier 1 Sequential Orchestrator for content creation workflow.
    
    This example demonstrates:
    - Sequential execution of sub-agents
    - State passing between agents
    - Quality validation at each step
    - A2A protocol integration
    
    Workflow:
    1. Research Agent - Gathers information
    2. Writing Agent - Creates content
    3. Review Agent - Quality check
    4. Publishing Agent - Formats and publishes
    """
    
    def __init__(self):
        super().__init__(
            agent_name="ContentCreationOrchestrator",
            description="Orchestrates multi-stage content creation workflow",
            instructions="""
            You are a content creation orchestrator responsible for managing
            a complete content pipeline from research to publication.
            
            Your workflow stages:
            1. Research: Gather relevant information and sources
            2. Writing: Create high-quality content based on research
            3. Review: Ensure quality, accuracy, and compliance
            4. Publishing: Format and prepare for publication
            
            Coordinate these stages efficiently while maintaining quality.
            """,
            quality_config={
                "domain": QualityDomain.BUSINESS,
                "thresholds": {
                    "accuracy": 0.95,
                    "completeness": 0.9,
                    "relevance": 0.9
                }
            }
        )
        self.workflow_state = {}
        self.sub_agents = []
        
    async def init_agent(self):
        """Initialize the orchestrator with sub-agents."""
        await super().init_agent()
        
        # Create sub-agents for each stage
        self.sub_agents = [
            await self._create_research_agent(),
            await self._create_writing_agent(),
            await self._create_review_agent(),
            await self._create_publishing_agent()
        ]
        
        # Initialize ADK Sequential Agent
        self.adk_agent = SequentialAgent(
            name=self.agent_name,
            sub_agents=self.sub_agents,
            description=self.description,
            before_agent_callback=self._before_agent_callback,
            after_agent_callback=self._after_agent_callback
        )
        
        logger.info(f"{self.agent_name}: Initialized with {len(self.sub_agents)} sub-agents")
        
    async def _create_research_agent(self) -> Agent:
        """Create research sub-agent."""
        return Agent(
            name="ResearchAgent",
            model="gemini-2.0-flash",
            instruction="""
            You are a research specialist. Your task is to:
            1. Understand the content topic requirements
            2. Search for relevant information and sources
            3. Verify credibility of sources
            4. Compile research findings in a structured format
            
            Output a JSON with:
            - topic: The researched topic
            - key_points: List of main points discovered
            - sources: List of credible sources used
            - research_summary: Brief overview of findings
            """,
            tools=self.tools  # MCP tools for research
        )
        
    async def _create_writing_agent(self) -> Agent:
        """Create content writing sub-agent."""
        return Agent(
            name="WritingAgent",
            model="gemini-2.0-flash",
            instruction="""
            You are a professional content writer. Using the research provided:
            1. Create engaging, well-structured content
            2. Maintain consistent tone and style
            3. Include relevant examples and data
            4. Ensure proper flow and readability
            
            Input: Research findings from previous stage
            Output: Well-written content draft
            """,
            tools=[]  # Writing doesn't need external tools
        )
        
    async def _create_review_agent(self) -> Agent:
        """Create quality review sub-agent."""
        return Agent(
            name="ReviewAgent",
            model="gemini-2.0-flash",
            instruction="""
            You are a content quality reviewer. Your responsibilities:
            1. Check content accuracy against research
            2. Verify grammar, spelling, and style
            3. Ensure compliance with guidelines
            4. Suggest improvements if needed
            
            Output a JSON with:
            - quality_score: 0-100
            - issues_found: List of any issues
            - suggestions: Improvement recommendations
            - approved: Boolean approval status
            """,
            tools=[]
        )
        
    async def _create_publishing_agent(self) -> Agent:
        """Create publishing sub-agent."""
        return Agent(
            name="PublishingAgent",
            model="gemini-2.0-flash",
            instruction="""
            You are a content publishing specialist. Your tasks:
            1. Format content for the target platform
            2. Add appropriate metadata and tags
            3. Optimize for SEO if applicable
            4. Prepare final publication-ready version
            
            Output the final formatted content with all metadata.
            """,
            tools=self.tools  # May need tools for formatting
        )
        
    async def _before_agent_callback(self, agent_name: str, input_data: Any) -> Any:
        """Callback executed before each sub-agent."""
        logger.info(f"Starting {agent_name} with input: {type(input_data)}")
        
        # Add workflow state to input
        if isinstance(input_data, dict):
            input_data['workflow_state'] = self.workflow_state
        
        # Quality check before proceeding
        if agent_name == "PublishingAgent":
            # Ensure content was approved before publishing
            if not self.workflow_state.get('content_approved', False):
                raise ValueError("Content not approved for publication")
                
        return input_data
        
    async def _after_agent_callback(self, agent_name: str, output_data: Any) -> Any:
        """Callback executed after each sub-agent."""
        logger.info(f"Completed {agent_name}")
        
        # Update workflow state based on agent output
        if agent_name == "ResearchAgent":
            self.workflow_state['research_complete'] = True
            self.workflow_state['research_data'] = output_data
            
        elif agent_name == "WritingAgent":
            self.workflow_state['draft_complete'] = True
            self.workflow_state['draft_content'] = output_data
            
        elif agent_name == "ReviewAgent":
            # Parse review results
            if isinstance(output_data, dict):
                self.workflow_state['content_approved'] = output_data.get('approved', False)
                self.workflow_state['quality_score'] = output_data.get('quality_score', 0)
                
        elif agent_name == "PublishingAgent":
            self.workflow_state['published'] = True
            self.workflow_state['final_content'] = output_data
            
        return output_data
        
    async def execute_workflow(self, content_request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete content creation workflow."""
        try:
            # Initialize workflow state
            self.workflow_state = {
                'request': content_request,
                'started_at': datetime.now().isoformat(),
                'status': 'in_progress'
            }
            
            # Run the sequential workflow
            result = await self.adk_agent.run(content_request)
            
            # Prepare final response
            return {
                'success': True,
                'workflow_state': self.workflow_state,
                'final_content': self.workflow_state.get('final_content'),
                'quality_metrics': {
                    'quality_score': self.workflow_state.get('quality_score', 0),
                    'approved': self.workflow_state.get('content_approved', False)
                },
                'execution_time': self._calculate_execution_time()
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'workflow_state': self.workflow_state
            }
            
    def _calculate_execution_time(self) -> float:
        """Calculate total execution time."""
        from datetime import datetime
        start = datetime.fromisoformat(self.workflow_state['started_at'])
        return (datetime.now() - start).total_seconds()
        
    async def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status."""
        return {
            'agent_name': self.agent_name,
            'workflow_state': self.workflow_state,
            'sub_agents': [agent.name for agent in self.sub_agents],
            'a2a_enabled': self.a2a_client is not None
        }


# Example usage
async def main():
    """Example of using the Content Creation Orchestrator."""
    # Create orchestrator
    orchestrator = ContentCreationOrchestrator()
    await orchestrator.init_agent()
    
    # Execute workflow
    content_request = {
        'topic': 'Best Practices for Multi-Agent Systems',
        'content_type': 'blog_post',
        'target_audience': 'software developers',
        'word_count': 1500,
        'style': 'technical but accessible'
    }
    
    result = await orchestrator.execute_workflow(content_request)
    
    if result['success']:
        print(f"Content created successfully!")
        print(f"Quality Score: {result['quality_metrics']['quality_score']}")
        print(f"Execution Time: {result['execution_time']}s")
    else:
        print(f"Workflow failed: {result['error']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())