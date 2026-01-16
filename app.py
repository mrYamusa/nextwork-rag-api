from typing import Annotated
from uuid import uuid4
from fastapi import FastAPI, UploadFile, Depends
from contextlib import asynccontextmanager
from rich import panel, print
import chromadb
import ollama
from ollama import Client
from pathlib import Path
import shutil
from scalar_fastapi import get_scalar_api_reference
from embed_code.embed import load_data_from_directory

UPLOAD_DIR = Path("./collection_of_random_data")


async def dummyfunc():
    pass


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    print("Starting App!")
    load_data_from_directory()
    await dummyfunc()
    yield
    print("Shutting Down App!")


chroma_client = chromadb.PersistentClient("./chroma_db")
# ollama_client = Client(host="http://host.docker.internal:11434") -> Use this line when running in Docker
ollama_client = Client(host="http://localhost:11434")

app = FastAPI(title="RAG APP", lifespan=lifespan_handler)


@app.post("/query")
async def get(question: str) -> dict[str, str]:
    document_that_matches_query = collection.query(query_texts=[question], n_results=1)
    print("document_that_matches_query active")
    context_text_documents = (
        document_that_matches_query["documents"][0][0]
        if document_that_matches_query["documents"]
        else ""
    )
    print("context_text_documents active")

    answer = ollama_client.generate(
        model="tinyllama",
        prompt=f"Context: \n{context_text_documents}.\n \nQuestion: \n{question} \nAnswer clearly and concisely ",
    )
    print("answer active")

    return {
        "question": question,
        "answer": f"This is you answer to the question: \n{answer['response']}",
    }


collection = chroma_client.get_or_create_collection(name="NextWorkRagApp")
# Dependency to get the collection


def get_chroma_collection():
    """
    FastAPI dependency that returns the Chroma collection.
    """
    return chroma_client.get_or_create_collection(name="NextWorkRagApp")


@app.post("/uploadfile/")
async def create_upload_file(
    collection: Annotated[
        chromadb.api.models.Collection.Collection, Depends(get_chroma_collection)
    ],
    file: UploadFile | None = None,
):
    if not file:
        return {"message": "No upload file sent"}

    # Ensure upload directory exists
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    file_path = UPLOAD_DIR / file.filename
    print(
        panel.Panel(
            f"Saving file to {file_path} \nand {file.filename}",
            style="bold green",
            border_style="green",
        )
    )

    # Read file content once
    file_content = await file.read()

    # Save file to disk
    try:
        with open(file_path, "wb") as f:
            f.write(file_content)
    except Exception as e:
        return {"message": f"Error saving file: {e}"}

    # Add to Chroma collection
    collection.add(
        ids=[str(uuid4())],
        documents=[file_content.decode("utf-8")],
        metadatas=[{"source": file.filename}],
    )

    print(
        panel.Panel(
            f"Added {file.filename} to collection",
            style="bold green",
            border_style="green",
        )
    )

    return {"filename": file.filename}


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        # Your OpenAPI document
        openapi_url=app.openapi_url,
        # Avoid CORS issues (optional)
        scalar_proxy_url="https://proxy.scalar.com",
        title="RAG APP Scalar API Reference",
    )
