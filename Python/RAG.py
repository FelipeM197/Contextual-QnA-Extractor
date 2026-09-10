import sys
import re
from typing import TypedDict, Any
from pathlib import Path
from pydantic import BaseModel, Field, create_model
from langgraph.graph import END, START, StateGraph
import utils
from logger import get_logger

# total=False permite mutar e incorporar claves incrementalmente según avanza el grafo
class QAState(TypedDict, total=False):
    transcripcion_original: str
    conceptos_clave: list[str]
    preguntas_generadas: list[str]
    respuestas_crudas: list[dict[str, str]]
    perfil_objetivo: str
    cuestionario_final: str
    intentos_auditoria: int
    aprobado_por_auditor: bool

def certeza_contexto(contexto: str) -> float:
    """Heurística de certeza ligada a la densidad de fragmentos recuperados (tope 0.95)."""
    if contexto == "NO HAY CONTEXTO RECUPERADO.":
        return 0.0
    chunks = contexto.count("--- INICIO CHUNK")
    return round(min(0.95, 0.45 + chunks * 0.15), 2)

def recuperar_contexto_local(store, pregunta: str, top_k: int) -> str:
    """Consulta similitud en DuckDB y formatea delimitadores que los prompts usan como contrato de cita."""
    chunks = store.retrieve(pregunta, top_k=top_k)
    if not chunks:
        return "NO HAY CONTEXTO RECUPERADO."
        
    bloques = []
    for index, chunk in enumerate(chunks, start=1):
        # Los delimitadores explícitos previenen que el LLM confunda metadatos de fuente con texto de autor
        bloques.append(
            f"--- INICIO CHUNK {index} ---\nFuente: CHUNK {index}\n{chunk.text}\n"
            f"--- FIN CHUNK {index} ---"
        )
    return "\n\n".join(bloques)

def cargar_prompt(prompts_dir: Path, nombre_archivo: str) -> str:
    prompt_path = prompts_dir / f"{nombre_archivo}.md"
    if not prompt_path.exists():
        return ""
    return prompt_path.read_text(encoding="utf-8")

