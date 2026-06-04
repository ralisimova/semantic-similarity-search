from sematch.semantic.similarity import EntitySimilarity, WordNetSimilarity

from mapping import qid_to_dbpedia
from geoproject.similarity import load_graph
from utils import build_label_index

# Initialize once (IMPORTANT for performance)
wns = WordNetSimilarity()
entity_sim = EntitySimilarity()

# ------------------------------------------------------------
# 1. BASIC LABEL-BASED SEMATCH SIMILARITY
# ------------------------------------------------------------
def sematch_similarity(G, a, b, method="path"):
    """
    Compute semantic similarity between two nodes using ONLY labels.
    No external APIs (fully offline except Sematch resources).
    """

    # label_a = G.nodes[a].get("label", "")
    # label_b = G.nodes[b].get("label", "")
    # print(f"Comparing '{label_a}' and '{label_b}' using method '{method}'")
    # if not label_a or not label_b:
    #     return 0.0

    try:
        print(a,b)
        a_uri = qid_to_dbpedia(a)
        b_uri = qid_to_dbpedia(b)

        score = entity_sim.relatedness(
           a_uri,
           b_uri,
            # method
        )

        return float(score) if score is not None else 0.0

    except Exception:
        return 0.0


# ------------------------------------------------------------
# 2. HYBRID SEMATCH SCORE (ROBUST FOR DEMO)
# ------------------------------------------------------------
def sematch_hybrid_similarity(G, a, b):
    """
    Combines multiple Sematch WordNet strategies for stability.
    This is MUCH better for demo purposes than a single method.
    """

    label_a = G.nodes[a].get("label", "")
    label_b = G.nodes[b].get("label", "")

    if not label_a or not label_b:
        return {
            "score": 0.0,
            "path": 0.0,
            "wup": 0.0,
            "lch": 0.0
        }

    try:
        path = wns.word_similarity(label_a, label_b, "path")
        wup = wns.word_similarity(label_a, label_b, "wup")
        lch = wns.word_similarity(label_a, label_b, "lch")

        path = float(path) if path else 0.0
        wup = float(wup) if wup else 0.0
        lch = float(lch) if lch else 0.0

        final = (
            0.4 * path +
            0.3 * wup +
            0.3 * lch
        )

        return {
            "score": round(final, 4),
            "path": round(path, 4),
            "wup": round(wup, 4),
            "lch": round(lch, 4)
        }

    except Exception:
        return {
            "score": 0.0,
            "path": 0.0,
            "wup": 0.0,
            "lch": 0.0
        }


# ------------------------------------------------------------
# 3. FIND MOST SIMILAR ENTITIES (FAST, STREAMLIT SAFE)
# ------------------------------------------------------------
def most_similar_entities(G, entity, top_k=10, method="path"):
    """
    Finds most semantically similar nodes inside YOUR subgraph only.
    """

    results = []

    if entity not in G:
        return []

    for node in G.nodes():

        if node == entity:
            continue

        score = sematch_similarity(G, entity, node, method=method)
        results.append((node, score))

    results.sort(key=lambda x: x[1], reverse=True)

    return results[:top_k]

# @st.cache_resource
def get_graph():
  # Why isnt this a subgraph
    return load_graph("data/processed/geo_graph.gpickle")


G = get_graph()
label_index = build_label_index(G)

if __name__ == "__main__":
    print(sematch_similarity(G,"Q472", "Q219"))
    print(most_similar_entities(G,"Q472", top_k=5))
    # print(
    # entity_sim.relatedness(
    #     'http://dbpedia.org/resource/Sofia',
    #     'http://dbpedia.org/resource/Plovdiv'
    # )
# )