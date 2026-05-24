from sentence_transformers import SentenceTransformer
from config import settings


class EmbeddingService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _load_model(self):
        if self._model is None:
            self._model = SentenceTransformer(settings.embedding_model)
        return self._model

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of text chunks."""
        model = self._load_model()
        embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        return embeddings.tolist()

    def generate_query_embedding(self, query: str) -> list[float]:
        """Generate embedding for a single query."""
        model = self._load_model()
        embedding = model.encode([query], normalize_embeddings=True)
        return embedding[0].tolist()
