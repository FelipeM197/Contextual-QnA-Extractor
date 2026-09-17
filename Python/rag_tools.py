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


def extract_extractive_summary(text: str, max_sentences: int = 15) -> str:
    """Extrae un resumen del texto usando TF-IDF para evaluar la importancia de las oraciones. Optimiza el consumo de RAM."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if len(sentences) <= max_sentences:
        return text
    
    vectorizer = TfidfVectorizer(stop_words=list(STOP_WORDS_ES_EN))
    try:
        matrix = vectorizer.fit_transform(sentences)
        scores = matrix.sum(axis=1).A1
        top_indices = scores.argsort()[-max_sentences:][::-1]
        top_indices = sorted(top_indices)
        return " ".join([sentences[i] for i in top_indices])
    except Exception:
        return text[:3000]

def extract_query_keywords(question: str) -> str:
    """Extrae palabras clave determinísticamente sin LLM para acelerar el self-correction."""
    clean_q = re.sub(r'[^\w\s]', '', question.lower())
    words = clean_q.split()
    keywords = [w for w in words if w not in STOP_WORDS_ES_EN and len(w) > 2]
    return " ".join(keywords) if keywords else question

def calculate_lexical_grounding(answer: str, context: str) -> float:
    """Calcula el solapamiento léxico de palabras clave entre la respuesta y la evidencia."""
    ans_words = set(re.sub(r'[^\w\s]', '', answer.lower()).split()) - STOP_WORDS_ES_EN
    ctx_words = set(re.sub(r'[^\w\s]', '', context.lower()).split()) - STOP_WORDS_ES_EN
    if not ans_words:
        return 0.0
    intersection = ans_words.intersection(ctx_words)
    return round(len(intersection) / len(ans_words), 2)
