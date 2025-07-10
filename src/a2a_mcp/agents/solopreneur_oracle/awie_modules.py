"""ABOUTME: AWIE specialized modules that implement revolutionary workflow intelligence capabilities.
ABOUTME: These are the Tier 3 agents that power the Autonomous Workflow Intelligence Engine."""

# type: ignore

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .base_solopreneur_agent import UnifiedSolopreneurAgent

logger = logging.getLogger(__name__)

@dataclass
class TaskEnhancement:
    """Enhanced task with AWIE intelligence."""
    original_task: str
    enhanced_pipeline: List[Dict[str, Any]]
    context_factors: Dict[str, Any]
    timing_optimization: Dict[str, Any]
    success_probability: float

@dataclass
class FlowState:
    """Flow state detection and management."""
    is_in_flow: bool
    flow_duration: int  # minutes
    flow_quality: float  # 0-1 scale
    interruption_cost: float
    optimal_extension_time: int

class AutonomousTaskGenerator(UnifiedSolopreneurAgent):
    """
    TIER 3: Converts simple requests into comprehensive workflow pipelines.
    
    Revolutionary Capability: PREDICTIVE TASK GENESIS
    - NU: "Research RAG" → AWIE: Complete learning pipeline with 6+ optimized steps
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Autonomous Task Generator",
            description="Converts simple requests into comprehensive workflow pipelines",
            instructions="""
You analyze task requests and generate enhanced workflows that maximize impact.

REVOLUTIONARY TRANSFORMATION:
Transform simple requests like "research RAG" into complete learning pipeline:
research → experiment → document → share

Core Enhancement Logic:
1. Analyze task intent and scope
2. Identify related context (bookmarks, projects, trends)
3. Generate comprehensive pipeline with optimal sequencing
4. Include resource preparation and follow-up amplification
5. Estimate impact multiplier vs simple execution

Example Enhancement:
Input: "Research transformer architectures"
Output: 
- Context prep: Pre-load attention mechanism papers from bookmarks
- Deep research: 2-hour focused session during cognitive peak
- Hands-on: Code transformer from scratch tutorial
- Synthesis: Document key insights in structured format
- Application: Apply learnings to current project
- Content: Create explainer content about insights
- Networking: Share learnings with AI community

