import chromadb
from chromadb.config import Settings as ChromaSettings
from config import settings
import os


class VectorStore:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _get_client(self):
        if self._client is None:
            os.makedirs(settings.chroma_persist_dir, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=settings.chroma_persist_dir,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
        return self._client

    def get_collection(self, collection_name: str):
        client = self._get_client()
        return client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(
        self,
        collection_name: str,
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
        ids: list[str],
    ):
        """Add document chunks with embeddings to a collection."""
        collection = self.get_collection(collection_name)
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            end = min(i + batch_size, len(documents))
            collection.add(
                documents=documents[i:end],
                embeddings=embeddings[i:end],
                metadatas=metadatas[i:end],
                ids=ids[i:end],
            )

    def query(
        self,
        collection_name: str,
        query_embedding: list[float],
        n_results: int = 5,
        where: dict | None = None,
    ) -> dict:
        """Query a collection for similar documents."""
        collection = self.get_collection(collection_name)
        params = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            params["where"] = where
        return collection.query(**params)

    def get_collection_count(self, collection_name: str) -> int:
        collection = self.get_collection(collection_name)
        return collection.count()

    def get_all_documents(self, collection_name: str, limit: int = 100) -> dict:
        collection = self.get_collection(collection_name)
        return collection.get(limit=limit, include=["documents", "metadatas"])
