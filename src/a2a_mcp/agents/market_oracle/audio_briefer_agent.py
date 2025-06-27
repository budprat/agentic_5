"""Audio Briefer - Voice Update Generation Agent."""

import logging
import json
from collections.abc import AsyncIterable
from typing import Dict, Any, List
from datetime import datetime, timedelta
import base64
import hashlib

from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import init_api_key
from a2a_mcp.common.supabase_client import SupabaseClient
from google import genai

logger = logging.getLogger(__name__)

AUDIO_SCRIPT_PROMPT = """
You are Audio Briefer, an AI that creates engaging voice briefings for investors.

Create a natural, conversational script for an audio briefing based on this data:

Portfolio Summary:
{portfolio_summary}

Market Updates:
{market_updates}

Key Recommendations:
{recommendations}

Risk Alerts:
{risk_alerts}

Generate a voice briefing script in JSON format:
{{
    "briefing_type": "daily/weekly/alert",
    "greeting": "Personalized greeting",
    "portfolio_overview": {{
        "opening": "Natural language portfolio summary",
        "performance": "Performance description",
        "key_changes": "Notable changes description"
    }},
    "market_summary": {{
        "headline": "Top market news",
        "key_points": ["point1", "point2", "point3"],
        "market_mood": "Overall market sentiment"
    }},
    "recommendations": [
        {{
            "symbol": "SYMBOL",
            "action": "Recommended action",
            "rationale": "Brief explanation",
            "urgency": "high/medium/low"
        }}
    ],
    "risk_update": {{
        "alert_level": "normal/elevated/high",
        "key_risks": ["risk1", "risk2"],
        "protective_actions": ["action1", "action2"]
    }},
    "closing": {{
        "summary": "Key takeaway message",
        "next_steps": "What to do next",
        "sign_off": "Professional closing"
    }},
    "estimated_duration": "Duration in seconds",
    "voice_parameters": {{
        "tone": "professional/casual/urgent",
        "pace": "normal/slow/fast",
        "emphasis_points": ["key phrase 1", "key phrase 2"]
    }}
}}
"""

SSML_TEMPLATE = """<speak>
  <prosody rate="{pace}">
    {greeting}
    
    <break time="0.5s"/>
    
    <emphasis level="moderate">Portfolio Overview:</emphasis>
    <break time="0.3s"/>
    {portfolio_overview}
    
    <break time="0.7s"/>
    
    <emphasis level="moderate">Market Update:</emphasis>
    <break time="0.3s"/>
    {market_summary}
    
    <break time="0.7s"/>
    
    <emphasis level="strong">Today's Recommendations:</emphasis>
    <break time="0.3s"/>
    {recommendations}
    
    <break time="0.7s"/>
    
    {risk_update}
    
    <break time="0.7s"/>
    
    {closing}
  </prosody>
</speak>"""