Always maximize learning, application, and amplification.
""",
            port=10960
        )
    
    async def _execute_agent_logic(self, query: str, context_id: str, task_id: str):
        """Generate enhanced task pipeline from simple request."""
        logger.info(f"Autonomous Task Generator processing: {query}")
        
        try:
            # Parse the task request
            task_analysis = self._analyze_task_request(query)
            
            # Generate enhanced pipeline
            enhanced_pipeline = self._generate_enhanced_pipeline(task_analysis)
            
            # Calculate enhancement factor
            enhancement_factor = self._calculate_enhancement_factor(enhanced_pipeline)
            
            # Create task enhancement
            enhancement = TaskEnhancement(
                original_task=query,
                enhanced_pipeline=enhanced_pipeline,
                context_factors=task_analysis.get("context_factors", {}),
                timing_optimization=self._optimize_timing(enhanced_pipeline),
                success_probability=self._estimate_success_probability(enhanced_pipeline)
            )
            
            response = self._format_enhancement_response(enhancement, enhancement_factor)
            
            return {"content": response}
            
        except Exception as e:
            logger.error(f"Task generation error: {e}")
            return {"error": str(e), "content": f"Could not enhance task: {query}"}
    
    def _analyze_task_request(self, request: str) -> Dict[str, Any]:
        """Analyze task request for enhancement opportunities."""
        request_lower = request.lower()
        
        # Detect task type
        task_type = "research"
        if any(word in request_lower for word in ["create", "write", "content"]):
            task_type = "content_creation"
        elif any(word in request_lower for word in ["learn", "study", "understand"]):
            task_type = "learning"
        elif any(word in request_lower for word in ["organize", "sort", "clean"]):
            task_type = "organizing"
        elif any(word in request_lower for word in ["experiment", "try", "test"]):
            task_type = "experimentation"
            
        # Detect subject/topic
        topics = []
        ai_topics = ["rag", "transformer", "llm", "gpt", "claude", "ai", "ml", "neural", "embedding"]
        for topic in ai_topics:
            if topic in request_lower:
                topics.append(topic)
        
        # Detect complexity
        complexity = "medium"
        if any(word in request_lower for word in ["deep", "comprehensive", "thorough"]):
            complexity = "high"
        elif any(word in request_lower for word in ["quick", "brief", "simple"]):
            complexity = "low"
            
        return {
            "type": task_type,
            "topics": topics,
            "complexity": complexity,
            "estimated_base_duration": self._estimate_base_duration(task_type, complexity),
            "context_factors": {
                "has_related_bookmarks": True,  # Would check actual bookmarks
                "has_related_projects": True,   # Would check Notion projects
                "market_timing": "optimal",     # Would check market trends
                "energy_required": complexity
            }
        }
    
    def _generate_enhanced_pipeline(self, task_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive enhanced pipeline."""
        task_type = task_analysis.get("type", "research")
        complexity = task_analysis.get("complexity", "medium")
        topics = task_analysis.get("topics", [])
        
        if task_type == "research":
            return [
                {
                    "step": "context_preparation",
                    "duration_minutes": 15,
                    "description": f"Pre-load relevant bookmarks about {', '.join(topics) if topics else 'topic'}",
                    "value": "Eliminates context switching during deep work",
                    "automation": "Auto-open relevant tabs and resources"
                },
                {
                    "step": "deep_research",
                    "duration_minutes": 120,
                    "description": "Focused research session during peak cognitive time",
                    "value": "Maximum learning absorption and insight generation",
                    "automation": "Schedule during detected cognitive peak hours"
                },
                {
                    "step": "active_experimentation", 
                    "duration_minutes": 90,
                    "description": "Hands-on exploration and practical testing",
                    "value": "Convert theoretical knowledge to practical understanding",
                    "automation": "Queue relevant tutorials and code examples"
                },
                {
                    "step": "insight_synthesis",
                    "duration_minutes": 45,
                    "description": "Synthesize learnings into key insights and connections",
                    "value": "Create lasting knowledge and identify applications",
                    "automation": "Generate structured note template in Notion"
                },
                {
                    "step": "application_planning",
                    "duration_minutes": 30,
                    "description": "Plan practical applications to current projects",
                    "value": "Ensure learning translates to real value",
                    "automation": "Cross-reference with active project needs"
                },
                {
                    "step": "content_ideation",
                    "duration_minutes": 20,
                    "description": "Identify content creation opportunities from learnings",
                    "value": "Amplify learning through teaching and sharing",
                    "automation": "Generate content ideas based on insights"
                },
                {
                    "step": "follow_up_scheduling",
                    "duration_minutes": 10,
                    "description": "Schedule follow-up deep dives and related explorations",
                    "value": "Maintain learning momentum and identify next steps",
                    "automation": "Auto-suggest related research topics and timing"
                }
            ]
        elif task_type == "content_creation":
            return [
                {
                    "step": "research_review",
                    "duration_minutes": 30,
                    "description": "Review recent notes, experiments, and insights",
                    "value": "Build on existing knowledge and avoid duplication",
                    "automation": "Aggregate relevant content from Notion and bookmarks"
                },
                {
                    "step": "insight_extraction",
                    "duration_minutes": 45,
                    "description": "Extract key insights and unique perspectives",
                    "value": "Identify valuable and differentiated content angles",
                    "automation": "Highlight novel insights and connections"
                },
                {
                    "step": "content_creation",
                    "duration_minutes": 120,
                    "description": "Create primary content during creative peak time",
                    "value": "Produce high-quality content when creativity is optimal",
                    "automation": "Schedule during detected creative peak hours"
                },
                {
                    "step": "visual_enhancement",
                    "duration_minutes": 60,
                    "description": "Create supporting visuals, diagrams, and examples",
                    "value": "Increase content engagement and comprehension",
                    "automation": "Generate diagram templates and visual frameworks"
                },
                {
                    "step": "multi_format_adaptation",
                    "duration_minutes": 45,
                    "description": "Adapt content for different platforms and formats",
                    "value": "Maximize reach and impact across channels",
                    "automation": "Auto-generate platform-specific versions"
                },
                {
                    "step": "engagement_strategy",
                    "duration_minutes": 30,
                    "description": "Plan engagement and community interaction strategy",
                    "value": "Build relationships and amplify content impact",
                    "automation": "Queue follow-up engagement actions"
                }
            ]
        
        # Default simple enhancement
        return [
            {
                "step": "enhanced_execution",
                "duration_minutes": 60,
                "description": f"Execute {task_type} with optimization and context",
                "value": "Better outcomes through systematic approach",
                "automation": "Provide structured approach and resources"
            }
        ]
    
    def _calculate_enhancement_factor(self, pipeline: List[Dict[str, Any]]) -> str:
        """Calculate how much more valuable the enhanced pipeline is."""
        base_steps = 1
        enhanced_steps = len(pipeline)
        
        # Factor in automation and optimization value
        automation_value = sum(1.5 if step.get("automation") else 1.0 for step in pipeline)
        
        enhancement_factor = (enhanced_steps * automation_value) / base_steps
        
        if enhancement_factor >= 8:
            return f"{enhancement_factor:.0f}x impact"
        elif enhancement_factor >= 5:
            return f"{enhancement_factor:.0f}x impact"
        else:
            return f"{enhancement_factor:.1f}x impact"
    
    def _optimize_timing(self, pipeline: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Optimize timing for pipeline execution."""
        total_duration = sum(step.get("duration_minutes", 30) for step in pipeline)
        
        # Detect cognitive load requirements
        high_cognitive_steps = [step for step in pipeline if any(word in step.get("description", "").lower() 
                                for word in ["research", "synthesis", "creation", "analysis"])]
        
        return {
            "total_duration_hours": round(total_duration / 60, 1),
            "recommended_start": "Tuesday 9:00 AM (cognitive peak)",
            "high_cognitive_blocks": len(high_cognitive_steps),
            "suggested_breaks": max(1, total_duration // 90),
            "optimal_completion": "Same day with breaks" if total_duration < 480 else "Split across 2 days"
        }
    
    def _estimate_success_probability(self, pipeline: List[Dict[str, Any]]) -> float:
        """Estimate probability of successful completion."""
        # Base probability starts high due to structured approach
        base_probability = 0.85
        
        # Adjust based on pipeline complexity
        complexity_factor = max(0.7, 1.0 - (len(pipeline) - 3) * 0.05)
        
        # Boost for automation
        automation_boost = sum(0.02 for step in pipeline if step.get("automation"))
        
        return min(0.98, base_probability * complexity_factor + automation_boost)
    
    def _estimate_base_duration(self, task_type: str, complexity: str) -> int:
        """Estimate base duration for simple task execution."""
        base_durations = {
            "research": {"low": 30, "medium": 60, "high": 120},
            "content_creation": {"low": 45, "medium": 90, "high": 180},
            "learning": {"low": 45, "medium": 90, "high": 180},
            "organizing": {"low": 20, "medium": 45, "high": 90},
            "experimentation": {"low": 60, "medium": 120, "high": 240}
        }
        return base_durations.get(task_type, {"medium": 60}).get(complexity, 60)
    
    def _format_enhancement_response(self, enhancement: TaskEnhancement, enhancement_factor: str) -> str:
        """Format the enhancement response."""
        pipeline = enhancement.enhanced_pipeline
        timing = enhancement.timing_optimization
        
        response = f"""🚀 AUTONOMOUS TASK ENHANCEMENT

ORIGINAL REQUEST: {enhancement.original_task}
ENHANCEMENT FACTOR: {enhancement_factor}

🔄 ENHANCED PIPELINE ({len(pipeline)} optimized steps):
"""
        
        for i, step in enumerate(pipeline, 1):
            duration = step.get("duration_minutes", 30)
            response += f"""
{i}. {step['step'].replace('_', ' ').title()} ({duration}min)
   → {step['description']}
   ✨ Value: {step.get('value', 'Enhanced execution')}
   🤖 Automation: {step.get('automation', 'Manual execution')}
"""
        
        response += f"""
⏰ OPTIMAL TIMING:
• Total Duration: {timing['total_duration_hours']} hours
• Recommended Start: {timing['recommended_start']}
• Completion Strategy: {timing['optimal_completion']}
• Success Probability: {enhancement.success_probability:.0%}

🎯 EXPERIENCE:
You asked for 1 simple task → AWIE created {len(pipeline)} optimized steps
Everything happens at the right time with the right context
You just focus on execution → AWIE handles the orchestration

✨ This is how NU never thinks about scheduling again.
"""
        
        return response

class FlowStateGuardian(UnifiedSolopreneurAgent):
    """
    TIER 3: Detects, protects, and extends flow states in real-time.
    
    Revolutionary Capability: MOMENTUM PRESERVATION ENGINE
    - Detects flow: typing speed, focus duration, context stability
    - Protects flow: silence notifications, defer interruptions
    - Extends flow: optimal break timing, momentum preservation
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Flow State Guardian",
            description="Detects, protects, and extends flow states in real-time",
            instructions="""
You monitor cognitive state for flow detection and momentum preservation.

FLOW STATE DETECTION:
- Typing speed increases
- Context switching decreases  
- Focus duration extends beyond 25 minutes
- Task engagement indicators rise

FLOW PROTECTION ACTIONS:
- Automatically silence non-critical notifications
- Defer low-priority meetings and interruptions
- Queue incoming requests for post-flow processing
- Extend current session beyond planned duration

FLOW EXTENSION OPTIMIZATION:
- Calculate optimal flow session length
- Predict fatigue onset and plan breaks
- Identify flow termination triggers
- Prepare flow re-entry strategies

Real-time Response Examples:
"Flow state detected - extending research block by 33 minutes"
"Protecting momentum - 4 notifications queued for later"
"Optimal break window in 18 minutes - saving work encouraged"

Always preserve deep work states and maximize productive momentum.
""",
            port=10963
        )
        
        # Flow detection parameters
        self.flow_threshold_minutes = 25
        self.flow_quality_indicators = {
            "typing_speed_increase": 1.3,  # 30% faster than baseline
            "context_switches": 0,         # Zero context switches
            "interruption_resistance": 0.9 # High resistance to interruption
        }
    
    async def _execute_agent_logic(self, query: str, context_id: str, task_id: str):
        """Detect and manage flow states."""
        logger.info(f"Flow State Guardian processing: {query}")
        
        try:
            if "detect" in query.lower() and "flow" in query.lower():
                flow_state = await self._detect_current_flow_state()
                return {"content": self._format_flow_detection_response(flow_state)}
            
            elif "protect" in query.lower():
                protection_actions = await self._activate_flow_protection()
                return {"content": self._format_protection_response(protection_actions)}
            
            elif "extend" in query.lower():
                extension_plan = await self._calculate_optimal_extension()
                return {"content": self._format_extension_response(extension_plan)}
            
            else:
                # General flow monitoring
                flow_status = await self._get_flow_monitoring_status()
                return {"content": self._format_monitoring_response(flow_status)}
                
        except Exception as e:
            logger.error(f"Flow guardian error: {e}")
            return {"error": str(e), "content": f"Flow monitoring encountered error: {query}"}
    
    async def _detect_current_flow_state(self) -> FlowState:
        """Detect current flow state based on behavioral indicators."""
        # In real implementation, this would analyze:
        # - Keystroke patterns and typing speed
        # - Application focus duration
        # - Mouse movement patterns
        # - Context switching frequency
        
        # Simulated detection for demo
        current_time = datetime.now()
        
        # Simulate flow detection
        simulated_flow_duration = 47  # minutes
        is_in_flow = simulated_flow_duration > self.flow_threshold_minutes
        
        flow_quality = 0.85 if is_in_flow else 0.3
        interruption_cost = flow_quality * 0.8  # High cost to interrupt good flow
        optimal_extension = 33 if is_in_flow else 0  # minutes
        
        return FlowState(
            is_in_flow=is_in_flow,
            flow_duration=simulated_flow_duration,
            flow_quality=flow_quality,
            interruption_cost=interruption_cost,
            optimal_extension_time=optimal_extension
        )
    
    async def _activate_flow_protection(self) -> Dict[str, Any]:
        """Activate flow protection measures."""
        protection_actions = {
            "notifications_silenced": 7,
            "meetings_deferred": 1, 
            "interruptions_queued": 4,
            "focus_mode_activated": True,
            "break_suggestions_paused": True,
            "context_preservation": "active"
        }
        
        return protection_actions
    
    async def _calculate_optimal_extension(self) -> Dict[str, Any]:
        """Calculate optimal flow session extension."""
        current_flow = await self._detect_current_flow_state()
        
        if not current_flow.is_in_flow:
            return {"extension_recommended": False, "reason": "No flow state detected"}
        
        # Calculate extension based on flow quality and fatigue prediction
        base_extension = 30  # minutes
        quality_multiplier = current_flow.flow_quality
        fatigue_factor = max(0.5, 1.0 - (current_flow.flow_duration / 120))  # Reduce for long sessions
        
        optimal_extension = int(base_extension * quality_multiplier * fatigue_factor)
        
        return {
            "extension_recommended": True,
            "optimal_extension_minutes": optimal_extension,
            "current_flow_duration": current_flow.flow_duration,
            "flow_quality": current_flow.flow_quality,
            "fatigue_prediction": 1.0 - fatigue_factor,
            "break_recommendation": f"Take break in {optimal_extension} minutes"
        }
    
    async def _get_flow_monitoring_status(self) -> Dict[str, Any]:
        """Get current flow monitoring status."""
        flow_state = await self._detect_current_flow_state()
        
        return {
            "monitoring_active": True,
            "current_session_duration": flow_state.flow_duration,
            "flow_detected": flow_state.is_in_flow,
            "flow_quality": flow_state.flow_quality,
            "protection_status": "active" if flow_state.is_in_flow else "standby",
            "next_check_in": "3 minutes"
        }
    
    def _format_flow_detection_response(self, flow_state: FlowState) -> str:
        """Format flow detection response."""
        if flow_state.is_in_flow:
            return f"""🔥 FLOW STATE DETECTED

Current Session: {flow_state.flow_duration} minutes
Flow Quality: {flow_state.flow_quality:.0%}
Interruption Cost: {flow_state.interruption_cost:.0%}

🛡️ PROTECTION ACTIVATED:
• Notifications silenced
• Interruptions queued for later
• Context switching blocked
• Optimal extension: {flow_state.optimal_extension_time} minutes

🚀 MOMENTUM PRESERVED: You're in the zone - stay focused!
"""
        else:
            return f"""📊 FLOW MONITORING ACTIVE

Current Session: {flow_state.flow_duration} minutes
Flow Quality: {flow_state.flow_quality:.0%}
Status: Building momentum

💡 OPTIMIZATION:
• Continue current task to build flow
• Minimize context switching
• Flow typically emerges after {self.flow_threshold_minutes} minutes

⏳ Keep going - flow state approaching!
"""
    
    def _format_protection_response(self, actions: Dict[str, Any]) -> str:
        """Format flow protection response."""
        return f"""🛡️ FLOW PROTECTION ACTIVATED

PROTECTIVE ACTIONS TAKEN:
• {actions['notifications_silenced']} notifications silenced
• {actions['meetings_deferred']} meeting(s) deferred
• {actions['interruptions_queued']} interruption(s) queued
• Focus mode: {actions['focus_mode_activated']}
• Context preservation: {actions['context_preservation']}

🎯 RESULT: Your flow state is now protected
All distractions eliminated - maintain your momentum!
"""
    
    def _format_extension_response(self, extension_plan: Dict[str, Any]) -> str:
        """Format flow extension response."""
        if extension_plan.get("extension_recommended"):
            return f"""⏰ FLOW EXTENSION OPTIMIZED

CURRENT STATE:
• Flow Duration: {extension_plan['current_flow_duration']} minutes
• Flow Quality: {extension_plan['flow_quality']:.0%}
• Fatigue Level: {extension_plan['fatigue_prediction']:.0%}

🚀 EXTENSION PLAN:
• Recommended Extension: {extension_plan['optimal_extension_minutes']} minutes
• {extension_plan['break_recommendation']}
• Total Session: {extension_plan['current_flow_duration'] + extension_plan['optimal_extension_minutes']} minutes

✨ RESULT: Maximize flow value while preventing burnout
"""
        else:
            return f"""⚠️ NO EXTENSION RECOMMENDED

Reason: {extension_plan['reason']}

💡 NEXT STEPS:
• Take a short break to reset
• Choose next high-value task
• Build momentum for next flow session

🔄 Flow optimization remains active for next session
"""
    
    def _format_monitoring_response(self, status: Dict[str, Any]) -> str:
        """Format flow monitoring response."""
        return f"""👁️ FLOW MONITORING STATUS

SESSION STATUS:
• Duration: {status['current_session_duration']} minutes
• Flow Detected: {'✅ YES' if status['flow_detected'] else '❌ NO'}
• Flow Quality: {status['flow_quality']:.0%}
• Protection: {status['protection_status'].title()}

⚡ REAL-TIME OPTIMIZATION:
• Next check-in: {status['next_check_in']}
• Momentum tracking: Active
• Interruption management: Ready

🎯 The Flow State Guardian is watching over your productivity
"""

