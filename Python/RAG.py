# Celda 5: define el estado compartido y las herramientas de los agentes.
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from sklearn.feature_extraction.text import TfidfVectorizer


class QAState(TypedDict, total=False):
    transcripcion_original: str
    conceptos_clave: list[str]
    preguntas_generadas: list[str]
    respuestas_crudas: list[dict[str, str]]
    perfil_objetivo: str
    cuestionario_final: str


def certeza_contexto(contexto: str) -> float:
    """Certeza heuristica basada en cantidad y extension de evidencia recuperada."""
    if contexto == "NO HAY CONTEXTO RECUPERADO.":
        return 0.0
    chunks = contexto.count("--- INICIO CHUNK")
    return round(min(0.95, 0.45 + chunks * 0.15), 2)


@tool
def extraer_conceptos(texto: str, top_n: int = 5) -> list[str]:
    """Extrae los conceptos mas relevantes mediante TF-IDF adaptado al español."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", texto) if s.strip()]
    if len(sentences) < 2:
        sentences.append(texto)
        
    # Lista robusta de stop words en español
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
    scores = matrix.sum(axis=0).A1
    terms = vectorizer.get_feature_names_out()
    
    ranked = sorted(zip(terms, scores), key=lambda pair: pair[1], reverse=True)
    return [term for term, _ in ranked[:top_n]]

@tool
def recuperar_contexto(pregunta: str) -> str:
    """Recupera hasta tres chunks y los devuelve con etiquetas de fuente."""
    chunks = store.retrieve(pregunta, top_k=3)
    if not chunks:
        return "NO HAY CONTEXTO RECUPERADO."
    bloques = []
    for index, chunk in enumerate(chunks, start=1):
        bloques.append(
            f"--- INICIO CHUNK {index} ---\nFuente: CHUNK {index}\n{chunk.text}\n"
            f"--- FIN CHUNK {index} ---"
        )
    return "\n\n".join(bloques)


class PreguntasEstructuradas(BaseModel):
    preguntas: list[str] = Field(description="Exactamente cinco preguntas en español")

print("[Celda 5] QAState y tools RAG definidos")


