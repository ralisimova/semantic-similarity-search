import streamlit as st
from sematch_similarity import sematch_similarity
from geoproject.similarity import (
    most_similar_sematch,
    semantic_similarity,
    most_similar_entities,
    load_graph
)
from utils import build_label_index, wikidata_search


# ------------------------------------------------------------
# LOAD GRAPH
# ------------------------------------------------------------
@st.cache_resource
def get_graph():
    return load_graph("data/processed/geo_graph.gpickle")


G = get_graph()
label_index = build_label_index(G)


# ------------------------------------------------------------
# ENTITY RESOLUTION
# ------------------------------------------------------------
def resolve_entity_candidates(user_input, label_index):
    user_input = user_input.strip()

    # local graph exact match first
    local_qid = label_index.get(user_input.lower())

    if local_qid:
        return [{
            "qid": local_qid,
            "label": G.nodes[local_qid].get("label", user_input),
            "description": "Local graph match"
        }]

    # fallback to Wikidata API
    return wikidata_search(user_input)


# ------------------------------------------------------------
# PAGE TITLE
# ------------------------------------------------------------
st.set_page_config(
    page_title="Semantic Similarity Search",
    layout="wide"
)

st.title("Semantic Similarity Search in Knowledge Graphs")

st.write(
    """
    Demonstrator for semantic similarity search over a
    Wikidata geographic knowledge graph.
    """
)

# ------------------------------------------------------------
# TABS
# ------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "Compare Two Places",
    "Explore Similar",
    "Graph Overview"
])


# ============================================================
# TAB 1 — COMPARE
# ============================================================
with tab1:

    st.header("Compare Two Geographic Entities")

    col1, col2 = st.columns(2)

    with col1:
        entity_a_text = st.text_input(
            "Entity A",
            value="Sofia"
        )

    with col2:
        entity_b_text = st.text_input(
            "Entity B",
            value="Plovdiv"
        )

    # candidate resolution
    candidates_a = resolve_entity_candidates(
        entity_a_text,
        label_index
    )

    candidates_b = resolve_entity_candidates(
        entity_b_text,
        label_index
    )

    entity_a_choice = st.selectbox(
        "Select entity A",
        candidates_a,
        format_func=lambda x:
            f"{x.get('label','?')} "
            f"({x.get('qid', x.get('id','?'))}) — "
            f"{x.get('description','')}",
        key="entity_a_select"
    )

    entity_b_choice = st.selectbox(
        "Select entity B",
        candidates_b,
        format_func=lambda x:
            f"{x.get('label','?')} "
            f"({x.get('qid', x.get('id','?'))}) — "
            f"{x.get('description','')}",
        key="entity_b_select"
    )

    entity_a = entity_a_choice.get(
        "qid",
        entity_a_choice.get("id")
    )

    entity_b = entity_b_choice.get(
        "qid",
        entity_b_choice.get("id")
    )

    # graph membership warnings
    if entity_a not in G:
        st.warning(
            f"{entity_a_choice['label']} "
            f"is not present in the geographic subgraph."
        )

    if entity_b not in G:
        st.warning(
            f"{entity_b_choice['label']} "
            f"is not present in the geographic subgraph."
        )

    if st.button("Compute Similarity"):
      if entity_a is None or entity_b is None:
        st.error("Entity not found. Try a different name (e.g., Sofia, France).")
      else:
        score = sematch_similarity(
    entity_a,
    entity_b
)
        st.subheader("Similarity Results")
        st.metric(
    "Sematch Similarity",
    score
)
        # if entity_a not in G or entity_b not in G:
        #     st.error(
        #         "One or both entities are outside "
        #         "the geographic subgraph."
        #     )

        # else:
        #     result = semantic_similarity(
        #         G,
        #         entity_a,
        #         entity_b
        #     )

        #     st.subheader("Similarity Results")

        #     st.metric(
        #         "Final Similarity Score",
        #         round(result["score"], 4)
        #     )

        #     c1, c2, c3 = st.columns(3)

        #     with c1:
        #         st.metric(
        #             "Path Similarity",
        #             round(result["path_similarity"], 4)
        #         )

        #     with c2:
        #         st.metric(
        #             "Neighbor Similarity",
        #             round(result["neighbor_similarity"], 4)
        #         )

        #     with c3:
        #         st.metric(
        #             "Relation Similarity",
        #             round(result["relation_similarity"], 4)
        #         )

        st.success(
                "Similarity computed successfully"
            )


# ============================================================
# TAB 2 — EXPLORE
# ============================================================
with tab2:

    st.header("Explore Similar Geographic Entities")

    query_text = st.text_input(
        "Search entity",
        value="Sofia",
        key="explore_input"
    )

    explore_candidates = resolve_entity_candidates(
        query_text,
        label_index
    )

    explore_choice = st.selectbox(
        "Select entity",
        explore_candidates,
        format_func=lambda x:
            f"{x.get('label','?')} "
            f"({x.get('qid', x.get('id','?'))}) — "
            f"{x.get('description','')}",
        key="explore_select"
    )

    selected_qid = explore_choice.get(
        "qid",
        explore_choice.get("id")
    )

    if st.button("Find Similar Entities"):

        if selected_qid not in G:
            st.error(
                "Entity not present in geographic subgraph."
            )

        else:
            results = most_similar_sematch(
                G,
                selected_qid
            )

            st.subheader("Most Similar Entities")

            for node, score in results:
                label = G.nodes[node].get(
                    "label",
                    node
                )

                st.write(
                    f"**{label}** ({node}) "
                    f"→ {round(score,4)}"
                )


# ============================================================
# TAB 3 — GRAPH
# ============================================================
with tab3:

    st.header("Knowledge Graph Overview")

    st.metric(
        "Nodes",
        G.number_of_nodes()
    )

    st.metric(
        "Edges",
        G.number_of_edges()
    )

    st.write("Sample entities:")

    sample = list(G.nodes())[:15]

    for node in sample:
        label = G.nodes[node].get(
            "label",
            node
        )
        st.write(f"- {label} ({node})")