# Trend Analysis Agent

A strategic trend intelligence agent built with Google ADK and Pydantic models for identifying content opportunities and market momentum analysis.

## Features

### 📈 **Comprehensive Trend Models**
- **TrendMetrics**: Momentum scoring, velocity, and lifecycle analysis
- **KeywordAnalysis**: Search volume, competition, and hashtag trends
- **ContentOpportunity**: Specific content angles and platform strategies
- **MarketSentiment**: Audience emotions and sentiment drivers
- **TrendSource**: Multi-source validation and credibility scoring

### 🎯 **Analysis Capabilities**
- Real-time trend momentum scoring (1-10)
- Lifecycle stage identification (emerging → peak → declining)
- Content opportunity identification with urgency levels
- Competitive landscape assessment
- Risk factor evaluation and mitigation strategies
- Strategic timing recommendations

### 📊 **Trend Status Tracking**
- **Emerging**: Early signals, low competition, high potential
- **Growing**: Increasing momentum, moderate competition
- **Peak**: Maximum attention, high competition
- **Declining**: Waning interest, contrarian opportunities
- **Resurgent**: Renewed interest, nostalgia potential

### 🔧 **Intelligence Features**
- **Momentum Scoring**: Quantified trend velocity and trajectory
- **Opportunity Assessment**: Critical/High/Medium/Low classification
- **Multi-Source Validation**: Credibility-weighted trend verification
- **Content Strategy**: Platform-specific recommendations
- **Success Metrics**: Measurable performance indicators

## Usage Examples

### Basic Usage
```python
from trend_analysis_agent.agent import root_agent

# Analyze a trend
result = root_agent.run("Analyze the trend around [Topic] in [Industry]")

# Access structured output
analysis_data = result.analysis
print(f"Trend: {analysis_data.trend_topic}")
print(f"Momentum: {analysis_data.trend_metrics.momentum_score}")
print(f"Opportunity: {analysis_data.opportunity_level}")
```

### Memory-Enabled Session Usage
```python
import uuid
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from trend_analysis_agent.agent import root_agent

load_dotenv()

# Create session service
session_service = InMemorySessionService()

# Initialize trend context
initial_state = {
    "user_name": "Your Name",
    "user_industry": "Your Industry",
    "content_preferences": {
        "primary_platforms": ["LinkedIn", "Twitter", "YouTube"],
        "content_formats": ["carousels", "articles", "videos"],
        "audience_focus": ["your", "target", "audience"],
        "expertise_areas": ["your", "expertise", "areas"],
        "posting_frequency": "daily",
        "engagement_goals": "thought leadership + lead generation"
    },
    "trend_history": {
        "successful_trends": [],
        "missed_opportunities": [],
        "content_performance": [],
        "prediction_success_rate": 0.0
    },
    "competitive_context": {
        "main_competitors": ["Competitor 1", "Competitor 2"],
        "content_differentiation": "Your unique approach",
        "unique_angles": ["Angle 1", "Angle 2", "Angle 3"]
    }
}

# Create session and run
SESSION_ID = str(uuid.uuid4())
session = session_service.create_session(
    app_name="Trend Analysis Agent",
    user_id="your_user_id",
    session_id=SESSION_ID,
    state=initial_state
)

runner = Runner(
    agent=root_agent,
    app_name="Trend Analysis Agent",
    session_service=session_service
)

# Generate trend analysis
trend_request = types.Content(
    role="user",
    parts=[types.Part(text="Analyze the trend around [Specific Topic] and identify content opportunities for maximum engagement")]
)

for event in runner.run(
    user_id="your_user_id",
    session_id=SESSION_ID,
    new_message=trend_request
):
    if event.is_final_response():
        print(f"Trend Analysis: {event.content.parts[0].text}")
```

## Schema Structure

```python
class TrendAnalysis(BaseModel):
    analysis_date: str                          # ISO timestamp
    trend_topic: str                           # 5-100 chars
    trend_status: TrendStatus                  # emerging/growing/peak/declining/resurgent
    trend_metrics: TrendMetrics               # Momentum, velocity, saturation
    opportunity_level: OpportunityLevel       # critical/high/medium/low
    keyword_analysis: KeywordAnalysis         # Search and hashtag data
    market_sentiment: MarketSentiment         # Sentiment analysis
    content_opportunities: List[ContentOpportunity]  # Max 7 opportunities
    trend_sources: List[TrendSource]          # Max 5 validated sources
    risk_factors: List[str]                   # Max 5 potential risks
    competitive_landscape: List[str]          # Max 8 key players
    recommended_actions: List[str]            # Max 5 immediate actions
    success_metrics: List[str]                # Max 5 success measures
```

## Analysis Framework

### Trend Intelligence Dimensions
- **Momentum Analysis**: Growth velocity and trajectory measurement
- **Lifecycle Assessment**: Current stage and future trajectory
- **Opportunity Sizing**: Content potential and market gaps
- **Competitive Intelligence**: Player analysis and differentiation
- **Risk Evaluation**: Challenge identification and mitigation
- **Strategic Timing**: Optimal entry points and content calendar

### Content Strategy Outputs
- **Platform Optimization**: Channel-specific recommendations
- **Content Angles**: Multiple perspectives for comprehensive coverage
- **Timing Strategy**: Optimal publishing schedules and frequency
- **Success Metrics**: Quantifiable performance indicators
- **Risk Mitigation**: Challenge anticipation and response planning

## Model Configuration

- **Model**: Environment-driven via `GEMINI_MODEL`
- **Agent Type**: `LlmAgent`
- **Output Schema**: `TrendAnalysis`
- **Output Key**: `analysis`

## Benefits

1. **Early Opportunity Detection**: Identify trends before saturation
2. **Strategic Timing**: Optimal entry points for maximum impact
3. **Content Strategy**: Multi-angle approach for comprehensive coverage
4. **Risk Assessment**: Challenge identification and mitigation planning
5. **Competitive Intelligence**: Player analysis and differentiation opportunities
6. **Performance Prediction**: Success metrics and outcome forecasting

This agent provides strategic trend intelligence for content opportunity identification and market advantage through early trend adoption and strategic positioning.