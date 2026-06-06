import requests

CACHE = {}

def qid_to_dbpedia(qid):
    """Return a DBpedia resource URI for a Wikidata QID.

    Results are cached in the module-level `CACHE` dict. Returns `None`
    when no English Wikipedia sitelink is available or on error.
    """

    if qid in CACHE:
        return CACHE[qid]

    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    headers = {"User-Agent": "SemanticSimilarityDemo/1.0"}

    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        data = r.json()

        entities = data.get("entities", {})
        if qid not in entities:
            CACHE[qid] = None
            return None

        entity = entities[qid]
        if "missing" in entity:
            CACHE[qid] = None
            return None

        sitelinks = entity.get("sitelinks", {})
        enwiki = sitelinks.get("enwiki")
        if not enwiki:
            CACHE[qid] = None
            return None

        title = enwiki.get("title", "")
        uri = f"http://dbpedia.org/resource/{title.replace(' ', '_')}"
        CACHE[qid] = uri
        return uri

    except Exception:
        CACHE[qid] = None
        return None