import streamlit as st

from similarity_engine import semantic_search, sematch_similarity, word_similarity
from helpers import (
    build_label_index,
    build_local_graph,
    load_graph,
    visualize_graph,
    get_entity_info,
)

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
    return load_graph("data/processed/geo_graph_v2.gpickle")


G = get_graph()
label_index = build_label_index(G)

# ------------------------------------------------------------
# BUILD LABELS
# ------------------------------------------------------------
labels = []

for node, data in G.nodes(data=True):
    label = data.get("label", "")

    if not label:
        continue

    label = str(label).strip()

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
st.title("🌍 Semantic Similarity in Knowledge Graphs")
st.caption(
    "Explore entities and compute semantic similarity using "
    "Wikidata5M + Sematch"
)

# ------------------------------------------------------------
# TABS
# ------------------------------------------------------------
tab_home, tab_compare, tab_search, tab_entity, tab_graph = st.tabs(
    [
        "🏠 Home",
        "🔎 Compare Entities",
           "🔍 Semantic Search",
        "📄 View Entity",
        "🕸️ Explore Graph",
    ]
)

# ============================================================
# HOME TAB
# ============================================================
with tab_home:

    st.header("Knowledge Graph Overview")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Nodes", f"{G.number_of_nodes():,}")

    with col2:
        st.metric("Edges", f"{G.number_of_edges():,}")

    st.markdown("---")

    st.write(
        """
        This demo allows you to:

        - Compare semantic similarity between entities
        - Inspect entity metadata and relationships
        - Explore local graph neighborhoods
        - Visualize graph structure around a selected entity
        """
    )

# ============================================================
# COMPARE ENTITIES TAB
# ============================================================
with tab_compare:

    st.header("Compare Two Entities")

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
    print(entity_a)
    print(entity_b)
    print(entity_a == entity_b)

    if st.button(
        "Compute Semantic Similarity",
        type="primary",
        key="similarity_btn"
    ):

        similarity_result = sematch_similarity(entity_a, entity_b)
        word_result = word_similarity(entity_a_label, entity_b_label)
        

        st.success("Similarity computed successfully")

        st.metric(
            label="Semantic Similarity Score",
            value=f"{similarity_result:.4f}"
            if isinstance(similarity_result, (float, int))
            else similarity_result
        )


        st.metric(
            label="Word Similarity Score",
            value=f"{word_result:.4f}"
            if isinstance(word_result, (float, int))
            else word_result
        )
# ============================================================
# VIEW ENTITY TAB
# ============================================================
with tab_entity:

    st.header("Entity Information")

    selected_label = st.selectbox(
        "Select Entity",
        [l for _, l in labels],
        key="entity_info"
    )

    selected_node = label_to_node[selected_label]

    info = get_entity_info(G, selected_node)

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**QID:** {info['qid']}")
        st.write(f"**Label:** {info['label']}")

    with col2:
        st.write(f"**Degree:** {info['degree']}")
        st.write(f"**DBpedia:** {info['dbpedia']}")

    st.markdown("### Relations")

    if info["relations"]:
        for rel in info["relations"][:20]:
            st.write(
                f"• **{rel['relation']}** → {rel['target']}"
            )
    else:
        st.info("No relations found.")

# ============================================================
# EXPLORE GRAPH TAB
# ============================================================
with tab_graph:

    st.header("Local Graph Visualization")

    graph_center_label = st.selectbox(
        "Graph Center",
        [l for _, l in labels],
        key="graph_center"
    )

    graph_center_node = label_to_node[graph_center_label]

    H = build_local_graph(
        G,
        graph_center_node
    )

    visualize_graph(H)
    
with tab_search:

    st.header("Semantic Search")

    query = st.text_input(
        "Enter a concept",
        placeholder="e.g. space adventure"
    )

    top_k = st.slider(
        "Results",
        min_value=5,
        max_value=50,
        value=10
    )

    if st.button(
        "Search",
        key="semantic_search"
    ):

        results = semantic_search(
            query,
            G,
            top_k
        )

        st.subheader("Results")

        if not results:
            st.warning("No matches found.")

        else:

            for node, label, score in results:

                st.write(
                    f"**{label}** "
                    f"(score={score:.3f})"
                )