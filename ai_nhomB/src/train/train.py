"""
Training Module - Skeleton cho future model training.

Hiện tại FocusBuddy dùng:
    - Whisper pretrained (không cần train)
    - Gemini API (không cần train)

File này chuẩn bị sẵn cấu trúc để sau này có thể:
    - Fine-tune Whisper cho tiếng Việt
    - Train custom NLP model thay Gemini
    - Train intent classifier, v.v.
"""

import os
import json
from datetime import datetime
from src.utils.config import load_config
from src.utils.logger import setup_logger


def train(version: str = "v1"):
    """
    Entry point cho training.

    Args:
        version: Version config để sử dụng.
    """
    config = load_config(version)
    logger = setup_logger("Train", config)

    logger.info(f"Bắt đầu training với config version: {version}")
    logger.info("(Chưa có model nào cần train. Đây là skeleton.)")

    # Placeholder: training loop
    # for epoch in range(config["training"]["epochs"]):
    #     train_loss = train_one_epoch(model, dataloader)
    #     val_loss = validate(model, val_dataloader)
    #     logger.info(f"Epoch {epoch}: train_loss={train_loss:.4f}, val_loss={val_loss:.4f}")

    # Lưu metrics mẫu
    metrics_dir = config["paths"]["metrics_dir"]
    os.makedirs(metrics_dir, exist_ok=True)

    metrics = {
        "version": version,
        "timestamp": datetime.now().isoformat(),
        "status": "skeleton - no training executed",
        "note": "Thêm logic training ở đây khi cần fine-tune model."
    }

    metrics_path = os.path.join(metrics_dir, "training_metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    logger.info(f"Metrics đã lưu tại: {metrics_path}")
    logger.info("Training hoàn tất (skeleton).")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="FocusBuddy Training")
    parser.add_argument("--version", type=str, default="v1", help="Config version (v1, v2, ...)")
    args = parser.parse_args()
    train(args.version)
