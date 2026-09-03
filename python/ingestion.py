from pathlib import Path

from markitdown import MarkItDown
from raghilda.chunker import MarkdownChunker
from raghilda.read import read_as_markdown
from raghilda.store import DuckDBStore

from .config import Settings


def convert_to_markdown(source_path: Path, target_path: Path) -> Path:
    if target_path.exists() and target_path.stat().st_size > 0:
        print("[Ingesta] Markdown existente reutilizado")
        return target_path
    if not source_path.exists():
        raise FileNotFoundError(f"No se encontro el documento: {source_path}")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    result = MarkItDown().convert(source_path)
    target_path.write_text(result.markdown, encoding="utf-8")
    print("[Ingesta] PDF convertido a Markdown")
    return target_path


def open_or_create_store(settings: Settings) -> DuckDBStore:
    if settings.database_path.exists():
        print("[Ingesta] Base existente: conexion de solo lectura")
        return DuckDBStore.connect(settings.database_path, read_only=True)

    from raghilda.embedding import EmbeddingSentenceTransformers

    convert_to_markdown(settings.input_path, settings.markdown_path)
    embedding = EmbeddingSentenceTransformers(model=settings.embedding_model)
    writable_store = DuckDBStore.create(settings.database_path, embed=embedding)
    document = read_as_markdown(str(settings.markdown_path))
    chunks = MarkdownChunker().chunk(document)
    writable_store.upsert(chunks)
    writable_store.build_index()
    del writable_store
    print("[Ingesta] Nueva base creada e indexada")
    return DuckDBStore.connect(settings.database_path, read_only=True)
