#!/usr/bin/env python3
# ABOUTME: A2A JSON-RPC protocol compliant client for AI Solopreneur Oracle System
# ABOUTME: Uses proper message/send and message/stream methods per A2A specification

import asyncio
import aiohttp
import json
import uuid
from typing import Dict, Any, Optional, AsyncIterator
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.markdown import Markdown

console = Console()

class A2ASolopreneurClient:
    """A2A Protocol compliant client for AI Solopreneur Oracle System."""
    
    def __init__(self, orchestrator_url: str = "http://localhost:10901"):
        self.orchestrator_url = orchestrator_url
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
    
    async def query_oracle(self, query: str, show_progress: bool = True) -> Dict[str, Any]:
        """Query the Solopreneur Oracle and return structured result."""
        
        if show_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Querying Solopreneur Oracle...", total=None)
                
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
        """Parse the result into structured format."""
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
    
    def display_analysis(self, analysis: Dict[str, Any]) -> None:
        """Display analysis results in a formatted way."""
        
        if "error" in analysis:
            console.print(f"[red]Error: {analysis['error']}[/red]")
            return
        
        if analysis.get("type") == "text":
            console.print(Panel(analysis["content"], title="Oracle Response", style="blue"))
            return
        
        # Display structured analysis
        if "executive_summary" in analysis:
            console.print(Panel(
                f"{analysis['executive_summary']}\n\n"
                f"Confidence: {analysis.get('confidence_score', 0)*100:.0f}%",
                title="📋 Executive Summary",
                style="bold green"
            ))
        
        # Technical Assessment
        if "technical_assessment" in analysis:
            tech = analysis["technical_assessment"]
            table = Table(title="🔧 Technical Assessment", show_header=True)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="white")
            
            table.add_row("Feasibility", f"{tech.get('feasibility_score', 0)}%")
            table.add_row("Complexity", tech.get('implementation_complexity', 'N/A'))
            table.add_row("Architecture", ', '.join(tech.get('architecture_recommendations', [])))
            
            if tech.get('technical_risks'):
                table.add_row("Risks", ', '.join(tech['technical_risks'][:2]))
            
            console.print(table)
        
        # Personal Optimization
        if "personal_optimization" in analysis:
            personal = analysis["personal_optimization"]
            table = Table(title="🧠 Personal Optimization", show_header=True)
            table.add_column("Aspect", style="cyan")
            table.add_column("Assessment", style="white")
            
            table.add_row("Energy Impact", personal.get('energy_impact', 'N/A'))
            table.add_row("Cognitive Load", personal.get('cognitive_load', 'N/A'))
            table.add_row("Sustainability", f"{personal.get('sustainability_score', 0)}%")
            
            console.print(table)
        
        # Strategic Insights
        if "strategic_insights" in analysis:
            console.print("\n💡 [bold]Key Insights:[/bold]")
            for insight in analysis["strategic_insights"][:3]:
                confidence = insight.get('confidence', 0) * 100
                console.print(f"  • {insight.get('insight', 'N/A')} [dim]({confidence:.0f}% confidence)[/dim]")
        
        # Action Plan
        if "action_plan" in analysis:
            plan = analysis["action_plan"]
            console.print("\n📅 [bold]Action Plan:[/bold]")
            
            if plan.get("immediate_actions"):
                console.print("  [yellow]Immediate:[/yellow]")
                for action in plan["immediate_actions"][:2]:
                    console.print(f"    • {action}")
            
            if plan.get("short_term_goals"):
                console.print("  [cyan]Short-term:[/cyan]")
                for goal in plan["short_term_goals"][:2]:
                    console.print(f"    • {goal}")
            
            if plan.get("long_term_vision"):
                console.print(f"  [green]Vision:[/green] {plan['long_term_vision']}")


async def interactive_session():
    """Run an interactive session with the A2A-compliant Solopreneur Oracle."""
    console.print(Panel(
        "🔮 [bold magenta]AI Solopreneur Oracle[/bold magenta] 🔮\n\n"
        "Your AI-powered developer/entrepreneur assistant\n"
        "Using A2A JSON-RPC Protocol\n\n"
        "Type 'help' for commands or 'quit' to exit",
        style="bold blue"
    ))
    
    async with A2ASolopreneurClient() as client:
        while True:
            try:
                query = console.input("\n[bold cyan]You:[/bold cyan] ")
                
                if query.lower() in ['quit', 'exit', 'q']:
                    console.print("[yellow]Goodbye! May your code be bug-free! 🚀[/yellow]")
                    break
                
                if query.lower() == 'help':
                    console.print(Panel(
                        "**Available Queries:**\n\n"
                        "• Technical: Architecture, frameworks, AI/ML, development practices\n"
                        "• Personal: Work-life balance, productivity, energy management\n"
                        "• Learning: Skill development, learning paths, knowledge gaps\n"
                        "• Integration: Workflow optimization, tool integration, automation\n"
                        "• Strategic: Project planning, decision making, risk assessment\n\n"
                        "Example: 'How can I implement a scalable microservices architecture while maintaining productivity as a solo developer?'\n\n"
                        "Type 'quit' to exit",
                        title="Help",
                        style="green"
                    ))
                    continue
                
                # Query the oracle
                result = await client.query_oracle(query)
                
                # Display results
                console.print(f"\n[bold magenta]Oracle:[/bold magenta]")
                client.display_analysis(result)
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted. Type 'quit' to exit.[/yellow]")
            except Exception as e:
                console.print(f"\n[red]Error: {e}[/red]")


async def demo_queries():
    """Run demonstration queries."""
    demo_questions = [
        "How can I architect a scalable SaaS application while maintaining work-life balance as a solo developer?",
        "What's the most efficient way to learn Kubernetes for deploying my AI applications?",
        "How should I integrate MCP tools with my existing development workflow for maximum productivity?"
    ]
    
    async with A2ASolopreneurClient() as client:
        for i, question in enumerate(demo_questions, 1):
            console.print(f"\n[bold]Demo Query {i}:[/bold] {question}")
            
            result = await client.query_oracle(question)
            client.display_analysis(result)
            
            if i < len(demo_questions):
                console.print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        # Run demo queries
        asyncio.run(demo_queries())
    else:
        # Run interactive session
        asyncio.run(interactive_session())