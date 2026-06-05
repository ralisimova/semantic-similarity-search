import collections
import collections.abc

# Patch collections.Hashable for Python 3.10+ compatibility
collections.Hashable = collections.abc.Hashable

from sematch.semantic.similarity import WordNetSimilarity
from sematch.semantic.similarity import EntitySimilarity
from sematch_helpers import qid_to_dbpedia

entity_sim = EntitySimilarity()
wns = WordNetSimilarity()

print(wns.word_similarity("comedy", "drama", "wup"))
print(wns.word_similarity("Comedy horror", "Comedy thriller", "wup"))
print(wns.word_similarity("Rome", "Paris", "li"))

# TODO rename relatedness, find suitable examples for wordnet, find if semantic search can work
def sematch_similarity(a_qid, b_qid):

    a_uri = qid_to_dbpedia(a_qid)
    b_uri = qid_to_dbpedia(b_qid)

    if not a_uri or not b_uri:
        return 0.0
    print(a_qid, b_qid)
    print(a_uri)
    print(b_uri)
    
    try:
        score = entity_sim.relatedness(
            a_uri,
            b_uri,  
        )

        if score is None:
            return 0.0

        return float(score)

    except Exception as e:
        print("Sematch error:", e)
        return 0.0


# Computing English word similarity using Li method
def word_similarity(word1, word2, method='wup'):
    try:
        score = wns.word_similarity(word1, word2, method)
        return float(score) if score is not None else 0.0
    except Exception as e:
        print("WordNet similarity error:", e)
        return 0.0


def semantic_search(query, G, top_k=10):

    query_tokens = [
        t.lower()
        for t in query.split()
        if len(t) > 2
    ]

    results = []

    for node, data in G.nodes(data=True):

        label = data.get("label")

        if not label:
            continue

        label_tokens = label.lower().split()

        scores = []

        for q in query_tokens:
            for l in label_tokens:

                try:
                    score = wns.word_similarity(
                        q,
                        l,
                        "wup"
                    )

                    if score is not None:
                        scores.append(score)

                except Exception:
                    pass

        if scores:

            avg_score = sum(scores) / len(scores)

            results.append(
                (
                    node,
                    label,
                    avg_score
                )
            )

    results.sort(
        key=lambda x: x[2],
        reverse=True
    )

    return results[:top_k]