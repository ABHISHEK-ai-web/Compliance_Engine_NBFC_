"""Ingest regulation documents into ChromaDB (PDF or HTML text)."""
import os
import re
import uuid
from html import unescape
from pathlib import Path

from models.schemas import DocumentType
from services.pdf_processor import PDFProcessor
from services.embedding_service import EmbeddingService
from services.vector_store import VectorStore
from config import settings

pdf_processor = PDFProcessor()
embedding_service = EmbeddingService()
vector_store = VectorStore()


def strip_html(html: str) -> str:
    text = re.sub(r"<script[^>]*>[\s\S]*?</script>", " ", html, flags=re.I)
    text = re.sub(r"<style[^>]*>[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def ingest_regulation_pdf(
    file_path: str,
    filename: str,
    metadata_extra: dict | None = None,
) -> dict:
    """Index a PDF file into the regulations collection."""
    document_id = str(uuid.uuid4())
    chunks = pdf_processor.process_pdf(file_path)
    if not chunks:
        return {"document_id": document_id, "chunks_created": 0, "status": "empty"}

    embeddings = embedding_service.generate_embeddings([c["text"] for c in chunks])
    base_meta = {
        "document_id": document_id,
        "filename": filename,
        "document_type": DocumentType.REGULATION.value,
        "source": "rbi_sync",
    }
    if metadata_extra:
        base_meta.update(metadata_extra)

    vector_store.add_documents(
        collection_name="regulations",
        documents=[c["text"] for c in chunks],
        embeddings=embeddings,
        metadatas=[
            {
                **base_meta,
                "chunk_index": c["chunk_index"],
                "page_number": c["page_number"],
            }
            for c in chunks
        ],
        ids=[f"{document_id}_chunk_{i}" for i in range(len(chunks))],
    )
    return {
        "document_id": document_id,
        "chunks_created": len(chunks),
        "status": "success",
        "filename": filename,
    }


def ingest_regulation_text(
    text: str,
    title: str,
    metadata_extra: dict | None = None,
) -> dict:
    """Index plain text (e.g. from RBI RSS HTML) into regulations collection."""
    document_id = str(uuid.uuid4())
    cleaned = pdf_processor.clean_text(text)
    if not cleaned or len(cleaned) < 50:
        return {"document_id": document_id, "chunks_created": 0, "status": "empty"}

    chunks = []
    global_idx = 0
    for page_chunk in pdf_processor.chunk_text(cleaned, page_number=1):
        page_chunk["chunk_index"] = global_idx
        chunks.append(page_chunk)
        global_idx += 1

    embeddings = embedding_service.generate_embeddings([c["text"] for c in chunks])
    filename = metadata_extra.get("filename", title[:80]) if metadata_extra else title[:80]
    base_meta = {
        "document_id": document_id,
        "filename": filename,
        "document_type": DocumentType.REGULATION.value,
        "source": "rbi_sync",
    }
    if metadata_extra:
        base_meta.update(metadata_extra)

    vector_store.add_documents(
        collection_name="regulations",
        documents=[c["text"] for c in chunks],
        embeddings=embeddings,
        metadatas=[
            {**base_meta, "chunk_index": c["chunk_index"], "page_number": 1}
            for c in chunks
        ],
        ids=[f"{document_id}_chunk_{i}" for i in range(len(chunks))],
    )
    return {
        "document_id": document_id,
        "chunks_created": len(chunks),
        "status": "success",
        "filename": filename,
    }


def save_downloaded_file(content: bytes, filename: str) -> str:
    os.makedirs(settings.upload_dir, exist_ok=True)
    safe_name = re.sub(r"[^\w.\-]", "_", filename)[:120]
    path = os.path.join(settings.upload_dir, f"rbi_{uuid.uuid4().hex[:8]}_{safe_name}")
    Path(path).write_bytes(content)
    return path
