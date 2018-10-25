import sys
import json
import re
import os
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


HOST = 'http://localhost:9200/'
FOLDER = "json/hep-th-2002/"
FIELDS = [("author", re.compile(" +author *= *")),
          ("date", re.compile(" +date *= *"))]


def anti_stupidity_function(folder):
    print(len(os.listdir(folder)))
    for filename in os.listdir(folder):
        print('.', end="", flush=True)
        txt = ""
        with open(folder + filename, 'r') as f:
            txt = f.read()
        txt = txt.replace("'", '"')
        txt = txt.replace(' "": "",', "")

        with open(folder + filename, 'w') as f:
            f.write(txt)
    print()


def json_to_bulk(folder, index, doc_type="document"):
    print("Building a new one with", len(os.listdir(folder)), "documents.")

    for filename in os.listdir(folder):
        print('.', end="")
        with open(folder + filename) as f:

            f_json = ""
            try :
                f_json = json.load(f)
            except json.decoder.JSONDecodeError:
                continue

            f_json["_index"] = index
            f_json["_type"] = doc_type

            yield f_json


def get_date(index, txt, query):
    j0 = txt[index.end():].find("'")
    if j0 == -1:
        return txt
    j0 += index.end() + 1

    j1 = txt[j0:].find("'")
    if j1 == -1:
        return txt
    j1 += j0

    date = txt[j0:j1]
    sep = date.find(':')
    if sep == -1:
        query["bool"]["must"].append({"match" : {'date' : date}})
        return txt[:index.start()] + txt[j1 + 1:]

    date0 = date[:sep]
    date1 = date[sep+1:]

    if not 'filter' in query['bool']:
        query['bool']['filter'] = { 'range' : { 'date' : {} } }

    query['bool']['filter']['range']['date']['gte'] = date0
    query['bool']['filter']['range']['date']['lt'] = date1

    return txt[:index.start()] + txt[j1 + 1:]


def text_to_query(txt, fields=FIELDS):
    query = { "bool" : {}}

    for field, pattern in fields:
        for i in re.finditer(pattern, txt):

            if field == "date":
                txt = get_date(i, txt, query)
                continue

            j0, j1 = txt[i.end():].find("'"), -1
            if j0 > -1:
                j1 = txt[i.end() + j0 + 1:].find("'")

            if j0 > -1 and j1 > -1:
                if not "must" in query["bool"]:
                    query["bool"]["must"] = []

                j0 += i.end() + 1
                j1 += j0
                query["bool"]["must"].append({"match" : {field : txt[j0 : j1]}})
                txt = txt[:i.start()] + txt[j1 + 1:]

    if txt.strip() != "":
        query["bool"]["should"] = {"match" : {"content" : txt}}

    return {"query" : query}


if __name__ == "__main__":
    es = Elasticsearch(hosts=[HOST])
    # es.indices.delete("test")
    if not es.indices.exists("test"):
        print("No test index found, ", end="", flush=True)
        es.indices.create("test")
        bulk(es, json_to_bulk(FOLDER, 'test'), stats_only=True)
        print("\nTest index is build.")

    query = text_to_query("theory date = '2001:2003'")

    print(query, end='\n\n')
    results = es.search(index="test", body=query)['hits']['hits']
    for i, doc in enumerate(results):
        print(doc)
        break