import json
from datetime import datetime
from pathlib import Path


class RoutingTelemetry:

    def __init__(self, file_path="routing_logs.jsonl"):
        self.file_path = file_path

    def log(self, data: dict):

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            **data
        }

        try:
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            pass