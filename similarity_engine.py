import re
import collections
import collections.abc

# Patch collections.Hashable for Python 3.10+ compatibility used by sematch.
collections.Hashable = collections.abc.Hashable

from sematch.semantic.similarity import EntitySimilarity, WordNetSimilarity
from sematch_helpers import qid_to_dbpedia


entity_sim = EntitySimilarity()
wns = WordNetSimilarity()


def sematch_similarity(a_qid, b_qid):
    """Compute Sematch relatedness between two Wikidata QIDs.
    """
    a_uri = qid_to_dbpedia(a_qid)
    b_uri = qid_to_dbpedia(b_qid)

    if not a_uri or not b_uri:
        return 0.0

    try:
        score = entity_sim.relatedness(a_uri, b_uri)
        return float(score) if score is not None else 0.0
    except Exception:
        return 0.0


def tokenize(text):
    """Simple tokenization: split on common separators and filter short tokens."""
    return [
        t.lower()
        for t in re.split(r"[\s,;/\\|_\-()]+", text)
        if t and len(t) > 2
    ]


def word_similarity(text1, text2, method="wup"):
    """Compute an aggregate WordNet similarity between two strings.

    The function tokenizes both inputs and computes pairwise WordNet
    similarity scores, returning the mean of available scores.
    """
    tokens1 = tokenize(text1)
    tokens2 = tokenize(text2)
    scores = []

    for w1 in tokens1:
        for w2 in tokens2:
            try:
                score = wns.word_similarity(w1, w2, method)
                if score is not None:
                    scores.append(float(score))
            except Exception:
                pass

    return sum(scores) / len(scores) if scores else 0.0


def semantic_search(query, G, top_k=10):
    """Perform a simple semantic search over graph node labels.

    Returns up to `top_k` tuples (node, label, score) sorted by score.
    """
    query_tokens = [t.lower() for t in tokenize(query)]
    results = []

    for node, data in G.nodes(data=True):
        label = data.get("label")
        if not label:
            continue

        label_tokens = tokenize(str(label))
        scores = []

        for q in query_tokens:
            for l in label_tokens:
                try:
                    score = wns.word_similarity(q, l, "wup")
                    if score is not None:
                        scores.append(score)
                except Exception:
                    pass

        if scores:
            avg_score = sum(scores) / len(scores)
            results.append((node, label, avg_score))

    results.sort(key=lambda x: x[2], reverse=True)
    return results[:top_k]