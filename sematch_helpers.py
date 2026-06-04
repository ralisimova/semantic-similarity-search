import requests

CACHE = {}


def qid_to_dbpedia(qid):

    if qid in CACHE:
        return CACHE[qid]

    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"

    headers = {
        "User-Agent": "SemanticSimilarityDemo/1.0"
    }

    try:
        r = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        r.raise_for_status()

        data = r.json()

        entities = data.get("entities", {})

        if qid not in entities:
           print("Missing:", qid)
           return None

        entity = entities[qid]
        if "missing" in entity:
           return None
        sitelinks = entity.get("sitelinks", {})

        if "enwiki" not in sitelinks:
            CACHE[qid] = None
            return None

        title = sitelinks["enwiki"]["title"]

        uri = f"http://dbpedia.org/resource/{title.replace(' ','_')}"

        CACHE[qid] = uri

        return uri

    except Exception as e:
        print(
            f"Error fetching entity data for {qid}:",
            e
        )

        CACHE[qid] = None
        return None