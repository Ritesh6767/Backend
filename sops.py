from typing import Optional

SOP_RULES = [
    {
        "name": "Booking enquiry",
        "keywords": ["book", "reservation", "schedule", "appointment"],
        "response": "I can help you confirm availability and complete your booking. Can you share the preferred date and time?",
    },
    {
        "name": "Pricing question",
        "keywords": ["price", "cost", "rate", "fee", "quote"],
        "response": "I can share pricing details. Which product or service are you interested in?",
    },
    {
        "name": "Complaint",
        "keywords": ["complaint", "problem", "issue", "not working", "bad", "wrong"],
        "response": "I'm sorry you're facing this issue. Please tell me a bit more so I can help resolve it quickly.",
    },
    {
        "name": "After-hours message",
        "keywords": ["after hours", "night", "late", "weekend", "closed"],
        "response": "Thank you for reaching out. Our team is currently offline, but we will follow up when we're back.",
    },
]


def match_sop(message: str) -> Optional[dict]:
    normalized = message.lower()
    for rule in SOP_RULES:
        for keyword in rule["keywords"]:
            if keyword in normalized:
                return rule
    return None
