import json
import networkx as nx
import pandas as pd
from tqdm import tqdm
import pickle

ENTITY_FILE = "data/raw/wikidata5m_entity.txt"
RELATION_FILE = "data/raw/wikidata5m_relation.txt"
TRIPLE_FILE = "data/raw/wikidata5m_transductive_train.txt"

OUTPUT_PATH = "data/processed/geo_subgraph_v2.txt"
STATS_OUTPUT_PATH = "data/processed/geo_graph_stats.json"



# =========================
# LOAD ENTITIES
# =========================
print("Loading entity labels...")

# TODO check the need for these
entity_labels = {}
label_to_qid = {}

def best_label(labels):

    labels = [x.strip() for x in labels if x.strip()]

    # prefer ASCII-ish English-looking labels
    labels = sorted(labels, key=len)

    return labels[0]

with open(ENTITY_FILE, encoding="utf8") as f:
    for line in tqdm(f):

        parts = line.strip().split("\t")
        qid = parts[0]

        labels = parts[1:]

        # store primary label
        entity_labels[qid] = best_label(labels)

        # store ALL aliases
        for label in labels:
            label = label.strip().lower()
            if label:
                label_to_qid[label] = qid
                
    
# =========================
# WIKIDATA PROPERTIES
# =========================

# TODO add share border
P_CAPITAL = "P36"
P_LANGUAGE = "P37"
P_CURRENCY = "P38"
P_CONTINENT = "P30"
UN_QID = "Q1065"  # United Nations
P_MEMBER_OF = "P463"
P_BORDER = "P47"

# =========================
# LOAD COUNTRY SEEDS
# =========================


countries = set()
neighbors = set()

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
            
            # Neighboring countries
        elif r == P_BORDER:

            if t not in countries or h not in countries:
                continue

            G.add_edge(
                h,
                t,
                relation="shares_border_with"
            )
            # We want both directions since the relationship is symmetric
            G.add_edge(
                t,
                h,
                relation="shares_border_with"
            )

            neighbors.add((h, t))
            
            
            
print("Countries:", len(countries))
print("Capitals:", len(capitals))
print("Currencies:", len(currencies))
print("Continents:", len(continents))
print("Languages:", len(languages))

print("Final nodes:", G.number_of_nodes())
print("Final edges:", G.number_of_edges())

stats = {
    "countries": len(countries),
    "capitals": len(capitals),
    "currencies": len(currencies),
    "continents": len(continents),
    "languages": len(languages),
    "final_nodes": G.number_of_nodes(),
    "final_edges": G.number_of_edges(),
}





import requests
from tqdm import tqdm

WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"


def fetch_labels_sparql(qids):
    values = " ".join(f"wd:{qid}" for qid in qids)

    query = f"""
    SELECT ?item ?itemLabel
    WHERE {{
      VALUES ?item {{ {values} }}

      SERVICE wikibase:label {{
        bd:serviceParam wikibase:language "en".
      }}
    }}
    """


    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "GeoGraphBuilder/1.0"
    }

    r = requests.get(
        WIKIDATA_SPARQL,
        params={"query": query},
        headers=headers,
        timeout=60,
    )

    r.raise_for_status()

    data = r.json()

    labels = {}

    for row in data["results"]["bindings"]:
        qid = row["item"]["value"].split("/")[-1]
        label = row["itemLabel"]["value"]

        labels[qid] = label

    return labels
all_nodes = list(G.nodes())

print("Fetching canonical Wikidata labels...")

canonical_labels = {}

BATCH_SIZE = 50

for i in tqdm(range(0, len(all_nodes), BATCH_SIZE)):
    batch = all_nodes[i:i+BATCH_SIZE]

    try:
        canonical_labels.update(
            fetch_labels_sparql(batch)
        )
    except Exception as e:
        print("Failed batch:", e)
        
for node in G.nodes():

    if node in canonical_labels:
        print('Updating label for node:', node, '->', canonical_labels[node])
        G.nodes[node]["label"] = canonical_labels[node] 
        
        
with open(
    "data/processed/canonical_labels.json",
    "w",
    encoding="utf8"
) as f:
    json.dump(
        canonical_labels,
        f,
        ensure_ascii=False,
        indent=2
    )

with open(STATS_OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    for u, v, d in G.edges(data=True):
        relation = d.get("relation", "")
        f.write(f"{u}\t{relation}\t{v}\n")
