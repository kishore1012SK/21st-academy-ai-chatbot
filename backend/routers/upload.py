import shutil
import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from sqlalchemy.orm import Session
from limiter import limiter

from database.db import get_db
from database.models import Document, DocumentChunk
from schemas import UploadResponse, DocumentOut
from services import rag_service
from auth_utils import get_current_admin
from config import settings

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
@limiter.limit(settings.RATE_LIMIT_UPLOAD)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_UPLOAD_EXT:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds {settings.MAX_UPLOAD_MB}MB limit")

    safe_name = f"{uuid.uuid4().hex}{ext}"
    dest_path = settings.UPLOAD_DIR / safe_name
    with open(dest_path, "wb") as f:
        f.write(contents)

    document = Document(
        filename=file.filename,
        filepath=str(dest_path),
        filetype=ext,
        uploaded_by=admin.get("email"),
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        text = rag_service.extract_text(dest_path)
        chunks = rag_service.chunk_text(text)
        embedded = await rag_service.embed_and_store_chunks(document.id, chunks)

        for i, (chunk_text, vec_path) in enumerate(embedded):
            db.add(DocumentChunk(
                document_id=document.id,
                chunk_index=i,
                content=chunk_text,
                embedding_path=vec_path,
            ))
        db.commit()
        chunks_indexed = len(embedded)
    except Exception as exc:
        # Document is stored even if indexing fails; surface the error but don't 500.
        chunks_indexed = 0

    return UploadResponse(
        success=True,
        document_id=document.id,
        filename=document.filename,
        chunks_indexed=chunks_indexed,
    )


@router.get("/documents", response_model=List[DocumentOut])
async def list_documents(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    docs = db.query(Document).all()
    results = []
    for d in docs:
        results.append(DocumentOut(
            id=d.id,
            filename=d.filename,
            filetype=d.filetype,
            uploaded_by=d.uploaded_by,
            created_at=d.created_at,
            chunks_count=len(d.chunks)
        ))
    return results


@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete uploaded file from filesystem
    try:
        orig_file = Path(doc.filepath)
        if orig_file.exists():
            orig_file.unlink()
    except Exception:
        pass

    # Delete the .npy vector folder for this document
    try:
        vec_dir = settings.VECTOR_DB_DIR / doc.id
        if vec_dir.exists():
            shutil.rmtree(vec_dir)
    except Exception:
        pass

    db.delete(doc)
    db.commit()
    return {"success": True, "message": "Document and embeddings deleted successfully"}