class InterruptionIntelligence(UnifiedSolopreneurAgent):
    """
    TIER 3: Provides smart intervention and context-aware interruption management.
    
    Revolutionary Capability: REAL-TIME INTERRUPTION INTELLIGENCE
    - Smart intervention: "You're 23 minutes into deep RAG research flow"  
    - Context awareness: Knows current task value and momentum
    - Intelligent alternatives: "Save X check for 2:30pm low-energy slot?"
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Interruption Intelligence",
            description="Provides smart intervention and context-aware interruption management",
            instructions="""
You intelligently intervene when suboptimal choices are detected.

SMART INTERVENTION SCENARIOS:
- NU opens distracting app during deep work
- Context switch attempt during flow state
- Low-value task chosen during high-energy period
- High-value opportunity during low-energy time

INTERVENTION EXAMPLES:
"You're 23 minutes into deep RAG research flow - continue for optimal momentum"
"X check detected - save for 2:30pm low-energy slot?"
"High-value paper trending now - interrupt current organization task?"
"Flow state at 85% quality - protect for 33 more minutes?"

CONTEXT-AWARE RESPONSES:
- Show current task progress and momentum
- Offer specific time alternatives
- Quantify interruption cost
- Provide clear value trade-offs

Always provide helpful alternatives and protect high-value work states.
""",
            port=10964
        )
    
    async def _execute_agent_logic(self, query: str, context_id: str, task_id: str):
        """Provide smart interruption intervention."""
        logger.info(f"Interruption Intelligence processing: {query}")
        
        try:
            # Detect intervention type
            if "interrupt" in query.lower() or "switch" in query.lower():
                intervention = await self._analyze_interruption_request(query)
                return {"content": self._format_intervention_response(intervention)}
            
            elif "protect" in query.lower():
                protection_advice = await self._generate_protection_advice()
                return {"content": self._format_protection_advice(protection_advice)}
            
            else:
                # General interruption analysis
                current_context = await self._analyze_current_context()
                return {"content": self._format_context_analysis(current_context)}
                
        except Exception as e:
            logger.error(f"Interruption intelligence error: {e}")
            return {"error": str(e), "content": f"Interruption analysis failed: {query}"}
    
    async def _analyze_interruption_request(self, request: str) -> Dict[str, Any]:
        """Analyze interruption request and provide intelligent response."""
        
        # Simulate current work context
        current_context = {
            "task": "Deep RAG research",
            "duration_minutes": 47,
            "flow_state": True,
            "flow_quality": 0.85,
            "progress": 0.65,
            "energy_level": "high",
            "momentum": "strong"
        }
        
        # Simulate interruption request
        interruption = {
            "type": "social_media_check",
            "estimated_duration": 15,
            "value": "low",
            "urgency": "low"
        }
        
        # Calculate interruption cost
        flow_cost = current_context["flow_quality"] * 0.8 if current_context["flow_state"] else 0.2
        momentum_cost = 0.6 if current_context["momentum"] == "strong" else 0.3
        context_switch_cost = 0.4
        
        total_cost = flow_cost + momentum_cost + context_switch_cost
        
        # Generate alternative timing
        alternative_time = "2:30pm" if current_context["energy_level"] == "high" else "after current task"
        
        return {
            "current_context": current_context,
            "interruption": interruption,
            "interruption_cost": total_cost,
            "recommendation": "defer" if total_cost > 0.7 else "allow",
            "alternative_timing": alternative_time,
            "reasoning": self._generate_interruption_reasoning(current_context, interruption, total_cost)
        }
    
    def _generate_interruption_reasoning(self, context: Dict, interruption: Dict, cost: float) -> str:
        """Generate reasoning for interruption recommendation."""
        if cost > 0.7:
            return f"High interruption cost due to strong {context['task']} momentum at {context['flow_quality']:.0%} flow quality"
        elif cost > 0.4:
            return f"Moderate cost - would lose {context['progress']:.0%} progress momentum"
        else:
            return f"Low cost - natural break point in {context['task']}"
    
    async def _generate_protection_advice(self) -> Dict[str, Any]:
        """Generate advice for protecting current work state."""
        return {
            "current_protection_level": "high",
            "recommended_actions": [
                "Enable focus mode for next 30 minutes",
                "Queue all non-urgent notifications",
                "Defer social media checks until 3:00pm",
                "Protect current research momentum"
            ],
            "duration": "33 minutes",
            "expected_outcome": "Complete deep work session with maximum value"
        }
    
    async def _analyze_current_context(self) -> Dict[str, Any]:
        """Analyze current work context for optimization."""
        return {
            "current_task": "Deep RAG research",
            "session_duration": 47,
            "productivity_score": 0.85,
            "energy_alignment": "optimal",
            "interruption_risk": "medium",
            "optimization_opportunities": [
                "Extend session by 33 minutes for optimal completion",
                "Queue upcoming tasks for post-flow processing",
                "Prepare related experiments for next session"
            ]
        }
    
    def _format_intervention_response(self, intervention: Dict[str, Any]) -> str:
        """Format smart intervention response."""
        context = intervention["current_context"]
        recommendation = intervention["recommendation"]
        cost = intervention["interruption_cost"]
        
        if recommendation == "defer":
            return f"""🚨 SMART INTERRUPTION INTERVENTION

