#!/usr/bin/env python3
"""Nexus Oracle with First Principles Question Deconstruction."""

import os
import sys
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any

# Set up environment
sys.path.insert(0, './src')
sys.path.insert(0, '.')
os.environ['GOOGLE_API_KEY'] = os.environ.get('GOOGLE_API_KEY', 'your-api-key-here')

class FirstPrinciplesOracle:
    """Oracle that deconstructs questions using first principles before analysis."""
    
    def __init__(self):
        self.oracle = None
        self.session_id = f"first_principles_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.question_count = 0
        self.clarification_state = {}
        
    async def initialize(self):
        """Initialize the First Principles Oracle."""
        print("🧠 NEXUS ORACLE - FIRST PRINCIPLES RESEARCH COLLABORATOR")
        print("=" * 70)
        print("🎯 REVOLUTIONARY APPROACH:")
        print("   • Deconstructs questions using first principles thinking")
        print("   • Interactive clarification before analysis begins")
        print("   • Collaborative research partnership experience")
        print("   • Precise, targeted analysis based on refined understanding")
        print("=" * 70)
        
        try:
            from a2a_mcp.agents.nexus_oracle_agent import NexusOracleAgent
            self.oracle = NexusOracleAgent()
            
            print(f"✅ First Principles Oracle initialized: {self.oracle.agent_name}")
            print(f"🎯 Session ID: {self.session_id}")
            print(f"🧠 Ready for collaborative research inquiry!")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize Oracle: {e}")
            return False
    
    async def deconstruct_question(self, question: str) -> Dict[str, Any]:
        """Deconstruct question using first principles thinking."""
        print(f"\n🧠 FIRST PRINCIPLES DECONSTRUCTION")
        print("═" * 50)
        print(f"📝 Original Question: {question}")
        print("─" * 50)
        
        # Use AI to analyze the question along first principles dimensions
        from google import genai
        client = genai.Client()
        
        deconstruction_prompt = f"""
        You are a master research strategist. Analyze this research question using first principles thinking:
        
        QUESTION: "{question}"
        
        Break down this question along these fundamental dimensions:
        
        1. CORE COMPONENTS: What are the key entities, concepts, or systems involved?
        2. RELATIONSHIPS: How do these components interact or relate to each other?
        3. CONTEXT: What's the broader environment, situation, or domain?
        4. CONSTRAINTS: What are the limitations, boundaries, or constraints?
        5. OBJECTIVES: What is the user trying to achieve or understand?
        6. SCOPE: What should be included or excluded from analysis?
        7. ASSUMPTIONS: What unstated assumptions or premises are being made?
        8. PERSPECTIVES: From whose viewpoint should this be analyzed?
        9. TEMPORAL: What timeframe or temporal considerations are relevant?
        10. SUCCESS: How would we measure a successful answer?
        
        For each dimension, identify what is CLEAR vs what is AMBIGUOUS in the original question.
        
        Then identify the 2-3 MOST CRITICAL ambiguities that need clarification for precise analysis.
        
        Provide your analysis in JSON format:
        {{
            "dimensions_analysis": {{
                "core_components": {{"clear": "...", "ambiguous": "..."}},
                "relationships": {{"clear": "...", "ambiguous": "..."}},
                "context": {{"clear": "...", "ambiguous": "..."}},
                "constraints": {{"clear": "...", "ambiguous": "..."}},
                "objectives": {{"clear": "...", "ambiguous": "..."}},
                "scope": {{"clear": "...", "ambiguous": "..."}},
                "assumptions": {{"clear": "...", "ambiguous": "..."}},
                "perspectives": {{"clear": "...", "ambiguous": "..."}},
                "temporal": {{"clear": "...", "ambiguous": "..."}},
                "success": {{"clear": "...", "ambiguous": "..."}}
            }},
            "critical_ambiguities": [
                {{"dimension": "...", "issue": "...", "impact": "..."}},
                {{"dimension": "...", "issue": "...", "impact": "..."}},
                {{"dimension": "...", "issue": "...", "impact": "..."}}
            ],
            "precision_score": 0.0-1.0
        }}
        """
        
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=deconstruction_prompt,
                config={
                    "temperature": 0.1,
                    "response_mime_type": "application/json"
                }
            )
            
            analysis = json.loads(response.text)
            return analysis
            
        except Exception as e:
            print(f"⚠️  Deconstruction error: {e}")
            # Fallback to manual analysis
            return self._manual_deconstruction(question)
    
    def _manual_deconstruction(self, question: str) -> Dict[str, Any]:
        """Fallback manual deconstruction."""
        return {
            "dimensions_analysis": {"core_components": {"clear": "Basic concepts", "ambiguous": "Specific focus"}},
            "critical_ambiguities": [
                {"dimension": "objectives", "issue": "Unclear specific goals", "impact": "May analyze wrong aspects"},
                {"dimension": "scope", "issue": "Undefined boundaries", "impact": "Analysis may be too broad/narrow"},
                {"dimension": "perspectives", "issue": "Unclear viewpoint", "impact": "May miss key stakeholder concerns"}
            ],
            "precision_score": 0.4
        }
    
    async def generate_clarifying_questions(self, analysis: Dict[str, Any], original_question: str) -> List[str]:
        """Generate targeted clarifying questions based on critical ambiguities."""
        critical_ambiguities = analysis.get('critical_ambiguities', [])
        
        from google import genai
        client = genai.Client()
        
        question_prompt = f"""
        Based on this first principles analysis of the research question: "{original_question}"
        
        Critical Ambiguities Identified:
        {json.dumps(critical_ambiguities, indent=2)}
        
        Generate 2-3 targeted clarifying questions that would help resolve these ambiguities.
        Each question should:
        1. Be specific and actionable
        2. Offer clear choices or examples
        3. Help narrow down the analysis focus
        4. Feel natural and conversational
        
        Format as JSON array:
        [
            "Question 1 with specific choices?",
            "Question 2 offering examples?",
            "Question 3 about scope/perspective?"
        ]
        """
        
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=question_prompt,
                config={
                    "temperature": 0.2,
                    "response_mime_type": "application/json"
                }
            )
            
            questions = json.loads(response.text)
            return questions[:3]  # Max 3 questions
            
        except Exception as e:
            print(f"⚠️  Question generation error: {e}")
            return self._default_clarifying_questions(original_question)
    
    def _default_clarifying_questions(self, question: str) -> List[str]:
        """Fallback clarifying questions."""
        return [
            f"What specific aspect of this topic are you most interested in exploring?",
            f"Are you looking for technical analysis, implementation guidance, or strategic overview?",
            f"What would be the most valuable outcome from this research analysis?"
        ]
    
    async def synthesize_refined_question(self, original: str, clarifications: List[str]) -> str:
        """Synthesize user responses into a refined, precise question."""
        from google import genai
        client = genai.Client()
        
        synthesis_prompt = f"""
        Original Question: "{original}"
        
        User Clarifications:
        {chr(10).join([f"- {clarification}" for clarification in clarifications])}
        
        Synthesize this into a refined, precise research question that:
        1. Incorporates the user's clarifications
        2. Is specific and actionable
        3. Maintains the original intent but with better precision
        4. Would lead to targeted, valuable analysis
        
        Return just the refined question as plain text.
        """
        
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=synthesis_prompt,
                config={"temperature": 0.1}
            )
            
            return response.text.strip()
            
        except Exception as e:
            print(f"⚠️  Synthesis error: {e}")
            return f"Refined analysis of: {original} (incorporating: {', '.join(clarifications)})"
    
    def display_deconstruction_analysis(self, analysis: Dict[str, Any]):
        """Display the first principles analysis."""
        dimensions = analysis.get('dimensions_analysis', {})
        ambiguities = analysis.get('critical_ambiguities', [])
        precision = analysis.get('precision_score', 0.5)
        
        print(f"🎯 PRECISION SCORE: {precision:.1f}/1.0")
        if precision >= 0.8:
            print("   ✅ Question is well-defined - minimal clarification needed")
        elif precision >= 0.6:
            print("   👍 Question is moderately clear - some clarification helpful")
        else:
            print("   ⚠️  Question has significant ambiguities - clarification essential")
        
        print(f"\n📊 CRITICAL AMBIGUITIES IDENTIFIED:")
        for i, ambiguity in enumerate(ambiguities[:3], 1):
            dimension = ambiguity.get('dimension', 'Unknown')
            issue = ambiguity.get('issue', 'Not specified')
            impact = ambiguity.get('impact', 'Unknown impact')
            print(f"   {i}. {dimension.title()}: {issue}")
            print(f"      Impact: {impact}")
        
        print(f"\n💡 WHAT THIS MEANS:")
        if precision < 0.6:
            print("   🔍 Your question touches on multiple complex areas")
            print("   🎯 Clarification will lead to much more valuable analysis")
            print("   🤝 Let's work together to refine your inquiry")
        else:
            print("   👍 Your question is well-structured")
            print("   🔍 Brief clarification will optimize the analysis")
    
    async def interactive_clarification(self, question: str) -> str:
        """Interactive clarification process using first principles."""
        self.question_count += 1
        
        print(f"\n🔬 FIRST PRINCIPLES RESEARCH COLLABORATION #{self.question_count}")
        print("═" * 60)
        
        # Step 1: Deconstruct the question
        print("🧠 Analyzing your question using first principles...")
        analysis = await self.deconstruct_question(question)
        
        # Step 2: Display analysis
        self.display_deconstruction_analysis(analysis)
        
        # Step 3: Check if clarification is needed
        precision = analysis.get('precision_score', 0.5)
        if precision >= 0.8:
            print(f"\n✅ Your question is well-defined! Proceeding with enhanced analysis...")
            return question
        
        # Step 4: Generate clarifying questions
        print(f"\n❓ COLLABORATIVE CLARIFICATION:")
        print("─" * 35)
        clarifying_questions = await self.generate_clarifying_questions(analysis, question)
        
        clarifications = []
        for i, q in enumerate(clarifying_questions, 1):
            print(f"\n{i}. {q}")
            response = input(f"   Your response: ").strip()
            if response:
                clarifications.append(response)
        
        # Step 5: Synthesize refined question
        if clarifications:
            print(f"\n🎯 SYNTHESIZING REFINED QUESTION...")
            refined_question = await self.synthesize_refined_question(question, clarifications)
            
            print(f"\n📝 REFINED RESEARCH QUESTION:")
            print("─" * 40)
            print(f"   {refined_question}")
            
            # Confirm with user
            confirmation = input(f"\n✅ Does this capture what you want to explore? (y/n/edit): ").strip().lower()
            
            if confirmation == 'y' or confirmation == 'yes':
                print(f"🎉 Perfect! Starting enhanced analysis of refined question...")
                return refined_question
            elif confirmation.startswith('edit'):
                edit = input(f"   Please provide your refinement: ").strip()
                if edit:
                    return edit
            
        return question
    
    async def run_first_principles_session(self):
        """Run the first principles research collaboration session."""
        if not await self.initialize():
            return
            
        print(f"\n💬 Ready for first principles research collaboration!")
        print("💡 I'll help you refine your questions before providing analysis")
        
        while True:
            try:
                user_input = input(f"\n🧠 Research Question> ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print(f"\n👋 First principles session ended. Refined {self.question_count} questions.")
                    break
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                # First principles clarification process
                refined_question = await self.interactive_clarification(user_input)
                
                # Now run enhanced analysis on refined question
                print(f"\n🚀 ENHANCED ANALYSIS OF REFINED QUESTION")
                print("═" * 55)
                
                session_id = f"{self.session_id}_q{self.question_count}"
                task_id = f"refined_task_{self.question_count:03d}"
                
                # Show domain preview for refined question
                analysis = self.oracle.analyze_research_dependencies(refined_question)
                domains = list(analysis['domain_groups'].keys())
                print(f"🎯 Domains Detected: {', '.join(domains)} ({len(domains)} domains)")
                
                # Run full analysis
                print(f"⚡ Starting enhanced analysis...")
                
                responses = []
                async for response in self.oracle.stream(refined_question, session_id, task_id):
                    responses.append(response)
                    content = response.get('content', '')
                    
                    if not response.get('is_task_complete'):
                        if 'Step' in content or 'Executing' in content or 'Completed' in content:
                            print(f"📋 {content}")
                        else:
                            print(f"⚡ {content}")
                    else:
                        print(f"\n🎯 FIRST PRINCIPLES ANALYSIS COMPLETE!")
                        print("═" * 50)
                        
                        if response.get('response_type') == 'data':
                            analysis_result = response.get('content', {})
                            synthesis = analysis_result.get('synthesis', {})
                            summary = synthesis.get('executive_summary', 'Analysis completed')
                            confidence = synthesis.get('research_confidence', 'N/A')
                            
                            print(f"📊 RESULTS:")
                            print(f"   Confidence: {confidence}")
                            print(f"   Responses: {len(responses)}")
                            print(f"📝 SUMMARY: {summary}")
                            
                            print(f"\n💡 FIRST PRINCIPLES IMPACT:")
                            print(f"   ✅ Refined question led to targeted analysis")
                            print(f"   🎯 Analysis directly addresses your refined inquiry")
                            print(f"   🤝 Collaborative approach improved precision")
                        break
                
            except KeyboardInterrupt:
                print(f"\n\n👋 First principles session interrupted.")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    def show_help(self):
        """Show first principles help."""
        print(f"\n📚 FIRST PRINCIPLES RESEARCH COLLABORATION")
        print("═" * 50)
        print("🧠 HOW IT WORKS:")
        print("   1. You ask a research question")
        print("   2. I deconstruct it using first principles thinking")
        print("   3. We collaborate to refine and clarify the question")
        print("   4. I provide enhanced analysis of the refined question")
        print()
        print("🎯 EXAMPLE TRANSFORMATION:")
        print("   Original: 'How can AI help climate change?'")
        print("   Refined: 'How can machine learning optimize renewable energy")
        print("            grid management in developing countries over the next")
        print("            5 years, and what are the key implementation barriers?'")
        print()
        print("💡 BENEFITS:")
        print("   • More precise, targeted analysis")
        print("   • Better understanding of your real questions")
        print("   • Collaborative research partnership")
        print("   • Learn to think more clearly about complex problems")

if __name__ == "__main__":
    print("🚀 Starting First Principles Nexus Oracle...")
    
    oracle = FirstPrinciplesOracle()
    asyncio.run(oracle.run_first_principles_session())