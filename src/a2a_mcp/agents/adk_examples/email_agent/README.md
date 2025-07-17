# Advanced Email Agent

An enhanced email generation agent built with Google ADK and Pydantic models for structured, professional email creation.

## Features

### 🏗️ **Comprehensive Pydantic Models**
- **EmailContent**: Main email structure with validation
- **EmailAttachment**: Structured attachment suggestions
- **EmailPriority**: Enum for priority levels (low, normal, high, urgent)
- **EmailType**: Enum for email categories (business, personal, marketing, etc.)

### 📧 **Email Generation Capabilities**
- Professional subject line generation (5-100 characters)
- Well-structured email body with proper formatting
- Intelligent tone adaptation based on email type
- Priority assessment and classification
- Relevant attachment suggestions
- Clear call-to-action recommendations

### 🎯 **Email Types Supported**
- **Business**: Formal professional communication
- **Personal**: Friendly, conversational emails
- **Marketing**: Engaging, persuasive content
- **Support**: Helpful, empathetic responses
- **Follow-up**: Polite, persistent follow-ups
- **Announcement**: Clear, informative updates

### 🔧 **Technical Features**
- **Schema Validation**: Pydantic models ensure structured output
- **Field Validation**: Min/max length constraints
- **Type Safety**: Enum-based classifications
- **Optional Fields**: Flexible schema for different use cases
- **JSON Output**: Clean, parseable responses

## Usage Examples

### Basic Usage
```python
from email_agent.agent import root_agent

# Generate a business email
result = root_agent.run("Create a follow-up email to a client about a project proposal")

# Access structured output
email_data = result.email
print(f"Subject: {email_data.subject}")
print(f"Priority: {email_data.priority}")
print(f"Type: {email_data.email_type}")
print(f"Body: {email_data.body}")
```

### Memory-Enabled Session Usage
```python
import uuid
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from email_agent.agent import root_agent

load_dotenv()

# Create session service
session_service = InMemorySessionService()

# Initialize user context
initial_state = {
    "user_name": "Your Name",
    "user_preferences": {
        "email_style": "professional but personable",
        "signature": "Best regards,\nYour Name",
        "company": "Your Company",
        "role": "Your Role",
        "tone_preference": "confident and authoritative"
    },
    "email_context": {
        "recent_topics": [],
        "follow_ups_needed": []
    }
}

# Create session
SESSION_ID = str(uuid.uuid4())
session = session_service.create_session(
    app_name="Email Agent",
    user_id="your_user_id",
    session_id=SESSION_ID,
    state=initial_state
)

# Run with memory
runner = Runner(
    agent=root_agent,
    app_name="Email Agent",
    session_service=session_service
)

# Generate personalized email
email_request = types.Content(
    role="user",
    parts=[types.Part(text="Create a follow-up email to a LinkedIn collaboration partner")]
)

for event in runner.run(
    user_id="your_user_id",
    session_id=SESSION_ID,
    new_message=email_request
):
    if event.is_final_response():
        print(f"Generated Email: {event.content.parts[0].text}")
```

## Schema Structure

```python
class EmailContent(BaseModel):
    subject: str                              # 5-100 chars
    body: str                                # Min 20 chars
    priority: EmailPriority                  # low/normal/high/urgent
    email_type: EmailType                    # business/personal/etc
    suggested_attachments: List[EmailAttachment]  # Optional attachments
    call_to_action: Optional[str]           # Specific action requested
    tone: str                               # Email tone description
```

## Model Configuration

- **Model**: `gemini-2.0-flash`
- **Agent Type**: `LlmAgent`
- **Output Schema**: `EmailContent`
- **Output Key**: `email`

## Benefits Over Basic Email Agents

1. **Structured Output**: Guaranteed JSON schema compliance
2. **Enhanced Validation**: Field-level constraints and type checking
3. **Intelligent Classification**: Automatic email type and priority detection
4. **Comprehensive Metadata**: Rich context about generated emails
5. **Attachment Intelligence**: Smart suggestions for relevant attachments
6. **Tone Adaptation**: Context-aware tone selection

This agent demonstrates best practices for implementing Google ADK agents with Pydantic models for reliable, structured AI outputs.