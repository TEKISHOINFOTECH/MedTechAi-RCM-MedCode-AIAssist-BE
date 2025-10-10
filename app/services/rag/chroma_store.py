"""
ChromaDB-backed vector store with ingestion from local docs and query API.
"""
from __future__ import annotations

import os
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings
from pypdf import PdfReader

from app.utils.llm import EmbeddingClient
from config import settings


class ChromaVectorStore:
    def __init__(self, collection_name: str = "medtechai_docs"):
        self.client = chromadb.Client(ChromaSettings(anonymized_telemetry=False, persist_directory=settings.vector_db_dir))
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.embedding_client = EmbeddingClient()

    def _read_text(self, path: str) -> str:
        if path.lower().endswith(".pdf"):
            reader = PdfReader(path)
            text = "\n".join([p.extract_text() or "" for p in reader.pages])
            return text
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            return ""

    async def ingest_directory(self, directory: Optional[str] = None) -> int:
        dir_path = directory or settings.ingest_docs_dir
        files: List[str] = []
        for root, _, names in os.walk(dir_path):
            for n in names:
                if any(n.lower().endswith(ext) for ext in [".md", ".txt", ".pdf"]):
                    files.append(os.path.join(root, n))

        texts: List[str] = []
        metadatas: List[Dict[str, Any]] = []
        ids: List[str] = []
        for i, fpath in enumerate(files):
            content = self._read_text(fpath)
            if not content:
                continue
            texts.append(content)
            metadatas.append({"source": fpath})
            ids.append(f"doc-{i}")

        if not texts:
            return 0

        embeddings = await self.embedding_client.embed(texts)
        self.collection.add(documents=texts, metadatas=metadatas, ids=ids, embeddings=embeddings)
        self.client.persist()
        return len(texts)

    async def query(self, query_text: str, k: int = 5) -> List[Dict[str, Any]]:
        query_embeddings = await self.embedding_client.embed([query_text])
        results = self.collection.query(query_embeddings=query_embeddings, n_results=k)
        docs = []
        for i in range(len(results.get("ids", [[]])[0])):
            docs.append(
                {
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None,
                }
            )
        return docs


