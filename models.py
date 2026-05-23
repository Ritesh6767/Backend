from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Enquiry(Base):
    __tablename__ = "enquiries"

    id = Column(Integer, primary_key=True, index=True)
    channel = Column(String(32), nullable=False)
    customer_name = Column(String(128), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(32), nullable=False, default="open")
    sop = Column(String(128), nullable=True)
    suggested_response = Column(Text, nullable=True)
    follow_up_delay_minutes = Column(Integer, nullable=True)
    follow_up_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    history_entries = relationship("HistoryEntry", back_populates="enquiry", cascade="all, delete-orphan")

class HistoryEntry(Base):
    __tablename__ = "history_entries"

    id = Column(Integer, primary_key=True, index=True)
    enquiry_id = Column(Integer, ForeignKey("enquiries.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(64), nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    enquiry = relationship("Enquiry", back_populates="history_entries")
