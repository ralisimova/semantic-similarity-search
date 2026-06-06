import json
import pickle
import requests
import networkx as nx

from tqdm import tqdm

TRIPLE_FILE = "data/raw/wikidata5m_transductive_train.txt"

SUBGRAPH_OUTPUT = "data/processed/geo_subgraph_v2.txt"
LABELS_OUTPUT = "data/processed/labels.json"
STATS_OUTPUT = "data/processed/geo_graph_stats.json"
GRAPH_OUTPUT = "data/processed/geo_graph_v2.gpickle"

# ============================================================
# WIKIDATA PROPERTIES
# ============================================================

P_CAPITAL = "P36"
P_LANGUAGE = "P37"
P_CURRENCY = "P38"
P_CONTINENT = "P30"
P_MEMBER_OF = "P463"
P_BORDER = "P47"

UN_QID = "Q1065"

WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"

# ============================================================
# LABEL FETCHING
# ============================================================

def fetch_labels_sparql(qids):
    """
    Fetch English labels for Wikidata entities.
    """

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
        "User-Agent": "GeoGraphBuilder/1.0",
    }

    response = requests.get(
        WIKIDATA_SPARQL,
        params={"query": query},
        headers=headers,
        timeout=60,
    )

    response.raise_for_status()

    data = response.json()

    labels = {}

    for row in data.get("results", {}).get("bindings", []):
        qid = row["item"]["value"].split("/")[-1]
        label = row.get("itemLabel", {}).get("value", "")
        labels[qid] = label

    return labels


# ============================================================
# STEP 1: BUILD GEOGRAPHIC SUBGRAPH
# ============================================================

def build_geo_subgraph():
    countries = set()

    capitals = set()
    languages = set()
    currencies = set()
    continents = set()
    neighbors = set()

    print("Finding UN member countries...")

    with open(TRIPLE_FILE, encoding="utf8") as f:
        for line in f:
            h, r, t = line.strip().split("\t")

            if r == P_MEMBER_OF and t == UN_QID:
                countries.add(h)

    print(f"Countries found: {len(countries)}")

    G = nx.MultiDiGraph()

    for country in countries:
        G.add_node(country, type="country")

    print("Extracting relations...")

    with open(TRIPLE_FILE, encoding="utf8") as f:
        for line in tqdm(f):

            h, r, t = line.strip().split("\t")

            if h not in countries:
                continue

            # Capital
            if r == P_CAPITAL:
                G.add_node(t, type="capital")
                G.add_edge(h, t, relation="capital")
                capitals.add(t)

            # Official language
            elif r == P_LANGUAGE:
                G.add_node(t, type="language")
                G.add_edge(h, t, relation="official_language")
                languages.add(t)

            # Currency
            elif r == P_CURRENCY:
                G.add_node(t, type="currency")
                G.add_edge(h, t, relation="currency")
                currencies.add(t)

            # Continent
            elif r == P_CONTINENT:
                G.add_node(t, type="continent")
                G.add_edge(h, t, relation="continent")
                continents.add(t)

            # Border
            elif r == P_BORDER:

                if t not in countries:
                    continue

                G.add_edge(h, t, relation="shares_border_with")
                G.add_edge(t, h, relation="shares_border_with")

                neighbors.add((h, t))

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

    print("\nSubgraph Statistics")
    print(json.dumps(stats, indent=2))

    return G, stats


# ============================================================
# STEP 2: FETCH LABELS
# ============================================================

def fetch_all_labels(graph):

    all_nodes = list(graph.nodes())

    labels = {}

    batch_size = 30

    print("\nFetching labels from Wikidata...")

    for i in tqdm(range(0, len(all_nodes), batch_size)):

        batch = all_nodes[i:i + batch_size]

        try:
            labels.update(fetch_labels_sparql(batch))
        except Exception as e:
            print("Failed batch:", e)

    return labels


# ============================================================
# STEP 3: SAVE SUBGRAPH
# ============================================================

def save_subgraph_triples(graph, path):

    with open(path, "w", encoding="utf-8") as f:

        for u, v, d in graph.edges(data=True):

            relation = d.get("relation", "")

            f.write(f"{u}\t{relation}\t{v}\n")


# ============================================================
# STEP 4: CONVERT TO FINAL GRAPH
# ============================================================

def build_final_graph(multigraph, labels):

    G = nx.Graph()

    print("\nBuilding final graph...")

    for u, v, data in tqdm(multigraph.edges(data=True)):

        relation = data["relation"]

        if u not in G:
            G.add_node(
                u,
                label=labels.get(u, u)
            )

        if v not in G:
            G.add_node(
                v,
                label=labels.get(v, v)
            )

        G.add_edge(
            u,
            v,
            relation=relation
        )

    return G


# ============================================================
# STEP 5: COMPUTE NODE FEATURES
# ============================================================

def compute_node_features(G):

    degree_dict = dict(G.degree())

    for node in G.nodes():
        G.nodes[node]["degree"] = degree_dict[node]


# ============================================================
# STEP 6: SAVE DATA
# ============================================================

def save_outputs(
    final_graph,
    labels,
    stats,
):

    with open(LABELS_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(
            labels,
            f,
            ensure_ascii=False,
            indent=2
        )

    with open(STATS_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(
            stats,
            f,
            indent=2
        )

    with open(GRAPH_OUTPUT, "wb") as f:
        pickle.dump(final_graph, f)


# ============================================================
# MAIN
# ============================================================

def main():

    print("Building geographic knowledge graph")

    geo_multigraph, stats = build_geo_subgraph()

    print("\nSaving extracted triples...")
    save_subgraph_triples(
        geo_multigraph,
        SUBGRAPH_OUTPUT
    )

    labels = fetch_all_labels(
        geo_multigraph
    )

    graph = build_final_graph(
        geo_multigraph,
        labels
    )

    compute_node_features(graph)

    save_outputs(
        graph,
        labels,
        stats,
    )

    print("\nFinished.")

    print("\nFinal Graph Statistics")
    print("----------------------")
    print("Nodes :", graph.number_of_nodes())
    print("Edges :", graph.number_of_edges())

    print("\nSaved:")
    print("  ", SUBGRAPH_OUTPUT)
    print("  ", LABELS_OUTPUT)
    print("  ", STATS_OUTPUT)
    print("  ", GRAPH_OUTPUT)


if __name__ == "__main__":
    main()