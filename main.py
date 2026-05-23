from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Path, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app import crud, database, logger, models, schemas, sops

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Closira Enquiry Backend",
    description="Prototype API for inbound customer enquiries with async processing and history tracking.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def process_enquiry_task(enquiry_id: int):
    db = database.SessionLocal()
    try:
        enquiry = crud.get_enquiry(db, enquiry_id)
        if not enquiry:
            logger.logger.error("background_task_missing_enquiry", {"enquiry_id": enquiry_id})
            return

        rule = sops.match_sop(enquiry.message)
        if rule:
            crud.update_enquiry_processing(
                db,
                enquiry,
                sop=rule["name"],
                suggested_response=rule["response"],
                escalate=False,
            )
            logger.logger.info(
                "task_processed",
                {"enquiry_id": enquiry.id, "sop": rule["name"]},
            )
        else:
            crud.update_enquiry_processing(
                db,
                enquiry,
                sop=None,
                suggested_response=None,
                escalate=True,
            )
            logger.logger.info(
                "escalation_triggered",
                {"enquiry_id": enquiry.id, "reason": "no_sop_matched"},
            )
    finally:
        db.close()


@app.get("/health", response_model=schemas.HealthResponse)
def health_check():
    try:
        db = database.SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {"status": "ok", "database": "connected"}
    except OperationalError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")


@app.post("/enquiry", response_model=schemas.EnquiryCreatedResponse, status_code=status.HTTP_202_ACCEPTED)
def create_enquiry(enquiry: schemas.EnquiryCreate, background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    created = crud.create_enquiry(db, enquiry.channel.value, enquiry.customer_name, enquiry.message)
    logger.logger.info(
        "enquiry_created",
        {"enquiry_id": created.id, "channel": created.channel, "customer": created.customer_name},
    )
    background_tasks.add_task(process_enquiry_task, created.id)
    return {"job_id": created.id, "status": "queued"}


@app.post("/enquiry/{enquiry_id}/follow-up", status_code=status.HTTP_200_OK)
def follow_up(
    enquiry_id: int = Path(..., gt=0),
    follow_up: schemas.FollowUpRequest = Depends(),
    db: Session = Depends(database.get_db),
):
    enquiry = crud.get_enquiry(db, enquiry_id)
    if not enquiry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enquiry not found")
    if enquiry.status == "escalated":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Escalated enquiry cannot schedule follow-up")
    crud.schedule_follow_up(db, enquiry, follow_up.delay_minutes, follow_up.message_template)
    return JSONResponse({"message": "Follow-up scheduled", "enquiry_id": enquiry.id})


@app.post("/enquiry/{enquiry_id}/escalate", status_code=status.HTTP_200_OK)
def escalate_enquiry(
    escalation: schemas.EscalationRequest,
    enquiry_id: int = Path(..., gt=0),
    db: Session = Depends(database.get_db),
):
    enquiry = crud.get_enquiry(db, enquiry_id)
    if not enquiry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enquiry not found")
    if enquiry.status == "escalated":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Enquiry already escalated")
    crud.escalate_enquiry(db, enquiry, escalation.reason)
    logger.logger.info(
        "enquiry_escalated",
        {"enquiry_id": enquiry.id, "reason": escalation.reason},
    )
    return JSONResponse({"message": "Enquiry escalated", "enquiry_id": enquiry.id})


@app.get("/enquiry/{enquiry_id}/history", response_model=schemas.EnquiryHistoryResponse)
def enquiry_history(enquiry_id: int = Path(..., gt=0), db: Session = Depends(database.get_db)):
    enquiry = crud.get_enquiry(db, enquiry_id)
    if not enquiry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enquiry not found")
    return {
        "id": enquiry.id,
        "channel": enquiry.channel,
        "customer_name": enquiry.customer_name,
        "message": enquiry.message,
        "status": enquiry.status,
        "sop": enquiry.sop,
        "suggested_response": enquiry.suggested_response,
        "follow_up_delay_minutes": enquiry.follow_up_delay_minutes,
        "follow_up_message": enquiry.follow_up_message,
        "created_at": enquiry.created_at,
        "updated_at": enquiry.updated_at,
        "history": enquiry.history_entries,
    }


@app.exception_handler(HTTPException)
def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
