import networkx as nx
import pandas as pd
from tqdm import tqdm
import pickle
ENTITY_FILE = "data/raw/wikidata5m_entity.txt"
RELATION_FILE = "data/raw/wikidata5m_relation.txt"
TRIPLE_FILE = "data/raw/wikidata5m_transductive_train.txt"

OUTPUT_PATH = "data/processed/geo_subgraph_v2.txt"



# =========================
# LOAD ENTITIES
# =========================
print("Loading entity labels...")

entity_labels = {}
label_to_qid = {}

with open(ENTITY_FILE, encoding="utf8") as f:
    for line in tqdm(f):

        parts = line.strip().split("\t")
        qid = parts[0]

        labels = parts[1:]

        # store primary label
        entity_labels[qid] = labels[0]

        # store ALL aliases
        for label in labels:
            label = label.strip().lower()
            if label:
                label_to_qid[label] = qid
                
# entity_labels = {}

# with open(ENTITY_FILE, encoding="utf8") as f:
#     for line in tqdm(f):
#         parts = line.strip().split("\t")
#         if len(parts) >= 2:
#             entity_labels[parts[0]] = parts[1]

# print("Entities:", len(entity_labels))

# label_to_qid = {}

# for qid, label in entity_labels.items():
#     label_to_qid[label.strip().lower()] = qid
    
# =========================
# WIKIDATA PROPERTIES
# =========================

# TODOadd share border
P_CAPITAL = "P36"
P_LANGUAGE = "P37"
P_CURRENCY = "P38"
P_CONTINENT = "P30"
UN_QID = "Q1065"  # United Nations
P_MEMBER_OF = "P463"

# =========================
# LOAD COUNTRY SEEDS
# =========================

print("Loading UN countries...")

countries = set()
missing = []
# with open("data/raw/un_countries.txt") as f:
#     # for line in f:
#     #     countries.add(line.strip())
    
#     for line in f:

#         country_name = line.strip()

#         qid = label_to_qid.get(
#             country_name.lower()
#         )

#         if qid:
#             countries.add(qid)
#         else:
#             missing.append(country_name)

# print("Countries:", len(countries), "Missing:", missing)

# =========================
# BUILD GRAPH
# =========================

with open(TRIPLE_FILE, encoding="utf8") as f:
    for line in f:
        h, r, t = line.strip().split("\t")

        if r == P_MEMBER_OF and t == UN_QID:
            countries.add(h)
            
for country in countries:

  
    label=entity_labels.get(country, country),
    if(label is None):
        print("Missing label for:", country)
    
G = nx.MultiDiGraph()

for country in countries:

    G.add_node(
        country,
        label=entity_labels.get(country, country),
        type="country"
    )

# country_nodes = [n for n, attrs in G.nodes(data=True) if attrs.get("type") == "country"]
# print(country_nodes)

# =========================
# EXTRACT RELATIONS
# =========================

capitals = set()
languages = set()
currencies = set()
continents = set()

print("Countries sample:")
print(list(countries)[:10])

with open(TRIPLE_FILE, encoding="utf8") as f:
    for i, line in enumerate(f):
        h, r, t = line.strip().split("\t")

        if i < 10:
            print("Triple head:", repr(h))
            
print("Extracting geographic relations...")

with open(TRIPLE_FILE, encoding="utf8") as f:

    for line in tqdm(f):

        h, r, t = line.strip().split("\t")

        if h not in countries:
            continue
        # print('here')
        # CAPITAL
        if r == P_CAPITAL:

            G.add_node(
                t,
                label=entity_labels.get(t, t),
                type="capital"
            )

            G.add_edge(
                h,
                t,
                relation="capital"
            )

            capitals.add(t)

        # LANGUAGE
        elif r == P_LANGUAGE:

            G.add_node(
                t,
                label=entity_labels.get(t, t),
                type="language"
            )

            G.add_edge(
                h,
                t,
                relation="official_language"
            )

            languages.add(t)

        # CURRENCY
        elif r == P_CURRENCY:

            G.add_node(
                t,
                label=entity_labels.get(t, t),
                type="currency"
            )

            G.add_edge(
                h,
                t,
                relation="currency"
            )

            currencies.add(t)

        # CONTINENT
        elif r == P_CONTINENT:

            G.add_node(
                t,
                label=entity_labels.get(t, t),
                type="continent"
            )

            G.add_edge(
                h,
                t,
                relation="continent"
            )

            continents.add(t)
            
            
            
print("Countries:", len(countries))
print("Capitals:", len(capitals))
print("Currencies:", len(currencies))
print("Continents:", len(continents))
print("Languages:", len(languages))
print ('Current countries',countries)

print("Final nodes:", G.number_of_nodes())
print("Final edges:", G.number_of_edges())

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    for u, v, d in G.edges(data=True):
        relation = d.get("relation", "")
        f.write(f"{u}\t{relation}\t{v}\n")
