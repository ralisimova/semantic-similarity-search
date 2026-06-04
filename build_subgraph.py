import networkx as nx
import pandas as pd
from tqdm import tqdm
import pickle

# =========================
# FILES
# =========================
ENTITY_FILE = "data/raw/wikidata5m_entity.txt"
RELATION_FILE = "data/raw/wikidata5m_relation.txt"
TRIPLE_FILE = "data/raw/wikidata5m_transductive_train.txt"


# GRAPH_OUTPUT_PATH = "data/processed/movies_graph.gpickle"

OUTPUT_PATH = "data/processed/movies_subgraph.txt"

# =========================
# WIKIDATA CONSTANTS
# =========================
INSTANCE_OF = "P31"

P_CAST = "P161"
P_DIRECTOR = "P57"
P_GENRE = "P136"
P_COUNTRY = "P495"

MOVIE_CLASS = "Q11424"

# =========================
# LOAD ENTITIES
# =========================
print("Loading entity labels...")

entity_labels = {}

with open(ENTITY_FILE, encoding="utf8") as f:
    for line in tqdm(f):
        parts = line.strip().split("\t")
        if len(parts) >= 2:
            entity_labels[parts[0]] = parts[1]

print("Entities:", len(entity_labels))

# =========================
# STEP 1: FIND MOVIES
# =========================
print("Finding movies...")

movies = set()

with open(TRIPLE_FILE, encoding="utf8") as f:
    for line in tqdm(f):
        h, r, t = line.strip().split("\t")

        if r == INSTANCE_OF and t == MOVIE_CLASS:
            movies.add(h)

print("Movies found:", len(movies))

# LIMIT FOR GRAPH SIZE (IMPORTANT)
MAX_MOVIES = 1500
movies = set(list(movies)[:MAX_MOVIES])

# =========================
# STEP 2: BUILD GRAPH
# =========================
print("Building graph...")

G = nx.MultiDiGraph()

# Add movies
for m in movies:
    G.add_node(
        m,
        label=entity_labels.get(m, m),
        type="movie"
    )

# =========================
# STEP 3: EXTRACT RELATIONS
# =========================
print("Extracting relations...")

actors = set()
directors = set()
genres = set()
countries = set()

with open(TRIPLE_FILE, encoding="utf8") as f:
    for line in tqdm(f):
        h, r, t = line.strip().split("\t")

        if h not in movies:
            continue

        # CAST
        if r == P_CAST:
            G.add_node(t, label=entity_labels.get(t, t), type="actor")
            G.add_edge(h, t, relation="cast")
            actors.add(t)

        # DIRECTOR
        elif r == P_DIRECTOR:
            G.add_node(t, label=entity_labels.get(t, t), type="director")
            G.add_edge(h, t, relation="director")
            directors.add(t)

        # GENRE
        elif r == P_GENRE:
            G.add_node(t, label=entity_labels.get(t, t), type="genre")
            G.add_edge(h, t, relation="genre")
            genres.add(t)

        # COUNTRY
        elif r == P_COUNTRY:
            G.add_node(t, label=entity_labels.get(t, t), type="country")
            G.add_edge(h, t, relation="country")
            countries.add(t)

print("Movies:", len(movies))
print("Actors:", len(actors))
print("Directors:", len(directors))
print("Genres:", len(genres))
print("Countries:", len(countries))

print("Final nodes:", G.number_of_nodes())
print("Final edges:", G.number_of_edges())

# =========================
# STEP 4: EXPORT NODE TABLE
# =========================
# nodes_df = pd.DataFrame([
#     {
#         "id": n,
#         "label": G.nodes[n].get("label", n),
#         "type": G.nodes[n].get("type", "unknown")
#     }
#     for n in G.nodes()
# ])

# nodes_df.to_csv("movie_nodes.csv", index=False)

# # =========================
# # STEP 5: EXPORT EDGE TABLE
# # =========================
# edges_df = pd.DataFrame([
#     {
#         "source": u,
#         "target": v,
#         "relation": d["relation"]
#     }
#     for u, v, d in G.edges(data=True)
# ])

# edges_df.to_csv("movie_edges.csv", index=False)

# =========================
# STEP 5.1: SAVE FILTERED TRIPLES
# =========================
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    for u, v, d in G.edges(data=True):
        relation = d.get("relation", "")
        f.write(f"{u}\t{relation}\t{v}\n")

# # =========================
# # STEP 6: SAVE GRAPH
# # =========================
# nx.write_graphml(G, "movie_graph.graphml")
# nx.write_gexf(G, "movie_graph.gexf")

# with open("movie_graph.pkl", "wb") as f:
#     pickle.dump(G, f)

# print("DONE ✅")