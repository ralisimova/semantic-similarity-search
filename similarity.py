import networkx as nx
from collections import defaultdict
import pickle

GRAPH_PATH = "data/processed/geo_graph.gpickle"


# ------------------------------------------------------------
# LOAD GRAPH
# ------------------------------------------------------------
def load_graph(path):
    with open(path, "rb") as f:
        return pickle.load(f)


# ------------------------------------------------------------
# 1. SHORTEST PATH SIMILARITY
# ------------------------------------------------------------
def shortest_path_similarity(G, a, b):
    try:
        path_length = nx.shortest_path_length(G, a, b)
        return 1 / (1 + path_length)
    except:
        return 0.0


# ------------------------------------------------------------
# 2. NEIGHBORHOOD (JACCARD) SIMILARITY
# ------------------------------------------------------------
def jaccard_similarity(G, a, b):
    neighbors_a = set(G.neighbors(a))
    neighbors_b = set(G.neighbors(b))

    if not neighbors_a and not neighbors_b:
        return 0.0

    intersection = neighbors_a.intersection(neighbors_b)
    union = neighbors_a.union(neighbors_b)

    return len(intersection) / len(union)


# ------------------------------------------------------------
# 3. RELATION-BASED SIMILARITY
# (P17, P36, P131 importance)
# ------------------------------------------------------------
def relation_similarity(G, a, b):
    def get_relations(node):
        rels = defaultdict(set)

        for neighbor in G.neighbors(node):
            edge_data = G.get_edge_data(node, neighbor)
            rel = edge_data.get("relation")
            rels[rel].add(neighbor)

        return rels

    rel_a = get_relations(a)
    rel_b = get_relations(b)

    all_rels = set(rel_a.keys()).union(set(rel_b.keys()))

    if not all_rels:
        return 0.0

    score = 0.0
    for r in all_rels:
        set_a = rel_a.get(r, set())
        set_b = rel_b.get(r, set())

        if not set_a and not set_b:
            continue

        inter = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))

        if union > 0:
            score += inter / union

    return score / len(all_rels)


# ------------------------------------------------------------
# 4. FINAL SEMANTIC SIMILARITY SCORE
# ------------------------------------------------------------
def semantic_similarity(G, a, b):
    path_sim = shortest_path_similarity(G, a, b)
    neighbor_sim = jaccard_similarity(G, a, b)
    relation_sim = relation_similarity(G, a, b)

    final_score = (
        0.4 * path_sim +
        0.4 * neighbor_sim +
        0.2 * relation_sim
    )

    return {
        "score": round(final_score, 4),
        "path_similarity": round(path_sim, 4),
        "neighbor_similarity": round(neighbor_sim, 4),
        "relation_similarity": round(relation_sim, 4)
    }


# ------------------------------------------------------------
# 5. FIND MOST SIMILAR ENTITIES
# ------------------------------------------------------------
def most_similar_entities(G, entity, top_k=5):
    scores = []
    print(entity,'search for similar entities')
    for node in G.nodes():
        if node == entity:
            continue

        sim = semantic_similarity(G, entity, node)["score"]
        scores.append((node, sim))

    scores.sort(key=lambda x: x[1], reverse=True)
    print(len(scores),'found similar entities')
    return scores[:top_k]


# ------------------------------------------------------------
# 6. DEMO TEST
# ------------------------------------------------------------
if __name__ == "__main__":
    G = load_graph()

    a = "Q472"   # Sofia (example QID)
    b = "Q459"  # Plovdiv (example QID)

    result = semantic_similarity(G, a, b)

    print("\nSemantic Similarity Result:")
    print(result)

    print("\nTop similar entities to Sofia:")
    print(most_similar_entities(G, a))