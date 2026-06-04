def build_label_index(G):
    label_to_qid = {}

    for node, data in G.nodes(data=True):
        label = data.get("label", "").strip()

        if label:
            label_to_qid[label.lower()] = node

    return label_to_qid
  

import requests


GOOD_HINTS = [
    "city", "capital", "municipality", "settlement",
    "country", "region", "district", "province"
]

BAD_HINTS = [
    "female given name", "male given name",
    "surname", "genus", "protein", "gene",
    "species", "film", "album"
]


# def score_candidate(item):
#     score = 0

#     label = (item.get("label") or "").lower()
#     desc = (item.get("description") or "").lower()

#     # boost geographic meaning
#     for w in GOOD_HINTS:
#         if w in desc:
#             score += 50

#     # penalize irrelevant meanings
#     for w in BAD_HINTS:
#         if w in desc:
#             score -= 100

#     # exact label match bonus
#     if label == item.get("search", "").lower():
#         score += 10

#     return score


def wikidata_search(label, limit=5):
    url = "https://www.wikidata.org/w/api.php"

    params = {
        "action": "wbsearchentities",
        "search": label,
        "language": "en",
        "format": "json",
        "limit": limit
    }

    headers = {
        "User-Agent": "SemanticSimilarityDemo/1.0"
    }

    r = requests.get(url, params=params, headers=headers, timeout=10)
    data = r.json()
    results= []
    for item in data.get("search", []):
         results.append({
        "qid": item["id"],
        "label": item.get("label", ""),
        "description": item.get("description", "")
    })

    return results
    candidates = data.get("search", [])
    return candidates
    if not candidates:
        return []

    # rank candidates
    best = None
    best_score = -999

    for c in candidates:
        s = score_candidate(c)

        if s > best_score:
            best_score = s
            best = c

    if best:
        return [{
            "qid": best["id"],
            "label": best.get("label", ""),
            "description": best.get("description", "")
        }]

    return []
# def wikidata_search(label, limit=5):
#     url = "https://www.wikidata.org/w/api.php"

#     params = {
#         "action": "wbsearchentities",
#         "search": label,
#         "language": "en",
#         "format": "json",
#         "limit": limit
#     }

#     headers = {
#         "User-Agent": "SemanticSimilarityDemo/1.0 (MasterProject)"
#     }

#     try:
#         r = requests.get(
#             url,
#             params=params,
#             headers=headers,
#             timeout=15
#         )

#         r.raise_for_status()

#         # debug if needed
#         # print(r.text[:500])

#         data = r.json()

#         results = []

#         for item in data.get("search", []):
#             results.append({
#                 "qid": item["id"],
#                 "label": item.get("label", ""),
#                 "description": item.get("description", "")
#             })

#         return results

#     except Exception as e:
#         print("Wikidata API error:", e)
#         print("Response preview:", r.text[:300] if 'r' in locals() else "")
#         return []
      
from utils import wikidata_search


def resolve_entity(user_input, label_index, G):
    user_input = user_input.strip()

    # already QID
    if user_input in G:
        return user_input

    # local label
    local = label_index.get(user_input.lower())
    print(local)
    if local:
        return local

    # Wikidata API fallback
    results = wikidata_search(user_input, limit=1)
    print(results)
    if results:
        qid = results[0]["qid"]
        print(qid)
        if qid in G:
            return qid

    return None


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


import networkx as nx


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

from  pyvis.network import Network
import streamlit.components.v1 as components
import tempfile
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