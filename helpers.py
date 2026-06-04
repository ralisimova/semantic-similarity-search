import pickle
import networkx as nx
from  pyvis.network import Network
import streamlit.components.v1 as components
import tempfile


def load_graph(path):
    with open(path, "rb") as f:
        return pickle.load(f)


def build_label_index(G):
    label_to_qid = {}

    for node, data in G.nodes(data=True):
        label = data.get("label", "").strip()

        if label:
            label_to_qid[label.lower()] = node

    return label_to_qid
  
  
def build_local_graph(G, center_node):

    H = nx.Graph()

    H.add_node(
        center_node,
        label=G.nodes[center_node].get("label", center_node)
    )

    for neighbor in G.neighbors(center_node):

        H.add_node(
            neighbor,
            label=G.nodes[neighbor].get("label", neighbor)
        )

        edge = G.get_edge_data(center_node, neighbor)

        H.add_edge(
            center_node,
            neighbor,
            label=edge.get("relation", "")
        )

    return H
  
  



def visualize_graph(H):

    net = Network(
        height="600px",
        width="100%",
        bgcolor="#ffffff",
        font_color="black"
    )

    for node, data in H.nodes(data=True):

        net.add_node(
            node,
            label=data.get("label", node)
        )

    for u, v, data in H.edges(data=True):

        net.add_edge(
            u,
            v,
            title=data.get("label", "")
        )

    tmp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".html"
    )

    net.save_graph(tmp_file.name)

    html = open(
        tmp_file.name,
        "r",
        encoding="utf-8"
    ).read()

    components.html(
        html,
        height=650
    )


def get_entity_info(G, node):
    data = G.nodes[node]

    info = {
        "qid": node,
        "label": data.get("label", node),
        "dbpedia": data.get("dbpedia", "N/A"),
        "degree": G.degree(node),
        "relations": []
    }

    for neighbor in G.neighbors(node):
        edge_data = G.get_edge_data(node, neighbor)

        info["relations"].append({
            "target": G.nodes[neighbor].get("label", neighbor),
            "relation": edge_data.get("relation", "unknown")
        })

    return info
