"""
AI Solopreneur System Client - A2A JSON-RPC Protocol compliant client.
Supports both REST API and WebSocket connections for streaming updates.
"""

import asyncio
import json
import logging
import os
import sys
import uuid
from typing import Dict, Any, Optional, AsyncIterator
from datetime import datetime
import aiohttp
import websockets
from rich.console import Console
from rich.panel import Panel

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

def create_a2a_request(method: str, message: str, metadata: dict = None):
    """Standardize A2A request format - local copy for client."""
    return {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": method,  # Use 'message/send' or 'message/stream'
        "params": {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": message}],
                "messageId": str(uuid.uuid4()),
                "kind": "message"
            },
            "metadata": metadata or {}
        }
    }
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.markdown import Markdown

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

console = Console()

class SolopreneurClient:
    """Advanced client for AI Solopreneur System with WebSocket support."""
    
    def __init__(
        self, 
        orchestrator_url: str = "http://localhost:10901",
        ws_url: Optional[str] = "ws://localhost:10901/ws"
    ):
        self.orchestrator_url = orchestrator_url
        self.ws_url = ws_url
        self.session = None
        self.websocket = None
        self.context_id = f"solopreneur-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.websocket:
            await self.websocket.close()
        if self.session:
            await self.session.close()
    
    async def connect_websocket(self) -> None:
        """Establish WebSocket connection for real-time updates."""
        try:
            self.websocket = await websockets.connect(self.ws_url)
            console.print("[green]✓ WebSocket connected[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠ WebSocket connection failed: {e}[/yellow]")
            console.print("[yellow]Falling back to REST API[/yellow]")
    
    async def send_request(
        self, 
        query: str,
        stream: bool = True,
        include_metrics: bool = True
    ) -> AsyncIterator[Dict[str, Any]]:
        """Send request to Solopreneur Oracle using A2A JSON-RPC protocol."""
        
        # Create A2A JSON-RPC request using standardized format
        method = "message/stream" if stream else "message/send"
        metadata = {"include_metrics": include_metrics}
        
        request_data = create_a2a_request(
            method=method,
            message=query,
            metadata=metadata
        )
        
        # Try WebSocket first if available and streaming requested
        if stream and self.websocket:
            try:
                await self.websocket.send(json.dumps(request_data))
                
                async for message in self.websocket:
                    data = json.loads(message)
                    yield data
                    
                    if data.get("is_task_complete", False):
                        break
                        
            except Exception as e:
                console.print(f"[red]WebSocket error: {e}[/red]")
                console.print("[yellow]Switching to REST API[/yellow]")
                # Fall through to REST API
        
        # REST API with A2A JSON-RPC protocol
        async with self.session.post(
            self.orchestrator_url,  # Direct URL, no /stream endpoint
            json=request_data,
            headers={"Content-Type": "application/json"}
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
                # Handle SSE stream response
                async for line in response.content:
                    if line:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data: '):
                            data_str = line_str[6:]  # Remove 'data: ' prefix
                            try:
                                event = json.loads(data_str)
                                
                                if 'result' in event and isinstance(event['result'], dict):
                                    result = event['result']
                                    
                                    # Convert A2A format to client expected format
                                    if result.get('kind') == 'task':
                                        yield {
                                            "content": f"Task created: {result.get('id')}",
                                            "is_task_complete": False,
                                            "task_id": result.get('id'),
                                            "context_id": result.get('contextId')
                                        }
                                    elif result.get('kind') == 'status-update':
                                        yield {
                                            "content": f"Status: {result.get('status', {}).get('state')}",
                                            "is_task_complete": result.get('final', False)
                                        }
                                    elif result.get('kind') == 'streaming-response':
                                        message = result.get('message', {})
                                        parts = message.get('parts', [])
                                        for part in parts:
                                            if part.get('kind') == 'text':
                                                yield {
                                                    "content": part.get('text'),
                                                    "is_task_complete": result.get('final', False),
                                                    "response_type": "data" if result.get('final') else "stream"
                                                }
                                
                            except json.JSONDecodeError as e:
                                logger.warning(f"Failed to parse SSE data: {e}")
            else:
                # Regular JSON response
                response_data = await response.json()
                
                if 'error' in response_data:
                    yield {
                        "error": response_data['error'],
                        "is_task_complete": True
                    }
                elif 'result' in response_data:
                    # Handle non-streaming response
                    result = response_data['result']
                    if result.get('kind') == 'message':
                        parts = result.get('parts', [])
                        for part in parts:
                            if part.get('kind') == 'text':
                                yield {
                                    "content": part.get('text'),
                                    "is_task_complete": True,
                                    "response_type": "data"
                                }
                    else:
                        yield {
                            "content": result,
                            "is_task_complete": True,
                            "response_type": "data"
                        }
    
    async def analyze_technical_intelligence(self, research_areas: list[str]) -> None:
        """Analyze technical intelligence for given research areas."""
        query = f"Analyze technical intelligence for: {', '.join(research_areas)}"
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Analyzing technical intelligence...", total=None)
            
            async for update in self.send_request(query):
                if update.get("content"):
                    if update.get("is_task_complete"):
                        progress.update(task, completed=100)
                        self._display_technical_analysis(update.get("content"))
                    else:
                        progress.update(task, description=update["content"])
    
    async def optimize_daily_schedule(self, tasks: list[Dict[str, Any]]) -> None:
        """Optimize daily schedule based on tasks and energy patterns."""
        query = f"Optimize my daily schedule for these tasks: {json.dumps(tasks)}"
        
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        layout["header"].update(Panel("🗓️ Daily Schedule Optimization", style="bold magenta"))
        layout["footer"].update(Panel("Processing...", style="dim"))
        
        with Live(layout, console=console, refresh_per_second=4) as live:
            async for update in self.send_request(query):
                if update.get("content"):
                    if update.get("is_task_complete"):
                        schedule = update.get("content", {})
                        layout["body"].update(self._create_schedule_table(schedule))
                        layout["footer"].update(Panel("✅ Optimization complete!", style="green"))
                    else:
                        layout["footer"].update(Panel(update["content"], style="yellow"))
    
    async def track_learning_progress(self, skill: str) -> None:
        """Track learning progress for a specific skill."""
        query = f"Track my learning progress for {skill} and provide recommendations"
        
        console.print(Panel(f"📚 Analyzing Learning Progress: {skill}", style="bold blue"))
        
        async for update in self.send_request(query):
            if update.get("content"):
                if update.get("is_task_complete") and update.get("response_type") == "data":
                    self._display_learning_progress(update["content"])
                else:
                    console.print(f"  {update['content']}")
    
    async def get_productivity_insights(self, timeframe: str = "week") -> None:
        """Get productivity insights and recommendations."""
        query = f"Analyze my productivity patterns for the past {timeframe} and provide optimization strategies"
        
        console.print(Panel(f"📊 Productivity Analysis: Past {timeframe}", style="bold cyan"))
        
        insights = {}
        async for update in self.send_request(query):
            if update.get("content"):
                if update.get("is_task_complete") and update.get("response_type") == "data":
                    insights = update["content"]
                    self._display_productivity_insights(insights)
                else:
                    console.print(f"  🔍 {update['content']}")
    
    def _display_technical_analysis(self, analysis: Dict[str, Any]) -> None:
        """Display technical analysis results."""
        if isinstance(analysis, str):
            try:
                analysis = json.loads(analysis)
            except:
                console.print(Markdown(analysis))
                return
        
        # Executive Summary
        console.print(Panel(
            analysis.get("executive_summary", "Analysis complete."),
            title="Executive Summary",
            style="bold green"
        ))
        
        # Domain Synthesis
        if "domain_synthesis" in analysis:
            tech = analysis["domain_synthesis"].get("technical", {})
            if tech:
                table = Table(title="🔬 Technical Intelligence", show_header=True)
                table.add_column("Category", style="cyan")
                table.add_column("Details", style="white")
                
                if "key_findings" in tech:
                    table.add_row("Key Findings", "\n".join(tech["key_findings"]))
                if "opportunities" in tech:
                    table.add_row("Opportunities", "\n".join(tech["opportunities"]))
                if "priority_actions" in tech:
                    table.add_row("Priority Actions", "\n".join(tech["priority_actions"]))
                
                console.print(table)
    
    def _create_schedule_table(self, schedule: Dict[str, Any]) -> Table:
        """Create a formatted schedule table."""
        table = Table(title="📅 Optimized Daily Schedule", show_header=True)
        table.add_column("Time", style="cyan", width=12)
        table.add_column("Task", style="white")
        table.add_column("Energy Match", style="green")
        table.add_column("Notes", style="yellow")
        
        if "integrated_strategy" in schedule and "weekly_plan" in schedule["integrated_strategy"]:
            for day, plan in schedule["integrated_strategy"]["weekly_plan"].items():
                for task in plan.get("tasks", []):
                    table.add_row(
                        day.title(),
                        task,
                        plan.get("focus", ""),
                        "Optimized for energy"
                    )
        
        return table
    
    def _display_learning_progress(self, progress_data: Dict[str, Any]) -> None:
        """Display learning progress visualization."""
        console.print("\n📈 Learning Progress Report\n", style="bold")
        
        if "progress" in progress_data:
            progress = progress_data["progress"]
            
            # Progress bar
            current = progress.get("current_level", 1)
            target = progress.get("target_level", 10)
            percentage = (current / target) * 100
            
            console.print(f"Current Level: {current}/{target} ({percentage:.1f}%)")
            console.print(f"Hours Invested: {progress.get('hours_invested', 0):.1f}")
            
        if "learning_velocity" in progress_data:
            velocity = progress_data["learning_velocity"]
            console.print(f"\n⚡ Learning Velocity: {velocity.get('velocity', 0):.3f} levels/hour")
            console.print(f"📍 Trajectory: {velocity.get('trajectory', 'unknown')}")
            
            if "estimated_hours_to_target" in velocity:
                hours = velocity["estimated_hours_to_target"]
                if hours != float('inf'):
                    console.print(f"⏱️ Estimated Time to Target: {hours:.1f} hours")
        
        if "recommendations" in progress_data:
            console.print("\n💡 Recommendations:", style="bold yellow")
            for rec in progress_data["recommendations"]:
                console.print(f"  • {rec}")
    
    def _display_productivity_insights(self, insights: Dict[str, Any]) -> None:
        """Display productivity insights and patterns."""
        # Create insights dashboard
        layout = Layout()
        layout.split_row(
            Layout(name="energy", ratio=1),
            Layout(name="focus", ratio=1),
            Layout(name="optimization", ratio=1)
        )
        
        # Energy patterns
        if "domain_synthesis" in insights and "personal" in insights["domain_synthesis"]:
            personal = insights["domain_synthesis"]["personal"]
            energy_text = f"**Energy Insights**\n\n{personal.get('energy_insights', 'No data')}"
            layout["energy"].update(Panel(Markdown(energy_text), style="green"))
        
        # Focus patterns
        if "domain_synthesis" in insights and "workflow" in insights["domain_synthesis"]:
            workflow = insights["domain_synthesis"]["workflow"]
            focus_text = "**Workflow Analysis**\n\n"
            if "bottlenecks" in workflow:
                focus_text += "Bottlenecks:\n" + "\n".join(f"• {b}" for b in workflow["bottlenecks"])
            layout["focus"].update(Panel(Markdown(focus_text), style="yellow"))
        
        # Optimization strategies
        if "integrated_strategy" in insights and "immediate_actions" in insights["integrated_strategy"]:
            actions = insights["integrated_strategy"]["immediate_actions"]
            opt_text = "**Immediate Actions**\n\n"
            for action in actions[:3]:  # Top 3 actions
                opt_text += f"• {action['action']} ({action['impact']} impact)\n"
            layout["optimization"].update(Panel(Markdown(opt_text), style="blue"))
        
        console.print(layout)


# Example usage functions
async def demo_technical_analysis():
    """Demo: Analyze technical intelligence."""
    async with SolopreneurClient() as client:
        await client.connect_websocket()
        await client.analyze_technical_intelligence([
            "multi-agent systems",
            "LangGraph patterns",
            "RAG optimization"
        ])

async def demo_schedule_optimization():
    """Demo: Optimize daily schedule."""
    async with SolopreneurClient() as client:
        await client.connect_websocket()
        
        tasks = [
            {
                "title": "Implement Oracle agent handoffs",
                "complexity_score": 4,
                "estimated_hours": 3,
                "type": "development"
            },
            {
                "title": "Study LangGraph documentation",
                "complexity_score": 3,
                "estimated_hours": 2,
                "type": "learning"
            },
            {
                "title": "Code review and testing",
                "complexity_score": 2,
                "estimated_hours": 1,
                "type": "review"
            }
        ]
        
        await client.optimize_daily_schedule(tasks)

async def demo_learning_progress():
    """Demo: Track learning progress."""
    async with SolopreneurClient() as client:
        await client.connect_websocket()
        await client.track_learning_progress("LangGraph")

async def demo_productivity_insights():
    """Demo: Get productivity insights."""
    async with SolopreneurClient() as client:
        await client.connect_websocket()
        await client.get_productivity_insights("week")

async def interactive_session():
    """Run an interactive session with the Solopreneur Oracle."""
    console.print(Panel(
        "🔮 [bold magenta]AI Solopreneur Oracle[/bold magenta] 🔮\n\n"
        "Your AI-powered developer/entrepreneur assistant\n"
        "Type 'help' for commands or 'quit' to exit",
        style="bold blue"
    ))
    
    async with SolopreneurClient() as client:
        await client.connect_websocket()
        
        while True:
            try:
                query = console.input("\n[bold cyan]You:[/bold cyan] ")
                
                if query.lower() in ['quit', 'exit', 'q']:
                    console.print("[yellow]Goodbye! May your code be bug-free! 🚀[/yellow]")
                    break
                
                if query.lower() == 'help':
                    console.print(Panel(
                        "**Available Commands:**\n\n"
                        "• Technical analysis: Ask about AI research, frameworks, tools\n"
                        "• Schedule optimization: 'Optimize my schedule for [tasks]'\n"
                        "• Learning progress: 'Track progress for [skill]'\n"
                        "• Productivity insights: 'Analyze my productivity'\n"
                        "• General questions: Ask anything about development or productivity\n\n"
                        "Type 'quit' to exit",
                        title="Help",
                        style="green"
                    ))
                    continue
                
                console.print(f"\n[bold magenta]Oracle:[/bold magenta]", end=" ")
                
                response_parts = []
                async for update in client.send_request(query):
                    if update.get("content"):
                        if update.get("is_task_complete"):
                            if update.get("response_type") == "data":
                                # Pretty print JSON response
                                console.print("\n")
                                console.print_json(json.dumps(update["content"]))
                            else:
                                console.print(update["content"])
                        else:
                            # Streaming update
                            console.print(f"\n  {update['content']}", end="")
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted. Type 'quit' to exit.[/yellow]")
            except Exception as e:
                console.print(f"\n[red]Error: {e}[/red]")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "technical":
            asyncio.run(demo_technical_analysis())
        elif command == "schedule":
            asyncio.run(demo_schedule_optimization())
        elif command == "learning":
            asyncio.run(demo_learning_progress())
        elif command == "productivity":
            asyncio.run(demo_productivity_insights())
        else:
            console.print(f"[red]Unknown command: {command}[/red]")
            console.print("Available: technical, schedule, learning, productivity")
    else:
        # Run interactive session by default
        asyncio.run(interactive_session())