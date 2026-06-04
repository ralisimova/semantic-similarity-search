import nltk
nltk.download('wordnet')
nltk.download('wordnet_ic')

nltk.download('omw-1.4')

from sematch.semantic.similarity import WordNetSimilarity
import networkx as nx

wns = WordNetSimilarity()


def sematch_label_similarity(G, a, b):
    """
    Semantic similarity using Sematch + labels
    """

    # label_a = G.nodes[a].get("label", "")
    # label_b = G.nodes[b].get("label", "")

    # if not label_a or not label_b:
    #     return 0.0

    try:
        score = wns.word_similarity(
            a.lower(),
            b.lower(),
            "wpath"
        )

        if score is None:
            return 0.0

        return float(score)

    except:
        return 0.0

from sematch.semantic.similarity import EntitySimilarity
from mapping import qid_to_dbpedia

entity_sim = EntitySimilarity()


# def sematch_similarity(a_qid, b_qid):

#     a_uri = qid_to_dbpedia(a_qid)
#     b_uri = qid_to_dbpedia(b_qid)

#     if not a_uri or not b_uri:
#         return 0.0

#     try:
#         score = entity_sim.similarity(a_uri, b_uri)

#         if score is None:
#             return 0.0

#         return round(float(score), 4)

#     except:
#         return 0.0


from sematch.semantic.similarity import EntitySimilarity
from mapping import qid_to_dbpedia

entity_sim = EntitySimilarity()


def sematch_similarity(a_qid, b_qid):

    a_uri = qid_to_dbpedia(a_qid)
    b_uri = qid_to_dbpedia(b_qid)

    # print("A:", a_uri)
    # print("B:", b_uri)

    if not a_uri or not b_uri:
        return 0.0

    try:
        score = entity_sim.relatedness(
            a_uri,
            b_uri,  
        )

        # print("Raw score:", score)

        if score is None:
            return 0.0

        return float(score)

    except Exception as e:
        print("Sematch error:", e)
        return 0.0
      
      
# def sematch_similarity(G, a, b):

#     a_uri = G.nodes[a].get("dbpedia")
#     b_uri = G.nodes[b].get("dbpedia")

#     if not a_uri or not b_uri:
#         return 0.0

#     try:
#         score = entity_sim.similarity(
#             a_uri,
#             b_uri
#         )

#         return float(score or 0)

#     except:
#         return 0.0
      
if __name__ == "__main__":
    print(sematch_similarity("Q472", "Q219"))
    print(
    entity_sim.relatedness(
        'http://dbpedia.org/resource/Sofia',
        'http://dbpedia.org/resource/Plovdiv'
    )
)