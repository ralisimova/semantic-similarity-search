import pandas as pd
from collections import defaultdict
from tqdm import tqdm

RAW_PATH = "data/raw/wikidata5m_transductive_train.txt"
ENTITY_PATH = "data/raw/wikidata5m_entity.txt"

OUTPUT_PATH = "data/processed/geo_subgraph.txt"

# ------------------------------------------------------------
# STEP 1: Load entity labels (QIDs → names)
# ------------------------------------------------------------
def load_entity_map(path):
    entity_map = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) >= 2:
                entity_map[parts[0]] = parts[1]
    return entity_map

# ------------------------------------------------------------
# STEP 2: Load triples
# ------------------------------------------------------------
def load_triples(path):
    triples = []
    with open(path, "r", encoding="utf-8") as f:
        for line in tqdm(f, desc="Loading triples"):
            parts = line.strip().split("\t")
            if len(parts) == 3:
                h, r, t = parts
                triples.append((h, r, t))
    return triples


# ------------------------------------------------------------
# STEP 3: Extract geographic KG
# ------------------------------------------------------------
# def build_geo_subgraph(triples):
#     allowed_relations = { "P17", "P36", "P1082",  "P131", }

#     geo_triples = []
#     city_population = defaultdict(int)

#     for h, r, t in tqdm(triples, desc="Filtering geo triples"):
#         if r not in allowed_relations:
#             continue

#         geo_triples.append((h, r, t))

#         # population tracking
#         if r == "P1082":
#             try:
#                 city_population[h] = int(t)
#             except:
#                 pass

#     return geo_triples, city_population
def build_geo_subgraph(triples):

    allowed_relations = {
        "P17",     # country
        "P36",     # capital
        "P131",    # located in admin territory
        "P1082"    # population
    }

    GEO_CLASSES = {
        "Q515",      # city
        "Q6256",     # country
        "Q486972",   # human settlement
        "Q82794"     # geographic region
    }

    print("Pass 1: collecting geographic entities...")

    geo_entities = set()

    # PASS 1:
    # Use P31 only for filtering
    for h, r, t in tqdm(triples):

        if r == "P31" and t in GEO_CLASSES:
            geo_entities.add(h)

    print("Geo entities:", len(geo_entities))

    print("Pass 2: filtering triples...")

    geo_triples = []
    city_population = defaultdict(int)

    # PASS 2:
    for h, r, t in tqdm(triples):

        if r not in allowed_relations:
            continue

        # only keep triples involving geo entities
        if h not in geo_entities:
            continue

        if r != "P1082" and t not in geo_entities:
            continue

        geo_triples.append((h, r, t))

        if r == "P1082":
            try:
                city_population[h] = int(t)
            except:
                pass

    print("Filtered triples:", len(geo_triples))

    return geo_triples, city_population, geo_entities

# ------------------------------------------------------------
# STEP 4: Identify countries and cities
# ------------------------------------------------------------
# def extract_entities(geo_triples):
#     countries = set()
#     capitals = set()
#     city_country = defaultdict(set)

#     for h, r, t in geo_triples:
#         # instance of country
#         if r == "P31" and "Q6256" in t:
#             countries.add(h)

#         # country relation
#         if r == "P17":
#             city_country[h].add(t)

#         # capital
#         if r == "P36":
#             capitals.add(t)

#     return countries, capitals, city_country
def extract_entities(geo_triples, geo_entities):

    countries = set()
    capitals = set()
    city_country = defaultdict(set)

    for h, r, t in geo_triples:

        if r == "P17":
            city_country[h].add(t)
            countries.add(t)

        if r == "P36":
            capitals.add(t)

    return countries, capitals, city_country

# ------------------------------------------------------------
# STEP 5: Select top 5 cities per country
# ------------------------------------------------------------
def select_top_cities(city_country, city_population, entity_map):
    country_cities = defaultdict(list)

    for city, countries in city_country.items():
        pop = city_population.get(city, 0)
        for c in countries:
            country_cities[c].append((city, pop))

    top_cities = defaultdict(list)

    for country, cities in country_cities.items():
        sorted_cities = sorted(cities, key=lambda x: x[1], reverse=True)
        top_cities[country] = sorted_cities[:5]

    return top_cities


# ------------------------------------------------------------
# STEP 6: Save cleaned geographic subgraph
# ------------------------------------------------------------
def save_subgraph(geo_triples, top_cities, entity_map):
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:

        # Save filtered triples
        for h, r, t in geo_triples:
            f.write(f"{h}\t{r}\t{t}\n")

        # Add top city structure explicitly
        for country, cities in top_cities.items():
            for city, pop in cities:
                f.write(f"{city}\tTOP_CITY_OF\t{country}\n")


# ------------------------------------------------------------
# MAIN PIPELINE
# ------------------------------------------------------------
def main():
    print("Loading entity map...")
    entity_map = load_entity_map(ENTITY_PATH)

    print("Loading triples...")
    triples = load_triples(RAW_PATH)

    print("Building geographic subgraph...")
    geo_triples, city_population, geo_entities = build_geo_subgraph(triples)

    print("Extracting entities...")
    countries, capitals, city_country = extract_entities(
    geo_triples,
    geo_entities
)

    print("Selecting top cities per country...")
    top_cities = select_top_cities(city_country, city_population, entity_map)

    print("Saving subgraph...")
    save_subgraph(geo_triples, top_cities, entity_map)

    print("DONE ✔")
    print(f"Geo subgraph saved to: {OUTPUT_PATH}")

    print("\nStats:")
    print("Countries:", len(countries))
    print("Capitals:", len(capitals))
    print("Cities with country links:", len(city_country))


if __name__ == "__main__":
    main()