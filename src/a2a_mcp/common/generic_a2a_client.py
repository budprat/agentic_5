#!/usr/bin/env python3
# ABOUTME: Generic A2A JSON-RPC protocol compliant client template for Framework V2.0
# ABOUTME: Base class that domains can extend with their specific display and business logic

import asyncio
import aiohttp
import json
import uuid
import sys
import os
from typing import Dict, Any, Optional, AsyncIterator
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Framework V2.0 types import with fallback
try:
    from a2a_mcp.common.types import AgentResponse
except ImportError:
    # Fallback if types not available
    AgentResponse = None

console = Console()

class GenericA2AClient:
    """
    Generic A2A Protocol compliant client template for Framework V2.0.
    
    This base class provides:
    - Core A2A JSON-RPC protocol handling
    - Stream processing logic
    - Basic progress display
    - Generic query methods
    
    Domains should inherit from this and override display methods for their specific needs.
    """
    
    def __init__(self, orchestrator_url: str = "http://localhost:10901", domain_name: str = "Generic"):
        self.orchestrator_url = orchestrator_url
        self.domain_name = domain_name
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def send_message(self, query: str, stream: bool = True) -> AsyncIterator[Dict[str, Any]]:
        """Send message using A2A JSON-RPC protocol."""
        
        # Generate IDs
        request_id = str(uuid.uuid4())
        message_id = str(uuid.uuid4())
        
        # Create A2A JSON-RPC request
        json_rpc_request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "message/stream" if stream else "message/send",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [
                        {
                            "kind": "text",
                            "text": query
                        }
                    ],
                    "messageId": message_id,
                    "kind": "message"
                },
                "metadata": {}
            }
        }
        
        timeout = aiohttp.ClientTimeout(total=180)  # 3 minute timeout
        
        async with self.session.post(
            self.orchestrator_url,
            json=json_rpc_request,
            headers={"Content-Type": "application/json"},
            timeout=timeout
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                yield {
                    "error": f"HTTP {response.status}: {error_text}",
                    "is_task_complete": True
                }
                return
            
            content_type = response.headers.get('Content-Type', '')
            
            if stream and 'text/event-stream' in content_type:
                # Handle SSE stream
                task_info = {}
                
                async for line in response.content:
                    if line:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data: '):
                            data = line_str[6:]
                            try:
                                event = json.loads(data)
                                
                                if 'result' in event and isinstance(event['result'], dict):
                                    result = event['result']
                                    
                                    # Initial task creation
                                    if result.get('kind') == 'task':
                                        task_info = {
                                            "task_id": result.get('id'),
                                            "context_id": result.get('contextId'),
                                            "status": result.get('status', {}).get('state')
                                        }
                                        yield {
                                            "type": "task_created",
                                            "content": f"Task created: {task_info['task_id']}",
                                            "task_info": task_info,
                                            "is_task_complete": False
                                        }
                                    
                                    # Status updates
                                    elif result.get('kind') == 'status-update':
                                        status = result.get('status', {})
                                        yield {
                                            "type": "status_update",
                                            "content": f"Status: {status.get('state')}",
                                            "status": status,
                                            "is_task_complete": result.get('final', False)
                                        }
                                    
                                    # Message responses
                                    elif result.get('kind') == 'streaming-response':
                                        message = result.get('message', {})
                                        parts = message.get('parts', [])
                                        
                                        for part in parts:
                                            if part.get('kind') == 'text':
                                                yield {
                                                    "type": "message",
                                                    "content": part.get('text'),
                                                    "is_task_complete": result.get('final', False),
                                                    "response_type": "data" if result.get('final') else "stream"
                                                }
                                    
                                    # Artifact updates
                                    elif result.get('kind') == 'artifact-update':
                                        artifact = result.get('artifact', {})
                                        parts = artifact.get('parts', [])
                                        
                                        for part in parts:
                                            if part.get('kind') == 'text':
                                                yield {
                                                    "type": "artifact",
                                                    "content": part.get('text'),
                                                    "append": result.get('append', False),
                                                    "is_task_complete": result.get('lastChunk', False)
                                                }
                                
                            except json.JSONDecodeError as e:
                                console.print(f"[yellow]Failed to parse SSE data: {e}[/yellow]")
            else:
                # Regular JSON response (non-streaming)
                result = await response.json()
                
                if 'error' in result:
                    yield {
                        "error": result['error'],
                        "is_task_complete": True
                    }
                elif 'result' in result:
                    # Handle message or task response
                    response_data = result['result']
                    
                    if response_data.get('kind') == 'message':
                        # Direct message response
                        parts = response_data.get('parts', [])
                        for part in parts:
                            if part.get('kind') == 'text':
                                yield {
                                    "type": "message",
                                    "content": part.get('text'),
                                    "is_task_complete": True,
                                    "response_type": "data"
                                }
                    elif response_data.get('kind') == 'task':
                        # Task response with results
                        yield {
                            "type": "task_complete",
                            "content": response_data,
                            "is_task_complete": True,
                            "response_type": "data"
                        }
    
    async def query_agent(self, query: str, show_progress: bool = True) -> Dict[str, Any]:
        """
        Query the agent and return structured result.
        This is the main method domains should override for custom behavior.
        """
        
        if show_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"Querying {self.domain_name} Agent...", total=None)
                
                result = None
                async for update in self.send_message(query, stream=True):
                    if update.get("error"):
                        progress.update(task, description=f"Error: {update['error']}")
                        return {"error": update["error"]}
                    
                    content = update.get("content", "")
                    
                    if update.get("type") == "task_created":
                        progress.update(task, description="Task created, processing...")
                    elif update.get("type") == "status_update":
                        progress.update(task, description=f"Status: {update.get('status', {}).get('state', 'processing')}")
                    elif update.get("type") in ["message", "artifact"]:
                        if update.get("is_task_complete"):
                            progress.update(task, completed=100, description="Analysis complete")
                            result = content
                        else:
                            progress.update(task, description=content[:50] + "..." if len(content) > 50 else content)
                
                return self._parse_result(result)
        else:
            # No progress display
            result = None
            async for update in self.send_message(query, stream=True):
                if update.get("error"):
                    return {"error": update["error"]}
                
                if update.get("is_task_complete") and update.get("type") in ["message", "artifact"]:
                    result = update.get("content")
            
            return self._parse_result(result)
    
    def _parse_result(self, result: Any) -> Dict[str, Any]:
        """Parse the result into structured format. Domains can override this."""
        if not result:
            return {"error": "No result received"}
        
        if isinstance(result, str):
            try:
                # Try to parse as JSON
                return json.loads(result)
            except json.JSONDecodeError:
                # Return as plain text
                return {"content": result, "type": "text"}
        
        return result
    
    def display_result(self, result: Dict[str, Any]) -> None:
        """
        Display result in a formatted way.
        Domains should override this method for custom display formatting.
        """
        
        if "error" in result:
            console.print(f"[red]Error: {result['error']}[/red]")
            return
        
        if result.get("type") == "text":
            console.print(Panel(result["content"], title=f"{self.domain_name} Response", style="blue"))
            return
        
        # Generic structured display
        console.print(Panel(
            json.dumps(result, indent=2),
            title=f"{self.domain_name} Analysis",
            style="green"
        ))
    
    def get_help_content(self) -> str:
        """
        Get help content for the domain.
        Domains should override this to provide domain-specific help.
        """
        return f"""
**{self.domain_name} Agent Help**

This is a generic A2A client. Available commands:
• Type your query or question
• Type 'help' for this help
• Type 'quit' to exit

Example: "Analyze this request..."
"""


