# Competitor Analysis Agent

A strategic intelligence agent built with Google ADK and Pydantic models for comprehensive competitor analysis and competitive advantage identification.

## Features

### 🔍 **Comprehensive Analysis Models**
- **CompetitorProfile**: Basic competitor information and positioning
- **EngagementMetrics**: Performance data and engagement analysis
- **ContentStrategy**: Content mix, timing, and strategic approach
- **SWOTAnalysis**: Strengths, weaknesses, opportunities, threats
- **CompetitiveGap**: Specific gaps and exploitation opportunities

### 📊 **Analysis Capabilities**
- Multi-dimensional competitor profiling
- Content strategy deconstruction
- Engagement pattern analysis
- Strategic gap identification
- Opportunity scoring and threat assessment
- Actionable competitive intelligence

### 🎯 **Competitor Tiers Supported**
- **Direct**: Head-to-head competitors in same space
- **Indirect**: Adjacent competitors with audience overlap
- **Aspirational**: Market leaders to learn from
- **Emerging**: Rising competitors to monitor

### 🔧 **Intelligence Features**
- **SWOT Framework**: Systematic competitive assessment
- **Gap Analysis**: Opportunity identification and sizing
- **Performance Benchmarking**: Quantitative competitive metrics
- **Strategic Recommendations**: Specific actions for advantage
- **Threat Assessment**: Risk evaluation and mitigation strategies

## Usage Examples

### Basic Usage
```python
from competitor_analysis_agent.agent import root_agent

# Analyze a competitor
result = root_agent.run("Analyze [Competitor Name] in the [Industry] space")

# Access structured output
analysis_data = result.analysis
print(f"Competitor: {analysis_data.competitor_profile.name}")
print(f"Threat Level: {analysis_data.threat_level}")
print(f"Opportunity Score: {analysis_data.opportunity_score}")
```

### Memory-Enabled Session Usage
```python
import uuid
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from competitor_analysis_agent.agent import root_agent

load_dotenv()

# Create session service
session_service = InMemorySessionService()

# Initialize competitive context
initial_state = {
    "user_name": "Your Name",
    "user_industry": "Your Industry",
    "competitive_landscape": {
        "primary_competitors": ["Competitor 1", "Competitor 2"],
        "competitive_positioning": "Your unique positioning",
        "unique_advantages": ["Advantage 1", "Advantage 2"],
        "target_metrics": {
            "follower_growth": "Target growth rate",
            "engagement_rate": "Target engagement",
            "market_position": "Target position"
        }
    },
    "analysis_history": {
        "completed_analyses": [],
        "key_learnings": [],
        "competitive_gaps_identified": []
    },
    "strategic_goals": {
        "short_term": ["Goal 1", "Goal 2"],
        "long_term": ["Goal 3", "Goal 4"],
        "differentiation": "Your differentiation strategy"
    }
}

# Create session and run
SESSION_ID = str(uuid.uuid4())
session = session_service.create_session(
    app_name="Competitor Analysis Agent",
    user_id="your_user_id",
    session_id=SESSION_ID,
    state=initial_state
)

runner = Runner(
    agent=root_agent,
    app_name="Competitor Analysis Agent",
    session_service=session_service
)

# Generate competitor analysis
analysis_request = types.Content(
    role="user",
    parts=[types.Part(text="Analyze [Specific Competitor] including their content strategy, engagement metrics, and competitive gaps I could exploit")]
)

for event in runner.run(
    user_id="your_user_id",
    session_id=SESSION_ID,
    new_message=analysis_request
):
    if event.is_final_response():
        print(f"Analysis Result: {event.content.parts[0].text}")
```

## Schema Structure

```python
class CompetitorAnalysis(BaseModel):
    analysis_date: str                          # ISO timestamp
    competitor_profile: CompetitorProfile       # Basic competitor info
    engagement_metrics: EngagementMetrics      # Performance data
    content_strategy: ContentStrategy          # Strategy breakdown
    swot_analysis: SWOTAnalysis               # Strategic assessment
    competitive_gaps: List[CompetitiveGap]    # Max 10 opportunities
    key_insights: List[str]                   # Max 7 key takeaways
    recommended_actions: List[str]            # Max 5 specific actions
    threat_level: str                         # low/medium/high
    opportunity_score: float                  # 1-10 rating
```

## Analysis Framework

### Competitive Intelligence Dimensions
- **Profile Analysis**: Positioning, audience, value proposition
- **Content Strategy**: Themes, formats, posting patterns
- **Engagement Metrics**: Performance data and trends
- **SWOT Assessment**: Strategic strengths and vulnerabilities
- **Gap Identification**: Missed opportunities and weaknesses

### Strategic Outputs
- **Threat Assessment**: Risk evaluation and competitive positioning
- **Opportunity Scoring**: Quantified potential for competitive advantage
- **Actionable Recommendations**: Specific tactics for market advantage
- **Strategic Insights**: Key learnings for competitive strategy

## Model Configuration

- **Model**: Environment-driven via `GEMINI_MODEL`
- **Agent Type**: `LlmAgent`
- **Output Schema**: `CompetitorAnalysis`
- **Output Key**: `analysis`

## Benefits

1. **Strategic Intelligence**: Comprehensive competitive landscape understanding
2. **Opportunity Identification**: Systematic gap analysis and advantage discovery
3. **Risk Assessment**: Threat evaluation and mitigation planning
4. **Actionable Insights**: Specific recommendations for competitive advantage
5. **Performance Benchmarking**: Quantitative competitive metrics
6. **Strategic Memory**: Historical analysis tracking and trend identification

This agent provides systematic competitive intelligence for strategic market advantage and sustainable competitive positioning.