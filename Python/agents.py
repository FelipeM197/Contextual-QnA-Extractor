from pathlib import Path

from langchain_ollama import ChatOllama

from config import Settings
from rag_tools import QAState, StructuredQuestions, context_certainty


def load_prompt(settings: Settings, name: str) -> str:
    return (settings.prompts_dir / name).read_text(encoding="utf-8")


def build_agents(settings: Settings, store, extract_concepts, retrieve_context):
    llm = ChatOllama(
        model=settings.model_name,
        temperature=0,
        num_ctx=settings.num_ctx,
        num_predict=settings.num_predict,
        keep_alive="0",
    )

    def analyst(state: QAState) -> dict:
        concepts = extract_concepts.invoke({"text": state["transcripcion_original"]})
        print("[Agente 1] Conceptos:", ", ".join(concepts))
        return {"conceptos_clave": concepts}

    def question_generator(state: QAState) -> dict:
        prompt = load_prompt(settings, "questions.md").format(
            concepts=", ".join(state["conceptos_clave"]),
            transcription=state["transcripcion_original"],
        )
        questions = llm.with_structured_output(StructuredQuestions).invoke(prompt).questions[:5]
        terms = state["conceptos_clave"] or ["the document"]
        for term in terms:
            if len(questions) >= 5:
                break
            questions.append(f"What does the document explain about {term}?")
        while len(questions) < 5:
            questions.append(f"What is the main point of section {len(questions) + 1}?")
        print("[Agente 2] Preguntas generadas:", len(questions))
        return {"preguntas_generadas": questions}

    def resolver(state: QAState) -> dict:
        answers = []
        answer_template = load_prompt(settings, "answer.md")
        for question in state["preguntas_generadas"]:
            context = retrieve_context.invoke({"question": question})
            response = llm.invoke(answer_template.format(question=question, context=context)).content
            print(f"[Agente 3] Certeza: {context_certainty(context):.2f}")
            answers.append({"pregunta": question, "respuesta": response, "fuente": context})
        return {"respuestas_crudas": answers}

    def adapter(state: QAState) -> dict:
        profile = state.get("perfil_objetivo", settings.target_profile)
        lines = [f"# Cuestionario para {profile}", ""]
        for index, item in enumerate(state["respuestas_crudas"], start=1):
            lines.extend([f"## {index}. {item['pregunta']}", "", item["respuesta"], ""])
        print("[Agente 4] Se conservaron todas las respuestas")
        return {"cuestionario_final": "\n".join(lines)}

    return analyst, question_generator, resolver, adapter
