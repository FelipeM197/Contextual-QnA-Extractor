from typing import TypedDict, Any
from pathlib import Path
from pydantic import BaseModel, Field, create_model
from langgraph.graph import END, START, StateGraph
import utils

# total=False permite mutar e incorporar claves incrementalmente según avanza el grafo
class QAState(TypedDict, total=False):
    transcripcion_original: str
    conceptos_clave: list[str]
    preguntas_generadas: list[str]
    respuestas_crudas: list[dict[str, str]]
    perfil_objetivo: str
    cuestionario_final: str

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

    # Metaprogramación con Pydantic: define el esquema en tiempo de ejecución para obligar
    # a la API estructurada a devolver la cantidad exacta configurada en el CLI/Bash.
    PreguntasEstructuradas = create_model(
        'PreguntasEstructuradas',
        preguntas=(list[str], Field(description=f"Exactamente {top_n} preguntas en español"))
    )

    def agente_1_analista(state: QAState) -> dict:
        # Extraer anclas conceptuales deterministas previo a invocar LLM previene alucinación temática
        conceptos = utils.extraer_conceptos_tfidf(state["transcripcion_original"], top_n=top_n)
        print("[Agente 1] Evidencia: transcripcion recibida")
        print("[Agente 1] Decision: conceptos extraidos con TF-IDF")
        print("[Agente 1] Conceptos:", ", ".join(conceptos))
        print("[Agente 1] Certeza del metodo: 1.00 (calculo deterministico)")
        return {"conceptos_clave": conceptos}

    def agente_2_preguntas(state: QAState) -> dict:
        prompt_base = cargar_prompt(prompts_dir, "prompt_agente_2")
        conceptos_str = ", ".join(state["conceptos_clave"])
        
        # Inyección dinámica de directrices operativas sin alterar la plantilla física en disco
        prompt = prompt_base.replace("{conceptos}", conceptos_str)\
                            .replace("{texto}", state["transcripcion_original"])\
                            .replace("{q_len}", q_len)
        
        if llm is not None:
            structured_llm = llm.with_structured_output(PreguntasEstructuradas)
            preguntas = structured_llm.invoke(prompt).preguntas[:top_n]
            certeza = 0.85
            metodo = "respuesta estructurada del LLM"
        else:
            # Estrategia de degradación elegante cuando Ollama no está en ejecución
            terms = state["conceptos_clave"] or ["el documento"]
            preguntas = [f"¿Qué explica el documento sobre {term}?" for term in terms[:top_n]]
            certeza = 0.70
            metodo = "fallback deterministico basado en conceptos"
            
        print("[Agente 2] Evidencia: conceptos del Agente 1")
        print(f"[Agente 2] Decision: {metodo}")
        print(f"[Agente 2] Preguntas generadas: {len(preguntas)}")
        print(f"[Agente 2] Certeza estimada: {certeza:.2f}")
        return {"preguntas_generadas": preguntas}

    def agente_3_resolutor(state: QAState) -> dict:
        prompt_base = cargar_prompt(prompts_dir, "prompt_agente_3")
        respuestas = []
        
        for pregunta in state["preguntas_generadas"]:
            contexto = recuperar_contexto_local(store, pregunta, top_k)
            certeza = certeza_contexto(contexto)
            
            if llm is not None:
                prompt = prompt_base.replace("{pregunta}", pregunta)\
                                    .replace("{contexto}", contexto)\
                                    .replace("{a_len}", a_len)
                respuesta = llm.invoke(prompt).content
                metodo = "respuesta del LLM limitada al contexto"
            else:
                # Extrae únicamente el primer bloque de evidencia para garantizar trazabilidad mínima
                first_chunk = contexto.split("--- FIN CHUNK 1 ---")[0]
                respuesta = first_chunk.replace("--- INICIO CHUNK 1 ---", "").strip()
                respuesta += "\n\nFuente: CHUNK 1"
                metodo = "primer chunk recuperado como fallback"
                
            print(f"[Agente 3] Pregunta: {pregunta}")
            print(f"[Agente 3] Decision: {metodo}")
            print(f"[Agente 3] Certeza por evidencia recuperada: {certeza:.2f}")
            respuestas.append({"pregunta": pregunta, "respuesta": respuesta, "fuente": contexto})
            
        return {"respuestas_crudas": respuestas}

    def agente_4_adaptador(state: QAState) -> dict:
        perfil = state.get("perfil_objetivo", "estudiante universitario")
        
        if llm is not None:
            contenido = "\n\n".join(
                f"Q: {item['pregunta']}\nA: {item['respuesta']}" for item in state["respuestas_crudas"]
            )
            prompt_base = cargar_prompt(prompts_dir, "prompt_agente_4")
            prompt = prompt_base.replace("{perfil}", perfil).replace("{contenido}", contenido)
            final = llm.invoke(prompt).content
            metodo = "adaptacion del LLM con etiquetas preservadas"
            certeza = 0.85
        else:
            # Generador Markdown estándar que garantiza no perder la referencia de citas
            lines = [f"# Cuestionario para {perfil}", ""]
            for index, item in enumerate(state["respuestas_crudas"], start=1):
                lines.extend([f"## {index}. {item['pregunta']}", "", item["respuesta"], ""])
            final = "\n".join(lines)
            metodo = "formateo Markdown deterministico"
            certeza = 1.00
            
        print("[Agente 4] Evidencia: respuestas y fuentes del Agente 3")
        print(f"[Agente 4] Decision: {metodo}")
        print(f"[Agente 4] Certeza de formato: {certeza:.2f}")
        return {"cuestionario_final": final}

    # Topología estrictamente secuencial: Analista -> Formulador -> Resolutor -> Adaptador
    graph_builder = StateGraph(QAState)
    graph_builder.add_node("agente_1_analista", agente_1_analista)
    graph_builder.add_node("agente_2_preguntas", agente_2_preguntas)
    graph_builder.add_node("agente_3_resolutor", agente_3_resolutor)
    graph_builder.add_node("agente_4_adaptador", agente_4_adaptador)
    
    graph_builder.add_edge(START, "agente_1_analista")
    graph_builder.add_edge("agente_1_analista", "agente_2_preguntas")
    graph_builder.add_edge("agente_2_preguntas", "agente_3_resolutor")
    graph_builder.add_edge("agente_3_resolutor", "agente_4_adaptador")
    graph_builder.add_edge("agente_4_adaptador", END)
    
    print("[RAG] Grafo compilado correctamente.")
    return graph_builder.compile()
