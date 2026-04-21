"""Điểm khởi động chính của FastAPI cho Nhóm A."""

from __future__ import annotations

import asyncio
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.logger import logger
from src.version_1.communication.router import router as voice_v1_router
from src.version_1.communication.router import warmup_version_1


def create_app() -> FastAPI:
    """Khởi tạo ứng dụng FastAPI và cấu hình các middleware cơ bản."""
    app = FastAPI(title="AI Voice Server - Nhóm A")

    # Cấu hình CORS để client HTML có thể gọi API trong giai đoạn kiểm thử.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Gắn router Version 1 để phục vụ API xử lý audio cho luồng ghi âm một lần.
    app.include_router(voice_v1_router)

    return app


app = create_app()


@app.on_event("startup")
async def on_startup() -> None:
    """Ghi nhận thời điểm server bắt đầu khởi động."""
    logger.info("AI Voice Server - Nhóm A đang bắt đầu khởi động.")

    # Warmup module AI từ NHOM_B để giảm thời gian chờ của request đầu tiên.
    try:
        await asyncio.to_thread(warmup_version_1)
        logger.info("Warmup Version 1 thanh cong.")
    except Exception as exc:
        logger.warning("Warmup Version 1 that bai, chuyen sang fallback. Ly do: %s", exc)


@app.get("/")
async def health_check() -> Dict[str, str]:
    """API kiểm tra trạng thái hoạt động của server."""
    return {
        "status": "success",
        "message": "Server FastAPI Nhóm A đang chạy ổn định trên laptop",
    }
