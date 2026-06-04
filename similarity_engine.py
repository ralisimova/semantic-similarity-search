from sematch.semantic.similarity import EntitySimilarity
from sematch_helpers import qid_to_dbpedia

entity_sim = EntitySimilarity()


def sematch_similarity(a_qid, b_qid):

    a_uri = qid_to_dbpedia(a_qid)
    b_uri = qid_to_dbpedia(b_qid)

    if not a_uri or not b_uri:
        return 0.0

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