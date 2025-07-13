# ABOUTME: Generic planner agent for task decomposition across any domain
# ABOUTME: Framework V2.0 compliant planner using LangGraph and generic task types

# type: ignore

import logging

from collections.abc import AsyncIterable
from typing import Any, Literal, Optional

from a2a_mcp.common import prompts
from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.types import GenericTaskList
from a2a_mcp.common.utils import init_api_key
from langchain_core.messages import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field


memory = MemorySaver()
logger = logging.getLogger(__name__)


class GenericResponseFormat(BaseModel):
    """Generic response format for any domain planner."""

    status: Literal['input_required', 'completed', 'error'] = 'input_required'
    question: str = Field(
        description='Input needed from the user to generate the plan'
    )
    content: GenericTaskList = Field(
        description='List of tasks when the plan is generated'
    )


class GenericPlannerAgent(BaseAgent):
    """Generic Planner Agent backed by LangGraph for any domain."""

    def __init__(self, domain: str = "General", agent_name: str = None, custom_prompt: Optional[str] = None):
        init_api_key()

        agent_name = agent_name or f"{domain} Planner Agent"
        logger.info(f'Initializing {agent_name}')

        super().__init__(
            agent_name=agent_name,
            description=f'Breakdown {domain.lower()} user requests into executable tasks',
            content_types=['text', 'text/plain'],
        )

        self.domain = domain
        self.model = ChatGoogleGenerativeAI(
            model='gemini-2.0-flash', temperature=0.0
        )

        # Use custom prompt or default to generic planner instructions
        planning_prompt = custom_prompt or prompts.GENERIC_PLANNER_COT_INSTRUCTIONS

        self.graph = create_react_agent(
            self.model,
            checkpointer=memory,
            prompt=planning_prompt,
            response_format=GenericResponseFormat,
            tools=[],
        )

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
        config = {'configurable': {'thread_id': sessionId}}
        self.graph.invoke({'messages': [('user', query)]}, config)
        return self.get_agent_response(config)

    async def stream(
        self, query, sessionId, task_id
    ) -> AsyncIterable[dict[str, Any]]:
        inputs = {'messages': [('user', query)]}
        config = {'configurable': {'thread_id': sessionId}}

        logger.info(
            f'Running {self.agent_name} stream for session {sessionId} {task_id} with input {query}'
        )

        for item in self.graph.stream(inputs, config, stream_mode='values'):
            message = item['messages'][-1]
            if isinstance(message, AIMessage):
                yield {
                    'response_type': 'text',
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': message.content,
                }
        yield self.get_agent_response(config)

    def get_agent_response(self, config):
        current_state = self.graph.get_state(config)
        structured_response = current_state.values.get('structured_response')
        if structured_response and isinstance(
            structured_response, GenericResponseFormat
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
            'is_task_complete': False,
            'require_user_input': True,
            'content': 'We are unable to process your request at the moment. Please try again.',
        }