class AudioBrieferAgent(BaseAgent):
    """Voice update generation agent with Supabase integration."""

    def __init__(self):
        init_api_key()
        super().__init__(
            agent_name="Audio Briefer",
            description="Voice briefing generation with Supabase integration",
            content_types=["text", "text/plain"],
        )
        self.supabase = SupabaseClient()
        self.model = genai.Client()

    async def gather_briefing_data(self, user_id: str = "demo_user") -> Dict[str, Any]:
        """Gather all data needed for audio briefing from Supabase."""
        try:
            client = self.supabase.get_client()
            
            # Get portfolio data
            portfolio_response = client.table('portfolios').select(
                "*, positions(*)"
            ).eq('user_id', user_id).limit(1).execute()
            
            portfolio = portfolio_response.data[0] if portfolio_response.data else {}
            portfolio_id = portfolio.get('id')
            
            # Get recent signals (last 24 hours)
            yesterday = (datetime.now() - timedelta(days=1)).isoformat()
            signals_response = client.table('trading_signals').select("*").gte(
                'created_at', yesterday
            ).order('confidence_score', desc=True).limit(10).execute()
            
            # Get latest risk metrics
            risk_response = client.table('risk_metrics').select("*").eq(
                'portfolio_id', portfolio_id
            ).order('calculated_at', desc=True).limit(1).execute() if portfolio_id else None
            
            # Get recent research
            research_response = client.table('investment_research').select("*").gte(
                'created_at', yesterday
            ).order('created_at', desc=True).limit(5).execute()
            
            # Calculate portfolio performance
            positions = portfolio.get('positions', [])
            total_pnl = sum(p.get('profit_loss', 0) for p in positions)
            total_invested = sum(p['quantity'] * p['entry_price'] for p in positions)
            performance_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0
            
            return {
                "portfolio": {
                    "total_value": portfolio.get('total_value', 0),
                    "cash_balance": portfolio.get('cash_balance', 0),
                    "positions_count": len(positions),
                    "total_pnl": total_pnl,
                    "performance_percentage": performance_pct,
                    "top_performers": sorted(positions, key=lambda x: x.get('profit_loss', 0), reverse=True)[:3],
                    "worst_performers": sorted(positions, key=lambda x: x.get('profit_loss', 0))[:3]
                },
                "trading_signals": signals_response.data if signals_response else [],
                "risk_metrics": risk_response.data[0] if risk_response and risk_response.data else {},
                "research": research_response.data if research_response else [],
                "briefing_date": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            
        except Exception as e:
            logger.error(f"Error gathering briefing data: {e}")
            return {}

    async def generate_ssml_script(self, briefing_data: Dict[str, Any]) -> str:
        """Convert briefing data to SSML format for text-to-speech."""
        script = briefing_data
        
        # Format portfolio overview
        portfolio_text = script['portfolio_overview']['opening'] + " " + \
                        script['portfolio_overview']['performance'] + " " + \
                        script['portfolio_overview']['key_changes']
        
        # Format market summary
        market_text = script['market_summary']['headline'] + ". "
        market_text += " ".join(script['market_summary']['key_points']) + ". "
        market_text += f"The overall market mood is {script['market_summary']['market_mood']}."
        
        # Format recommendations
        rec_text = ""
        for rec in script['recommendations'][:3]:  # Top 3 recommendations
            rec_text += f"For {rec['symbol']}, {rec['action']}. {rec['rationale']}. "
            if rec['urgency'] == 'high':
                rec_text += "<emphasis level='strong'>This is a high priority recommendation.</emphasis> "
            rec_text += "<break time='0.3s'/>"
        
        # Format risk update
        risk_text = ""
        if script['risk_update']['alert_level'] != 'normal':
            risk_text = f"<emphasis level='strong'>Risk Alert:</emphasis> "
            risk_text += f"Risk level is {script['risk_update']['alert_level']}. "
            risk_text += " ".join(script['risk_update']['key_risks']) + ". "
            risk_text += "Recommended protective actions: " + " ".join(script['risk_update']['protective_actions'])
        else:
            risk_text = "Risk levels remain within normal parameters."
        
        # Format closing
        closing_text = script['closing']['summary'] + " " + \
                      script['closing']['next_steps'] + " " + \
                      script['closing']['sign_off']
        
        # Apply voice parameters
        pace_map = {"normal": "medium", "slow": "slow", "fast": "fast"}
        pace = pace_map.get(script['voice_parameters']['pace'], "medium")
        
        return SSML_TEMPLATE.format(
            pace=pace,
            greeting=script['greeting'],
            portfolio_overview=portfolio_text,
            market_summary=market_text,
            recommendations=rec_text,
            risk_update=risk_text,
            closing=closing_text
        )

    async def stream(
        self, query: str, context_id: str, task_id: str
    ) -> AsyncIterable[Dict[str, Any]]:
        """Execute audio briefing generation workflow with Supabase integration."""
        logger.info(f"Audio Briefer generating briefing: {query}")
        
        # Determine briefing type from query
        briefing_type = "daily"
        if "weekly" in query.lower():
            briefing_type = "weekly"
        elif "alert" in query.lower() or "urgent" in query.lower():
            briefing_type = "alert"
        
        try:
            # Step 1: Gather briefing data
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Audio Briefer: Gathering portfolio and market data..."
            }
            
            briefing_data = await self.gather_briefing_data()
            
            # Step 2: Analyze portfolio changes
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Audio Briefer: Analyzing portfolio performance..."
            }
            
            portfolio_summary = {
                "value": f"${briefing_data['portfolio']['total_value']:,.2f}",
                "change": f"{briefing_data['portfolio']['performance_percentage']:.1f}%",
                "positions": briefing_data['portfolio']['positions_count'],
                "top_performer": briefing_data['portfolio']['top_performers'][0]['symbol'] if briefing_data['portfolio']['top_performers'] else "None"
            }
            
            # Step 3: Summarize market updates
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Audio Briefer: Summarizing market updates..."
            }
            
            # Group signals by symbol
            signals_by_symbol = {}
            for signal in briefing_data['trading_signals']:
                symbol = signal['symbol']
                if symbol not in signals_by_symbol:
                    signals_by_symbol[symbol] = []
                signals_by_symbol[symbol].append(signal)
            
            market_updates = {
                "active_symbols": list(signals_by_symbol.keys()),
                "total_signals": len(briefing_data['trading_signals']),
                "bullish_count": len([s for s in briefing_data['trading_signals'] if s['signal_type'] == 'buy']),
                "bearish_count": len([s for s in briefing_data['trading_signals'] if s['signal_type'] == 'sell'])
            }
            
            # Step 4: Extract key recommendations
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Audio Briefer: Identifying key recommendations..."
            }
            
            recommendations = []
            for symbol, signals in signals_by_symbol.items():
                # Average confidence for this symbol
                avg_confidence = sum(s['confidence_score'] for s in signals) / len(signals)
                # Most common signal type
                signal_types = [s['signal_type'] for s in signals]
                most_common = max(set(signal_types), key=signal_types.count)
                
                if avg_confidence > 0.7:  # High confidence recommendations only
                    recommendations.append({
                        "symbol": symbol,
                        "action": most_common,
                        "confidence": avg_confidence,
                        "signal_count": len(signals)
                    })
            
            recommendations.sort(key=lambda x: x['confidence'], reverse=True)
            
            # Step 5: Assess risk alerts
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Audio Briefer: Checking risk levels..."
            }
            
            risk_metrics = briefing_data.get('risk_metrics', {})
            risk_alerts = {
                "var_95": risk_metrics.get('var_95', 0),
                "max_drawdown": risk_metrics.get('max_drawdown', 0),
                "high_risk": risk_metrics.get('var_95', 0) > 0.15 or risk_metrics.get('max_drawdown', 0) > 0.20
            }
            
            # Step 6: Generate audio script
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Audio Briefer: Generating voice briefing script..."
            }
            
            prompt = AUDIO_SCRIPT_PROMPT.format(
                portfolio_summary=json.dumps(portfolio_summary, indent=2),
                market_updates=json.dumps(market_updates, indent=2),
                recommendations=json.dumps(recommendations[:5], indent=2),  # Top 5
                risk_alerts=json.dumps(risk_alerts, indent=2)
            )
            
            response = self.model.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config={"temperature": 0.3, "response_mime_type": "application/json"}
            )
            
            briefing_script = json.loads(response.text)
            
            # Step 7: Generate SSML
            yield {
                "is_task_complete": False,
                "require_user_input": False,
                "content": "Audio Briefer: Formatting for text-to-speech..."
            }
            
            ssml_script = await self.generate_ssml_script(briefing_script)
            
            # Step 8: Save to Supabase
            client = self.supabase.get_client()
            
            # Create briefing record
            briefing_record = {
                'portfolio_id': briefing_data['portfolio'].get('id'),
                'briefing_type': briefing_type,
                'transcript': json.dumps(briefing_script),
                'audio_url': None,  # Would be populated after TTS generation
                'duration_seconds': briefing_script.get('estimated_duration', 120)
            }
            
            if briefing_data['portfolio'].get('id'):
                briefing_response = client.table('audio_briefings').insert(briefing_record).execute()
                briefing_id = briefing_response.data[0]['id'] if briefing_response.data else None
            else:
                briefing_id = None
            
            # Return final response
            final_response = {
                "briefing_script": briefing_script,
                "ssml_script": ssml_script,
                "plain_text": self._extract_plain_text(briefing_script),
                "metadata": {
                    "briefing_id": briefing_id,
                    "briefing_type": briefing_type,
                    "duration": briefing_script.get('estimated_duration', 120),
                    "generated_at": datetime.now().isoformat(),
                    "portfolio_value": portfolio_summary['value'],
                    "recommendations_count": len(recommendations)
                },
                "audio_config": {
                    "voice": "en-US-Neural2-F",  # Google Cloud TTS voice
                    "speaking_rate": 1.0 if briefing_script['voice_parameters']['pace'] == 'normal' else 0.9,
                    "pitch": 0.0,
                    "format": "mp3"
                }
            }
            
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "response_type": "data",
                "content": final_response
            }
            
        except Exception as e:
            logger.error(f"Audio Briefer error: {e}")
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": f"Audio Briefer: Error generating briefing - {str(e)}"
            }

    def _extract_plain_text(self, briefing_script: Dict[str, Any]) -> str:
        """Extract plain text version of briefing for display."""
        sections = []
        
        sections.append(briefing_script['greeting'])
        sections.append("\n\nPORTFOLIO OVERVIEW:")
        sections.append(briefing_script['portfolio_overview']['opening'])
        sections.append(briefing_script['portfolio_overview']['performance'])
        sections.append(briefing_script['portfolio_overview']['key_changes'])
        
        sections.append("\n\nMARKET UPDATE:")
        sections.append(briefing_script['market_summary']['headline'])
        sections.extend(briefing_script['market_summary']['key_points'])
        
        sections.append("\n\nRECOMMENDATIONS:")
        for rec in briefing_script['recommendations']:
            sections.append(f"- {rec['symbol']}: {rec['action']} ({rec['rationale']})")
        
        if briefing_script['risk_update']['alert_level'] != 'normal':
            sections.append("\n\nRISK ALERT:")
            sections.extend(briefing_script['risk_update']['key_risks'])
        
        sections.append("\n\n" + briefing_script['closing']['summary'])
        sections.append(briefing_script['closing']['next_steps'])
        sections.append("\n" + briefing_script['closing']['sign_off'])
        
        return "\n".join(sections)

    async def invoke(self, query: str, session_id: str) -> dict:
        """Non-streaming invoke (not implemented)."""
        raise NotImplementedError("Please use the streaming interface")