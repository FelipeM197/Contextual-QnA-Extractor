import logging
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict

_logger_instance = None

class CustomDatasetLogger:
    def __init__(self, log_path: Path, jsonl_path: Path):
        self.jsonl_path = jsonl_path
        
        self.logger = logging.getLogger("RAG_Dataset")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        
        # Prevent handler duplication in persistent sessions
        if not self.logger.handlers:
            file_handler = logging.FileHandler(log_path, encoding="utf-8")
            formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def log_event(self, node_name: str, event_type: str, data: Dict[str, Any]):
        """Persists the event to both plain text (.log) and structured (.jsonl) formats."""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # 1. Plain text (.log)
        log_message = f"NODE: {node_name} | EVENT: {event_type} | DATA: {json.dumps(data, ensure_ascii=False)}"
        self.logger.info(log_message)
        
        # 2. Structured (.jsonl) for ML fine-tuning
        jsonl_record = {
            "timestamp": timestamp,
            "node": node_name,
            "event": event_type,
            "data": data
        }
        with open(self.jsonl_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(jsonl_record, ensure_ascii=False) + "\n")

def init_logger(output_dir: Path):
    global _logger_instance
    log_path = output_dir / "dataset_training.log"
    jsonl_path = output_dir / "dataset_training.jsonl"
    _logger_instance = CustomDatasetLogger(log_path, jsonl_path)

def get_logger() -> CustomDatasetLogger:
    if _logger_instance is None:
        raise ValueError("Logger no inicializado. Llama a init_logger() primero.")
    return _logger_instance
