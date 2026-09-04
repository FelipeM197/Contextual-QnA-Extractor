"""
Orquestador LangGraph con bucle reflexivo, integración a DuckDB y logging en JSONL.
"""
import argparse
import json
from pathlib import Path
from dataclasses import replace

from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END

from schemas import QAState, GenerationOutput
from utils import clean_text, extract_tfidf_terms, map_bloom_level
from config import load_settings, Settings
from ingestion import open_or_create_store
from logger import init_logger, get_logger

# Se usa un objeto global store y config para simplificar el acceso en los nodos
_store = None
_settings = None

def load_prompt_file(filename: str) -> str:
    return (_settings.prompts_dir / filename).read_text(encoding="utf-8")

# --- NODO 1: PREPROCESAMIENTO Y ENRIQUECIMIENTO ---
def node_preprocess(state: QAState) -> dict:
    logger = get_logger()
    logger.log_node_start("preprocess", state)
    
    cleaned = clean_text(state.get("raw_content", ""))
    terms = extract_tfidf_terms(cleaned, top_n=5)
    bloom = map_bloom_level(state.get("target_profile", "estudiante"))

    result = {
        "cleaned_text": cleaned,
        "key_terms": terms,
        "bloom_level": bloom,
        "iteration_count": 0,
        "critic_approved": False,
        "critic_notes": ""
    }
    logger.log_node_end("preprocess", result)
    return result

# --- NODO 2: GENERADOR (LLM) ---
def node_generate_gemma(state: QAState) -> dict:
    logger = get_logger()
    logger.log_node_start("generate_gemma", state)
    
    template = load_prompt_file("prompt_gemma_generator.md")
    
    feedback_clause = ""
    if state.get("critic_notes"):
        feedback_clause = f"ADVERTENCIA DE ERROR PREVIO: Corrige esto: {state['critic_notes']}"

    # Context Retrieval via DuckDB
    query = " ".join(state["key_terms"])
    chunks = _store.retrieve(query, top_k=3)
    context = "\n\n---\n\n".join([chunk.text for chunk in chunks]) if chunks else "NO HAY CONTEXTO."
    
    prompt = template.format(
        key_terms=", ".join(state["key_terms"]),
        bloom_level=state["bloom_level"],
        context_chunks=context,
        critic_feedback=feedback_clause
    )

    llm = ChatOllama(
        model=_settings.model_name,
        temperature=0.2,
    )
    
    # Langchain Structured Output garantiza extracción correcta de JSON
    structured_llm = llm.with_structured_output(GenerationOutput)
    response = structured_llm.invoke(prompt)
    
    questions_list = [q.model_dump() for q in response.questions] if response and response.questions else []
    
    # Logging the interaction
    logger.log_llm_interaction(prompt=prompt, raw_response="", parsed_response=questions_list)

    result = {
        "candidate_questions": questions_list,
        "iteration_count": state.get("iteration_count", 0) + 1
    }
    logger.log_node_end("generate_gemma", result)
    return result

# --- NODO 3: CRÍTICO ANTI-ALUCINACIÓN ---
def node_critic(state: QAState) -> dict:
    logger = get_logger()
    logger.log_node_start("critic", state)
    
    questions = state.get("candidate_questions", [])
    context = state["cleaned_text"].lower()

    if not questions or len(questions) < 5:
        result = {
            "critic_approved": False,
            "critic_notes": f"Se requieren exactamente 5 preguntas (se recibieron {len(questions)})."
        }
    else:
        hallucinations = 0
        for item in questions:
            ans = item.get("correct_answer", "").strip().lower()
            if len(ans) > 3 and ans not in context:
                hallucinations += 1

        if hallucinations == 0:
            result = {
                "critic_approved": True,
                "critic_notes": "Aprobado: las 5 preguntas y sus respuestas están ancladas en el texto original."
            }
        else:
            result = {
                "critic_approved": False,
                "critic_notes": f"Se detectaron {hallucinations} respuestas no fundamentadas en el texto original."
            }
            
    logger.log_node_end("critic", result)
    return result

# --- ARISTA CONDICIONAL ---
def conditional_route(state: QAState) -> str:
    if state["critic_approved"] or state.get("iteration_count", 0) >= 2:
        return "export"
    return "retry"

# --- NODO 4: EXPORTADOR ---
def node_export(state: QAState) -> dict:
    logger = get_logger()
    logger.log_node_start("export", state)
    
    final_data = state.get("candidate_questions", [])
    out_file = _settings.output_path
    
    # Guardar JSON final
    out_file.with_suffix('.json').write_text(json.dumps(final_data, indent=2, ensure_ascii=False), encoding="utf-8")
    
    result = {
        "final_questionnaire": final_data
    }
    logger.log_node_end("export", result)
    return result

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

def main():
    global _store, _settings
    
    parser = argparse.ArgumentParser(description="Ejecutar el sistema RAG (V2 + DuckDB)")
    parser.add_argument("--input", type=str, help="Nombre del archivo de entrada")
    parser.add_argument("--perfil", type=str, default="estudiante universitario", help="Perfil objetivo")
    parser.add_argument("--modelo", type=str, default="gemma4:e2b", help="Modelo Ollama a utilizar")
    args, unknown = parser.parse_known_args()

    _settings = load_settings()
    kwargs = {}
    if args.input:
        kwargs['input_file'] = args.input
        kwargs['markdown_file'] = f"{Path(args.input).stem}.md"
        kwargs['database_file'] = f"{Path(args.input).stem}.db"
        kwargs['output_file'] = f"cuestionario_{Path(args.input).stem}.json"
        
    kwargs['target_profile'] = args.perfil
    kwargs['model_name'] = args.modelo

    _settings = replace(_settings, **kwargs)

    # Inicializar Logger
    logger = init_logger(_settings.outputs_dir)
    print(f"[*] Iniciando con modelo {_settings.model_name} y archivo {_settings.input_file}")

    # Inicializar Base de Datos Vectorial (DuckDB)
    _store = open_or_create_store(_settings)

    # Cargar documento base
    if _settings.markdown_path.exists():
        raw_text = _settings.markdown_path.read_text(encoding="utf-8")
    else:
        raw_text = "No se pudo cargar el documento convertido."

    # Iniciar flujo
    app = build_graph()
    payload = {
        "raw_content": raw_text,
        "target_profile": _settings.target_profile
    }

    resultado = app.invoke(payload)
    print(f"\n=== CUESTIONARIO GENERADO ===")
    print(json.dumps(resultado.get("final_questionnaire", []), indent=2, ensure_ascii=False))
    print(f"=== LOGS GUARDADOS EN: {logger.log_file} ===")

if __name__ == "__main__":
    main()
