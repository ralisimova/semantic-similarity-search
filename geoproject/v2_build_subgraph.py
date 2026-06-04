# import random
# from collections import defaultdict
# from tqdm import tqdm

# RAW_PATH = "data/raw/wikidata5m_transductive_train.txt"
# OUTPUT_PATH = "data/processed/geo_subgraph.txt"


# # ------------------------------------------------------------
# # STEP 1: Load triples
# # ------------------------------------------------------------
# def load_triples(path):
#     triples = []
#     with open(path, "r", encoding="utf-8") as f:
#         for line in tqdm(f, desc="Loading triples"):
#             parts = line.strip().split("\t")
#             if len(parts) == 3:
#                 h, r, t = parts
#                 triples.append((h, r, t))
#     return triples


# # ------------------------------------------------------------
# # STEP 2: Extract GEO seed entities (countries + cities)
# # ------------------------------------------------------------
# def extract_geo_entities(triples):

#     countries = set()
#     cities = set()

#     for h, r, t in tqdm(triples, desc="Extracting geo entities"):

#         # instance-of country
#         if r == "P31" and t == "Q6256":
#             countries.add(h)

#         # instance-of city/settlement (very important)
#         if r == "P31" and t in {"Q515", "Q486972"}:
#             cities.add(h)

#     return countries, cities


# # ------------------------------------------------------------
# # STEP 3: Build a compact geographic subgraph (~1000 nodes)
# # ------------------------------------------------------------
# def build_geo_subgraph(triples, countries, cities):

#     allowed_nodes = set()

#     # --- LIMIT SIZE: pick top cities ---
#     cities = list(cities)
#     random.shuffle(cities)
#     cities = cities[:1000]

#     allowed_nodes.update(cities)

#     # --- keep countries ---
#     allowed_nodes.update(countries)

#     geo_triples = []

#     allowed_relations = {
#         "P17",   # country
#         "P131",  # located in admin region
#         "P36",   # capital
#         "P1082"  # population
#     }

#     for h, r, t in tqdm(triples, desc="Filtering geo triples"):

#         if r not in allowed_relations:
#             continue

#         # keep only edges inside our small subgraph
#         if h in allowed_nodes and t in allowed_nodes:
#             geo_triples.append((h, r, t))

#     return geo_triples, allowed_nodes


# # ------------------------------------------------------------
# # STEP 4: Save subgraph
# # ------------------------------------------------------------
# def save_subgraph(geo_triples, allowed_nodes):

#     with open(OUTPUT_PATH, "w", encoding="utf-8") as f:

#         # save edges
#         for h, r, t in geo_triples:
#             f.write(f"{h}\t{r}\t{t}\n")

#         # optional: mark nodes explicitly
#         for node in allowed_nodes:
#             f.write(f"{node}\tIN_SUBGRAPH\t1\n")


# # ------------------------------------------------------------
# # MAIN PIPELINE
# # ------------------------------------------------------------
# def main():

#     print("Loading triples...")
#     triples = load_triples(RAW_PATH)

#     print("Extracting geographic entities...")
#     countries, cities = extract_geo_entities(triples)

#     print(f"Found countries: {len(countries)}")
#     print(f"Found cities: {len(cities)}")

#     print("Building compact subgraph (~1000 nodes)...")
#     geo_triples, allowed_nodes = build_geo_subgraph(triples, countries, cities)

#     print(f"Final nodes in subgraph: {len(allowed_nodes)}")
#     print(f"Final edges in subgraph: {len(geo_triples)}")

#     print("Saving subgraph...")
#     save_subgraph(geo_triples, allowed_nodes)

#     print("DONE ✔")
#     print(f"Saved to: {OUTPUT_PATH}")


# if __name__ == "__main__":
#     main()

from collections import Counter, defaultdict
from tqdm import tqdm

RAW_PATH = "data/raw/wikidata5m_transductive_train.txt"
OUTPUT_PATH = "data/processed/geo_subgraph.txt"


