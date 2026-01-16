FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY app.py ./
COPY chroma_db/ /app/chroma_db/
COPY collection_of_random_data/ /app/collection_of_random_data/
COPY embed_code/ /app/embed_code/
RUN pip install fastapi uvicorn chromadb ollama python-multipart scalar-fastapi
RUN python embed_code/embed.py
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]