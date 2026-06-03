# # # debug_labels.py
# import pickle

# with open("data/processed/geo_graph.gpickle", "rb") as f:
#     G = pickle.load(f)

# count = 0

# for node, data in G.nodes(data=True):
#     label = data.get("label", "")

#     if "plovdiv" in label.lower():
#         print(node, label)
#         count += 1

# print("Matches:", count)

# import pickle

# with open("data/processed/geo_graph.gpickle","rb") as f:
#     G = pickle.load(f)

# print(G.nodes["Q459"])

# search_subgraph.py
# SUBGRAPH = "data/processed/geo_subgraph.txt"

# found = False

# with open(SUBGRAPH,"r",encoding="utf-8") as f:
#     for line in f:
#         if "Q3591" in line:   # temporary guess not reliable
#             print(line)

from utils import wikidata_search

results = wikidata_search("Sofia")

for r in results:
    print(r)