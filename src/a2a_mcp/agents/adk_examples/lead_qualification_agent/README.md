# Lead Qualification Agent

A strategic lead qualification agent built with Google ADK and Pydantic models for sales pipeline optimization and conversion rate improvement.

## Features

### 🎯 **Comprehensive Qualification Models**
- **LeadQualification**: Complete BANT assessment with scoring
- **PainPoint**: Detailed pain point analysis with severity and impact
- **DecisionMaker**: Stakeholder mapping and relationship assessment
- **QualificationCriteria**: Budget, Authority, Need, Timeline validation
- **FollowUpAction**: Personalized next steps with timing and templates

### 📊 **Qualification Capabilities**
- BANT methodology implementation (Budget, Authority, Need, Timeline)
- Lead scoring from 0-100 with clear criteria
- Pain point analysis and solution mapping
- Decision maker identification and relationship planning
- Competitive situation assessment
- Personalized follow-up strategy development

### 🎯 **Lead Status Classification**
- **Cold**: Initial contact, limited information
- **Warm**: Some engagement, basic qualification started
- **Hot**: Strong interest, qualified opportunity
- **Qualified**: Meets all BANT criteria, sales-ready
- **Disqualified**: Clear disqualifying factors identified

### 🔧 **Intelligence Features**
- **Lead Scoring**: 0-100 numerical scoring with rationale
- **BANT Assessment**: Systematic qualification framework
- **Pain Point Mapping**: Business impact and urgency analysis
- **Stakeholder Analysis**: Decision maker influence and relationships
- **Competitive Intelligence**: Known competitors and differentiation
- **Personalization Engine**: Individual context and preferences

## Usage Examples

### Basic Usage
```python
from lead_qualification_agent.agent import root_agent

# Qualify a lead
result = root_agent.run("Qualify this lead: [Lead details and context]")

# Access structured output
qualification_data = result.qualification
print(f"Lead: {qualification_data.lead_name}")
print(f"Score: {qualification_data.lead_score}")
print(f"Status: {qualification_data.qualification_status}")
```

### Memory-Enabled Session Usage
```python
import uuid
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from lead_qualification_agent.agent import root_agent

load_dotenv()

# Create session service
session_service = InMemorySessionService()

# Initialize sales context
initial_state = {
    "user_name": "Your Name",
    "business_info": {
        "company": "Your Company",
        "services": ["Service 1", "Service 2", "Service 3"],
        "target_market": "Your target market",
        "pricing_range": "$X-$Y",
        "sales_cycle": "X-Y weeks",
        "unique_advantages": ["Advantage 1", "Advantage 2"]
    },
    "ideal_customer_profile": {
        "company_size": ["startup", "small", "medium"],
        "budget_range": ["5k_to_10k", "10k_to_25k"],
        "pain_points": ["Pain 1", "Pain 2", "Pain 3"],
        "decision_makers": ["CEO", "CMO", "Marketing Director"],
        "industry_focus": ["Industry 1", "Industry 2"]
    },
    "sales_process": {
        "qualification_criteria": {
            "min_budget": 5000,
            "timeline": "within_6_months"
        },
        "typical_objections": ["Objection 1", "Objection 2"],
        "success_factors": ["Factor 1", "Factor 2"]
    }
}

# Create session and run
SESSION_ID = str(uuid.uuid4())
session = session_service.create_session(
    app_name="Lead Qualification Agent",
    user_id="your_user_id",
    session_id=SESSION_ID,
    state=initial_state
)

runner = Runner(
    agent=root_agent,
    app_name="Lead Qualification Agent",
    session_service=session_service
)

# Generate lead qualification
qualification_request = types.Content(
    role="user",
    parts=[types.Part(text="Qualify this lead: [Detailed lead information and interaction context]")]
)

for event in runner.run(
    user_id="your_user_id",
    session_id=SESSION_ID,
    new_message=qualification_request
):
    if event.is_final_response():
        print(f"Qualification Result: {event.content.parts[0].text}")
```

## Schema Structure

```python
class LeadQualification(BaseModel):
    qualification_date: str                     # ISO timestamp
    lead_name: str                             # Lead or company name
    lead_source: LeadSource                    # Acquisition channel
    company_info: Dict[str, str]               # Company details
    lead_score: int                            # 0-100 scoring
    qualification_status: LeadStatus           # cold/warm/hot/qualified/disqualified
    qualification_criteria: QualificationCriteria  # BANT assessment
    pain_points: List[PainPoint]               # Max 5 pain points
    decision_makers: List[DecisionMaker]       # Max 5 stakeholders
    budget_range: BudgetRange                  # Budget classification
    decision_timeline: str                     # Decision timeframe
    competitive_situation: List[str]           # Max 5 competitors
    value_proposition_fit: str                 # Solution fit assessment
    objections_concerns: List[str]             # Max 5 objections
    next_actions: List[FollowUpAction]         # Max 5 follow-up steps
    personalization_data: Dict[str, str]       # Personal context
    success_probability: float                 # 0-100% probability
    estimated_deal_value: Optional[str]        # Deal size estimate
    notes: List[str]                          # Max 3 additional notes
```

## BANT Qualification Framework

### Budget Assessment
- **Financial Capacity**: Ability to afford solution
- **Budget Allocation**: Funds allocated or available
- **Investment Priorities**: Where budget is focused
- **ROI Requirements**: Expected return expectations

### Authority Evaluation
- **Decision Makers**: Who has buying authority
- **Influencers**: Who influences the decision
- **Champions**: Internal advocates for solution
- **Blockers**: Potential decision obstacles

### Need Validation
- **Pain Points**: Current business challenges
- **Impact Assessment**: Cost of inaction
- **Solution Fit**: How well you address needs
- **Urgency**: Timeline pressure for solution

### Timeline Analysis
- **Decision Timeline**: When they plan to decide
- **Implementation Timeline**: When they need solution
- **Competing Priorities**: What else demands attention
- **Seasonal Factors**: Timing considerations

## Model Configuration

- **Model**: Environment-driven via `GEMINI_MODEL`
- **Agent Type**: `LlmAgent`
- **Output Schema**: `LeadQualification`
- **Output Key**: `qualification`

## Benefits

1. **Systematic Qualification**: BANT methodology ensures complete assessment
2. **Objective Scoring**: 0-100 scoring removes subjective bias
3. **Actionable Intelligence**: Specific next steps and personalization
4. **Relationship Mapping**: Stakeholder analysis and engagement strategy
5. **Competitive Awareness**: Situation analysis and differentiation
6. **Sales Optimization**: Data-driven pipeline management and forecasting

This agent provides systematic lead qualification for improved sales efficiency and higher conversion rates through strategic prospect assessment and personalized engagement.