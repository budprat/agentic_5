# type: ignore

import logging

from typing import Any, AsyncIterable, Dict, Literal

from a2a_mcp.common import prompts
from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.types import TaskList
from a2a_mcp.common.utils import init_api_key
from langchain_core.messages import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field


memory = MemorySaver()
logger = logging.getLogger(__name__)


class NexusResponseFormat(BaseModel):
    """Respond to the user in this format for research tasks."""

    status: Literal['input_required', 'completed', 'error'] = 'input_required'
    question: str = Field(
        description='Input needed from the user to generate the research plan'
    )
    content: TaskList = Field(
        description='List of research tasks when the plan is generated'
    )


class LangGraphNexusPlanner(BaseAgent):
    """Nexus Planner Agent backed by LangGraph for transdisciplinary research."""

    def __init__(self):
        init_api_key()

        logger.info('Initializing LangGraphNexusPlanner')

        super().__init__(
            agent_name='NexusPlannerAgent',
            description='Breakdown complex research requests into actionable transdisciplinary tasks',
            content_types=['text', 'text/plain'],
        )

        self.model = ChatGoogleGenerativeAI(
            model='gemini-2.0-flash', temperature=0.0
        )

        self.graph = create_react_agent(
            self.model,
            checkpointer=memory,
            prompt=prompts.NEXUS_PLANNER_COT_INSTRUCTIONS,
            response_format=NexusResponseFormat,
            tools=[],
        )

    def invoke(self, query, sessionId) -> str:
        config = {'configurable': {'thread_id': sessionId}}
        self.graph.invoke({'messages': [('user', query)]}, config)
        return self.get_agent_response(config)

    async def stream(
        self, query, sessionId, task_id
    ) -> AsyncIterable[Dict[str, Any]]:
        inputs = {'messages': [('user', query)]}
        config = {'configurable': {'thread_id': sessionId}}

        logger.info(
            f'Running LangGraphNexusPlanner stream for session {sessionId} {task_id} with input {query}'
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
            structured_response, NexusResponseFormat
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
            elif structured_response.status == 'error':
                return {
                    'response_type': 'text',
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': structured_response.question,
                }
            elif structured_response.status == 'completed':
                return {
                    'response_type': 'data',
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': structured_response.content.model_dump(),
                }
        return {
            'is_task_complete': False,
            'require_user_input': True,
            'content': 'We are unable to process your research request at the moment. Please try again.',
        }