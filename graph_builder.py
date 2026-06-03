import re

import networkx as nx
from collections import defaultdict
from tqdm import tqdm
import pickle

INPUT_PATH = "data/processed/geo_subgraph.txt"
ENTITY_PATH = "data/raw/wikidata5m_entity.txt"
OUTPUT_PATH = "data/processed/geo_graph.gpickle"


# ------------------------------------------------------------
# STEP 1: Load entity labels (QID -> human name)
# ------------------------------------------------------------
def load_entity_map(path):
    entity_map = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= 2:
                entity_map[parts[0]] = parts[1]
    return entity_map
# import re


# def score_alias(alias):
#     alias = alias.strip()

#     score = 0

#     # heavy penalties
#     if "/" in alias:
#         score -= 1000
#     if "comments" in alias.lower():
#         score -= 1000

#     # prefer readable title case
#     if re.match(r"^[A-ZÀ-Ž][A-Za-zÀ-ÿ0-9 .,'()-]+$", alias):
#         score += 100

#     # prefer alphabetic names
#     if re.match(r"^[A-Za-zÀ-ÿ .,'()-]+$", alias):
#         score += 30

#     # penalize all lowercase
#     if alias.islower():
#         score -= 40

#     # shorter often cleaner
#     score -= len(alias) * 0.2

#     return score


# def load_entity_map(path):
#     entity_map = {}

#     with open(path, "r", encoding="utf-8") as f:
#         for line in f:
#             parts = line.strip().split("\t")

#             if len(parts) < 2:
#                 continue

#             qid = parts[0]
#             aliases = parts[1:]

#             best = max(aliases, key=score_alias)
#             entity_map[qid] = best.strip()

#     return entity_map
# ------------------------------------------------------------
# STEP 2: Load cleaned geographic triples
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
# STEP 4: Compute node statistics (optional but useful for similarity)
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
# STEP 6: Load graph (utility function for later)
# ------------------------------------------------------------
def load_graph(path):
    with open(path, "rb") as f:
        return pickle.load(f)


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():
    print("Loading entity map...")
    entity_map = load_entity_map(ENTITY_PATH)

    print("Loading triples...")
    triples = load_triples(INPUT_PATH)

    print("Building NetworkX graph...")
    G = build_graph(triples, entity_map)

    print("Computing node features...")
    compute_node_features(G)

    print("Saving graph...")
    save_graph(G, OUTPUT_PATH)

    print("DONE ✔")
    print(f"Graph saved to: {OUTPUT_PATH}")

    print("\nGraph stats:")
    print("Nodes:", G.number_of_nodes())
    print("Edges:", G.number_of_edges())


if __name__ == "__main__":
    main()