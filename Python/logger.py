import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

class RAGLogger:
    def __init__(self, outputs_dir: Path):
        self.logs_dir = outputs_dir / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.log_file_jsonl = self.logs_dir / "dataset_training.jsonl"
        self.log_file_txt = self.logs_dir / "dataset_training.log"
        
        self.log_event("system_start", {"timestamp": timestamp})
        print(f"[Logger] Inicializado: {self.log_file_txt} y .jsonl")

    def log_event(self, event_type: str, data: Dict[str, Any]):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event_type,
            "data": data
        }
        
        json_line = json.dumps(log_entry, ensure_ascii=False) + "\n"
        
        # Dual-write for ML pipelines (JSONL) and manual auditing (.log).
        with open(self.log_file_jsonl, "a", encoding="utf-8") as f:
            f.write(json_line)
            
        with open(self.log_file_txt, "a", encoding="utf-8") as f:
            f.write(f"[{log_entry['timestamp']}] EVENT: {event_type}\n")
            f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
            f.write("-" * 50 + "\n")

    def log_node_start(self, node_name: str, state: Dict[str, Any]):
        self.log_event(f"node_start_{node_name}", state)

    def log_node_end(self, node_name: str, state_update: Dict[str, Any]):
        self.log_event(f"node_end_{node_name}", state_update)

    def log_llm_interaction(self, prompt: str, raw_response: str, parsed_response: Any = None):
        self.log_event("llm_interaction", {
            "prompt": prompt,
            "raw_response": raw_response,
            "parsed_response": parsed_response
        })

_logger = None

def init_logger(outputs_dir: Path) -> RAGLogger:
    global _logger
    _logger = RAGLogger(outputs_dir)
    return _logger

def get_logger() -> RAGLogger:
    global _logger
    if _logger is None:
        raise ValueError("Logger no inicializado. Se requiere llamada previa a init_logger().")
    return _logger
