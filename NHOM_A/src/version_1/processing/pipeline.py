"""Pipeline xử lý audio end-to-end cho Version 1."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from src.logger import logger
from src.version_1.integration.nhom_b_adapter import (
    NhomBIntegrationError,
    get_chatbot_response,
    speech_to_text,
    text_to_speech,
    warmup_nhom_b_integration,
)
from src.version_1.processing.storage import build_response_audio_path


@dataclass(frozen=True)
class PipelineResult:
    """Kết quả xử lý hoàn chỉnh của một request audio."""

    request_id: str
    request_audio_path: Path
    response_audio_path: Path
    transcript: str
    reply_text: str
    latency_ms: float


class VoiceRequestPipeline:
    """Điều phối luồng STT -> Chatbot -> TTS theo thứ tự tối ưu cho Version 1."""

    def warmup(self) -> None:
        """Preload module AI để giảm độ trễ request đầu tiên."""
        warmup_nhom_b_integration()

    async def process(self, request_id: str, request_audio_path: Path) -> PipelineResult:
        """Xử lý một file audio request và trả về kết quả đầy đủ."""
        started_at = perf_counter()

        # Bước 1: Chạy STT trong thread riêng để không chặn event loop FastAPI.
        try:
            transcript = await asyncio.to_thread(speech_to_text, str(request_audio_path))
        except NhomBIntegrationError:
            logger.exception("Loi STT request_id=%s", request_id)
            raise

        if not transcript:
            transcript = "(Khong nhan dien duoc noi dung tu audio)"

        # Bước 2: Tạo câu trả lời chatbot từ transcript đã chuẩn hóa.
        try:
            reply_text = await asyncio.to_thread(get_chatbot_response, transcript)
        except NhomBIntegrationError:
            logger.exception("Loi Chatbot request_id=%s", request_id)
            raise

        # Bước 3: Sinh file audio phản hồi để client có thể phát lại ngay.
        response_target_path = build_response_audio_path(request_id)
        try:
            response_audio_path = await asyncio.to_thread(
                text_to_speech,
                reply_text,
                str(response_target_path),
            )
        except NhomBIntegrationError:
            logger.exception("Loi TTS request_id=%s", request_id)
            raise

        total_latency_ms = (perf_counter() - started_at) * 1000.0
        logger.info(
            "Da xu ly xong request_id=%s | transcript_len=%s | latency_ms=%.2f",
            request_id,
            len(transcript),
            total_latency_ms,
        )

        return PipelineResult(
            request_id=request_id,
            request_audio_path=request_audio_path,
            response_audio_path=response_audio_path,
            transcript=transcript,
            reply_text=reply_text,
            latency_ms=total_latency_ms,
        )
