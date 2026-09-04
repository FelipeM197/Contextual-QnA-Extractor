"""
Definición de esquemas tipados con Pydantic y TypedDict para LangGraph.
"""
from typing import List, TypedDict, Optional
from pydantic import BaseModel, Field

# --- ESQUEMA DE SALIDA (OUTPUT CONTRACT) ---
class QuestionItem(BaseModel):
    id: int
    question: str = Field(description="Pregunta directa de máximo 18 palabras")
    options: List[str] = Field(description="4 opciones de respuesta")
    correct_answer: str = Field(description="Opción correcta exacta")
    explanation: str = Field(description="Cita o evidencia textual de respaldo")

class GenerationOutput(BaseModel):
    questions: List[QuestionItem]

# --- ESTADO COMPARTIDO LANGGRAPH ---
class QAState(TypedDict):
    raw_content: str
    cleaned_text: str
    key_terms: List[str]
    target_profile: str
    bloom_level: str
    candidate_questions: List[dict]
    critic_approved: bool
    critic_notes: str
    iteration_count: int
    final_questionnaire: List[dict]
