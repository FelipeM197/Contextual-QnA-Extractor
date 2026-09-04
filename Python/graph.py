from langgraph.graph import END, START, StateGraph

from rag_tools import QAState


def build_graph(analyst, question_generator, resolver, adapter):
    builder = StateGraph(QAState)
    builder.add_node("analyst", analyst)
    builder.add_node("question_generator", question_generator)
    builder.add_node("resolver", resolver)
    builder.add_node("adapter", adapter)
    builder.add_edge(START, "analyst")
    builder.add_edge("analyst", "question_generator")
    builder.add_edge("question_generator", "resolver")
    builder.add_edge("resolver", "adapter")
    builder.add_edge("adapter", END)
    return builder.compile()
