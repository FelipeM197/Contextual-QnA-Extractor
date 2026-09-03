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
        return self.project_dir / "inputs"

    @property
    def outputs_dir(self) -> Path:
        return self.project_dir / "outputs"

    @property
    def prompts_dir(self) -> Path:
        return self.project_dir / "prompts"

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

    def prepare_directories(self) -> None:
        self.inputs_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.prompts_dir.mkdir(parents=True, exist_ok=True)


def load_settings() -> Settings:
    project_dir = Path(__file__).resolve().parents[1]
    settings = Settings(project_dir=project_dir)
    settings.prepare_directories()
    os.environ.setdefault("OLLAMA_MODELS", str(project_dir / "ollama_models"))
    os.environ.setdefault("HF_HOME", str(project_dir / "huggingface_cache"))
    return settings
