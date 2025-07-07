#!/usr/bin/env python3
"""Interactive Nexus Oracle - Ask your own research questions!"""

import os
import sys
import asyncio
import json
from datetime import datetime

# Set up environment
sys.path.insert(0, './src')
sys.path.insert(0, '.')
os.environ['GOOGLE_API_KEY'] = os.environ.get('GOOGLE_API_KEY', 'your-api-key-here')

class InteractiveOracleSession:
    """Interactive session with the Nexus Oracle."""
    
    def __init__(self):
        self.oracle = None
        self.session_id = f"interactive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.question_count = 0
        
    async def initialize(self):
        """Initialize the Oracle for interactive use."""
        print("🔮 NEXUS ORACLE - INTERACTIVE RESEARCH SESSION")
        print("=" * 60)
        print("Ask any research question and get transdisciplinary analysis!")
        print("Type 'help' for examples, 'status' for Oracle state, or 'quit' to exit")
        print("=" * 60)
        
        try:
            from a2a_mcp.agents.nexus_oracle_agent import NexusOracleAgent
            self.oracle = NexusOracleAgent()
            
            print(f"✅ Oracle initialized: {self.oracle.agent_name}")
            print(f"🎯 Session ID: {self.session_id}")
            print(f"📊 Quality Standards:")
            print(f"   Min Confidence: {self.oracle.quality_thresholds['min_confidence_score']}")
            print(f"   Min Domains: {self.oracle.quality_thresholds['min_domain_coverage']}")
            print(f"   Evidence Threshold: {self.oracle.quality_thresholds['evidence_quality_threshold']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize Oracle: {e}")
            return False
    
    async def ask_question(self, question: str):
        """Ask the Oracle a research question."""
        if not question.strip():
            print("⚠️  Please enter a research question.")
            return
            
        self.question_count += 1
        task_id = f"interactive_task_{self.question_count:03d}"
        
        print(f"\n🔍 ANALYZING YOUR QUESTION #{self.question_count}")
        print("─" * 50)
        print(f"❓ Question: {question}")
        print("─" * 50)
        
        # Show what domains the Oracle thinks are relevant
        try:
            dependency_analysis = self.oracle.analyze_research_dependencies(question)
            domains = list(dependency_analysis['domain_groups'].keys())
            execution_steps = len(dependency_analysis['execution_plan'])
            parallel_opportunities = len(dependency_analysis['parallelization_opportunities'])
            
            print(f"🎯 Oracle Planning:")
            print(f"   Relevant Domains: {', '.join(domains)}")
            print(f"   Execution Steps: {execution_steps}")
            print(f"   Parallel Processing: {parallel_opportunities} opportunities")
            print("\n⚡ Analysis Starting...")
        except Exception as e:
            print(f"⚠️  Planning error: {e}")
            print("⚡ Proceeding with analysis...")
        
        start_time = datetime.now()
        responses = []
        
        try:
            async for response in self.oracle.stream(question, self.session_id, task_id):
                responses.append(response)
                content = response.get('content', '')
                
                if not response.get('is_task_complete'):
                    # Show live progress
                    print(f"   {content}")
                else:
                    # Final analysis result
                    duration = (datetime.now() - start_time).total_seconds()
                    
                    print(f"\n🎯 ORACLE ANALYSIS COMPLETE ({duration:.1f}s)")
                    print("=" * 50)
                    
                    if response.get('response_type') == 'data':
                        analysis = response.get('content', {})
                        await self.display_analysis(analysis)
                    else:
                        print(f"📝 Result: {content}")
                    break
                    
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            print("   The Oracle encountered an issue. Try rephrasing your question.")
    
    async def display_analysis(self, analysis: dict):
        """Display the Oracle's analysis in a user-friendly format."""
        if not isinstance(analysis, dict):
            print(f"📝 Analysis: {analysis}")
            return
            
        synthesis = analysis.get('synthesis', {})
        quality_validation = analysis.get('quality_validation', {})
        research_intelligence = analysis.get('research_intelligence', {})
        
        # Main summary
        summary = synthesis.get('executive_summary', 'No summary available')
        print(f"📋 EXECUTIVE SUMMARY:")
        print(f"   {summary}")
        
        # Quality metrics
        confidence = synthesis.get('research_confidence', 'N/A')
        domain_coverage = synthesis.get('domain_coverage', 0)
        quality_score = quality_validation.get('confidence_score', 'N/A')
        
        print(f"\n📊 ANALYSIS QUALITY:")
        print(f"   Research Confidence: {confidence}")
        print(f"   Domain Coverage: {domain_coverage} disciplines")
        print(f"   Quality Score: {quality_score}")
        
        # Cross-domain insights
        cross_patterns = synthesis.get('cross_domain_patterns', {})
        if cross_patterns:
            convergent = cross_patterns.get('convergent_findings', [])
            gaps = cross_patterns.get('knowledge_gaps', [])
            
            print(f"\n🔗 CROSS-DOMAIN PATTERNS:")
            print(f"   Convergent Findings: {len(convergent)}")
            print(f"   Knowledge Gaps: {len(gaps)}")
            
            # Show key finding
            if convergent:
                key_finding = convergent[0] if isinstance(convergent[0], str) else str(convergent[0])
                print(f"   Key Finding: {key_finding[:100]}...")
        
        # Novel hypotheses
        hypotheses = synthesis.get('novel_hypotheses', [])
        if hypotheses:
            print(f"\n💡 NOVEL HYPOTHESES ({len(hypotheses)} generated):")
            for i, hypothesis in enumerate(hypotheses[:2], 1):
                if isinstance(hypothesis, dict):
                    hyp_text = hypothesis.get('hypothesis', 'N/A')
                    confidence = hypothesis.get('confidence', 'N/A')
                    print(f"   {i}. {hyp_text[:80]}... (Confidence: {confidence})")
                else:
                    print(f"   {i}. {str(hypothesis)[:80]}...")
        
        # Research recommendations
        recommendations = synthesis.get('research_recommendations', {})
        if recommendations:
            print(f"\n🎯 RESEARCH RECOMMENDATIONS:")
            
            priority_areas = recommendations.get('priority_research_areas', [])
            if priority_areas:
                print(f"   Priority Areas: {', '.join(priority_areas[:3])}")
                
            methodologies = recommendations.get('recommended_methodologies', [])
            if methodologies:
                print(f"   Methodologies: {', '.join(methodologies[:3])}")
    
    def show_help(self):
        """Show help information."""
        print(f"\n📚 NEXUS ORACLE HELP")
        print("─" * 30)
        print("🎯 EXAMPLE RESEARCH QUESTIONS:")
        print("   • How can AI improve sustainable agriculture practices?")
        print("   • What are the psychological effects of remote work on productivity?")
        print("   • Analyze the intersection of blockchain and healthcare privacy")
        print("   • How do social media algorithms affect democratic processes?")
        print("   • What are the ethical implications of gene editing technology?")
        print()
        print("🛠️ COMMANDS:")
        print("   • 'help' - Show this help")
        print("   • 'status' - Show Oracle state")
        print("   • 'clear' - Clear Oracle memory")
        print("   • 'quit' or 'exit' - End session")
        print()
        print("💡 TIPS:")
        print("   • Ask complex, multi-disciplinary questions for best results")
        print("   • The Oracle excels at cross-domain analysis")
        print("   • Follow up questions maintain conversation context")
    
    def show_status(self):
        """Show Oracle status."""
        print(f"\n🤖 ORACLE STATUS")
        print("─" * 25)
        print(f"Session ID: {self.session_id}")
        print(f"Questions Asked: {self.question_count}")
        print(f"Query History: {len(self.oracle.query_history)} entries")
        print(f"Research Cache: {len(self.oracle.research_intelligence)} domains")
        print(f"Context ID: {self.oracle.context_id}")
        
        if self.oracle.query_history:
            print(f"\nRecent Questions:")
            for i, entry in enumerate(self.oracle.query_history[-3:], 1):
                query_text = entry.get('query', 'Unknown')
                timestamp = entry.get('timestamp', 'Unknown time')
                print(f"   {i}. {query_text[:50]}... ({timestamp})")
    
    def clear_memory(self):
        """Clear Oracle memory."""
        self.oracle.clear_state()
        print(f"🔄 Oracle memory cleared. Starting fresh!")
    
    async def run_interactive_session(self):
        """Run the interactive session."""
        if not await self.initialize():
            return
            
        print(f"\n💬 Ready for your questions! (Type your question and press Enter)")
        
        while True:
            try:
                # Get user input
                user_input = input(f"\n🔮 Oracle> ").strip()
                
                if not user_input:
                    continue
                    
                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print(f"\n👋 Session ended. Asked {self.question_count} questions.")
                    break
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                elif user_input.lower() == 'status':
                    self.show_status()
                    continue
                elif user_input.lower() == 'clear':
                    self.clear_memory()
                    continue
                
                # Process as research question
                await self.ask_question(user_input)
                
            except KeyboardInterrupt:
                print(f"\n\n👋 Session interrupted. Asked {self.question_count} questions.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Try asking your question again.")

if __name__ == "__main__":
    print("🚀 Starting Interactive Nexus Oracle...")
    
    session = InteractiveOracleSession()
    asyncio.run(session.run_interactive_session())