async def interactive_session(client_class=None, orchestrator_url: str = "http://localhost:10901", domain_name: str = "Generic"):
    """
    Run an interactive session with the A2A-compliant agent.
    Domains can pass their custom client class.
    """
    
    if client_class is None:
        client_class = GenericA2AClient
    
    console.print(Panel(
        f"🤖 [bold magenta]{domain_name} AI Agent[/bold magenta] 🤖\\n\\n"
        f"Your AI-powered {domain_name.lower()} assistant\\n"
        "Using A2A JSON-RPC Protocol\\n\\n"
        "Type 'help' for commands or 'quit' to exit",
        style="bold blue"
    ))
    
    async with client_class(orchestrator_url, domain_name) as client:
        while True:
            try:
                query = console.input("\\n[bold cyan]You:[/bold cyan] ")
                
                if query.lower() in ['quit', 'exit', 'q']:
                    console.print(f"[yellow]Goodbye! Have a great day! 🚀[/yellow]")
                    break
                
                if query.lower() == 'help':
                    console.print(Panel(
                        client.get_help_content(),
                        title="Help",
                        style="green"
                    ))
                    continue
                
                # Query the agent
                result = await client.query_agent(query)
                
                # Display results
                console.print(f"\\n[bold magenta]{domain_name} Agent:[/bold magenta]")
                client.display_result(result)
                
            except KeyboardInterrupt:
                console.print("\\n[yellow]Interrupted. Type 'quit' to exit.[/yellow]")
            except Exception as e:
                console.print(f"\\n[red]Error: {e}[/red]")


if __name__ == "__main__":
    import sys
    
    # Example usage - domains would create their own main sections
    if len(sys.argv) > 1:
        domain_name = sys.argv[1]
    else:
        domain_name = "Generic"
    
    # Run interactive session
    asyncio.run(interactive_session(domain_name=domain_name))