# Closira Enquiry Backend Prototype

A lightweight FastAPI backend that simulates Closira's customer enquiry workflow. The service accepts enquiries, processes them asynchronously with FastAPI `BackgroundTasks`, and exposes history, follow-up scheduling, escalation, and health endpoints.

## What is included

- `POST /enquiry` to create a new enquiry and return a job ID immediately
- `POST /enquiry/{id}/follow-up` to schedule a follow-up
- `POST /enquiry/{id}/escalate` to mark an enquiry as escalated
- `GET /enquiry/{id}/history` to read the enquiry timeline and conversation history
- `GET /health` to verify API + database connectivity

## Setup

1. Create a Python virtual environment and activate it.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

3. Run the app.

```powershell
uvicorn app.main:app --reload
```

The service will be available at `http://127.0.0.1:8000`.

## Design decisions

### Database

- Using **SQLite** for this prototype because it is lightweight, easy to set up, and sufficient for a single-developer assignment.
- The schema is intentionally simple, with one table for enquiries and one table for status/history events.
- If this were production, I would migrate to PostgreSQL for concurrency, shared state, and stronger SQL guarantees.

### Async processing

- I chose **FastAPI `BackgroundTasks`** instead of Celery.
- Reason: the assignment asks for a lightweight, backend fundamentals demonstration and does not require distributed task workers.
- `BackgroundTasks` keeps the implementation simple, avoids external brokers, and still demonstrates non-blocking request handling.
- Trade-off: this is fine for low-volume or prototype use, but a real service with long-running workflows or multiple worker processes should use Celery or a queue.

### Logging

- Structured JSON logging is enabled for key events: enquiry created, task processed, SOP matched, and escalation triggered.
- This makes logs easier to process and inspect in modern observability pipelines.

## Database schema

- `enquiries` table:
  - `id`
  - `channel`
  - `customer_name`
  - `message`
  - `status`
  - `sop`
  - `suggested_response`
  - `created_at`
  - `updated_at`
  - `follow_up_delay_minutes`
  - `follow_up_message`

- `history_entries` table:
  - `id`
  - `enquiry_id`
  - `event_type`
  - `details`
  - `created_at`

## Known limitations

- Follow-up scheduling only records the request; it does not send an actual reminder or trigger a delayed callback.
- Background task execution is tied to the same process; if the server restarts before processing, the task may not complete.
- There is no tenant isolation layer in this prototype, but the data model can be extended with `tenant_id` later.

## Examples

Use the included `requests.http` file or the `/docs` UI to exercise all endpoints.

## Testing

Run:

```powershell
pytest
```
