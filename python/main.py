from .agents import build_agents
from .config import load_settings
from .graph import build_graph
from .ingestion import convert_to_markdown, open_or_create_store
from .rag_tools import build_tools


def main() -> None:
    settings = load_settings()
    convert_to_markdown(settings.input_path, settings.markdown_path)
    store = open_or_create_store(settings)
    extract_concepts, retrieve_context = build_tools(store, settings)
    analyst, question_generator, resolver, adapter = build_agents(
        settings, store, extract_concepts, retrieve_context
    )
    graph = build_graph(analyst, question_generator, resolver, adapter)
    transcription = settings.markdown_path.read_text(encoding="utf-8")
    result = graph.invoke({
        "transcripcion_original": transcription,
        "perfil_objetivo": settings.target_profile,
    })
    settings.output_path.write_text(result["cuestionario_final"], encoding="utf-8")
    print("[Main] Preguntas:", len(result["preguntas_generadas"]))
    print("[Main] Respuestas:", len(result["respuestas_crudas"]))
    print("[Main] Resultado:", settings.output_path)


if __name__ == "__main__":
    main()
