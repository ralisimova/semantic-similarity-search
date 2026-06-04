from collections import defaultdict, Counter
import csv

##############################################################################
# CONFIG
##############################################################################

TRAIN_FILE = "data/raw/wikidata5m_transductive_train.txt"
VALID_FILE = "data/raw/wikidata5m_transductive_valid.txt"
TEST_FILE  = "data/raw/wikidata5m_transductive_test.txt"

OUTPUT_FILE = "data/processed/wikidata5m_geographic_subgraph.tsv"

P17 = "P17"   # country
P36 = "P36"   # capital

MIN_COUNTRY_FREQ = 20
TOP_K_CITIES = 5

##############################################################################
# LOAD TRIPLES
##############################################################################

def load_triples(files):

    triples = []

    for file in files:
        with open(file, "r", encoding="utf-8") as f:

            for line in f:

                parts = line.strip().split("\t")

                if len(parts) != 3:
                    continue

                h, r, t = parts
                triples.append((h, r, t))

    return triples


print("Loading triples...")

triples = load_triples([
    TRAIN_FILE,
    VALID_FILE,
    TEST_FILE
])

print(f"Loaded {len(triples):,} triples")

##############################################################################
# BUILD INDICES
##############################################################################

print("Building indices...")

country_frequency = Counter()

country_to_cities = defaultdict(set)
country_to_capital = {}

entity_degree = Counter()

for h, r, t in triples:

    entity_degree[h] += 1
    entity_degree[t] += 1

    if r == P17:

        country_frequency[t] += 1
        country_to_cities[t].add(h)

    elif r == P36:

        country_to_capital[h] = t

##############################################################################
# STEP 1: FIND CANDIDATE COUNTRIES
##############################################################################

print("Finding candidate countries...")

candidate_countries = {
    country
    for country, freq in country_frequency.items()
    if freq >= MIN_COUNTRY_FREQ
}

print("Candidate countries:", len(candidate_countries))

##############################################################################
# STEP 2: REQUIRE CAPITAL
##############################################################################

countries = {
    c
    for c in candidate_countries
    if c in country_to_capital
}

print("Countries with capitals:", len(countries))

##############################################################################
# STEP 3: SELECT TOP-K CITIES PER COUNTRY
##############################################################################

selected_cities = set()
selected_capitals = set()

for country in countries:

    capital = country_to_capital[country]

    if capital == country:
        continue

    selected_capitals.add(capital)

    cities = list(country_to_cities[country])

    ranked = sorted(
        cities,
        key=lambda x: entity_degree[x],
        reverse=True
    )

    top_cities = ranked[:TOP_K_CITIES]

    selected_cities.update(top_cities)

##############################################################################
# STEP 4: FINAL NODE SET
##############################################################################

nodes = (
    countries
    | selected_capitals
    | selected_cities
)

print(f"Final node count: {len(nodes):,}")

##############################################################################
# STEP 5: BUILD INDUCED SUBGRAPH
##############################################################################

print("Building induced graph...")

subgraph = []

for h, r, t in triples:

    if h == t:
        continue

    if h not in nodes:
        continue

    if t not in nodes:
        continue

    if r not in {P17, P36}:
        continue

    subgraph.append((h, r, t))

print(f"Final edge count: {len(subgraph):,}")

##############################################################################
# STEP 6: CONNECTIVITY CHECK
##############################################################################

adj = defaultdict(set)

for h, r, t in subgraph:
    adj[h].add(t)
    adj[t].add(h)

visited = set()

if nodes:

    start = next(iter(nodes))

    stack = [start]

    while stack:

        node = stack.pop()

        if node in visited:
            continue

        visited.add(node)

        stack.extend(adj[node] - visited)

print(f"Connected nodes: {len(visited):,}")
print(f"Disconnected nodes: {len(nodes)-len(visited):,}")

##############################################################################
# OPTIONAL:
# KEEP ONLY LARGEST CONNECTED COMPONENT
##############################################################################

if len(visited) < len(nodes):

    print("Keeping largest connected component...")

    nodes = visited

    subgraph = [
        (h, r, t)
        for h, r, t in subgraph
        if h in nodes and t in nodes
    ]

##############################################################################
# SAVE
##############################################################################

print("Saving subgraph...")

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:

    writer = csv.writer(
        f,
        delimiter="\t"
    )

    for triple in subgraph:
        writer.writerow(triple)

print()
print("DONE")
print("Saved:", OUTPUT_FILE)
print("Nodes:", len(nodes))
print("Edges:", len(subgraph))