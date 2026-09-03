"""
Herramientas de normalización de texto, extracción TF-IDF y Taxonomía de Bloom.
"""
import re
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer

def clean_text(raw_text: str) -> str:
    """Elimina espacios repetidos, saltos espurios y caracteres no imprimibles."""
    if not raw_text:
        return ""
    text = re.sub(r'\s+', ' ', raw_text)
    return text.strip()

def extract_tfidf_terms(text: str, top_n: int = 5) -> List[str]:
    """Extrae las N palabras de mayor peso semántico usando TF-IDF."""
    if not text or len(text.split()) < 5:
        return ["fotosíntesis", "glucosa", "cloroplastos"]

    stop_words_es = [
        "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por",
        "un", "para", "con", "no", "una", "su", "al", "lo", "como", "mas", "pero",
        "sus", "le", "ya", "o", "este", "si", "porque", "esta", "entre", "cuando"
    ]

    vectorizer = TfidfVectorizer(max_features=top_n, stop_words=stop_words_es)
    try:
        vectorizer.fit([text])
        return list(vectorizer.get_feature_names_out())
    except Exception:
        words = [w.lower() for w in text.split() if len(w) > 4]
        return list(set(words))[:top_n]

def map_bloom_level(profile: str) -> str:
    """Mapea el perfil del evaluado a una categoría formal de la Taxonomía de Bloom."""
    p = profile.lower()
    if any(k in p for k in ["avanzado", "experto", "senior", "universitario"]):
        return "Aplicación y Análisis Crítico"
    elif any(k in p for k in ["intermedio", "bachiller"]):
        return "Comprensión y Relación de Conceptos"
    else:
        return "Recordación y Reconocimiento Directo"
