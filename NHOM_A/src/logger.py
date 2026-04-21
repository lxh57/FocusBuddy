"""Cấu hình logging dùng chung cho toàn bộ hệ thống."""

from __future__ import annotations

import logging
from typing import Final

LOG_FORMAT: Final[str] = "[%(asctime)s] - [%(levelname)s] - %(message)s"
DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"
LOGGER_NAME: Final[str] = "ai_voice_server"


def configure_logger() -> logging.Logger:
    """Khởi tạo logger mặc định và gắn formatter theo chuẩn của dự án."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Chỉ gắn handler một lần để tránh log bị nhân đôi khi import lại module.
    if not root_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
    else:
        for handler in root_logger.handlers:
            handler.setFormatter(formatter)

    return logging.getLogger(LOGGER_NAME)


logger: Final[logging.Logger] = configure_logger()
