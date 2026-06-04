# # import requests


# # def qid_to_dbpedia(qid):
# #     """
# #     Convert Wikidata QID -> DBpedia URI
# #     """

# #     headers = {
# #         "User-Agent": "SemanticSimilarityDemo/1.0"
# #     }
# #     url = "https://www.wikidata.org/wiki/Special:EntityData/{}.json".format(qid)
# #     print (url)
# #     r = requests.get(
# #             url,
# #             headers=headers,
# #             timeout=10
# #         )

# #     print("Status:", r.status_code)
# #     print("Content-Type:", r.headers.get("Content-Type"))
# #     print("Preview:", r.text[:300])
# #     return None
# #     # data = requests.get(url, timeout=10).json()
# #     print(data)
# #     entity = data["entities"][qid]
# #     print(entity)
# #     sitelinks = entity.get("sitelinks", {})
# #     print (sitelinks)
# #     if "enwiki" not in sitelinks:
# #         return None

# #     title = sitelinks["enwiki"]["title"]

# #     title = title.replace(" ", "_")
        
# #     return f"http://dbpedia.org/resource/{title}"

  
      
# # if __name__ == "__main__":
# #     print(qid_to_dbpedia("Q472"))
# #     print(qid_to_dbpedia("Q219"))


# import requests


# def qid_to_dbpedia(qid):

#     url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"

#     headers = {
#         "User-Agent": "SemanticSimilarityDemo/1.0"
#     }
#     try: 
#       r = requests.get(
#         url,
#         headers=headers,
#         timeout=10
#     )

#       data = r.json()

#       entity = data["entities"][qid]

#       # print("ENTITY FOUND")

#       sitelinks = entity.get("sitelinks", {})

#       # print("Has enwiki:", "enwiki" in sitelinks)

#       if "enwiki" in sitelinks:
#           # print(sitelinks["enwiki"])

#           title = sitelinks["enwiki"]["title"]

#           uri = f"http://dbpedia.org/resource/{title.replace(' ','_')}"

#           # print("URI:", uri)

#           return uri

#       return None
#     except Exception as e:
#         print("Error fetching entity data:", e)
#         return None


# if __name__ == "__main__":
#     print(qid_to_dbpedia("Q472"))
#     print(qid_to_dbpedia("Q219"))


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