import streamlit as st
import networkx as nx
from geoproject.similarity import  most_similar_entities, load_graph, most_similar_sematch
from utils import build_label_index, resolve_entity, wikidata_search
from streamlit_searchbox import st_searchbox
from sematch_similarity import sematch_similarity

# ------------------------------------------------------------
# LOAD GRAPH 
# ------------------------------------------------------------
@st.cache_resource
def get_graph():
    return load_graph("data/processed/geo_graph.gpickle")


G = get_graph()
label_index = build_label_index(G)

# G = get_graph()

label_to_qid = {}
entity_labels = []

for node, data in G.nodes(data=True):
    label = data.get("label", "").strip()

    if label:
        label_to_qid[label] = node
        entity_labels.append(label)

entity_labels = sorted(set(entity_labels))
# ------------------------------------------------------------
# TITLE
# ------------------------------------------------------------
st.title("Semantic Similarity Search in Knowledge Graphs")
st.write("Compare geographic entities using a Wikidata-based knowledge graph.")


# ------------------------------------------------------------
# ENTITY INPUTS
# ------------------------------------------------------------
st.sidebar.header("Entity Comparison")



def resolve_entity_candidates(user_input, label_index):
    # exact local match first
    local_qid = label_index.get(user_input.lower())

    if local_qid:
        return [{
            "qid": local_qid,
            "label": user_input,
            "description": "Local graph match"
        }]

    return wikidata_search(user_input)

 
entity_a_text = st.text_input(
    "Entity A",
    value="Sofia"
)

entity_b_text = st.text_input(
    "Entity B",
    value="Plovdiv"
)

candidates_a = resolve_entity_candidates(
    entity_a_text,
    label_index
)

candidates_b = resolve_entity_candidates(
    entity_b_text,
    label_index
)

entity_a_choice = st.selectbox(
    "Select matching entity for A",
    candidates_a,
    format_func=lambda x:
    f"{x.get('label','?')} "
    f"({x.get('qid', x.get('id','?'))}) - "
    f"{x.get('description','')}"
)

entity_b_choice = st.selectbox(
    "Select matching entity for B",
    candidates_b,
    format_func=lambda x:
    f"{x.get('label','?')} "
    f"({x.get('qid', x.get('id','?'))}) - "
    f"{x.get('description','')}"
)


entity_a = entity_a_choice["qid"]
entity_b = entity_b_choice["qid"]


if entity_a not in G:
    st.warning(
        f"{entity_a_choice['label']} is not present in the geographic subgraph."
    )

if entity_b not in G:
    st.warning(
        f"{entity_b_choice['label']} is not present in the geographic subgraph."
    )
       
print (entity_a, entity_b)
# ------------------------------------------------------------
# RUN SIMILARITY
# ------------------------------------------------------------
if st.sidebar.button("Compute Similarity"):

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
    #     st.metric("Final Similarity Score", result["score"])

    #     col1, col2, col3, col4 = st.columns(4)

    #     with col1:
    #         st.metric("Path Similarity", result["path_similarity"])

    #     with col2:
    #         st.metric("Neighbor Similarity", result["neighbor_similarity"])

    #     with col3:
    #         st.metric("Relation Similarity", result["relation_similarity"])

    #     with col4:
    #         st.metric(
    #     "Sematch Similarity",
    #     result["sematch_similarity"]
    # )
        st.success("Similarity computed successfully ✔")


# ------------------------------------------------------------
# MOST SIMILAR ENTITIES
# ------------------------------------------------------------
st.sidebar.header("Explore Similar Cities")

selected_entity = st.sidebar.text_input("Entity for search", value="Q472")

if st.sidebar.button("Find Similar Entities"):

    if selected_entity not in G:
        st.error("Entity not found in graph.")
    else:
        
        results = most_similar_sematch(G, selected_entity)

        st.subheader("🔎 Most Similar Entities")

        for node, score in results:
            label = G.nodes[node].get("label", node)
            st.write(f"**{label}** ({node}) → Score: {round(score, 4)}")


# ------------------------------------------------------------
# GRAPH INFO
# ------------------------------------------------------------
st.sidebar.header("Graph Stats")

if st.sidebar.button("Show Graph Stats"):

    st.write("### 📌 Knowledge Graph Overview")
    st.write(f"Nodes: {G.number_of_nodes()}")
    st.write(f"Edges: {G.number_of_edges()}")


# ------------------------------------------------------------
# SAMPLE HELP SECTION
# ------------------------------------------------------------
st.sidebar.header("Example QIDs")

st.sidebar.write("""
- Sofia → Q472  
- Plovdiv → Q3591  
- Bulgaria → Q219  
- Greece → Q41  
- Europe → Q46  
""")