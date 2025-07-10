#!/usr/bin/env python3
# ABOUTME: Direct start of Oracle agent to see startup errors
# ABOUTME: Bypasses the __main__.py to isolate issues

import asyncio
import json
import os
from a2a.server.apps.jsonrpc.starlette_app import A2AStarletteApplication
from a2a.server.request_handlers.default_request_handler import DefaultRequestHandler
from a2a_mcp.common.agent_executor import GenericAgentExecutor
from a2a_mcp.agents.solopreneur_oracle.solopreneur_oracle_agent import SolopreneurOracleAgent
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard
import uvicorn

# Set environment
os.environ['GOOGLE_API_KEY'] = 'AIzaSyBGUGI7fZQT06Hl49OKcTMS5BgPEqC8fvY'

# Load agent card
with open('agent_cards/solopreneur_oracle_agent.json', 'r') as f:
    agent_card_data = json.load(f)
    agent_card = AgentCard(**agent_card_data)

print(f"Loading agent: {agent_card.name}")

# Create agent instance
agent = SolopreneurOracleAgent()
print(f"Agent created: {agent.agent_name}")

# Create executor and handler
task_store = InMemoryTaskStore()
agent_executor = GenericAgentExecutor(agent)
request_handler = DefaultRequestHandler(agent_executor, task_store)

# Create A2A application
app = A2AStarletteApplication(
    agent_card=agent_card,
    http_handler=request_handler
)

# Build Starlette app
starlette_app = app.build()

print(f"Starting server on port 10901...")

# Run server
if __name__ == "__main__":
    uvicorn.run(starlette_app, host="0.0.0.0", port=10901)