def load_triples(path):
    triples = []

    with open(path, "r", encoding="utf-8") as f:
        for line in tqdm(f, desc="Loading triples"):
            parts = line.strip().split("\t")

            if len(parts) == 3:
                triples.append(tuple(parts))

    return triples


# def extract_geo_data(triples):

#     countries = set()
#     capitals = set()
#     cities = set() 

#     city_country = defaultdict(set)
#     city_population = {}
#     count = 0

#     for h, r, t in triples:
#         if r == "P2046":
#             print(h, r, t)
#             count += 1

#         if count == 20:
#             break
        
#     for h, r, t in tqdm(triples, desc="Extracting geo data"):

#         # country
#         if r == "P17":
#             countries.add(h)


#         if r == "P31" and t in {"Q515", "Q486972"}:
#             cities.add(h)
#         # city / settlement
#         if r == "P17" and h in cities:
#             city_country[h].add(t)

#         # capital
#         if r == "P36":
#             capitals.add(t)

#         # population
#         if r == "P1082":
#             try:
#                 city_population[h] = int(t)
#             except:
#                 pass
#     print("Countries:", len(countries))
#     print("Capitals:", len(capitals))
#     print("Cities:", len(cities))   
    
#     return countries, capitals, city_country, city_population

def extract_geo_data(triples):
    """
    Extract:
        - countries
        - capitals
        - cities
        - city -> country
        - population
        - area

    Returns dictionaries suitable for selecting
    top-k cities per country.
    """
    CITY_TYPES = {"Q515", "Q486972"}
    countries = set()
    capitals = set()
    cities = set()

    city_country = defaultdict(set)

    city_population = {}
    city_area = {}

    # --------------------------------------------------
    # PASS 1: identify entities
    # --------------------------------------------------
    counter = Counter()

    for _, r, _ in triples:
        counter[r] += 1

    for prop in ["P17", "P31", "P36", "P1082", "P2046"]:
        print(prop, counter[prop])
    for h, r, t in tqdm(triples, desc="Pass 1"):

        # country relation
        if r == "P31" and t == "Q6256":
            countries.add(t)

        # city / settlement
        elif r == "P31" and t in CITY_TYPES:
            cities.add(h)

        # capital of country
        elif r == "P36":
            capitals.add(t)
            countries.add(h)

        # population
        elif r == "P1082":
            try:
                city_population[h] = float(t)
            except Exception:
                pass

        # area
        elif r == "P2046":
            try:
                city_area[h] = float(t)
            except Exception:
                pass

    print(f"Countries found: {len(countries)}")
    print(f"Cities found: {len(cities)}")
    print(f"Capitals found: {len(capitals)}")
    print(f"Population data points: {len(city_population)}")
    print(f"Area data points: {len(city_area)}")
    
    # --------------------------------------------------
    # PASS 2: city -> country links
    # --------------------------------------------------

    for h, r, t in tqdm(triples, desc="Pass 2"):
        if r == "P17" and h in cities:
            city_country[h].add(t)
    print(f"Cities with country links: {len(city_country)}")
    return {
        "countries": countries,
        "capitals": capitals,
        "cities": cities,
        "city_country": city_country,
        "population": city_population,
        "area": city_area,
    }
    
def select_top_cities(city_country, city_population):

    country_cities = defaultdict(list)

    for city, countries in city_country.items():

        pop = city_population.get(city, 0)

        for country in countries:
            country_cities[country].append((city, pop))

    top_cities = defaultdict(list)

    for country, cities in country_cities.items():

        cities = sorted(
            cities,
            key=lambda x: x[1],
            reverse=True
        )

        top_cities[country] = cities[:5]

    return top_cities

