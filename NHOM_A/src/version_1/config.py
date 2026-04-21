"""Cấu hình dùng chung cho Version 1."""

from __future__ import annotations

from pathlib import Path
from typing import Final

# Tự động suy ra thư mục gốc của dự án FocusBuddy để tránh hard-code đường dẫn.
PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parents[3]
NHOM_A_ROOT: Final[Path] = PROJECT_ROOT / "NHOM_A"
NHOM_B_AI_ROOT: Final[Path] = PROJECT_ROOT / "NHOM_B" / "ai_nhomB"

# Tạo hai vùng lưu file audio request/response để dễ debug và đo hiệu năng.
REQUEST_AUDIO_DIR: Final[Path] = NHOM_A_ROOT / "runtime" / "request_audio"
RESPONSE_AUDIO_DIR: Final[Path] = NHOM_A_ROOT / "runtime" / "response_audio"

DEFAULT_REQUEST_EXT: Final[str] = "webm"
DEFAULT_RESPONSE_EXT: Final[str] = "mp3"


def ensure_runtime_directories() -> None:
    """Đảm bảo các thư mục runtime tồn tại trước khi xử lý audio."""
    REQUEST_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    RESPONSE_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
