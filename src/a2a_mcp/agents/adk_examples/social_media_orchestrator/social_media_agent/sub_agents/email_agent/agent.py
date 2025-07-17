"""
ABOUTME: Email Agent using Google ADK with Pydantic models for structured email generation
ABOUTME: Demonstrates proper schema validation and professional email formatting
"""

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

# Load environment variables
load_dotenv()


# --- Define Email Priority Enum ---
class EmailPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


# --- Define Email Type Enum ---
class EmailType(str, Enum):
    BUSINESS = "business"
    PERSONAL = "personal"
    MARKETING = "marketing"
    SUPPORT = "support"
    FOLLOW_UP = "follow_up"
    ANNOUNCEMENT = "announcement"


# --- Define Attachment Schema ---
class EmailAttachment(BaseModel):
    filename: str = Field(description="Name of the attachment file")
    description: str = Field(description="Brief description of what the attachment contains")
    file_type: str = Field(description="File type/extension (e.g., 'pdf', 'docx', 'xlsx')")


# --- Define Complete Email Content Schema ---
class EmailContent(BaseModel):
    subject: str = Field(
        description="The subject line of the email. Should be concise, descriptive, and engaging.",
        min_length=5,
        max_length=100
    )
    body: str = Field(
        description="The main content of the email. Should be well-formatted with proper greeting, paragraphs, and signature.",
        min_length=20
    )
    priority: EmailPriority = Field(
        default=EmailPriority.NORMAL,
        description="Priority level of the email"
    )
    email_type: EmailType = Field(
        description="Type/category of the email being generated"
    )
    suggested_attachments: List[EmailAttachment] = Field(
        default=[],
        description="List of suggested attachments if applicable"
    )
    call_to_action: Optional[str] = Field(
        default=None,
        description="Specific action you want the recipient to take"
    )
    tone: str = Field(
        description="The tone of the email (e.g., 'professional', 'friendly', 'formal', 'casual')"
    )


# --- Create Advanced Email Generator Agent ---
email_agent = LlmAgent(
    name="advanced_email_agent",
    model=os.getenv("GEMINI_MODEL"),
    instruction="""
        You are an Advanced Email Generation Assistant powered by Google ADK with session memory.
        Your task is to generate professional, well-structured emails based on user requests while leveraging session context.

        CORE RESPONSIBILITIES:
        1. Analyze the user's request to understand context, purpose, and audience
        2. Use session state to personalize emails with user preferences and context
        3. Generate appropriate email content with proper structure and tone
        4. Suggest relevant attachments when applicable
        5. Determine appropriate priority and email type
        6. Include clear call-to-action when needed
        7. Remember email context for future sessions

        SESSION AWARENESS:
        - Check session state for user_name, user_preferences, and email_context
        - Use the user's preferred email style, signature, and tone
        - Reference the user's company, role, and industry when relevant
        - Consider recent email topics and follow-ups needed
        - Adapt recommendations based on user's priorities and common contacts

        EMAIL STRUCTURE GUIDELINES:
        - Subject Line: Concise (5-100 chars), descriptive, and engaging
        - Body Format:
            * Professional greeting appropriate to relationship
            * Opening paragraph: Context/purpose
            * Main content: Clear, organized information
            * Closing paragraph: Next steps/call-to-action
            * User's preferred signature from session state
        
        TONE ADAPTATION:
        - Business: Formal, professional, respectful
        - Personal: Friendly, warm, conversational
        - Marketing: Engaging, persuasive, action-oriented
        - Support: Helpful, empathetic, solution-focused
        - Follow-up: Polite, persistent, value-driven
        - Announcement: Clear, informative, exciting
        - Always adapt to user's tone_preference from session

        PRIORITY GUIDELINES:
        - LOW: FYI, general updates, non-urgent requests
        - NORMAL: Standard business communication, routine requests
        - HIGH: Important decisions, time-sensitive matters
        - URGENT: Critical issues, immediate action required

        ATTACHMENT SUGGESTIONS:
        - Only suggest attachments that add value
        - Provide clear filenames and descriptions
        - Consider user's industry and common document types
        - Reference user's priorities when suggesting content

        MEMORY INTEGRATION:
        - Reference previous email topics when relevant
        - Suggest follow-ups based on email_context
        - Maintain consistency with user's established communication style
        - Update session context with new email information

        OUTPUT REQUIREMENTS:
        Your response MUST be valid JSON matching the EmailContent schema.
        Include all required fields with appropriate values.
        Personalize based on session state whenever possible.
        Do not include explanations outside the JSON structure.
    """,
    description="Advanced email generator with comprehensive schema validation and intelligent content adaptation",
    output_schema=EmailContent,
    output_key="email",
)