def build_allowed_nodes(
    countries,
    capitals,
    top_cities
):

    allowed_nodes = set()

    allowed_nodes.update(countries)
    allowed_nodes.update(capitals)

    for country, cities in top_cities.items():

        allowed_nodes.add(country)

        for city, pop in cities:
            allowed_nodes.add(city)

    return allowed_nodes

# def build_geo_subgraph(
#     triples,
#     allowed_nodes
# ):

#     allowed_relations = {
#         "P17",
#         "P36",
#         "P131"
#     }

#     geo_triples = []

#     for h, r, t in tqdm(
#         triples,
#         desc="Building subgraph"
#     ):

#         if r not in allowed_relations:
#             continue

#         if h in allowed_nodes and t in allowed_nodes:
#             geo_triples.append((h, r, t))

#     return geo_triples

from collections import defaultdict, Counter
from tqdm import tqdm

COUNTRY_QID = "Q6256"

CITY_TYPES = {"Q515", "Q486972"}


# def build_geo_subgraph(triples, top_k=5):
#     """
#     Builds:
#     - Countries
#     - Capitals
#     - Cities
#     - Top-K cities per country (by graph popularity)
#     """
#     country_candidates = Counter()

#     for h, r, t in triples:
#         if r == "P17":
#             country_candidates[t] += 1

#     print(country_candidates.most_common(20))
#     # ----------------------------
#     # STEP 1: BASIC STRUCTURES
#     # ----------------------------
#     countries = set()
#     cities = set()
#     capitals = set()

#     city_country = defaultdict(set)

#     # graph popularity score (degree proxy)
#     city_score = Counter()

#     country_to_cities = defaultdict(set)

#     # ----------------------------
#     # PASS 1: IDENTIFY ENTITIES + SCORE POPULARITY
#     # ----------------------------
#     for h, r, t in tqdm(triples, desc="Pass 1"):

#         # score ALL nodes by occurrence
#         city_score[h] += 1
#         city_score[t] += 1

#         # identify countries
#         if r == "P17":
#             countries.add(h)

#         # identify cities
#         elif r == "P31" and t in CITY_TYPES:
#             cities.add(h)

#         # # capitals
#         # elif r == "P36":
#         #     capitals.add(t)

#     # ----------------------------
#     # PASS 2: COUNTRY-CITY LINKS
#     # ----------------------------
#     for h, r, t in tqdm(triples, desc="Pass 2"):
#         if r == "P36":
#             if t in countries:
#              capitals.add(t)
#         if r == "P17" and h in cities:
#             city_country[h].add(t)

#     # reverse index: country -> cities
#     for city, cs in city_country.items():
#         for c in cs:
#             country_to_cities[c].add(city)

#     # ----------------------------
#     # STEP 3: SELECT TOP-K CITIES PER COUNTRY
#     # ----------------------------
#     top_cities = {}

#     for country, city_set in country_to_cities.items():

#         ranked = sorted(
#             city_set,
#             key=lambda c: city_score[c],
#             reverse=True
#         )

#         top_cities[country] = ranked[:top_k]

#     # ----------------------------
#     # STEP 4: BUILD FINAL GRAPH
#     # ----------------------------
#     nodes = set()
#     edges = []

#     # add countries + capitals
#     nodes.update(countries)
#     nodes.update(capitals)

#     # country -> capital edges
#     for h, r, t in triples:
#         if r == "P36" and h in countries:
#             edges.append((h, "has_capital", t))
#             nodes.add(h)
#             nodes.add(t)

#     # country -> city edges (top-k only)
#     for country, cities_list in top_cities.items():
#         nodes.add(country)

#         for city in cities_list:
#             nodes.add(city)
#             edges.append((country, "has_city", city))

#     print("\nFINAL STATS")
#     print("Nodes:", len(nodes))
#     print("Edges:", len(edges))
#     print("Countries:", len(countries))
#     print("Cities:", len(cities))
#     print("Capitals:", len(capitals))

#     return nodes, edges, top_cities, city_score
from collections import defaultdict, Counter
from tqdm import tqdm

