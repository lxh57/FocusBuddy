"""
Logger Module - Thiết lập logging chuẩn cho toàn project.

Sử dụng:
    from src.utils.logger import setup_logger
    logger = setup_logger("module_name", config)
    logger.info("Thông báo...")
"""

import os
import logging
from datetime import datetime


def setup_logger(name: str, config: dict = None, level=logging.INFO) -> logging.Logger:
    """
    Tạo logger với output ra console và file.

    Args:
        name: Tên logger (thường là tên module).
        config: Dict config chứa paths.logs_dir.
        level: Logging level (mặc định INFO).

    Returns:
        logging.Logger đã được cấu hình.
    """
    logger = logging.getLogger(name)

    # Tránh thêm handler trùng lặp nếu logger đã tồn tại
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Formatter chung
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)-15s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler 1: Console output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler 2: File output (nếu có config)
    if config and "paths" in config:
        logs_dir = config["paths"].get("logs_dir")
        if logs_dir:
            os.makedirs(logs_dir, exist_ok=True)
            today = datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(logs_dir, f"{today}.log")

            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger
