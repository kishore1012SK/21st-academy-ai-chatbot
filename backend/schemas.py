from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str = Field(..., min_length=1, max_length=128)
    stream: bool = False


class ChatResponse(BaseModel):
    success: bool
    response: str
    conversation_id: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class LoginResponse(BaseModel):
    success: bool
    access_token: str
    token_type: str = "bearer"


class MessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class HistoryResponse(BaseModel):
    session_id: str
    messages: List[MessageOut]


class FeedbackRequest(BaseModel):
    conversation_id: Optional[str] = None
    message_id: Optional[str] = None
    rating: int = Field(..., ge=-1, le=1)
    comment: Optional[str] = None


class UploadResponse(BaseModel):
    success: bool
    document_id: str
    filename: str
    chunks_indexed: int


class HealthResponse(BaseModel):
    status: str
    ollama_reachable: bool
    model: str


class CourseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=256)
    description: str
    duration: Optional[str] = None
    fees: Optional[str] = None
    eligibility: Optional[str] = None
    prerequisites: Optional[str] = None
    learning_roadmap: Optional[str] = None
    modules: Optional[str] = None
    topics_covered: Optional[str] = None
    projects_included: Optional[str] = None
    internship_details: Optional[str] = None
    certification: Optional[str] = None
    placement_support: Optional[str] = None
    career_opportunities: Optional[str] = None
    expected_salary: Optional[str] = None
    tools_used: Optional[str] = None
    software_required: Optional[str] = None
    industry_applications: Optional[str] = None
    faqs: Optional[str] = None


class CourseCreate(CourseBase):
    pass


class CourseUpdate(CourseBase):
    pass


class CourseResponse(CourseBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class WorkshopInfoBase(BaseModel):
    date: Optional[str] = None
    time: Optional[str] = None
    venue: Optional[str] = None
    registration_process: Optional[str] = None
    eligibility: Optional[str] = None
    contact_number: Optional[str] = None
    whatsapp_number: Optional[str] = None
    email: Optional[str] = None
    google_maps_location: Optional[str] = None
    website: Optional[str] = None


class WorkshopInfoUpdate(WorkshopInfoBase):
    pass


class WorkshopInfoResponse(WorkshopInfoBase):
    id: str
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentOut(BaseModel):
    id: str
    filename: str
    filetype: str
    uploaded_by: Optional[str] = None
    created_at: datetime
    chunks_count: int

    class Config:
        from_attributes = True
