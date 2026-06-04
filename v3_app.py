import streamlit as st

from sematch_similarity import sematch_label_similarity, sematch_similarity
from geoproject.v2_sematch_similarity import (
    sematch_hybrid_similarity,
    most_similar_entities,
)

from utils import build_label_index, build_local_graph, get_entity_info, visualize_graph, wikidata_search
from geoproject.similarity import load_graph


# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
st.set_page_config(
    page_title="Semantic Similarity KG Demo",
    layout="wide"
)


# ------------------------------------------------------------
# LOAD GRAPH (cached)
# ------------------------------------------------------------
@st.cache_resource
def get_graph():
  # Why isnt this a subgraph
    return load_graph("data/processed/movies_graph.gpickle")


G = get_graph()
label_index = build_label_index(G)


# ------------------------------------------------------------
# BUILD LABEL LIST (for dropdown usability)
# ------------------------------------------------------------
labels = [
    (node, data.get("label", node))
    for node, data in G.nodes(data=True)
    if data.get("label")
]

labels = []

for node, data in G.nodes(data=True):
    label = data.get("label", "")

    if not label:
        continue

    label = str(label).strip()

    # FILTER BAD TOKENS
    if label.startswith("!") or label.startswith("config"):
        continue

    if len(label) < 2:
        continue

    labels.append((node, label))
    
labels = sorted(labels, key=lambda x: x[1])


node_to_label = {n: l for n, l in labels}
label_to_node = {l: n for n, l in labels}


# ------------------------------------------------------------
# TITLE
# ------------------------------------------------------------
st.title("🌍 Semantic Similarity in Knowledge Graphs (Sematch)")
st.caption("Compare geographic entities using Wikidata5M + Sematch WordNet similarity")


# ------------------------------------------------------------
# SIDEBAR INFO
# ------------------------------------------------------------
st.sidebar.header("📊 Graph Stats")

st.sidebar.write(f"Nodes: {G.number_of_nodes()}")
st.sidebar.write(f"Edges: {G.number_of_edges()}")


# ------------------------------------------------------------
# ENTITY SELECTION
# ------------------------------------------------------------
st.subheader("🔎 Compare Two Entities")

col1, col2 = st.columns(2)

with col1:
    entity_a_label = st.selectbox(
        "Entity A",
        [l for _, l in labels],
        index=0,
        key="entity_a"
    )

with col2:
    entity_b_label = st.selectbox(
        "Entity B",
        [l for _, l in labels],
        index=1,
        key="entity_b"
        
    )


entity_a = label_to_node[entity_a_label]
entity_b = label_to_node[entity_b_label]
# def resolve_entity_candidates(user_input, label_index):
#     # exact local match first
#     local_qid = label_index.get(user_input.lower())

#     if local_qid:
#         return [{
#             "qid": local_qid,
#             "label": user_input,
#             "description": "Local graph match"
#         }]

#     return wikidata_search(user_input)

 
# entity_a_text = st.text_input(
#     "Entity A",
#     value="Sofia"
# )

# entity_b_text = st.text_input(
#     "Entity B",
#     value="Plovdiv"
# )

# candidates_a = resolve_entity_candidates(
#     entity_a_text,
#     label_index
# )

# candidates_b = resolve_entity_candidates(
#     entity_b_text,
#     label_index
# )

# candidates_a = label_to_node[entity_a_text]
# candidates_b = label_to_node[entity_b_text]
# print(candidates_a,candidates_b)

# candidates_a = resolve_entity_candidates(
#     entity_a_text,
#     label_index
# )

# candidates_b = resolve_entity_candidates(
#     entity_b_text,
#     label_index
# )

# entity_a_choice = st.selectbox(
#     "Select matching entity for A",
#     candidates_a,
#     format_func=lambda x:
#     f"{x.get('label','?')} "
#     f"({x.get('qid', x.get('id','?'))}) - "
#     f"{x.get('description','')}"
# )

# entity_b_choice = st.selectbox(
#     "Select matching entity for B",
#     candidates_b,
#     format_func=lambda x:
#     f"{x.get('label','?')} "
#     f"({x.get('qid', x.get('id','?'))}) - "
#     f"{x.get('description','')}"
# )


# entity_a = entity_a_choice["qid"]
# entity_b = entity_b_choice["qid"]


# ------------------------------------------------------------
# COMPUTE SIMILARITY BUTTON
# ------------------------------------------------------------
if st.button("Compute Semantic Similarity", type="primary"):

    result = sematch_similarity( entity_a, entity_b)
    print(result)

    # result = sematch_hybrid_similarity(G, entity_a, entity_b)
    st.subheader("📌 Results")

    # col1, col2, col3, col4 = st.columns(4)

    # col1.metric("Final Score", result["score"])
    # col2.metric("Path", result["path"])
    # col3.metric("WUP", result["wup"])
    # col4.metric("LCH", result["lch"])

    # st.success(f"{entity_a_text} ↔ {entity_b_text} similarity computed successfully!")


# ------------------------------------------------------------
# MOST SIMILAR ENTITIES
# ------------------------------------------------------------
st.divider()

st.subheader("🔎 Explore Similar Entities")

selected_label = st.selectbox(
    "Choose entity",
    [l for _, l in labels],
    key="similar"
)

selected_node = label_to_node[selected_label]


top_k = st.slider("Top K results", 3, 20, 10)


if st.button("Find Similar Entities"):

    results = most_similar_entities(
        G,
        selected_node,
        top_k=top_k
    )

    st.write(f"### Most similar to: {selected_label}")

    for node, score in results:
        st.write(
            f"**{node_to_label.get(node, node)}** → `{round(score, 4)}`"
        )


# ------------------------------------------------------------
# OPTIONAL DEBUG SECTION
# ------------------------------------------------------------
with st.expander("🔧 Debug / Node Viewer"):

    node = st.selectbox(
        "Inspect node",
        list(G.nodes())
    )

    st.json(G.nodes[node])
    
st.subheader("Entity Information")

selected_label = st.selectbox(
    "Select entity",
    [l for _, l in labels]
)

selected_node = label_to_node[selected_label]

info = get_entity_info(G, selected_node)

st.write(f"**QID:** {info['qid']}")
st.write(f"**Label:** {info['label']}")
st.write(f"**DBpedia:** {info['dbpedia']}")
st.write(f"**Degree:** {info['degree']}")

st.write("### Relations")

for rel in info["relations"][:20]:
    st.write(
        f"- {rel['relation']} → {rel['target']}"
    )
    
    
    
st.subheader("Local Graph Visualization")

selected_label = st.selectbox(
    "Graph Center",
    [l for _, l in labels],
    key="graph_center"
)

selected_node = label_to_node[selected_label]

H = build_local_graph(
    G,
    selected_node
)

visualize_graph(H)