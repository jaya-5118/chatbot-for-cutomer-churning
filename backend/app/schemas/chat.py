from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ChatMessageRequest(BaseModel):
    message: str = Field(..., description="Customer input text", min_length=1)
    session_id: Optional[str] = Field(default="default_session", description="Session identifier")
    customer_name: Optional[str] = Field(default="Guest User", description="Customer display name")


class SentimentData(BaseModel):
    score: float = Field(..., description="Sentiment polarity from -1.0 (frustrated) to +1.0 (delighted)")
    label: str = Field(..., description="Positive, Neutral, Negative, or Frustrated")
    urgency: str = Field(..., description="Low, Medium, High, Critical")
    frustrated: bool = Field(default=False)


class Citation(BaseModel):
    title: str
    section: str
    snippet: str
    confidence: float


class ChatMessageResponse(BaseModel):
    reply: str
    intent: str
    confidence: float
    alternative_intents: List[Dict[str, Any]] = []
    sentiment: SentimentData
    citations: List[Citation] = []
    escalate_to_human: bool = False
    suggested_actions: List[str] = []
    response_time_ms: float
    timestamp: str


class EscalationRequest(BaseModel):
    customer_name: str
    session_id: str
    reason: str
    sentiment_label: str
    last_message: str


class EscalationTicket(BaseModel):
    ticket_id: str
    customer_name: str
    session_id: str
    reason: str
    sentiment_label: str
    status: str
    created_at: str
    priority: str
