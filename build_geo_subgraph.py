import json
import requests
import networkx as nx
from tqdm import tqdm

TRIPLE_FILE = "data/raw/wikidata5m_transductive_train.txt"

OUTPUT_PATH = "data/processed/geo_subgraph_v2.txt"
STATS_OUTPUT_PATH = "data/processed/geo_graph_stats.json"
LABELS_OUTPUT_PATH = "data/processed/labels.json"

# =========================
# WIKIDATA PROPERTIES
# =========================
P_CAPITAL = "P36"
P_LANGUAGE = "P37"
P_CURRENCY = "P38"
P_CONTINENT = "P30"
UN_QID = "Q1065" 
P_MEMBER_OF = "P463"
P_BORDER = "P47"

countries = set()
neighbors = set()
capitals = set()
languages = set()
currencies = set()
continents = set()

# =========================
# Add Countries
# =========================
with open(TRIPLE_FILE, encoding="utf8") as f:
    for line in f:
        h, r, t = line.strip().split("\t")

        if r == P_MEMBER_OF and t == UN_QID:
            countries.add(h)
            
    
G = nx.MultiDiGraph()

for country in countries:

    G.add_node(
        country,
        type="country"
    )


# =========================
# EXTRACT RELATIONS
# =========================
with open(TRIPLE_FILE, encoding="utf8") as f:
    for line in tqdm(f):
        h, r, t = line.strip().split("\t")
        if h not in countries:
            continue

        # CAPITAL
        if r == P_CAPITAL:
            G.add_node(t, type="capital")
            G.add_edge(h, t, relation="capital")
            capitals.add(t)

        # LANGUAGE
        elif r == P_LANGUAGE:
            G.add_node(t, type="language")
            G.add_edge(h, t, relation="official_language")
            languages.add(t)

        # CURRENCY
        elif r == P_CURRENCY:
            G.add_node(t, type="currency")
            G.add_edge(h, t, relation="currency")
            currencies.add(t)

        # CONTINENT
        elif r == P_CONTINENT:
            G.add_node(t, type="continent")
            G.add_edge(h, t, relation="continent")
            continents.add(t)

        # Neighboring countries (symmetric)
        elif r == P_BORDER:
            if t not in countries or h not in countries:
                continue
            G.add_edge(h, t, relation="shares_border_with")
            G.add_edge(t, h, relation="shares_border_with")
            neighbors.add((h, t))


print("Countries:", len(countries))
print("Capitals:", len(capitals))
print("Currencies:", len(currencies))
print("Continents:", len(continents))
print("Languages:", len(languages))
print("Neighbors:", len(neighbors))

print("Final nodes:", G.number_of_nodes())
print("Final edges:", G.number_of_edges())

stats = {
    "countries": len(countries),
    "capitals": len(capitals),
    "currencies": len(currencies),
    "continents": len(continents),
    "languages": len(languages),
    "neighbors": len(neighbors),
    "final_nodes": G.number_of_nodes(),
    "final_edges": G.number_of_edges(),
}


WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"


def fetch_labels_sparql(qids):
    """Fetch English labels for a list of QIDs using Wikidata SPARQL service."""
    values = " ".join(f"wd:{qid}" for qid in qids)
    query = f"""
    SELECT ?item ?itemLabel
    WHERE {{
      VALUES ?item {{ {values} }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """

    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "GeoGraphBuilder/1.0",
    }

    r = requests.get(WIKIDATA_SPARQL, params={"query": query}, headers=headers, timeout=60)
    r.raise_for_status()
    data = r.json()

    labels = {}
    for row in data.get("results", {}).get("bindings", []):
        qid = row["item"]["value"].split("/")[-1]
        label = row.get("itemLabel", {}).get("value", "")
        labels[qid] = label

    return labels


all_nodes = list(G.nodes())
labels = {}
BATCH_SIZE = 30

for i in tqdm(range(0, len(all_nodes), BATCH_SIZE)):
    batch = all_nodes[i : i + BATCH_SIZE]
    try:
        labels.update(fetch_labels_sparql(batch))
    except Exception as e:
        print("Failed batch:", e)


with open(LABELS_OUTPUT_PATH, "w", encoding="utf8") as f:
    json.dump(labels, f, ensure_ascii=False, indent=2)

with open(STATS_OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2)

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    for u, v, d in G.edges(data=True):
        relation = d.get("relation", "")
        f.write(f"{u}\t{relation}\t{v}\n")
