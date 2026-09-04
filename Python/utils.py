import os
import sys
import re
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from markitdown import MarkItDown
from raghilda.chunker import MarkdownChunker
from raghilda.embedding import EmbeddingSentenceTransformers
from raghilda.read import read_as_markdown
from raghilda.store import DuckDBStore

def configurar_entorno():
    """Redirige caches y pesos de modelos únicamente si existe la partición D: en Windows."""
    if sys.platform == "win32" and Path("D:/").exists():
        ollama_models_dir = Path(r"d:\Ollama_Modelos")
        hf_cache_dir = Path(r"d:\labADA\huggingface_cache")
        ollama_models_dir.mkdir(parents=True, exist_ok=True)
        hf_cache_dir.mkdir(parents=True, exist_ok=True)
        os.environ["OLLAMA_MODELS"] = str(ollama_models_dir)
        os.environ["HF_HOME"] = str(hf_cache_dir)
        print(f"[Utils] Entorno Windows configurado. OLLAMA_MODELS={ollama_models_dir}")
    else:
        print("[Utils] Entorno Linux/macOS configurado con rutas por defecto.")

def convertir_a_markdown(source_path: Path, target_path: Path) -> Path:
    """Convierte el documento origen a Markdown de forma idempotente."""
    # Evita re-procesar con OCR/parser si el artefacto limpio ya existe en disco
    if target_path.exists() and target_path.stat().st_size > 0:
        print("[Utils] Markdown existente reutilizado")
        return target_path
        
    if not source_path.exists():
        raise FileNotFoundError(f"No se encontro el documento original: {source_path}")
    
    resultado = MarkItDown().convert(str(source_path))
    # Compatibilidad defensiva entre versiones de markitdown (.text_content vs .markdown)
    contenido = getattr(resultado, 'text_content', getattr(resultado, 'markdown', ''))
    target_path.write_text(contenido, encoding="utf-8")
    print("[Utils] PDF convertido a Markdown")
    return target_path

def abrir_o_crear_store(markdown_path: Path, db_path: Path, embed_model_name: str = "all-MiniLM-L6-v2") -> DuckDBStore:
    """Gestiona persistencia local en DuckDB con VSS; crea HNSW si la BD no existe."""
    if db_path.exists():
        print("[Utils] Base vectorial existente: conexion de solo lectura")
        return DuckDBStore.connect(str(db_path), read_only=True)
    
    print("[Utils] Creando nueva base vectorial...")
    embedding = EmbeddingSentenceTransformers(model=embed_model_name)
    writable_store = DuckDBStore.create(str(db_path), embed=embedding)
    
    document = read_as_markdown(str(markdown_path))
    chunked_document = MarkdownChunker().chunk(document)
    
    writable_store.upsert(chunked_document)
    writable_store.build_index()
    
    # DuckDB bloquea el archivo durante indexación HNSW; liberar descriptor antes de reconectar solo-lectura
    del writable_store
    print("[Utils] Nueva base vectorial indexada y guardada en disco")
    return DuckDBStore.connect(str(db_path), read_only=True)

def extraer_conceptos_tfidf(texto: str, top_n: int = 5) -> list[str]:
    """Identifica términos de mayor relevancia ponderada mediante TF-IDF adaptado a español."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", texto) if s.strip()]
    
    # Scikit-learn colapsa si el corpus tiene < 2 muestras (IDF indeterminado)
    if len(sentences) < 2:
        sentences.append(texto)
        
    # Sklearn carece de stop words nativas para español; lista obligatoria para filtrar conectores
    stop_words_es = [
        "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las",
        "por", "un", "para", "con", "no", "una", "su", "al", "lo", "como",
        "más", "pero", "sus", "le", "ya", "o", "este", "sí", "porque", "esta",
        "entre", "cuando", "muy", "sin", "sobre", "también", "me", "hasta",
        "hay", "donde", "quien", "desde", "todo", "nos", "durante", "todos",
        "uno", "les", "ni", "contra", "otros", "ese", "eso", "ante", "ellos",
        "e", "esto", "mí", "antes", "algunos", "qué", "unos", "yo", "otro",
        "otras", "otra", "él", "tanto", "esa", "estos", "mucho", "quienes",
        "nada", "muchos", "cual", "poco", "ella", "estar", "estas", "algunas",
        "algo", "nosotros", "mi", "mis", "tú", "te", "ti", "tu", "tus", "ellas",
        "nosotras", "vosotros", "vosotras", "os", "mío", "mía", "míos", "mías",
        "tuyo", "tuya", "tuyos", "tuyas", "suyo", "suya", "suyos", "suyas",
        "nuestro", "nuestra", "nuestros", "nuestras", "vuestro", "vuestra",
        "vuestros", "vuestras", "es", "son", "fue", "ha", "han", "ser", "sido"
    ]
    
    vectorizer = TfidfVectorizer(stop_words=stop_words_es)
    matrix = vectorizer.fit_transform(sentences)
    
    # .A1 aplana directamente la matriz dispersa 2D a un array 1D contiguo sin duplicar memoria
    scores = matrix.sum(axis=0).A1
    terms = vectorizer.get_feature_names_out()
    
    ranked = sorted(zip(terms, scores), key=lambda pair: pair[1], reverse=True)
    return [term for term, _ in ranked[:top_n]]
