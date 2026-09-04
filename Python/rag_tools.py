import re
from typing import TypedDict

from langchain_core.tools import tool
from pydantic import BaseModel, Field
from sklearn.feature_extraction.text import TfidfVectorizer

from config import Settings


class QAState(TypedDict, total=False):
    transcripcion_original: str
    conceptos_clave: list[str]
    preguntas_generadas: list[str]
    respuestas_crudas: list[dict[str, str]]
    perfil_objetivo: str
    cuestionario_final: str


class StructuredQuestions(BaseModel):
    questions: list[str] = Field(description="Exactly five questions in English")


STOP_WORDS_ES_EN = {
    "a", "al", "con", "de", "del", "el", "en", "es", "la", "las", "los", "por", "para",
    "que", "se", "su", "un", "una", "y", "the", "and", "of", "to", "in", "is", "on", "for",
}


def build_tools(store, settings: Settings):
    @tool
    def extract_concepts(text: str, top_n: int = 5) -> list[str]:
        """Extract the most relevant concepts from the document."""
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        if len(sentences) < 2:
            sentences.append(text)
        vectorizer = TfidfVectorizer(stop_words=list(STOP_WORDS_ES_EN))
        matrix = vectorizer.fit_transform(sentences)
        scores = matrix.sum(axis=0).A1
        terms = vectorizer.get_feature_names_out()
        ranked = sorted(zip(terms, scores), key=lambda pair: pair[1], reverse=True)
        return [term for term, _ in ranked[:top_n]]

    @tool
    def retrieve_context(question: str) -> str:
        """Retrieve one relevant chunk while limiting memory usage."""
        chunks = store.retrieve(question, top_k=1)
        if not chunks:
            return "NO HAY CONTEXTO RECUPERADO."
        text = chunks[0].text[: settings.max_context_chars]
        return f"--- INICIO CHUNK 1 ---\nFuente: CHUNK 1\n{text}\n--- FIN CHUNK 1 ---"

    return extract_concepts, retrieve_context


def context_certainty(context: str) -> float:
    if context == "NO HAY CONTEXTO RECUPERADO.":
        return 0.0
    chunks = context.count("--- INICIO CHUNK")
    return round(min(0.95, 0.45 + chunks * 0.15), 2)