def crear_grafo(llm, store, prompts_dir: Path, params: dict):
    """
    Ensambla el StateGraph cerrando dependencias (LLM, store, prompts) en el ámbito local
    para evitar estado mutable global entre ejecuciones concurrentes.
    """
    top_n = int(params.get("top_n", 5))
    top_k = int(params.get("top_k", 3))
    q_len = params.get("q_len", "concisas y directas")
    a_len = params.get("a_len", "detalladas y analiticas")

    def agente_1_analista(state: QAState) -> dict:
        logger = get_logger()
        logger.log_node_start("agente_1_analista", dict(state))
        
        print("[Agente 1] Evidencia: transcripción recibida", flush=True)
        conceptos = utils.extraer_conceptos_tfidf(state["transcripcion_original"], top_n=top_n)
        print("[Agente 1] Decisión: conceptos extraídos con TF-IDF", flush=True)
        print("[Agente 1] Conceptos:", ", ".join(conceptos), flush=True)
        print("[Agente 1] Certeza del método: 1.00 (cálculo determinístico)", flush=True)
        
        update = {"conceptos_clave": conceptos}
        logger.log_node_end("agente_1_analista", update)
        return update

    def agente_2_preguntas(state: QAState) -> dict:
        logger = get_logger()
        logger.log_node_start("agente_2_preguntas", dict(state))
        print("[Agente 2] Generando preguntas a partir de los conceptos clave...", flush=True)
        prompt_base = cargar_prompt(prompts_dir, "prompt_agente_2")
        conceptos_str = ", ".join(state["conceptos_clave"])
        
        prompt = prompt_base.replace("{conceptos}", conceptos_str)\
                            .replace("{texto}", state["transcripcion_original"])\
                            .replace("{q_len}", q_len)
        
        if llm is not None:
            try:
                print(f"[Agente 2] Invocando Ollama ({params.get('modelo', 'LLM')}) para generar preguntas...", flush=True)
                # Invocación directa a ChatOllama rápida sin bloqueos de tool_calling
                resp_text = llm.invoke(prompt).content
                logger.log_llm_interaction(prompt, resp_text)
                lines = [line.strip() for line in resp_text.splitlines() if line.strip() and ("?" in line or line[0].isdigit() or "." in line[:3])]
                if len(lines) >= top_n:
                    preguntas = lines[:top_n]
                else:
                    terms = state["conceptos_clave"] or ["el documento"]
                    preguntas = [f"¿Qué explica el documento sobre {term}?" for term in terms[:top_n]]
                certeza = 0.85
                metodo = "respuesta de texto del LLM"
            except Exception as e:
                logger.log_event("llm_error", {"agent": "agente_2", "error": str(e)})
                terms = state["conceptos_clave"] or ["el documento"]
                preguntas = [f"¿Qué explica el documento sobre {term}?" for term in terms[:top_n]]
                certeza = 0.70
                metodo = f"fallback determinístico por excepción LLM ({str(e)})"
        else:
            terms = state["conceptos_clave"] or ["el documento"]
            preguntas = [f"¿Qué explica el documento sobre {term}?" for term in terms[:top_n]]
            certeza = 0.70
            metodo = "fallback determinístico basado en conceptos"
            
        print("[Agente 2] Evidencia: conceptos del Agente 1", flush=True)
        print(f"[Agente 2] Decisión: {metodo}", flush=True)
        print(f"[Agente 2] Preguntas generadas: {len(preguntas)}", flush=True)
        print(f"[Agente 2] Certeza estimada: {certeza:.2f}", flush=True)
        
        update = {"preguntas_generadas": preguntas}
        logger.log_node_end("agente_2_preguntas", update)
        return update

    def agente_3_resolutor(state: QAState) -> dict:
        logger = get_logger()
        logger.log_node_start("agente_3_resolutor", dict(state))
        print("[Agente 3] Iniciando resolución de preguntas y búsqueda de evidencia...", flush=True)
        prompt_base = cargar_prompt(prompts_dir, "prompt_agente_3")
        respuestas = []
        total_q = len(state["preguntas_generadas"])
        
        for idx, pregunta in enumerate(state["preguntas_generadas"], start=1):
            print(f"[Agente 3] ({idx}/{total_q}) Procesando pregunta: '{pregunta}'...", flush=True)
            contexto = recuperar_contexto_local(store, pregunta, top_k)
            certeza = certeza_contexto(contexto)
            
            if llm is not None:
                try:
                    prompt = prompt_base.replace("{pregunta}", pregunta)\
                                        .replace("{contexto}", contexto)\
                                        .replace("{a_len}", a_len)
                    print(f"[Agente 3] ({idx}/{total_q}) Invocando Ollama para responder con evidencia...", flush=True)
                    respuesta = llm.invoke(prompt).content
                    logger.log_llm_interaction(prompt, respuesta)
                    metodo = "respuesta del LLM limitada al contexto"
                except Exception as e:
                    logger.log_event("llm_error", {"agent": "agente_3", "error": str(e)})
                    first_chunk = contexto.split("--- FIN CHUNK 1 ---")[0]
                    respuesta = first_chunk.replace("--- INICIO CHUNK 1 ---", "").strip() + "\n\nFuente: CHUNK 1"
                    metodo = "primer chunk recuperado como fallback"
            else:
                first_chunk = contexto.split("--- FIN CHUNK 1 ---")[0]
                respuesta = first_chunk.replace("--- INICIO CHUNK 1 ---", "").strip()
                respuesta += "\n\nFuente: CHUNK 1"
                metodo = "primer chunk recuperado como fallback"
                
            print(f"[Agente 3] ({idx}/{total_q}) Decisión: {metodo}", flush=True)
            print(f"[Agente 3] ({idx}/{total_q}) Certeza por evidencia recuperada: {certeza:.2f}", flush=True)
            respuestas.append({"pregunta": pregunta, "respuesta": respuesta, "fuente": contexto})
            
        update = {"respuestas_crudas": respuestas}
        logger.log_node_end("agente_3_resolutor", update)
        return update

    def agente_4_adaptador(state: QAState) -> dict:
        logger = get_logger()
        logger.log_node_start("agente_4_adaptador", dict(state))
        print("[Agente 4] Adaptando respuestas al perfil y generando Markdown final...", flush=True)
        perfil = state.get("perfil_objetivo", "estudiante universitario")
        
        if llm is not None:
            try:
                contenido = "\n\n".join(
                    f"Q: {item['pregunta']}\nA: {item['respuesta']}" for item in state["respuestas_crudas"]
                )
                prompt_base = cargar_prompt(prompts_dir, "prompt_agente_4")
                prompt = prompt_base.replace("{perfil}", perfil).replace("{contenido}", contenido)
                print(f"[Agente 4] Invocando Ollama para formatear cuestionario al perfil '{perfil}'...", flush=True)
                final = llm.invoke(prompt).content
                # Eliminar etiquetas <think>...</think> que algunos modelos añaden
                final = re.sub(r'<think>.*?</think>\s*', '', final, flags=re.DOTALL).strip()
                logger.log_llm_interaction(prompt, final)
                metodo = "adaptación del LLM con etiquetas preservadas"
                certeza = 0.85
            except Exception as e:
                logger.log_event("llm_error", {"agent": "agente_4", "error": str(e)})
                lines = [f"# Cuestionario para {perfil}", ""]
                for index, item in enumerate(state["respuestas_crudas"], start=1):
                    lines.extend([f"## {index}. {item['pregunta']}", "", item["respuesta"], ""])
                final = "\n".join(lines)
                metodo = "formateo Markdown determinístico (fallback)"
                certeza = 1.00
        else:
            lines = [f"# Cuestionario para {perfil}", ""]
            for index, item in enumerate(state["respuestas_crudas"], start=1):
                lines.extend([f"## {index}. {item['pregunta']}", "", item["respuesta"], ""])
            final = "\n".join(lines)
            metodo = "formateo Markdown determinístico"
            certeza = 1.00
            
        print("[Agente 4] Evidencia: respuestas y fuentes del Agente 3", flush=True)
        print(f"[Agente 4] Decisión: {metodo}", flush=True)
        print(f"[Agente 4] Certeza de formato: {certeza:.2f}", flush=True)
        
        update = {"cuestionario_final": final}
        logger.log_node_end("agente_4_adaptador", update)
        return update

    def agente_5_auditor(state: QAState) -> dict:
        logger = get_logger()
        logger.log_node_start("agente_5_auditor", dict(state))
        print("[Agente 5] Auditando respuestas contra la evidencia (Guardrail)...", flush=True)
        
        intentos = state.get("intentos_auditoria", 0) + 1
        respuestas = state.get("respuestas_crudas", [])
        aprobado = True
        
        # Hard limit to prevent infinite RAG hallucination loops.
        if intentos >= 3:
            print("[Agente 5] Límite de intentos alcanzado. Forzando aprobación para evitar bucle infinito.", flush=True)
            logger.log_node_end("agente_5_auditor", {"aprobado_por_auditor": True, "intentos_auditoria": intentos})
            return {"aprobado_por_auditor": True, "intentos_auditoria": intentos}

        if llm is not None:
            prompt_base = cargar_prompt(prompts_dir, "prompt_critic_validation")
            if not prompt_base:
                prompt_base = "Evalúa si las respuestas se basan estrictamente en la evidencia. Responde APROBADO o RECHAZADO."
                
            for idx, item in enumerate(respuestas, start=1):
                prompt = prompt_base.replace("{candidate_question}", item["pregunta"])\
                                    .replace("{candidate_answer}", item["respuesta"])\
                                    .replace("{context_chunks}", item["fuente"])
                try:
                    evaluacion = llm.invoke(prompt).content
                    logger.log_llm_interaction(prompt, evaluacion)
                    
                    # Detect JSON field "is_grounded": false
                    # We accept both literal false or FALSE since LLMs can be unpredictable.
                    if '"is_grounded": false' in evaluacion.lower():
                        print(f"[Agente 5] ⚠️ Alucinación detectada en la pregunta {idx}. Rechazando el lote.", flush=True)
                        aprobado = False
                        break
                except Exception as e:
                    logger.log_event("llm_error", {"agent": "agente_5", "error": str(e)})
                    # Fallback in case of failure is to allow it to pass.
                    aprobado = True
        else:
            aprobado = True
            
        print(f"[Agente 5] Veredicto del Auditor: {'APROBADO' if aprobado else 'RECHAZADO'}", flush=True)
        
        update = {"aprobado_por_auditor": aprobado, "intentos_auditoria": intentos}
        logger.log_node_end("agente_5_auditor", update)
        return update

    def auditor_router(state: QAState) -> str:
        """Enruta el flujo dependiendo del veredicto del auditor."""
        if state.get("aprobado_por_auditor", False):
            return "agente_4_adaptador"
        else:
            return "agente_2_preguntas"

    graph_builder = StateGraph(QAState)
    graph_builder.add_node("agente_1_analista", agente_1_analista)
    graph_builder.add_node("agente_2_preguntas", agente_2_preguntas)
    graph_builder.add_node("agente_3_resolutor", agente_3_resolutor)
    graph_builder.add_node("agente_5_auditor", agente_5_auditor)
    graph_builder.add_node("agente_4_adaptador", agente_4_adaptador)
    
    graph_builder.add_edge(START, "agente_1_analista")
    graph_builder.add_edge("agente_1_analista", "agente_2_preguntas")
    graph_builder.add_edge("agente_2_preguntas", "agente_3_resolutor")
    graph_builder.add_edge("agente_3_resolutor", "agente_5_auditor")
    
    # Dynamic routing based on the Guardrail's evaluation.
    graph_builder.add_conditional_edges(
        "agente_5_auditor",
        auditor_router,
        {
            "agente_4_adaptador": "agente_4_adaptador",
            "agente_2_preguntas": "agente_2_preguntas"
        }
    )
    
    graph_builder.add_edge("agente_4_adaptador", END)
    
    print("[RAG] Grafo compilado correctamente (Flujo con Auditor 5 integrado).", flush=True)
    return graph_builder.compile()
