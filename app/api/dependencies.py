from app.graph.builder import build_graph

_graph_instance = None


def get_graph():
    global _graph_instance

    if _graph_instance is None:
        _graph_instance = build_graph()

    return _graph_instance