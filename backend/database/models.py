import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Integer, Float
from sqlalchemy.orm import relationship
from database.db import Base


def gen_id():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_id)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=gen_id)
    session_id = Column(String, index=True, nullable=False)  # anonymous visitor id (cookie/localStorage)
    created_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=gen_id)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # user | assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=gen_id)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    filetype = Column(String, nullable=False)
    uploaded_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, default=gen_id)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer, default=0)
    content = Column(Text, nullable=False)
    embedding_path = Column(String, nullable=True)  # path to .npy vector file

    document = relationship("Document", back_populates="chunks")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String, primary_key=True, default=gen_id)
    conversation_id = Column(String, nullable=True)
    message_id = Column(String, nullable=True)
    rating = Column(Integer, nullable=False)  # 1 = thumbs up, -1 = thumbs down
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Course(Base):
    __tablename__ = "courses"

    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    duration = Column(String, nullable=True)
    fees = Column(String, nullable=True)
    eligibility = Column(String, nullable=True)
    prerequisites = Column(String, nullable=True)
    learning_roadmap = Column(Text, nullable=True)
    modules = Column(Text, nullable=True)
    topics_covered = Column(Text, nullable=True)
    projects_included = Column(Text, nullable=True)
    internship_details = Column(Text, nullable=True)
    certification = Column(String, nullable=True)
    placement_support = Column(String, nullable=True)
    career_opportunities = Column(Text, nullable=True)
    expected_salary = Column(String, nullable=True)
    tools_used = Column(String, nullable=True)
    software_required = Column(String, nullable=True)
    industry_applications = Column(Text, nullable=True)
    faqs = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class WorkshopInfo(Base):
    __tablename__ = "workshop_info"

    id = Column(String, primary_key=True, default="default_workshop")
    date = Column(String, nullable=True)
    time = Column(String, nullable=True)
    venue = Column(String, nullable=True)
    registration_process = Column(Text, nullable=True)
    eligibility = Column(String, nullable=True)
    contact_number = Column(String, nullable=True)
    whatsapp_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    google_maps_location = Column(String, nullable=True)
    website = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
