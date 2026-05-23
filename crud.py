from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app import models


def create_enquiry(db: Session, channel: str, customer_name: str, message: str) -> models.Enquiry:
    enquiry = models.Enquiry(
        channel=channel,
        customer_name=customer_name,
        message=message,
        status="open",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(enquiry)
    db.flush()
    db.add(
        models.HistoryEntry(
            enquiry_id=enquiry.id,
            event_type="enquiry_created",
            details=f"Channel={channel}",
            created_at=datetime.utcnow(),
        )
    )
    db.commit()
    db.refresh(enquiry)
    return enquiry


def get_enquiry(db: Session, enquiry_id: int) -> Optional[models.Enquiry]:
    return db.query(models.Enquiry).filter(models.Enquiry.id == enquiry_id).first()


def add_history(db: Session, enquiry_id: int, event_type: str, details: Optional[str] = None) -> models.HistoryEntry:
    entry = models.HistoryEntry(
        enquiry_id=enquiry_id,
        event_type=event_type,
        details=details,
        created_at=datetime.utcnow(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def update_enquiry_processing(
    db: Session,
    enquiry: models.Enquiry,
    sop: Optional[str],
    suggested_response: Optional[str],
    escalate: bool = False,
):
    enquiry.sop = sop
    enquiry.suggested_response = suggested_response
    enquiry.status = "escalated" if escalate else "processed"
    enquiry.updated_at = datetime.utcnow()
    db.add(enquiry)
    add_history(
        db,
        enquiry.id,
        "sop_matched" if not escalate else "escalation_triggered",
        details=f"sop={sop or 'none'}",
    )
    db.commit()
    db.refresh(enquiry)
    return enquiry


def schedule_follow_up(db: Session, enquiry: models.Enquiry, delay_minutes: int, message_template: Optional[str]):
    enquiry.follow_up_delay_minutes = delay_minutes
    enquiry.follow_up_message = message_template
    enquiry.updated_at = datetime.utcnow()
    db.add(enquiry)
    add_history(
        db,
        enquiry.id,
        "follow_up_scheduled",
        details=f"delay={delay_minutes} min message_template={message_template or 'none'}",
    )
    db.commit()
    db.refresh(enquiry)
    return enquiry


def escalate_enquiry(db: Session, enquiry: models.Enquiry, reason: str):
    enquiry.status = "escalated"
    enquiry.updated_at = datetime.utcnow()
    db.add(enquiry)
    add_history(db, enquiry.id, "escalated_by_request", details=reason)
    db.commit()
    db.refresh(enquiry)
    return enquiry
