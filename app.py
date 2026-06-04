import streamlit as st

from similarity_engine import sematch_similarity
from helpers import build_label_index, build_local_graph, load_graph, visualize_graph, get_entity_info



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


# ------------------------------------------------------------
# COMPUTE SIMILARITY BUTTON
# ------------------------------------------------------------
if st.button("Compute Semantic Similarity", type="primary"):

    result = sematch_similarity( entity_a, entity_b)
    print(result)

    st.subheader("📌 Results")
    st.text(f"**Similarity Score:** `{result}`")



# --------------ENTITY INFO --------------
    
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
    
    
# ------------ LOCAL GRAPH VISUALIZATION --------------
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