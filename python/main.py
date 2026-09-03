"""
Orquestador LangGraph con bucle reflexivo e integración a Ollama (gemma4:e2b).
"""
import json
from pathlib import Path
import ollama
from langgraph.graph import StateGraph, END

from schemas import QAState
from utils import clean_text, extract_tfidf_terms, map_bloom_level
from rag import split_into_chunks, retrieve_relevant_context

MODEL_NAME = "gemma4:e2b"

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"
OUTPUTS_DIR = BASE_DIR / "outputs"

def load_prompt_file(filename: str) -> str:
    """Carga una plantilla de prompt desacoplada desde prompts/."""
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8")

# --- NODO 1: PREPROCESAMIENTO Y ENRIQUECIMIENTO ---
def node_preprocess(state: QAState) -> dict:
    cleaned = clean_text(state.get("raw_content", ""))
    chunks = split_into_chunks(cleaned)
    terms = extract_tfidf_terms(cleaned, top_n=5)
    bloom = map_bloom_level(state.get("target_profile", "estudiante"))

    return {
        "cleaned_text": cleaned,
        "chunks": chunks,
        "key_terms": terms,
        "bloom_level": bloom,
        "iteration_count": 0,
        "critic_approved": False,
        "critic_notes": ""
    }

# --- NODO 2: GENERADOR GEMMA (OLLAMA LOCAL) ---
def node_generate_gemma(state: QAState) -> dict:
    template = load_prompt_file("prompt_gemma_generator.md")
    
    feedback_clause = ""
    if state.get("critic_notes"):
        feedback_clause = f"ADVERTENCIA DE ERROR PREVIO: Corrige esto: {state['critic_notes']}"

    context = retrieve_relevant_context(state["chunks"], state["key_terms"])
    
    prompt = template.format(
        key_terms=", ".join(state["key_terms"]),
        bloom_level=state["bloom_level"],
        context_chunks=context,
        critic_feedback=feedback_clause
    )

    response = ollama.generate(
        model=MODEL_NAME,
        prompt=prompt,
        format="json",
        options={
            "temperature": 0.2,
            "top_p": 0.9
        }
    )

    try:
        data = json.loads(response["response"])
        questions = data.get("questions", [])
    except Exception:
        questions = []

    return {
        "candidate_questions": questions,
        "iteration_count": state.get("iteration_count", 0) + 1
    }

# --- NODO 3: CRÍTICO ANTI-ALUCINACIÓN (GUARDRAIL REFLEXIVO) ---
def node_critic(state: QAState) -> dict:
    questions = state.get("candidate_questions", [])
    context = state["cleaned_text"].lower()

    if not questions or len(questions) < 5:
        return {
            "critic_approved": False,
            "critic_notes": f"Se requieren exactamente 5 preguntas en JSON (se recibieron {len(questions)})."
        }

    hallucinations = 0
    for item in questions:
        ans = item.get("correct_answer", "").strip().lower()
        if len(ans) > 3 and ans not in context:
            hallucinations += 1

    if hallucinations == 0:
        return {
            "critic_approved": True,
            "critic_notes": "Aprobado: las 5 preguntas y sus respuestas están ancladas en el texto."
        }
    else:
        return {
            "critic_approved": False,
            "critic_notes": f"Se detectaron {hallucinations} respuestas no fundamentadas en el texto de origen."
        }

# --- ARISTA CONDICIONAL (LOOPBACK DINÁMICO) ---
def conditional_route(state: QAState) -> str:
    if state["critic_approved"] or state.get("iteration_count", 0) >= 2:
        return "export"
    return "retry"

# --- NODO 4: RESOLUTOR Y EXPORTADOR ---
def node_export(state: QAState) -> dict:
    final_data = state.get("candidate_questions", [])
    OUTPUTS_DIR.mkdir(exist_ok=True)
    out_file = OUTPUTS_DIR / "cuestionario_gemma.json"
    out_file.write_text(json.dumps(final_data, indent=2, ensure_ascii=False), encoding="utf-8")
    return {
        "final_questionnaire": final_data
    }

# --- COMPILACIÓN DEL GRAFO ---
def build_graph():
    builder = StateGraph(QAState)
    builder.add_node("preprocess", node_preprocess)
    builder.add_node("generate_gemma", node_generate_gemma)
    builder.add_node("critic", node_critic)
    builder.add_node("export", node_export)

    builder.set_entry_point("preprocess")
    builder.add_edge("preprocess", "generate_gemma")
    builder.add_edge("generate_gemma", "critic")

    builder.add_conditional_edges(
        "critic",
        conditional_route,
        {
            "retry": "generate_gemma",
            "export": "export"
        }
    )
    builder.add_edge("export", END)

    return builder.compile()

if __name__ == "__main__":
    app = build_graph()
    input_sample = BASE_DIR / "inputs" / "muestra.txt"
    
    if input_sample.exists():
        raw_text = input_sample.read_text(encoding="utf-8")
    else:
        raw_text = (
            "La fotosíntesis es el proceso bioquímico mediante el cual las plantas, "
            "algas y ciertas bacterias transforman la luz solar en energía química. "
            "Durante este proceso, el dióxido de carbono y el agua se convierten en "
            "glucosa y oxígeno molecular en los cloroplastos."
        )

    payload = {
        "raw_content": raw_text,
        "target_profile": "Estudiante Universitario"
    }

    resultado = app.invoke(payload)
    print("\n=== CUESTIONARIO GENERADO Y GUARDADO EN outputs/cuestionario_gemma.json ===")
    print(json.dumps(resultado["final_questionnaire"], indent=2, ensure_ascii=False))
