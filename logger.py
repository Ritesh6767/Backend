import json
import logging

class JsonLogFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if record.args:
            payload["details"] = record.args
        return json.dumps(payload)

logger = logging.getLogger("closira_backend")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JsonLogFormatter())
logger.addHandler(handler)
