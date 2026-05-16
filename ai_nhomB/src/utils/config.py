"""
Config Loader - Đọc và quản lý cấu hình YAML theo version.

Sử dụng:
    from src.utils.config import load_config
    config = load_config("v1")
"""

import os
import yaml
from pathlib import Path


def get_project_root() -> Path:
    """Trả về đường dẫn gốc của project (thư mục chứa main.py)."""
    return Path(__file__).resolve().parent.parent.parent


def load_config(version: str = "v1") -> dict:
    """
    Đọc file config YAML theo version.

    Args:
        version: Tên version (v1, v2, ...). Tương ứng file configs/v1.yaml

    Returns:
        dict chứa toàn bộ config.

    Raises:
        FileNotFoundError: Nếu file config không tồn tại.
    """
    root = get_project_root()
    config_path = root / "configs" / f"{version}.yaml"

    if not config_path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy config: {config_path}\n"
            f"Hãy tạo file configs/{version}.yaml"
        )

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Chuyển đổi các đường dẫn tương đối thành tuyệt đối
    if "paths" in config:
        for key, value in config["paths"].items():
            config["paths"][key] = str(root / value)

    # Tạo các thư mục output nếu chưa tồn tại
    _ensure_directories(config)

    return config


def _ensure_directories(config: dict):
    """Tự động tạo các thư mục cần thiết từ config."""
    if "paths" not in config:
        return

    for key in ["logs_dir", "metrics_dir", "models_dir"]:
        dir_path = config["paths"].get(key)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

    # Tạo thư mục output cho TTS
    if "tts" in config and "output_dir" in config["tts"]:
        root = get_project_root()
        output_dir = root / config["tts"]["output_dir"]
        os.makedirs(output_dir, exist_ok=True)
        config["tts"]["output_dir"] = str(output_dir)
