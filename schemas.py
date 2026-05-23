from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, PositiveInt


class Channel(str, Enum):
    whatsapp = "WhatsApp"
    email = "email"
    call = "call"


class EnquiryCreate(BaseModel):
    channel: Channel = Field(..., example="WhatsApp")
    customer_name: str = Field(..., min_length=1, example="Ritika Sharma")
    message: str = Field(..., min_length=5, example="I want to book a demo for tomorrow.")


class FollowUpRequest(BaseModel):
    delay_minutes: PositiveInt = Field(..., example=30)
    message_template: Optional[str] = Field(None, example="Hi {{name}}, checking in on your enquiry.")


class EscalationRequest(BaseModel):
    reason: str = Field(..., min_length=5, example="Customer asked for human support.")


class HistoryItem(BaseModel):
    event_type: str
    details: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


class EnquiryHistoryResponse(BaseModel):
    id: int
    channel: Channel
    customer_name: str
    message: str
    status: str
    sop: Optional[str]
    suggested_response: Optional[str]
    follow_up_delay_minutes: Optional[int]
    follow_up_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    history: List[HistoryItem]

    class Config:
        orm_mode = True


class HealthResponse(BaseModel):
    status: str
    database: str


class EnquiryCreatedResponse(BaseModel):
    job_id: int
    status: str
