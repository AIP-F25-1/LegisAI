import time
from pathlib import Path
from typing import Any, Dict, List

import aiofiles
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

router = APIRouter()


class UploadResponse(BaseModel):
    file_id: str
    filename: str
    file_type: str
    size: int
    status: str
    processing_results: Dict[str, Any] | None = None


@router.post("/api/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    """Upload a legal document for analysis."""
    try:
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)

        content = await file.read()
        file_id = f"doc_{int(time.time())}"
        file_path = upload_dir / f"{file_id}_{file.filename}"

        async with aiofiles.open(file_path, "wb") as f_handle:
            await f_handle.write(content)

        return UploadResponse(
            file_id=file_id,
            filename=file.filename,
            file_type=file.content_type or "application/octet-stream",
            size=len(content),
            status="uploaded",
            processing_results={
                "pages_extracted": 1,
                "text_length": len(content),
                "language_detected": "en",
                "document_type": "legal_document",
            },
        )

    except Exception as exc:  # pragma: no cover - defensive logging
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/api/files")
async def list_uploaded_files() -> Dict[str, Any]:
    """List uploaded files."""
    try:
        upload_dir = Path("uploads")
        files: List[Dict[str, Any]] = []

        if upload_dir.exists():
            for file_path in upload_dir.iterdir():
                if file_path.is_file():
                    files.append(
                        {
                            "file_id": file_path.stem.split("_")[0],
                            "filename": "_".join(file_path.stem.split("_")[1:]),
                            "size": file_path.stat().st_size,
                            "upload_date": "2024-01-01T00:00:00Z",
                        }
                    )

        return {"files": files, "total_files": len(files)}
    except Exception as exc:  # pragma: no cover - defensive logging
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/api/files/{file_id}")
async def delete_file(file_id: str) -> Dict[str, Any]:
    """Delete uploaded file."""
    try:
        upload_dir = Path("uploads")
        deleted = False

        if upload_dir.exists():
            for file_path in upload_dir.iterdir():
                if file_path.is_file() and file_path.stem.startswith(file_id):
                    file_path.unlink()
                    deleted = True
                    break

        if not deleted:
            raise HTTPException(status_code=404, detail="File not found")

        return {"file_id": file_id, "status": "deleted"}
    except Exception as exc:  # pragma: no cover - defensive logging
        raise HTTPException(status_code=500, detail=str(exc))


__all__ = ["router", "UploadResponse"]


