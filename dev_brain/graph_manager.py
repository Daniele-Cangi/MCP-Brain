import json
from pathlib import Path
from typing import Optional
from .models import Graph, FrameSnapshot, GraphEdge
from .paths import get_vault_root

def get_graph_path() -> Path:
    return get_vault_root() / "graph.json"

def load_graph() -> Graph:
    """Loads the causal graph from graph.json."""
    path = get_graph_path()
    if not path.exists():
        return Graph(frames=[], edges=[])
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return Graph(**data)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading graph from {path}: {e}")
        return Graph(frames=[], edges=[])

def save_graph(graph: Graph) -> None:
    """Saves the causal graph to graph.json."""
    path = get_graph_path()
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(graph.model_dump_json(indent=2))
    except IOError as e:
        print(f"Error saving graph to {path}: {e}")

def add_frame_node(graph: Graph, frame: FrameSnapshot) -> None:
    """Adds a frame node to the graph."""
    # Check if frame already exists (idempotency)
    if any(f.frame_id == frame.frame_id for f in graph.frames):
        return
    graph.frames.append(frame)

def add_edge(
    graph: Graph,
    from_frame_id: str,
    to_frame_id: str,
    edge_type: str,
    weight: float = 1.0,
) -> None:
    """Adds an edge between two frames."""
    # Check if edge already exists
    for edge in graph.edges:
        if (edge.from_frame_id == from_frame_id and 
            edge.to_frame_id == to_frame_id and 
            edge.type == edge_type):
            return
            
    graph.edges.append(GraphEdge(
        from_frame_id=from_frame_id,
        to_frame_id=to_frame_id,
        type=edge_type,
        weight=weight
    ))
