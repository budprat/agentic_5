#!/usr/bin/env python3
"""Improved Interactive Nexus Oracle with better performance and context handling."""

import os
import sys
import asyncio
import json
from datetime import datetime

# Set up environment
sys.path.insert(0, './src')
sys.path.insert(0, '.')
os.environ['GOOGLE_API_KEY'] = os.environ.get('GOOGLE_API_KEY', 'your-api-key-here')

class ImprovedOracleSession:
    """Enhanced interactive session with the Nexus Oracle."""
    
    def __init__(self):
        self.oracle = None
        self.session_id = f"improved_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.question_count = 0
        self.last_query = ""
        
    async def initialize(self):
        """Initialize the improved Oracle."""
        print("🔮 NEXUS ORACLE - ENHANCED INTERACTIVE SESSION")
        print("=" * 65)
        print("🎯 IMPROVEMENTS:")
        print("   • Better domain detection for complex queries")
        print("   • Smarter quality thresholds to avoid incomplete responses")
        print("   • Query-focused synthesis generation")
        print("   • Improved follow-up question handling")
        print("=" * 65)
        
        try:
            from a2a_mcp.agents.nexus_oracle_agent import NexusOracleAgent
            self.oracle = NexusOracleAgent()
            
            print(f"✅ Enhanced Oracle initialized: {self.oracle.agent_name}")
            print(f"🎯 Session ID: {self.session_id}")
            print(f"📊 Quality Standards:")
            print(f"   Min Confidence: {self.oracle.quality_thresholds['min_confidence_score']}")
            print(f"   Min Domains: {self.oracle.quality_thresholds['min_domain_coverage']}")
            print(f"   Evidence Threshold: {self.oracle.quality_thresholds['evidence_quality_threshold']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize Oracle: {e}")
            return False
    
    def test_domain_detection(self, question: str):
        """Test and show improved domain detection."""
        print(f"\n🧠 DOMAIN ANALYSIS PREVIEW:")
        print("─" * 40)
        
        try:
            analysis = self.oracle.analyze_research_dependencies(question)
            domains = list(analysis['domain_groups'].keys())
            execution_steps = len(analysis['execution_plan'])
            parallel_opportunities = len(analysis['parallelization_opportunities'])
            
            print(f"🎯 Detected Domains ({len(domains)}): {', '.join(domains)}")
            print(f"📋 Execution Plan: {execution_steps} steps")
            print(f"⚡ Parallel Opportunities: {parallel_opportunities}")
            
            # Show execution plan details
            for i, step in enumerate(analysis['execution_plan'], 1):
                analyses = step.get('analyses', [])
                parallel = step.get('parallel_execution', False)
                priority = step.get('priority_level', 'N/A')
                parallel_indicator = "🔄" if parallel else "➡️"
                print(f"   {parallel_indicator} Step {i}: {', '.join(analyses)} (Priority: {priority})")
                
            return len(domains)
            
        except Exception as e:
            print(f"❌ Domain analysis error: {e}")
            return 0
    
    async def ask_enhanced_question(self, question: str):
        """Ask with enhanced processing and feedback."""
        if not question.strip():
            print("⚠️  Please enter a research question.")
            return
            
        # Handle follow-up context
        if question.lower() in ['yes', 'expand', 'more', 'continue']:
            if self.last_query:
                print(f"🔄 Expanding analysis of: {self.last_query}")
                question = f"Provide expanded analysis of: {self.last_query}"
            else:
                print("⚠️  No previous query to expand. Please ask a new question.")
                return
        
        self.question_count += 1
        self.last_query = question
        task_id = f"enhanced_task_{self.question_count:03d}"
        
        print(f"\n🔍 ENHANCED ANALYSIS #{self.question_count}")
        print("═" * 60)
        print(f"❓ Question: {question}")
        print("═" * 60)
        
        # Test improved domain detection
        domain_count = self.test_domain_detection(question)
        
        if domain_count < 2:
            print(f"⚠️  Only {domain_count} domain(s) detected. Consider making your question more interdisciplinary.")
        
        print(f"\n⚡ STARTING ENHANCED ANALYSIS...")
        print("─" * 40)
        
        start_time = datetime.now()
        responses = []
        step_count = 0
        
        try:
            async for response in self.oracle.stream(question, self.session_id, task_id):
                responses.append(response)
                content = response.get('content', '')
                
                if not response.get('is_task_complete'):
                    step_count += 1
                    # Show detailed progress
                    if 'Step' in content or 'Executing' in content or 'Completed' in content:
                        print(f"📋 {content}")
                    else:
                        print(f"⚡ {content}")
                else:
                    # Final analysis result
                    duration = (datetime.now() - start_time).total_seconds()
                    
                    print(f"\n🎯 ENHANCED ANALYSIS COMPLETE!")
                    print("═" * 50)
                    print(f"⏱️  Duration: {duration:.1f}s | Steps: {step_count} | Responses: {len(responses)}")
                    
                    if response.get('response_type') == 'data':
                        analysis = response.get('content', {})
                        await self.display_enhanced_analysis(analysis, question)
                    else:
                        print(f"📝 Result: {content}")
                        
                    # Show follow-up suggestions
                    self.suggest_follow_ups(question, analysis if response.get('response_type') == 'data' else {})
                    break
                    
        except Exception as e:
            print(f"❌ Enhanced analysis error: {e}")
            print("   Try rephrasing your question or check your internet connection.")
    
    async def display_enhanced_analysis(self, analysis: dict, original_question: str):
        """Display enhanced analysis with better formatting."""
        if not isinstance(analysis, dict):
            print(f"📝 Analysis: {analysis}")
            return
            
        synthesis = analysis.get('synthesis', {})
        quality_validation = analysis.get('quality_validation', {})
        research_intelligence = analysis.get('research_intelligence', {})
        
        print(f"📊 COMPREHENSIVE RESEARCH SYNTHESIS")
        print("─" * 50)
        
        # Executive Summary with more detail
        summary = synthesis.get('executive_summary', 'No summary available')
        print(f"🎯 EXECUTIVE SUMMARY:")
        print(f"   {summary}")
        
        # Enhanced quality metrics
        confidence = synthesis.get('research_confidence', 'N/A')
        domain_coverage = synthesis.get('domain_coverage', 0)
        quality_score = quality_validation.get('confidence_score', 'N/A')
        quality_issues = quality_validation.get('quality_issues', [])
        
        print(f"\n📈 ANALYSIS QUALITY METRICS:")
        print(f"   Research Confidence: {confidence} {'✅' if isinstance(confidence, (int, float)) and confidence >= 0.7 else '⚠️'}")
        print(f"   Domain Coverage: {domain_coverage} disciplines {'✅' if domain_coverage >= 2 else '⚠️'}")
        print(f"   Quality Score: {quality_score} {'✅' if isinstance(quality_score, (int, float)) and quality_score >= 0.7 else '⚠️'}")
        
        if quality_issues:
            print(f"   Quality Issues: {', '.join(quality_issues)}")
        
        # Domain-specific insights
        if research_intelligence:
            print(f"\n🧬 DOMAIN-SPECIFIC INTELLIGENCE:")
            for domain, data in research_intelligence.items():
                insights = data.get('insights', [])
                evidence_quality = data.get('evidence_quality', 'N/A')
                domain_display = domain.replace('_', ' ').title()
                print(f"   📚 {domain_display}: {len(insights)} insights (Evidence: {evidence_quality})")
                
                # Show top insight from each domain
                if insights:
                    top_insight = insights[0]
                    if isinstance(top_insight, dict):
                        insight_text = top_insight.get('finding', 'N/A')
                        insight_confidence = top_insight.get('confidence', 'N/A')
                        print(f"      💡 Key: {insight_text[:60]}... (Conf: {insight_confidence})")
        
        # Enhanced cross-domain patterns
        cross_patterns = synthesis.get('cross_domain_patterns', {})
        if cross_patterns:
            print(f"\n🔗 CROSS-DOMAIN INSIGHTS:")
            convergent = cross_patterns.get('convergent_findings', [])
            contradictory = cross_patterns.get('contradictory_evidence', [])
            gaps = cross_patterns.get('knowledge_gaps', [])
            
            print(f"   ✅ Convergent Findings: {len(convergent)}")
            print(f"   ⚠️  Contradictory Evidence: {len(contradictory)}")
            print(f"   ❓ Knowledge Gaps: {len(gaps)}")
            
            # Show detailed findings
            if convergent:
                print(f"   🎯 Key Convergent Finding:")
                finding = convergent[0] if isinstance(convergent[0], str) else str(convergent[0])
                print(f"      {finding[:100]}...")
        
        # Novel hypotheses with more detail
        hypotheses = synthesis.get('novel_hypotheses', [])
        if hypotheses:
            print(f"\n💡 NOVEL RESEARCH HYPOTHESES:")
            for i, hypothesis in enumerate(hypotheses[:3], 1):
                if isinstance(hypothesis, dict):
                    hyp_text = hypothesis.get('hypothesis', 'N/A')
                    supporting_domains = hypothesis.get('supporting_domains', [])
                    testability = hypothesis.get('testability', 'N/A')
                    significance = hypothesis.get('significance', 'N/A')
                    
                    print(f"   {i}. {hyp_text[:80]}...")
                    print(f"      Domains: {', '.join(supporting_domains[:3])}")
                    print(f"      Testability: {testability} | Significance: {significance[:30]}...")
                else:
                    print(f"   {i}. {str(hypothesis)[:80]}...")
        
        # Actionable research recommendations
        recommendations = synthesis.get('research_recommendations', {})
        if recommendations:
            print(f"\n🎯 ACTIONABLE RESEARCH RECOMMENDATIONS:")
            
            priority_areas = recommendations.get('priority_directions', [])
            if priority_areas:
                print(f"   📋 Priority Research Areas:")
                for area in priority_areas[:3]:
                    print(f"      • {area}")
                    
            methodologies = recommendations.get('methodological_innovations', [])
            if methodologies:
                print(f"   🔬 Recommended Methodologies:")
                for method in methodologies[:3]:
                    print(f"      • {method}")
                    
            collaborations = recommendations.get('collaboration_opportunities', [])
            if collaborations:
                print(f"   🤝 Collaboration Opportunities:")
                for collab in collaborations[:3]:
                    print(f"      • {collab}")
    
    def suggest_follow_ups(self, original_question: str, analysis: dict):
        """Suggest intelligent follow-up questions."""
        print(f"\n💬 SUGGESTED FOLLOW-UP QUESTIONS:")
        print("─" * 35)
        
        # Extract key concepts from the original question
        synthesis = analysis.get('synthesis', {})
        hypotheses = synthesis.get('novel_hypotheses', [])
        recommendations = synthesis.get('research_recommendations', {})
        
        suggestions = []
        
        # Based on novel hypotheses
        if hypotheses:
            first_hypothesis = hypotheses[0]
            if isinstance(first_hypothesis, dict):
                hyp_text = first_hypothesis.get('hypothesis', '')
                if hyp_text:
                    suggestions.append(f"How could we test the hypothesis: {hyp_text[:50]}...?")
        
        # Based on recommendations
        priority_areas = recommendations.get('priority_directions', [])
        if priority_areas:
            suggestions.append(f"What are the main challenges in {priority_areas[0].lower()}?")
        
        # Based on knowledge gaps
        cross_patterns = synthesis.get('cross_domain_patterns', {})
        gaps = cross_patterns.get('knowledge_gaps', [])
        if gaps:
            suggestions.append(f"How can we address the knowledge gap: {gaps[0][:50]}...?")
        
        # Generic smart follow-ups
        if 'quantum' in original_question.lower():
            suggestions.append("What are the main technical barriers to implementing this?")
        if 'climate' in original_question.lower():
            suggestions.append("What are the economic implications of this approach?")
        if 'AI' in original_question.lower() or 'artificial intelligence' in original_question.lower():
            suggestions.append("What ethical considerations should we address?")
        
        # Show suggestions
        for i, suggestion in enumerate(suggestions[:4], 1):
            print(f"   {i}. {suggestion}")
        
        if not suggestions:
            print("   • What are the main challenges in implementing this?")
            print("   • What ethical considerations should we address?")
            print("   • How could we measure the success of this approach?")
    
    def show_enhanced_help(self):
        """Show enhanced help with better examples."""
        print(f"\n📚 ENHANCED NEXUS ORACLE HELP")
        print("═" * 40)
        print("🎯 EXAMPLE COMPLEX RESEARCH QUESTIONS:")
        print("   • How can quantum computing accelerate climate modeling while ensuring data privacy?")
        print("   • What are the psychological and economic factors behind successful remote work adoption?")
        print("   • How do AI algorithms in healthcare affect patient trust and treatment outcomes?")
        print("   • What role can biotechnology play in sustainable agriculture and food security?")
        print("   • How do social media platforms influence democratic processes and voter behavior?")
        print()
        print("🛠️ ENHANCED COMMANDS:")
        print("   • 'help' - Show this enhanced help")
        print("   • 'status' - Show detailed Oracle state")
        print("   • 'test <question>' - Test domain detection without full analysis")
        print("   • 'expand' or 'yes' - Expand the last analysis")
        print("   • 'clear' - Clear Oracle memory")
        print("   • 'quit' or 'exit' - End session")
        print()
        print("💡 ENHANCED TIPS:")
        print("   • Use multiple disciplines in your questions for richer analysis")
        print("   • Ask about implementations, challenges, and implications")
        print("   • Follow up on novel hypotheses and recommendations")
        print("   • The Oracle remembers context across questions")
    
    async def test_detection_only(self, question: str):
        """Test domain detection without full analysis."""
        print(f"\n🧪 DOMAIN DETECTION TEST")
        print("─" * 30)
        domain_count = self.test_domain_detection(question)
        print(f"\n📊 Detection Summary: {domain_count} domains identified")
        if domain_count >= 3:
            print("✅ Excellent - Rich interdisciplinary analysis expected")
        elif domain_count == 2:
            print("👍 Good - Solid cross-domain analysis expected")
        else:
            print("⚠️  Limited - Consider adding more interdisciplinary elements")
    
    async def run_enhanced_session(self):
        """Run the enhanced interactive session."""
        if not await self.initialize():
            return
            
        print(f"\n💬 Enhanced Oracle ready! (Type your question and press Enter)")
        print("💡 Try 'help' for examples or 'test <question>' to preview domain detection")
        
        while True:
            try:
                user_input = input(f"\n🔮 Enhanced> ").strip()
                
                if not user_input:
                    continue
                    
                # Handle enhanced commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print(f"\n👋 Enhanced session ended. Asked {self.question_count} questions.")
                    break
                elif user_input.lower() == 'help':
                    self.show_enhanced_help()
                    continue
                elif user_input.lower() == 'status':
                    self.show_status()
                    continue
                elif user_input.lower() == 'clear':
                    self.oracle.clear_state()
                    self.last_query = ""
                    print(f"🔄 Enhanced Oracle memory cleared!")
                    continue
                elif user_input.lower().startswith('test '):
                    test_question = user_input[5:].strip()
                    if test_question:
                        await self.test_detection_only(test_question)
                    else:
                        print("⚠️  Please provide a question to test. Example: test How can AI help climate change?")
                    continue
                
                # Process as enhanced research question
                await self.ask_enhanced_question(user_input)
                
            except KeyboardInterrupt:
                print(f"\n\n👋 Enhanced session interrupted. Asked {self.question_count} questions.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Try asking your question again.")
    
    def show_status(self):
        """Show detailed Oracle status."""
        print(f"\n🤖 ENHANCED ORACLE STATUS")
        print("═" * 35)
        print(f"Session ID: {self.session_id}")
        print(f"Questions Asked: {self.question_count}")
        print(f"Last Query: {self.last_query[:50]}..." if self.last_query else "Last Query: None")
        print(f"Query History: {len(self.oracle.query_history)} entries")
        print(f"Research Cache: {len(self.oracle.research_intelligence)} domains")
        print(f"Context ID: {self.oracle.context_id}")
        
        if self.oracle.research_intelligence:
            print(f"\nCached Domains:")
            for domain in self.oracle.research_intelligence.keys():
                print(f"   • {domain.replace('_', ' ').title()}")

if __name__ == "__main__":
    print("🚀 Starting Enhanced Interactive Nexus Oracle...")
    
    session = ImprovedOracleSession()
    asyncio.run(session.run_enhanced_session())