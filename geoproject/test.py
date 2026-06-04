# from app import get_graph
# from utils import build_label_index
# from sematch import word_similarity

# G = get_graph()
# label_index = build_label_index(G)

# result=word_similarity(G,'Sofia, Bulgaria','Plovdiv, Bulgaria')


from geoproject.similarity import load_graph


G=load_graph()
print(G.number_of_nodes())