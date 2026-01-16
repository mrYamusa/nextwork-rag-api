import chromadb
import os
from uuid import uuid4

chroma_client = chromadb.PersistentClient(path="./chroma_db/")

collection = chroma_client.get_or_create_collection(name="NextWorkRagApp")

for _ in os.listdir("collection_of_random_data"):
    print(_)
collection_client_document = []
for _ in os.listdir("collection_of_random_data"):
    with open(f"collection_of_random_data/{_}", "r", encoding="utf-8") as f:
        doc = f.read()
        collection_client_document.append(doc)


collection.add(
    ids=[str(uuid4()) for _ in os.listdir("collection_of_random_data")],
    documents=collection_client_document,
    metadatas=[{"source": _} for _ in os.listdir("collection_of_random_data")],
)


# results = collection.query(query_texts=["What is NextWork?"], n_results=1)
# print(results)
def load_data_from_directory():
    collection_client_document = []
    for _ in os.listdir("collection_of_random_data"):
        with open(f"collection_of_random_data/{_}", "r", encoding="utf-8") as f:
            doc = f.read()
            collection_client_document.append(doc)

    collection.add(
        ids=[str(uuid4()) for _ in os.listdir("collection_of_random_data")],
        documents=collection_client_document,
        metadatas=[{"source": _} for _ in os.listdir("collection_of_random_data")],
    )
    print("Data loaded into Chroma collection.")