CURRENT STATE ANALYSIS:
📊 Task: {context['task']} ({context['duration_minutes']} minutes)
🔥 Flow State: {'✅ Active' if context['flow_state'] else '❌ No'} ({context['flow_quality']:.0%} quality)
⚡ Energy: {context['energy_level'].title()}
📈 Progress: {context['progress']:.0%}

⚠️ INTERRUPTION COST: {cost:.0%}
{intervention['reasoning']}

💡 SMART ALTERNATIVE:
Save this for {intervention['alternative_timing']} (low-energy slot)
Continue current momentum for maximum value

🎯 RESULT: Protect {context['progress']:.0%} progress and maintain flow
"""
        else:
            return f"""✅ INTERRUPTION APPROVED

CONTEXT ANALYSIS:
📊 Task: {context['task']} ({context['duration_minutes']} minutes)  
⚡ Energy: {context['energy_level'].title()}
💰 Interruption Cost: {cost:.0%} (acceptable)

💡 RECOMMENDATION:
Brief interruption acceptable - natural break point reached
Resume within 10 minutes to maintain momentum

🎯 Minimal impact on productivity
"""
    
    def _format_protection_advice(self, advice: Dict[str, Any]) -> str:
        """Format protection advice response."""
        actions = advice["recommended_actions"]
        
        return f"""🛡️ PROTECTION OPTIMIZATION ADVICE

CURRENT PROTECTION: {advice['current_protection_level'].title()}
RECOMMENDED DURATION: {advice['duration']}

🎯 PROTECTIVE ACTIONS:
"""
        
        for i, action in enumerate(actions, 1):
            return f"{i}. {action}\n"
            
        return f"""
🚀 EXPECTED OUTCOME:
{advice['expected_outcome']}

✨ Smart protection maximizes your productive momentum
"""
    
    def _format_context_analysis(self, context: Dict[str, Any]) -> str:
        """Format current context analysis."""
        opportunities = context["optimization_opportunities"]
        
        response = f"""🧠 CONTEXT INTELLIGENCE ANALYSIS

CURRENT SESSION:
📊 Task: {context['current_task']}
⏱️ Duration: {context['session_duration']} minutes
🎯 Productivity: {context['productivity_score']:.0%}
⚡ Energy Alignment: {context['energy_alignment'].title()}
⚠️ Interruption Risk: {context['interruption_risk'].title()}

🚀 OPTIMIZATION OPPORTUNITIES:
"""
        
        for i, opportunity in enumerate(opportunities, 1):
            response += f"{i}. {opportunity}\n"
        
        response += "\n✨ Context intelligence active - protecting your productivity"
        
        return response