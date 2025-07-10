#!/usr/bin/env python3
"""
Interactive Chat Script for Solopreneur Oracle
==============================================

A comprehensive interactive testing interface for the Solopreneur Oracle system.
Provides real-time chat capabilities with the Oracle Master Agent and domain specialists.

Features:
- Direct Oracle communication with both message/send and message/stream
- Real-time streaming responses with progress indicators
- Domain-specific queries and analysis
- System health monitoring
- Performance metrics tracking
- Conversation history management
- Rich formatting and color output

Usage:
    python interactive_oracle_chat.py [options]

Options:
    --oracle-port PORT     Oracle Master Agent port (default: 10901)
    --streaming            Enable streaming mode by default
    --debug                Enable debug logging
    --save-history         Save conversation history to file
"""

import asyncio
import aiohttp
import json
import time
import argparse
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
import signal
import os

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    DIM = '\033[2m'

class SolopreneurOracleChat:
    """Interactive chat interface for Solopreneur Oracle."""
    
    def __init__(self, oracle_port: int = 10901, debug: bool = False, save_history: bool = False):
        self.oracle_port = oracle_port
        self.oracle_url = f"http://localhost:{oracle_port}"
        self.debug = debug
        self.save_history = save_history
        self.conversation_history = []
        self.session_start = datetime.now()
        self.message_count = 0
        self.total_response_time = 0
        self.streaming_mode = False
        
        # Domain agent ports for direct communication
        self.domain_agents = {
            "technical": {"port": 10902, "name": "Technical Intelligence"},
            "knowledge": {"port": 10903, "name": "Knowledge Management"},
            "personal": {"port": 10904, "name": "Personal Optimization"},
            "learning": {"port": 10905, "name": "Learning Enhancement"},
            "integration": {"port": 10906, "name": "Integration Synthesis"}
        }
        
        # Predefined query templates
        self.query_templates = {
            "1": "How can I optimize my development workflow for building AI applications?",
            "2": "What's the best architecture pattern for a scalable microservices system?",
            "3": "How should I manage my energy and focus while learning new technologies?",
            "4": "Analyze the trade-offs between different cloud platforms for my SaaS product.",
            "5": "What learning path should I follow to master distributed systems?",
            "6": "How can I integrate multiple development tools for maximum productivity?",
            "7": "Evaluate the technical feasibility of implementing real-time collaboration features.",
            "8": "Design a personal optimization system for maintaining high performance as a solo developer."
        }
    
    def print_colored(self, text: str, color: str = Colors.END, end: str = "\n"):
        """Print colored text to terminal."""
        print(f"{color}{text}{Colors.END}", end=end)
    
    def print_header(self):
        """Print the application header."""
        print("\n" + "="*80)
        self.print_colored("🧠 SOLOPRENEUR ORACLE - INTERACTIVE CHAT INTERFACE", Colors.BOLD + Colors.CYAN)
        print("="*80)
        self.print_colored(f"Oracle URL: {self.oracle_url}", Colors.DIM)
        self.print_colored(f"Session Started: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}", Colors.DIM)
        print("="*80 + "\n")
    
    def print_menu(self):
        """Print the main menu."""
        self.print_colored("\n📋 AVAILABLE COMMANDS:", Colors.BOLD + Colors.YELLOW)
        print("  🎯 Direct Commands:")
        print("    /oracle [message]     - Send message to Oracle Master Agent")
        print("    /stream [message]     - Send streaming message to Oracle")
        print("    /domain [agent] [msg] - Send message to specific domain agent")
        print("    /health               - Check system health status")
        print("    /performance          - Show performance metrics")
        print("    /history              - Show conversation history")
        print("    /templates            - Show predefined query templates")
        print("    /clear                - Clear conversation history")
        print("    /help                 - Show this menu")
        print("    /quit or /exit        - Exit the chat")
        print("\n  🏷️  Domain Agents:")
        for key, agent in self.domain_agents.items():
            print(f"    {key:12} - {agent['name']} (Port {agent['port']})")
        print("\n  📝 Quick Templates:")
        for num, template in self.query_templates.items():
            print(f"    /{num}               - {template[:60]}...")
        print()
    
    async def check_system_health(self) -> Dict[str, Any]:
        """Check the health of all system components."""
        self.print_colored("🏥 Checking system health...", Colors.YELLOW)
        
        health_status = {
            "oracle": {"status": "unknown", "response_time": None},
            "domains": {},
            "overall": "unknown"
        }
        
        # Check Oracle Master Agent
        try:
            start_time = time.time()
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"{self.oracle_url}/.well-known/ai-plugin.json") as response:
                    response_time = time.time() - start_time
                    if response.status == 200 or response.status == 404:  # 404 is OK, means agent is running
                        health_status["oracle"] = {"status": "healthy", "response_time": response_time}
                        self.print_colored(f"  ✅ Oracle Master Agent (Port {self.oracle_port}): Healthy ({response_time:.2f}s)", Colors.GREEN)
                    else:
                        health_status["oracle"] = {"status": "unhealthy", "response_time": response_time}
                        self.print_colored(f"  ❌ Oracle Master Agent (Port {self.oracle_port}): Unhealthy (HTTP {response.status})", Colors.RED)
        except Exception as e:
            health_status["oracle"] = {"status": "error", "error": str(e)}
            self.print_colored(f"  ❌ Oracle Master Agent (Port {self.oracle_port}): Error - {e}", Colors.RED)
        
        # Check Domain Agents
        for key, agent in self.domain_agents.items():
            try:
                start_time = time.time()
                timeout = aiohttp.ClientTimeout(total=5)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    url = f"http://localhost:{agent['port']}/.well-known/ai-plugin.json"
                    async with session.get(url) as response:
                        response_time = time.time() - start_time
                        if response.status == 200 or response.status == 404:  # 404 is OK
                            health_status["domains"][key] = {"status": "healthy", "response_time": response_time}
                            self.print_colored(f"  ✅ {agent['name']} (Port {agent['port']}): Healthy ({response_time:.2f}s)", Colors.GREEN)
                        else:
                            health_status["domains"][key] = {"status": "unhealthy", "response_time": response_time}
                            self.print_colored(f"  ❌ {agent['name']} (Port {agent['port']}): Unhealthy (HTTP {response.status})", Colors.RED)
            except Exception as e:
                health_status["domains"][key] = {"status": "error", "error": str(e)}
                self.print_colored(f"  ❌ {agent['name']} (Port {agent['port']}): Error - {e}", Colors.RED)
        
        # Determine overall health
        oracle_healthy = health_status["oracle"]["status"] == "healthy"
        domain_healthy_count = sum(1 for domain in health_status["domains"].values() if domain["status"] == "healthy")
        total_domains = len(self.domain_agents)
        
        if oracle_healthy and domain_healthy_count >= total_domains * 0.8:
            health_status["overall"] = "excellent"
            self.print_colored(f"\n🎉 Overall System Health: EXCELLENT ({domain_healthy_count}/{total_domains} domains healthy)", Colors.BOLD + Colors.GREEN)
        elif oracle_healthy and domain_healthy_count >= total_domains * 0.6:
            health_status["overall"] = "good"
            self.print_colored(f"\n✅ Overall System Health: GOOD ({domain_healthy_count}/{total_domains} domains healthy)", Colors.YELLOW)
        elif oracle_healthy:
            health_status["overall"] = "degraded"
            self.print_colored(f"\n⚠️ Overall System Health: DEGRADED ({domain_healthy_count}/{total_domains} domains healthy)", Colors.YELLOW)
        else:
            health_status["overall"] = "critical"
            self.print_colored(f"\n❌ Overall System Health: CRITICAL (Oracle unavailable)", Colors.RED)
        
        return health_status
    
    async def send_oracle_message(self, message: str, use_streaming: bool = False) -> Dict[str, Any]:
        """Send a message to the Oracle Master Agent."""
        method = "message/stream" if use_streaming else "message/send"
        
        payload = {
            "jsonrpc": "2.0",
            "id": f"chat-{self.message_count}",
            "method": method,
            "params": {
                "message": {
                    "role": "user",
                    "parts": [{"kind": "text", "text": message}],
                    "messageId": f"chat-msg-{self.message_count}",
                    "kind": "message"
                },
                "metadata": {"source": "interactive_chat", "streaming": use_streaming}
            }
        }
        
        start_time = time.time()
        self.print_colored(f"\n🤖 Sending to Oracle ({method})...", Colors.BLUE)
        
        try:
            timeout = aiohttp.ClientTimeout(total=120)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.oracle_url, json=payload) as response:
                    if response.status == 200:
                        content_type = response.headers.get('Content-Type', '')
                        
                        if use_streaming and 'text/event-stream' in content_type:
                            return await self._handle_streaming_response(response, start_time)
                        else:
                            return await self._handle_json_response(response, start_time)
                    else:
                        error_text = await response.text()
                        self.print_colored(f"❌ Oracle Error (HTTP {response.status}): {error_text}", Colors.RED)
                        return {"error": f"HTTP {response.status}: {error_text}", "response_time": time.time() - start_time}
        
        except Exception as e:
            response_time = time.time() - start_time
            self.print_colored(f"❌ Oracle Communication Error: {e}", Colors.RED)
            return {"error": str(e), "response_time": response_time}
    
    async def _handle_streaming_response(self, response, start_time: float) -> Dict[str, Any]:
        """Handle streaming SSE response from Oracle."""
        self.print_colored("🌊 Receiving streaming response...", Colors.CYAN)
        
        event_count = 0
        final_analysis = None
        task_id = None
        
        async for line in response.content:
            if line:
                line_str = line.decode('utf-8').strip()
                if line_str.startswith('data: '):
                    event_count += 1
                    data = line_str[6:]
                    try:
                        event = json.loads(data)
                        if 'result' in event:
                            result = event['result']
                            
                            if result.get('kind') == 'task':
                                task_id = result.get('id')
                                self.print_colored(f"  📋 Task created: {task_id}", Colors.DIM)
                            
                            elif result.get('kind') == 'artifact-update':
                                artifact = result.get('artifact', {})
                                name = artifact.get('name', '')
                                if 'Oracle' in name:
                                    self.print_colored(f"  🧠 Oracle synthesis update (event {event_count})", Colors.CYAN)
                            
                            elif result.get('kind') == 'status-update':
                                status = result.get('status', {})
                                if status.get('state') == 'completed' and result.get('final'):
                                    response_time = time.time() - start_time
                                    self.print_colored(f"  ✅ Analysis completed in {response_time:.1f}s ({event_count} events)", Colors.GREEN)
                                    final_analysis = "completed"
                                    break
                    
                    except json.JSONDecodeError:
                        pass
        
        response_time = time.time() - start_time
        self.total_response_time += response_time
        
        return {
            "status": "success",
            "method": "streaming",
            "events": event_count,
            "task_id": task_id,
            "final_status": final_analysis,
            "response_time": response_time
        }
    
    async def _handle_json_response(self, response, start_time: float) -> Dict[str, Any]:
        """Handle regular JSON response from Oracle."""
        try:
            result = await response.json()
            response_time = time.time() - start_time
            self.total_response_time += response_time
            
            self.print_colored(f"✅ Oracle Response received in {response_time:.1f}s", Colors.GREEN)
            
            # Extract and display analysis if available
            if 'result' in result:
                response_data = result['result']
                artifacts = response_data.get('artifacts', [])
                
                if artifacts:
                    artifact = artifacts[0]
                    parts = artifact.get('parts', [])
                    
                    for part in parts:
                        if part.get('kind') == 'data' and 'data' in part:
                            analysis = part['data']
                            self._display_analysis(analysis)
                            break
                        elif part.get('kind') == 'text' and 'text' in part:
                            text_content = part['text']
                            self.print_colored(f"\n📄 Oracle Analysis:\n{text_content}", Colors.CYAN)
                            break
            
            return {
                "status": "success",
                "method": "json",
                "data": result,
                "response_time": response_time
            }
        
        except json.JSONDecodeError as e:
            response_time = time.time() - start_time
            self.print_colored(f"❌ JSON Parse Error: {e}", Colors.RED)
            return {"error": f"JSON Parse Error: {e}", "response_time": response_time}
    
    def _display_analysis(self, analysis: Dict[str, Any]):
        """Display formatted analysis from Oracle."""
        self.print_colored("\n🎯 ORACLE ANALYSIS RESULTS", Colors.BOLD + Colors.CYAN)
        print("="*60)
        
        # Executive Summary
        if 'executive_summary' in analysis:
            self.print_colored("📋 Executive Summary:", Colors.BOLD + Colors.YELLOW)
            print(f"   {analysis['executive_summary']}\n")
        
        # Confidence Score
        if 'confidence_score' in analysis:
            confidence = analysis['confidence_score']
            color = Colors.GREEN if confidence >= 0.7 else Colors.YELLOW if confidence >= 0.5 else Colors.RED
            self.print_colored(f"📊 Confidence Score: {confidence:.2f}", Colors.BOLD + color)
        
        # Technical Assessment
        if 'technical_assessment' in analysis:
            tech = analysis['technical_assessment']
            self.print_colored("\n🔧 Technical Assessment:", Colors.BOLD + Colors.BLUE)
            if 'feasibility_score' in tech:
                print(f"   Feasibility: {tech['feasibility_score']}/100")
            if 'implementation_complexity' in tech:
                print(f"   Complexity: {tech['implementation_complexity']}")
            if 'technical_risks' in tech and tech['technical_risks']:
                print(f"   Risks: {', '.join(tech['technical_risks'][:3])}")
        
        # Personal Optimization
        if 'personal_optimization' in analysis:
            personal = analysis['personal_optimization']
            self.print_colored("\n⚡ Personal Optimization:", Colors.BOLD + Colors.GREEN)
            if 'sustainability_score' in personal:
                print(f"   Sustainability: {personal['sustainability_score']}/100")
            if 'energy_impact' in personal:
                print(f"   Energy Impact: {personal['energy_impact']}")
            if 'cognitive_load' in personal:
                print(f"   Cognitive Load: {personal['cognitive_load']}")
        
        # Strategic Insights
        if 'strategic_insights' in analysis and analysis['strategic_insights']:
            self.print_colored("\n💡 Strategic Insights:", Colors.BOLD + Colors.CYAN)
            for i, insight in enumerate(analysis['strategic_insights'][:3], 1):
                source = insight.get('source', 'Unknown')
                content = insight.get('insight', 'No insight provided')
                confidence = insight.get('confidence', 0)
                print(f"   {i}. [{source}] {content} (confidence: {confidence:.2f})")
        
        print("="*60 + "\n")
    
    async def send_domain_message(self, domain_key: str, message: str) -> Dict[str, Any]:
        """Send a message to a specific domain agent."""
        if domain_key not in self.domain_agents:
            return {"error": f"Unknown domain agent: {domain_key}"}
        
        agent = self.domain_agents[domain_key]
        url = f"http://localhost:{agent['port']}"
        
        payload = {
            "jsonrpc": "2.0",
            "id": f"domain-{self.message_count}",
            "method": "message/send",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [{"kind": "text", "text": message}],
                    "messageId": f"domain-msg-{self.message_count}",
                    "kind": "message"
                },
                "metadata": {"source": "interactive_chat", "domain": domain_key}
            }
        }
        
        start_time = time.time()
        self.print_colored(f"\n🎯 Sending to {agent['name']}...", Colors.BLUE)
        
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        result = await response.json()
                        self.print_colored(f"✅ {agent['name']} responded in {response_time:.1f}s", Colors.GREEN)
                        
                        # Extract and display basic response info
                        if 'result' in result:
                            response_data = result['result']
                            if response_data.get('kind') == 'task':
                                task_id = response_data.get('id')
                                self.print_colored(f"📋 Task created: {task_id}", Colors.DIM)
                        
                        return {"status": "success", "data": result, "response_time": response_time}
                    else:
                        error_text = await response.text()
                        self.print_colored(f"❌ {agent['name']} Error (HTTP {response.status}): {error_text}", Colors.RED)
                        return {"error": f"HTTP {response.status}: {error_text}", "response_time": response_time}
        
        except Exception as e:
            response_time = time.time() - start_time
            self.print_colored(f"❌ {agent['name']} Communication Error: {e}", Colors.RED)
            return {"error": str(e), "response_time": response_time}
    
    def show_performance_metrics(self):
        """Display session performance metrics."""
        session_duration = datetime.now() - self.session_start
        avg_response_time = self.total_response_time / self.message_count if self.message_count > 0 else 0
        
        self.print_colored("\n📊 SESSION PERFORMANCE METRICS", Colors.BOLD + Colors.YELLOW)
        print("="*50)
        print(f"Session Duration:      {session_duration}")
        print(f"Messages Sent:         {self.message_count}")
        print(f"Total Response Time:   {self.total_response_time:.1f}s")
        print(f"Average Response Time: {avg_response_time:.1f}s")
        print(f"Oracle URL:            {self.oracle_url}")
        print(f"Streaming Mode:        {'Enabled' if self.streaming_mode else 'Disabled'}")
        print("="*50 + "\n")
    
    def show_conversation_history(self):
        """Display conversation history."""
        if not self.conversation_history:
            self.print_colored("📝 No conversation history yet.", Colors.DIM)
            return
        
        self.print_colored(f"\n📝 CONVERSATION HISTORY ({len(self.conversation_history)} messages)", Colors.BOLD + Colors.YELLOW)
        print("="*60)
        
        for i, entry in enumerate(self.conversation_history[-10:], 1):  # Show last 10
            timestamp = entry['timestamp'].strftime('%H:%M:%S')
            message_type = entry['type']
            content = entry['content'][:100] + "..." if len(entry['content']) > 100 else entry['content']
            
            self.print_colored(f"{i}. [{timestamp}] {message_type}:", Colors.BLUE)
            print(f"   {content}")
            if 'response_time' in entry:
                print(f"   Response Time: {entry['response_time']:.1f}s")
            print()
        
        print("="*60 + "\n")
    
    def save_conversation_history_to_file(self):
        """Save conversation history to a file."""
        if not self.conversation_history:
            self.print_colored("📝 No conversation history to save.", Colors.DIM)
            return
        
        filename = f"oracle_chat_history_{self.session_start.strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump({
                    "session_start": self.session_start.isoformat(),
                    "session_end": datetime.now().isoformat(),
                    "message_count": self.message_count,
                    "total_response_time": self.total_response_time,
                    "conversation": self.conversation_history
                }, f, indent=2, default=str)
            
            self.print_colored(f"💾 Conversation history saved to: {filename}", Colors.GREEN)
        except Exception as e:
            self.print_colored(f"❌ Error saving history: {e}", Colors.RED)
    
    def add_to_history(self, message_type: str, content: str, **kwargs):
        """Add an entry to conversation history."""
        entry = {
            "timestamp": datetime.now(),
            "type": message_type,
            "content": content,
            **kwargs
        }
        self.conversation_history.append(entry)
    
    async def process_command(self, command: str) -> bool:
        """Process a user command. Returns False if user wants to quit."""
        command = command.strip()
        
        if not command:
            return True
        
        # Handle quit commands
        if command.lower() in ['/quit', '/exit', 'quit', 'exit']:
            return False
        
        # Handle help
        elif command.lower() in ['/help', 'help']:
            self.print_menu()
            return True
        
        # Handle health check
        elif command.lower() == '/health':
            await self.check_system_health()
            return True
        
        # Handle performance metrics
        elif command.lower() == '/performance':
            self.show_performance_metrics()
            return True
        
        # Handle conversation history
        elif command.lower() == '/history':
            self.show_conversation_history()
            return True
        
        # Handle clear history
        elif command.lower() == '/clear':
            self.conversation_history.clear()
            self.message_count = 0
            self.total_response_time = 0
            self.print_colored("🧹 Conversation history cleared.", Colors.GREEN)
            return True
        
        # Handle templates
        elif command.lower() == '/templates':
            self.print_colored("\n📝 PREDEFINED QUERY TEMPLATES:", Colors.BOLD + Colors.YELLOW)
            for num, template in self.query_templates.items():
                print(f"  /{num}: {template}")
            print()
            return True
        
        # Handle template shortcuts
        elif command.startswith('/') and command[1:] in self.query_templates:
            template_num = command[1:]
            message = self.query_templates[template_num]
            self.print_colored(f"📋 Using template {template_num}: {message}", Colors.CYAN)
            
            self.message_count += 1
            self.add_to_history("Template Query", message)
            
            result = await self.send_oracle_message(message, self.streaming_mode)
            self.add_to_history("Oracle Response", str(result), **result)
            return True
        
        # Handle Oracle commands
        elif command.startswith('/oracle '):
            message = command[8:].strip()
            if not message:
                self.print_colored("❌ Please provide a message after /oracle", Colors.RED)
                return True
            
            self.message_count += 1
            self.add_to_history("Oracle Message", message)
            
            result = await self.send_oracle_message(message, False)
            self.add_to_history("Oracle Response", str(result), **result)
            return True
        
        # Handle streaming commands
        elif command.startswith('/stream '):
            message = command[8:].strip()
            if not message:
                self.print_colored("❌ Please provide a message after /stream", Colors.RED)
                return True
            
            self.message_count += 1
            self.add_to_history("Oracle Streaming", message)
            
            result = await self.send_oracle_message(message, True)
            self.add_to_history("Oracle Stream Response", str(result), **result)
            return True
        
        # Handle domain commands
        elif command.startswith('/domain '):
            parts = command[8:].strip().split(' ', 1)
            if len(parts) < 2:
                self.print_colored("❌ Usage: /domain <agent> <message>", Colors.RED)
                self.print_colored("Available agents: " + ", ".join(self.domain_agents.keys()), Colors.DIM)
                return True
            
            domain_key, message = parts
            if domain_key not in self.domain_agents:
                self.print_colored(f"❌ Unknown domain agent: {domain_key}", Colors.RED)
                self.print_colored("Available agents: " + ", ".join(self.domain_agents.keys()), Colors.DIM)
                return True
            
            self.message_count += 1
            self.add_to_history(f"Domain Message ({domain_key})", message)
            
            result = await self.send_domain_message(domain_key, message)
            self.add_to_history(f"Domain Response ({domain_key})", str(result), **result)
            return True
        
        # Handle direct messages (no command prefix)
        else:
            # Default to Oracle message
            self.message_count += 1
            self.add_to_history("Direct Message", command)
            
            result = await self.send_oracle_message(command, self.streaming_mode)
            self.add_to_history("Oracle Response", str(result), **result)
            return True
    
    async def run_interactive_chat(self):
        """Run the main interactive chat loop."""
        self.print_header()
        self.print_colored("🌟 Welcome to the Solopreneur Oracle Interactive Chat!", Colors.BOLD + Colors.GREEN)
        self.print_colored("Type '/help' for available commands or just start chatting!", Colors.DIM)
        
        # Initial health check
        await self.check_system_health()
        self.print_menu()
        
        try:
            while True:
                # Get user input
                try:
                    self.print_colored("💬 You: ", Colors.BOLD + Colors.BLUE, end="")
                    user_input = input()
                    
                    # Process the command
                    continue_chat = await self.process_command(user_input)
                    if not continue_chat:
                        break
                        
                except KeyboardInterrupt:
                    self.print_colored("\n\n🛑 Chat interrupted by user.", Colors.YELLOW)
                    break
                except EOFError:
                    self.print_colored("\n\n🛑 Chat ended.", Colors.YELLOW)
                    break
        
        finally:
            # Cleanup and save history
            if self.save_history:
                self.save_conversation_history_to_file()
            
            self.show_performance_metrics()
            self.print_colored("👋 Thank you for using Solopreneur Oracle Chat!", Colors.BOLD + Colors.GREEN)
            self.print_colored("🎯 Session Summary:", Colors.BOLD + Colors.CYAN)
            print(f"   Messages Sent: {self.message_count}")
            print(f"   Average Response Time: {self.total_response_time / max(self.message_count, 1):.1f}s")
            print(f"   Session Duration: {datetime.now() - self.session_start}")

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    print(f"\n\n{Colors.YELLOW}🛑 Received signal {signum}. Exiting gracefully...{Colors.END}")
    sys.exit(0)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Interactive Chat Interface for Solopreneur Oracle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python interactive_oracle_chat.py
    python interactive_oracle_chat.py --oracle-port 10901 --streaming --save-history
    python interactive_oracle_chat.py --debug
        """
    )
    
    parser.add_argument(
        '--oracle-port',
        type=int,
        default=10901,
        help='Oracle Master Agent port (default: 10901)'
    )
    
    parser.add_argument(
        '--streaming',
        action='store_true',
        help='Enable streaming mode by default'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--save-history',
        action='store_true',
        help='Save conversation history to file'
    )
    
    args = parser.parse_args()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run the chat interface
    chat = SolopreneurOracleChat(
        oracle_port=args.oracle_port,
        debug=args.debug,
        save_history=args.save_history
    )
    
    if args.streaming:
        chat.streaming_mode = True
    
    try:
        asyncio.run(chat.run_interactive_chat())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}🛑 Chat interrupted. Goodbye!{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error running chat: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()