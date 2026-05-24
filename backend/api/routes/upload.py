from fastapi import APIRouter, UploadFile, File, HTTPException
from models.schemas import UploadResponse, DocumentType
from services.pdf_processor import PDFProcessor
from services.embedding_service import EmbeddingService
from services.vector_store import VectorStore
from config import settings
import uuid
import os

router = APIRouter()
pdf_processor = PDFProcessor()
embedding_service = EmbeddingService()
vector_store = VectorStore()


@router.post("/upload-regulation", response_model=UploadResponse)
async def upload_regulation(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    document_id = str(uuid.uuid4())
    file_path = os.path.join(settings.upload_dir, f"{document_id}_{file.filename}")

    os.makedirs(settings.upload_dir, exist_ok=True)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    chunks = pdf_processor.process_pdf(file_path)
    embeddings = embedding_service.generate_embeddings([c["text"] for c in chunks])
    vector_store.add_documents(
        collection_name="regulations",
        documents=[c["text"] for c in chunks],
        embeddings=embeddings,
        metadatas=[{
            "document_id": document_id,
            "filename": file.filename,
            "chunk_index": c["chunk_index"],
            "page_number": c["page_number"],
            "document_type": DocumentType.REGULATION.value,
        } for c in chunks],
        ids=[f"{document_id}_chunk_{i}" for i in range(len(chunks))],
    )

    return UploadResponse(
        document_id=document_id,
        filename=file.filename,
        document_type=DocumentType.REGULATION,
        chunks_created=len(chunks),
        status="success",
        message=f"Regulation document processed: {len(chunks)} chunks indexed",
    )


@router.post("/upload-policy", response_model=UploadResponse)
async def upload_policy(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    document_id = str(uuid.uuid4())
    file_path = os.path.join(settings.upload_dir, f"{document_id}_{file.filename}")

    os.makedirs(settings.upload_dir, exist_ok=True)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    chunks = pdf_processor.process_pdf(file_path)
    embeddings = embedding_service.generate_embeddings([c["text"] for c in chunks])
    vector_store.add_documents(
        collection_name="policies",
        documents=[c["text"] for c in chunks],
        embeddings=embeddings,
        metadatas=[{
            "document_id": document_id,
            "filename": file.filename,
            "chunk_index": c["chunk_index"],
            "page_number": c["page_number"],
            "document_type": DocumentType.POLICY.value,
        } for c in chunks],
        ids=[f"{document_id}_chunk_{i}" for i in range(len(chunks))],
    )

    return UploadResponse(
        document_id=document_id,
        filename=file.filename,
        document_type=DocumentType.POLICY,
        chunks_created=len(chunks),
        status="success",
        message=f"Policy document processed: {len(chunks)} chunks indexed",
    )
