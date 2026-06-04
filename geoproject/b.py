import pandas as pd
import networkx as nx
from tqdm import tqdm
import pickle

# =====================================================
# CONFIGURATION
# =====================================================

ENTITY_FILE = "data/raw/wikidata5m_entity.txt"
RELATION_FILE = "data/raw/wikidata5m_relation.txt"
TRIPLE_FILE = "data/raw/wikidata5m_transductive_train.txt"

MAX_CITIES = 5000  # safety limit

# =====================================================
# LOAD ENTITY LABELS
# =====================================================

print("Loading entities...")

entity_labels = {}

with open(ENTITY_FILE, "r", encoding="utf-8") as f:
    for line in tqdm(f):
        parts = line.strip().split("\t")

        if len(parts) >= 2:
            qid = parts[0]
            label = parts[1]
            entity_labels[qid] = label

print("Entities loaded:", len(entity_labels))

# =====================================================
# LOAD RELATION LABELS
# =====================================================

print("Loading relations...")

relation_labels = {}

with open(RELATION_FILE, "r", encoding="utf-8") as f:
    for line in tqdm(f):
        parts = line.strip().split("\t")

        if len(parts) >= 2:
            pid = parts[0]
            label = parts[1]
            relation_labels[pid] = label

print("Relations loaded:", len(relation_labels))

# =====================================================
# IMPORTANT WIKIDATA IDS
# =====================================================

COUNTRY_CLASSES = {
    "Q6256",      # country
    "Q3624078",   # sovereign state
} # country
CITY_CLASS = "Q515"      # city

INSTANCE_OF = "P31"
COUNTRY_REL = "P17"
CAPITAL_REL = "P36"

# =====================================================
# PASS 1:
# FIND COUNTRIES AND CITIES
# =====================================================

print("Pass 1: identifying countries and cities...")

countries = set()
cities = set()

with open(TRIPLE_FILE, "r", encoding="utf-8") as f:

    for line in tqdm(f):

        h, r, t = line.strip().split("\t")

        if r == INSTANCE_OF:

            if t in COUNTRY_CLASSES:
                countries.add(h)

            elif t == CITY_CLASS:
                cities.add(h)

print("Countries:", len(countries))
print("Cities:", len(cities))

# Optional cap
if len(cities) > MAX_CITIES:
    cities = set(list(cities)[:MAX_CITIES])

# =====================================================
# PASS 2:
# BUILD GEOGRAPHIC GRAPH
# =====================================================

print("Pass 2: building graph...")

G = nx.MultiDiGraph()

# Add countries

for qid in countries:

    G.add_node(
        qid,
        label=entity_labels.get(qid, qid),
        type="country"
    )

# Add cities

for qid in cities:

    G.add_node(
        qid,
        label=entity_labels.get(qid, qid),
        type="city"
    )

edge_count = 0

with open(TRIPLE_FILE, "r", encoding="utf-8") as f:

    for line in tqdm(f):

        h, r, t = line.strip().split("\t")

        # -------------------------------
        # instance of
        # -------------------------------

        if r == INSTANCE_OF:

            if h in countries and t in COUNTRY_CLASSES:

                G.add_edge(
                    h,
                    t,
                    relation="instance_of"
                )
                edge_count += 1

            elif h in cities and t == CITY_CLASS:

                G.add_edge(
                    h,
                    t,
                    relation="instance_of"
                )
                edge_count += 1

        # -------------------------------
        # city -> country
        # -------------------------------

        elif r == COUNTRY_REL:

            if h in cities and t in countries:

                G.add_edge(
                    h,
                    t,
                    relation="country"
                )
                edge_count += 1

        # -------------------------------
        # country -> capital
        # -------------------------------

        elif r == CAPITAL_REL:

            if h in countries and t in cities:

                G.add_edge(
                    h,
                    t,
                    relation="capital"
                )
                edge_count += 1

print("Nodes:", G.number_of_nodes())
print("Edges:", G.number_of_edges())

# =====================================================
# EXPORT NODE TABLE
# =====================================================

print("Saving node table...")

# nodes_df = pd.DataFrame(
#     [
#         {
#             "id": n,
#             "label": G.nodes[n]["label"],
#             "type": G.nodes[n]["type"]
#         }
#         for n in G.nodes()
#     ]
# )

# nodes_df.to_csv(
#     "wikidata_geo_nodes.csv",
#     index=False
# )

# =====================================================
# EXPORT EDGE TABLE
# =====================================================

print("Saving edge table...")

edge_rows = []

for u, v, data in G.edges(data=True):

    edge_rows.append(
        {
            "source": u,
            "target": v,
            "relation": data["relation"]
        }
    )

edges_df = pd.DataFrame(edge_rows)

edges_df.to_csv(
    "wikidata_geo_edges.csv",
    index=False
)

# =====================================================
# SAVE GRAPHML
# =====================================================

print("Saving GraphML...")

nx.write_graphml(
    G,
    "wikidata_geo.graphml"
)

# =====================================================
# SAVE GEXF
# =====================================================

print("Saving GEXF...")

nx.write_gexf(
    G,
    "wikidata_geo.gexf"
)

# =====================================================
# SAVE PICKLE
# =====================================================

print("Saving Pickle...")

with open("wikidata_geo.pkl", "wb") as f:
    pickle.dump(G, f)

# =====================================================
# SUMMARY
# =====================================================

print("\nDONE")
print("Nodes:", G.number_of_nodes())
print("Edges:", G.number_of_edges())

print("\nSaved files:")
print("wikidata_geo.graphml")
print("wikidata_geo.gexf")
print("wikidata_geo.pkl")
print("wikidata_geo_nodes.csv")
print("wikidata_geo_edges.csv")

print(entity_labels.get("Q515"))
print(entity_labels.get("Q6256"))
print(entity_labels.get("Q3624078"))



for qid, label in entity_labels.items():
    if label.lower() == "germany":
        print(qid, label)
       
       
for qid, label in entity_labels.items():
    if label.lower() == "city":
        print(qid, label)


for qid, label in entity_labels.items():
    if "city" == label.lower():
        print(qid)