CITY_TYPES = {"Q515", "Q486972"}

def build_geo_subgraph(triples, top_k=5, max_cities=2000):
    """
    Hard-bounded subgraph:
    - ~200 countries
    - ~200 capitals
    - ~1000–2000 cities
    TOTAL: <5000 nodes guaranteed
    """

    # -----------------------
    # PASS 1: STRUCTURE ONLY
    # -----------------------
    city_score = Counter()
    city_country = defaultdict(set)

    countries = set()
    cities = set()
    capitals = set()
    country_candidates = Counter()

    for h, r, t in triples:
        if r == "P17":
            country_candidates[t] += 1

# take TOP-K most frequent
    countries = set(
    [c for c, _ in country_candidates.most_common(250)]
)
    for h, r, t in tqdm(triples, desc="Pass 1"):

        # ONLY scoring (no node explosion)
        city_score[h] += 1
        city_score[t] += 1

        # countries = targets of P17 (IMPORTANT FIX)
        if r == "P17":
            city_country[h].add(t)

        # cities
        elif r == "P31" and t in CITY_TYPES:
            cities.add(h)

        # capitals
        elif r == "P36":
            capitals.add(t)

    # extract countries from observed structure
    # countries = set()
    # for _, cs in city_country.items():
    #     countries.update(cs)

    # countries = list(countries)#[:300]   # HARD LIMIT

    # -----------------------
    # PASS 2: ASSIGN CITIES
    # -----------------------
    country_to_cities = defaultdict(set)

    for city, cs in city_country.items():
        if city not in cities:
            continue
        for c in cs:
            country_to_cities[c].add(city)

    # -----------------------
    # SELECT TOP-K CITIES
    # -----------------------
    final_cities = set()
    final_capitals = set()

    for c in countries:
        c_cities = list(country_to_cities.get(c, []))

        ranked = sorted(
            c_cities,
            key=lambda x: city_score[x],
            reverse=True
        )

        top = ranked[:top_k]
        final_cities.update(top)

    # restrict size HARD
    final_cities = list(final_cities)[:max_cities]

    # capitals only for selected countries
    for h, r, t in triples:
        if r == "P36" and t in countries:
            final_capitals.add(t)

    # -----------------------
    # BUILD FINAL GRAPH
    # -----------------------
    nodes = set()
    edges = []

    nodes.update(countries)
    nodes.update(final_cities)
    nodes.update(final_capitals)

    # edges ONLY if both endpoints selected
    selected = nodes

    for h, r, t in triples:
        if h in selected and t in selected:

            if r == "P17":
                edges.append((h, "country", t))

            elif r == "P36":
                edges.append((h, "capital", t))

    print("\nFINAL STATS")
    print("Nodes:", len(nodes))
    print("Edges:", len(edges))
    print("Countries:", len(countries))
    print("Cities:", len(final_cities))
    print("Capitals:", len(final_capitals))

    return nodes, edges

def save_triples_tsv(edges):
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for h, r, t in edges:
            f.write(f"{h}\t{r}\t{t}\n")
            
def save_subgraph(geo_triples):

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        for h, r, t in geo_triples:
            f.write(f"{h}\t{r}\t{t}\n")
            
            
            
            
print("Loading triples...")
triples = load_triples(RAW_PATH)         
nodes,edges=build_geo_subgraph(triples, top_k=5)
save_triples_tsv(edges)
# result = extract_geo_data(triples)
# print("Extracting geo data...",result)
# top_cities = select_top_cities(
#     city_country,
#     city_population
# )

# allowed_nodes = build_allowed_nodes(
#     countries,
#     capitals,
#     top_cities
# )

# geo_triples = build_geo_subgraph(
#     triples,
#     allowed_nodes
# )

# save_subgraph(geo_triples)

# print("Nodes selected:", len(allowed_nodes))
# print("Triples saved:", len(geo_triples))