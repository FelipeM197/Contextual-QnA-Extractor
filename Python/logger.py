import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Nos aseguramos de que datetime tenga UTC por si acaso
if not hasattr(datetime, "UTC"):
    datetime.UTC = datetime.timezone.utc

class RAGLogger:
    def __init__(self, outputs_dir: Path):
        self.logs_dir = outputs_dir / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")
        self.log_file = self.logs_dir / f"run_{timestamp}.log"
        
        # Escribimos un evento de inicio
        self.log_event("system_start", {"timestamp": timestamp})
        print(f"[Logger] Inicializado: {self.log_file}")

    def log_event(self, event_type: str, data: Dict[str, Any]):
        """Escribe un evento en formato JSONL."""
        log_entry = {
            "timestamp": datetime.now(datetime.UTC).isoformat(),
            "event": event_type,
            "data": data
        }
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            # json.dumps asegura que se escriba en una sola línea (JSONL)
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

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

# Instancia global que inicializaremos desde main.py
_logger = None

def init_logger(outputs_dir: Path) -> RAGLogger:
    global _logger
    _logger = RAGLogger(outputs_dir)
    return _logger

def get_logger() -> RAGLogger:
    global _logger
    if _logger is None:
        raise ValueError("El logger no ha sido inicializado. Llama a init_logger() primero.")
    return _logger
