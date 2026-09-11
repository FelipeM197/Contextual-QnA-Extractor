from dataclasses import dataclass
import datetime
import enum
import os
from pathlib import Path


if not hasattr(datetime, "UTC"):
    datetime.UTC = datetime.timezone.utc
if not hasattr(enum, "StrEnum"):
    class StrEnum(str, enum.Enum):
        def __str__(self):
            return self.value
    enum.StrEnum = StrEnum


@dataclass(frozen=True)
class Settings:
    project_dir: Path
    input_file: str = "Manchester United Profile.pdf"
    markdown_file: str = "man_utd.md"
    database_file: str = "man_utd.db"
    output_file: str = "cuestionario_final.md"
    model_name: str = "qwen2.5:3b"
    embedding_model: str = "all-MiniLM-L6-v2"
    target_profile: str = "estudiante universitario"
    max_context_chars: int = 6000
    num_ctx: int = 2048
    num_predict: int = 256

    @property
    def inputs_dir(self) -> Path:
        return self._configured_path("CONTEXTUAL_QNA_INPUTS_DIR", "inputs")

    @property
    def outputs_dir(self) -> Path:
        return self._configured_path("CONTEXTUAL_QNA_OUTPUTS_DIR", "outputs")

    @property
    def prompts_dir(self) -> Path:
        return self._configured_path("CONTEXTUAL_QNA_PROMPTS_DIR", "prompts")

    @property
    def processed_dir(self) -> Path:
        return self._configured_path(
            "CONTEXTUAL_QNA_PROCESSED_DIR", str(self.outputs_dir / "processed")
        )

    @property
    def logs_dir(self) -> Path:
        return self._configured_path(
            "CONTEXTUAL_QNA_LOGS_DIR", str(self.outputs_dir / "cuestionarios-logs")
        )

    @property
    def squad_samples_dir(self) -> Path:
        return self._configured_path(
            "CONTEXTUAL_QNA_SQUAD_SAMPLES_DIR", str(self.inputs_dir / "squad_samples")
        )

    @property
    def squad_dataset_path(self) -> Path:
        return self._configured_path("CONTEXTUAL_QNA_SQUAD_DATASET", "train-v2.0.json")

    @property
    def ollama_models_dir(self) -> Path:
        return self._configured_path("OLLAMA_MODELS", "ollama_models")

    @property
    def hf_home_dir(self) -> Path:
        return self._configured_path("HF_HOME", "huggingface_cache")

    def _configured_path(self, variable_name: str, default: str) -> Path:
        configured = os.environ.get(variable_name, default)
        path = Path(configured).expanduser()
        return path if path.is_absolute() else self.project_dir / path

    @property
    def input_path(self) -> Path:
        return self.inputs_dir / self.input_file

    @property
    def markdown_path(self) -> Path:
        return self.outputs_dir / self.markdown_file

    @property
    def database_path(self) -> Path:
        return self.outputs_dir / self.database_file

    @property
    def output_path(self) -> Path:
        return self.outputs_dir / self.output_file

    def resolve_input_path(self, input_name: str) -> Path:
        """Resuelve un nombre, ruta relativa o ruta absoluta de entrada."""
        requested = Path(input_name).expanduser()
        if requested.is_absolute():
            return requested

        candidates = [
            self.project_dir / requested,
            self.inputs_dir / requested,
            self.project_dir / "data" / "input" / requested,
        ]
        return next((candidate for candidate in candidates if candidate.exists()), candidates[1])

    def prepare_directories(self) -> None:
        self.inputs_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.squad_samples_dir.mkdir(parents=True, exist_ok=True)


def load_settings() -> Settings:
    configured_project_dir = os.environ.get("CONTEXTUAL_QNA_PROJECT_DIR")
    project_dir = Path(configured_project_dir).expanduser() if configured_project_dir else Path(__file__).resolve().parents[1]
    if not project_dir.is_absolute():
        project_dir = Path.cwd() / project_dir
    project_dir = project_dir.resolve()
    settings = Settings(project_dir=project_dir)
    settings.prepare_directories()
    os.environ.setdefault("OLLAMA_MODELS", str(settings.ollama_models_dir))
    os.environ.setdefault("HF_HOME", str(settings.hf_home_dir))
    return settings
