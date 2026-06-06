import re
import json
import os

import networkx as nx
from collections import defaultdict
from tqdm import tqdm
import pickle

INPUT_PATH = "data/processed/geo_subgraph_v2.txt"
ENTITY_PATH = "data/raw/wikidata5m_entity.txt"
CANONICAL_PATH = "data/processed/canonical_labels.json"
OUTPUT_PATH = "data/processed/geo_graph_v2.gpickle"


# ------------------------------------------------------------
# STEP 1: Load entity labels 
# ------------------------------------------------------------
# def load_entity_map(path):
#     entity_map = {}
#     with open(path, "r", encoding="utf-8") as f:
#         for line in f:
#             parts = line.strip().split("\t")
#             if len(parts) >= 2:
#                 entity_map[parts[0]] = parts[1]
#     return entity_map


def load_canonical_labels(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except Exception as e:
        print("Failed to load canonical labels:", e)
        return {}

# ------------------------------------------------------------
# STEP 2: Load  triples
# ------------------------------------------------------------
def load_triples(path):
    triples = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == 3:
                h, r, t = parts
                triples.append((h, r, t))
    return triples


# ------------------------------------------------------------
# STEP 3: Build NetworkX graph
# ------------------------------------------------------------
def build_graph(triples, entity_map):
    G = nx.Graph()

    for h, r, t in tqdm(triples, desc="Building graph"):
        # Add nodes with labels
        if h not in G:
            G.add_node(h, label=entity_map.get(h, h))
        if t not in G:
            G.add_node(t, label=entity_map.get(t, t))

        # Add edges
        G.add_edge(h, t, relation=r)

    return G


# ------------------------------------------------------------
# STEP 4: Compute node statistics
# ------------------------------------------------------------
def compute_node_features(G):
    degree_dict = dict(G.degree())

    for node in G.nodes():
        G.nodes[node]["degree"] = degree_dict.get(node, 0)


# ------------------------------------------------------------
# STEP 5: Save graph
# ------------------------------------------------------------
def save_graph(G, path):
    with open(path, "wb") as f:
      pickle.dump(G, f)


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():
    print("Loading entity map...")
    entity_map = load_canonical_labels(CANONICAL_PATH)

    print("Loading triples...")
    triples = load_triples(INPUT_PATH)

    print("Building NetworkX graph...")
    G = build_graph(triples, entity_map)

    print("Computing node features...")
    compute_node_features(G)

    print("Saving graph...")
    save_graph(G, OUTPUT_PATH)

    print(f"Graph saved to: {OUTPUT_PATH}")

    print("\nGraph stats:")
    print("Nodes:", G.number_of_nodes())
    print("Edges:", G.number_of_edges())


if __name__ == "__main__":
    main()