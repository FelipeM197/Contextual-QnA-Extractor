"""
Módulo RAG: Segmentación en fragmentos (chunks) y recuperación por relevancia.
"""
from typing import List

def split_into_chunks(text: str, chunk_size: int = 350, overlap: int = 50) -> List[str]:
    """Divide el texto en bloques con solapamiento de palabras."""
    words = text.split()
    if len(words) <= chunk_size:
        return [text]

    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += (chunk_size - overlap)
    return chunks

def retrieve_relevant_context(chunks: List[str], key_terms: List[str], max_chunks: int = 3) -> str:
    """Selecciona los fragmentos que concentran la mayor densidad de términos clave."""
    if not chunks:
        return ""

    scored_chunks = []
    for c in chunks:
        c_lower = c.lower()
        score = sum(1 for term in key_terms if term.lower() in c_lower)
        scored_chunks.append((score, c))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    selected = [c for _, c in scored_chunks[:max_chunks]]
    return "\n\n---\n\n".join(selected)
