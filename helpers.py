import json
import pickle
import tempfile
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components


def load_graph(path):
    """Load a pickled NetworkX graph from `path`."""
    with open(path, "rb") as f:
        return pickle.load(f)


def load_stats(path):
    """Load JSON stats from `path`. Returns empty dict on error."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return {}


def build_label_index(G):
    """Return a mapping of lowercase label -> node id for quick lookups."""
    label_to_qid = {}
    for node, data in G.nodes(data=True):
        label = data.get("label", "").strip()
        if label:
            label_to_qid[label.lower()] = node
    return label_to_qid


def build_local_graph(G, center_node):
    """Create a small subgraph H containing `center_node` and its neighbors.

    The returned graph contains node labels and edge relation metadata used
    by the visualizer.
    """
    H = nx.Graph()

    H.add_node(center_node, label=G.nodes[center_node].get("label", center_node))

    for neighbor in G.neighbors(center_node):
        H.add_node(neighbor, label=G.nodes[neighbor].get("label", neighbor))
        edge = G.get_edge_data(center_node, neighbor) or {}
        H.add_edge(center_node, neighbor, label=edge.get("relation", ""))

    return H


def visualize_graph(H):
    """Render a small graph `H` as HTML and embed it in Streamlit."""
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")

    for node, data in H.nodes(data=True):
        net.add_node(node, label=data.get("label", node))

    for u, v, data in H.edges(data=True):
        net.add_edge(u, v, title=data.get("label", ""))

    # Save to a temporary file and embed the generated HTML into Streamlit.
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
        net.save_graph(tmp_file.name)
        tmp_path = tmp_file.name

    with open(tmp_path, "r", encoding="utf-8") as f:
        html = f.read()

    components.html(html, height=650)


def get_entity_info(G, node):
    """Return a small info dict for `node` including neighbors and relations."""
    data = G.nodes[node]
    info = {
        "qid": node,
        "label": data.get("label", node),
        "degree": G.degree(node),
        "relations": [],
    }

    for neighbor in G.neighbors(node):
        edge_data = G.get_edge_data(node, neighbor) or {}
        info["relations"].append(
            {
                "target": G.nodes[neighbor].get("label", neighbor),
                "relation": edge_data.get("relation", "unknown"),
            }
        )

    return info
