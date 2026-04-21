"""Các hàm tiện ích lưu/đọc file audio cho pipeline."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Dict, Optional
from uuid import uuid4

from src.version_1.config import (
    DEFAULT_REQUEST_EXT,
    DEFAULT_RESPONSE_EXT,
    REQUEST_AUDIO_DIR,
    RESPONSE_AUDIO_DIR,
    ensure_runtime_directories,
)

_MIME_TO_EXT: Dict[str, str] = {
    "audio/webm": "webm",
    "audio/wav": "wav",
    "audio/x-wav": "wav",
    "audio/mpeg": "mp3",
    "audio/mp3": "mp3",
    "audio/ogg": "ogg",
    "audio/x-m4a": "m4a",
    "audio/mp4": "m4a",
}


def normalize_extension(
    file_name_or_ext: Optional[str],
    mime_type: Optional[str],
    default_ext: str = DEFAULT_REQUEST_EXT,
) -> str:
    """Chuẩn hóa phần mở rộng file để tạo tên file an toàn trong runtime."""
    if file_name_or_ext:
        candidate = file_name_or_ext.strip().lower()

        # Cho phép truyền trực tiếp dạng 'webm' hoặc '.webm' từ WebSocket control message.
        if "." not in candidate and candidate.isalnum():
            return candidate

        suffix = Path(candidate).suffix.lower().lstrip(".")
        if suffix:
            return suffix

    if mime_type:
        mapped_ext = _MIME_TO_EXT.get(mime_type.lower())
        if mapped_ext:
            return mapped_ext

    return default_ext


def save_request_audio_bytes(audio_bytes: bytes, extension: str) -> Path:
    """Lưu audio request từ client thành file để chuyển tiếp qua các lớp xử lý."""
    ensure_runtime_directories()
    request_id = str(uuid4())
    file_path = REQUEST_AUDIO_DIR / f"{request_id}.{extension}"
    file_path.write_bytes(audio_bytes)
    return file_path


def build_response_audio_path(request_id: str, extension: str = DEFAULT_RESPONSE_EXT) -> Path:
    """Sinh đường dẫn file audio response tương ứng với request_id."""
    ensure_runtime_directories()
    return RESPONSE_AUDIO_DIR / f"{request_id}.{extension}"


def encode_audio_file_to_base64(file_path: Path) -> str:
    """Mã hóa file audio sang base64 để trả trực tiếp qua WebSocket."""
    return base64.b64encode(file_path.read_bytes()).decode("utf-8")
