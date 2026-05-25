import shutil
from pathlib import Path

from fastapi import UploadFile

from app.config import settings

ALLOWED_SOURCE_TYPES = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
    "image/gif",
    "application/pdf",
}


def save_template_source(workspace_id: str, upload: UploadFile) -> tuple[str, str]:
    if upload.content_type not in ALLOWED_SOURCE_TYPES:
        raise ValueError("Formato inválido. Use PNG, JPG, WEBP, GIF ou PDF.")

    ext_map = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/webp": ".webp",
        "image/gif": ".gif",
        "application/pdf": ".pdf",
    }
    ext = ext_map.get(
        upload.content_type or "", Path(upload.filename or "").suffix.lower() or ".png"
    )
    dest_dir = settings.upload_dir / workspace_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    filename = f"template{ext}"
    dest_path = dest_dir / filename

    with dest_path.open("wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)

    relative = str(dest_path.relative_to(settings.upload_dir.parent))
    return relative, upload.content_type or "application/octet-stream"
