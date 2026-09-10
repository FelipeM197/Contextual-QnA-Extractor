import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from langchain_ollama import ChatOllama
import utils
import RAG
import phoenix as px
from openinference.instrumentation.langchain import LangChainInstrumentor
# Asegura que los prints se muestren en tiempo real sin bloqueo de buffer en pipes/consola
sys.stdout.reconfigure(line_buffering=True)

def modelo_disponible(model_name: str, ollama_models_dir: str = "") -> bool:
    """Verifica si el binario de Ollama existe y si el modelo está descargado."""
    ollama = shutil.which("ollama")
    if not ollama:
        return False
        
    env = os.environ.copy()
    if ollama_models_dir:
        env["OLLAMA_MODELS"] = ollama_models_dir

    resultado = subprocess.run(
        [ollama, "list"], capture_output=True, text=True, check=False,
        env=env,
    )
    return any(line.startswith(model_name) for line in resultado.stdout.splitlines())

def main():
    parser = argparse.ArgumentParser(description="Disparador del Sistema QnA")
    parser.add_argument("--env", type=str, default="010")
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--encoding", type=str, default="utf-8")
    parser.add_argument("--perfil", type=str, default="estudiante universitario")
    parser.add_argument("--top_n", type=int, default=5)
    parser.add_argument("--q_len", type=str, default="concisas y directas")
    parser.add_argument("--a_len", type=str, default="detalladas y analiticas")
    parser.add_argument("--modelo", type=str, default="llama3.1")
    parser.add_argument("--temperatura", type=float, default=0.0)
    parser.add_argument("--embedding", type=str, default="all-MiniLM-L6-v2")
    parser.add_argument("--top_k", type=int, default=3)
    
    args = parser.parse_args()
    
    # 1. Configurar Entorno
    utils.configurar_entorno()
    
    # Normalize base path to support arbitrary execution contexts (repo root, sh/, or Python/).
    project_dir = Path.cwd().resolve()
    if project_dir.name == "Python":
        project_dir = project_dir.parent
    
    inputs_dir = project_dir / "inputs"
    outputs_dir = project_dir / "outputs"
    processed_dir = outputs_dir / "processed"
    logs_dir = outputs_dir / "cuestionarios-logs"
    prompts_dir = project_dir / "prompts"
    
    inputs_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    prompts_dir.mkdir(parents=True, exist_ok=True)
    
    # Iniciar Arize Phoenix y el auto-tracing de LangChain/LangGraph
    print("\n[Main] Iniciando servidor de observabilidad Arize Phoenix...")
    try:
        px.launch_app()
    except Exception as e:
        print(f"[Main] Advertencia: Arize Phoenix ya está corriendo o no pudo iniciar ({e})")
    LangChainInstrumentor().instrument()
    
    input_file_path = inputs_dir / args.input
    if not input_file_path.exists():
        print(f"Error: No se encontró el archivo de entrada en {input_file_path}")
        
        # Transparent backwards compatibility for legacy data/input structure.
        old_input = project_dir / "data" / "input" / args.input
        if old_input.exists():
            print(f"Moviendo {args.input} desde data/input hacia inputs/...")
            shutil.copy2(old_input, input_file_path)
        else:
            return
        
    base_name = input_file_path.stem
    markdown_path = processed_dir / f"{base_name}.md"
    db_path = processed_dir / f"{base_name}.db"
    cuestionario_path = logs_dir / f"cuestionario_{base_name}.md"
    
    utils.convertir_a_markdown(input_file_path, markdown_path)
    store = utils.abrir_o_crear_store(markdown_path, db_path, args.embedding)
    
    # Defensive fallback if the Ollama daemon is unreachable or missing weights.
    ollama_dir = os.environ.get("OLLAMA_MODELS", "")
    if modelo_disponible(args.modelo, ollama_dir):
        llm = ChatOllama(model=args.modelo, temperature=args.temperatura)
        print(f"[Main] Usando LLM: {args.modelo}")
    else:
        llm = None
        print(f"[Main] Modelo {args.modelo} no disponible. Usando modo fallback.")
        
    # Decouple CLI parameters from LangGraph node implementations.
    params = {
        "top_n": args.top_n,
        "top_k": args.top_k,
        "q_len": args.q_len,
        "a_len": args.a_len,
        "perfil": args.perfil
    }
    
    grafo = RAG.crear_grafo(llm, store, prompts_dir, params)
    
    # Initial graph state injection required by Agent 1.
    transcripcion = markdown_path.read_text(encoding="utf-8")
    initial_state = {
        "transcripcion_original": transcripcion,
        "perfil_objetivo": args.perfil
    }
    
    print(f"\n[Main] Iniciando flujo RAG para perfil: {args.perfil}")
    result = grafo.invoke(initial_state)
    
    cuestionario_path.write_text(result["cuestionario_final"], encoding="utf-8")
    print(f"\n[Main] Proceso terminado. Archivo generado en: {cuestionario_path}")

if __name__ == "__main__":
    main()
