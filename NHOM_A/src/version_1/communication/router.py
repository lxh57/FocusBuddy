"""Router API/WebSocket cho luồng ghi âm một lần của Version 1."""

from __future__ import annotations

import json
from typing import Any, Dict

from fastapi import APIRouter, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect, status
from fastapi.responses import FileResponse

from src.logger import logger
from src.version_1.config import DEFAULT_REQUEST_EXT, RESPONSE_AUDIO_DIR
from src.version_1.processing.pipeline import VoiceRequestPipeline
from src.version_1.processing.storage import (
    encode_audio_file_to_base64,
    normalize_extension,
    save_request_audio_bytes,
)
from src.version_1.schemas import VoiceProcessResponse

router = APIRouter(prefix="/api/v1", tags=["voice-v1"])
pipeline = VoiceRequestPipeline()


def _guess_audio_mime_type(file_name: str) -> str:
    """Suy ra mime type tu ten file audio de client phat dung dinh dang."""
    lower_name = file_name.lower()
    if lower_name.endswith(".wav"):
        return "audio/wav"
    if lower_name.endswith(".ogg"):
        return "audio/ogg"
    if lower_name.endswith(".webm"):
        return "audio/webm"
    if lower_name.endswith(".m4a"):
        return "audio/mp4"
    return "audio/mpeg"


def warmup_version_1() -> None:
    """Preload pipeline để giảm độ trễ request đầu tiên."""
    pipeline.warmup()


@router.post("/voice/process", response_model=VoiceProcessResponse)
async def process_audio_file(file: UploadFile = File(...)) -> VoiceProcessResponse:
    """API nhận file audio request và trả metadata của file audio response."""
    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File audio rong. Vui long ghi am va gui lai.",
        )

    request_ext = normalize_extension(file.filename, file.content_type)
    request_audio_path = save_request_audio_bytes(audio_bytes, request_ext)
    request_id = request_audio_path.stem

    logger.info(
        "Nhan API /voice/process request_id=%s | size=%s bytes",
        request_id,
        len(audio_bytes),
    )

    try:
        result = await pipeline.process(request_id, request_audio_path)
    except Exception as exc:
        logger.exception("Loi xu ly request_id=%s", request_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Khong the xu ly audio: {exc}",
        ) from exc

    return VoiceProcessResponse(
        request_id=result.request_id,
        transcript=result.transcript,
        reply_text=result.reply_text,
        response_file=result.response_audio_path.name,
        latency_ms=result.latency_ms,
    )


@router.get("/voice/response/{file_name}")
async def get_response_audio(file_name: str) -> FileResponse:
    """API trả trực tiếp file audio response theo file_name."""
    # Chặn path traversal để đảm bảo client chỉ truy cập vùng runtime của NHOM_A.
    if "/" in file_name or "\\" in file_name or ".." in file_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ten file khong hop le.",
        )

    audio_path = RESPONSE_AUDIO_DIR / file_name
    if not audio_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Khong tim thay file audio response.",
        )

    media_type = _guess_audio_mime_type(audio_path.name)

    return FileResponse(path=audio_path, media_type=media_type, filename=file_name)


@router.websocket("/ws/voice")
async def websocket_voice(websocket: WebSocket) -> None:
    """WebSocket nhận stream audio chunk và trả audio phản hồi khi client gửi stop."""
    await websocket.accept()
    logger.info("Client da ket noi WebSocket /api/v1/ws/voice")

    audio_buffer = bytearray()
    request_ext = DEFAULT_REQUEST_EXT

    try:
        while True:
            message = await websocket.receive()
            binary_chunk = message.get("bytes")
            text_payload = message.get("text")

            # Nhận dữ liệu nhị phân từ mic client và gom thành một file request hoàn chỉnh.
            if binary_chunk is not None:
                audio_buffer.extend(binary_chunk)
                continue

            if text_payload is None:
                continue

            control_message = _safe_parse_json(text_payload)
            event_type = str(control_message.get("type", "")).lower()

            # Client gửi start để báo định dạng file và reset buffer cho phiên ghi âm mới.
            if event_type == "start":
                request_ext = normalize_extension(
                    str(control_message.get("format", DEFAULT_REQUEST_EXT)),
                    None,
                )
                audio_buffer.clear()
                await websocket.send_json({"type": "ack", "message": "start_ok"})
                continue

            # Client gửi stop để chốt request audio và kích hoạt pipeline xử lý.
            if event_type == "stop":
                if not audio_buffer:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": "Chua nhan duoc du lieu audio nao truoc khi stop.",
                        }
                    )
                    continue

                request_audio_path = save_request_audio_bytes(bytes(audio_buffer), request_ext)
                request_id = request_audio_path.stem

                logger.info(
                    "Nhan WebSocket stop request_id=%s | size=%s bytes",
                    request_id,
                    len(audio_buffer),
                )

                try:
                    result = await pipeline.process(request_id, request_audio_path)
                except Exception as exc:
                    logger.exception("Loi xu ly WebSocket request_id=%s", request_id)
                    await websocket.send_json(
                        {
                            "type": "error",
                            "request_id": request_id,
                            "message": f"Khong the xu ly audio: {exc}",
                        }
                    )
                    audio_buffer.clear()
                    continue

                encoded_audio = encode_audio_file_to_base64(result.response_audio_path)

                await websocket.send_json(
                    {
                        "type": "result",
                        "request_id": result.request_id,
                        "transcript": result.transcript,
                        "reply_text": result.reply_text,
                        "latency_ms": result.latency_ms,
                        "response_file": result.response_audio_path.name,
                        "audio_mime_type": _guess_audio_mime_type(result.response_audio_path.name),
                        "audio_base64": encoded_audio,
                    }
                )
                audio_buffer.clear()
                continue

            # Hỗ trợ ping để client kiểm tra kết nối sống trước khi ghi âm.
            if event_type == "ping":
                await websocket.send_json({"type": "pong"})
                continue

            await websocket.send_json(
                {
                    "type": "error",
                    "message": "Control message khong hop le. Dung start/stop/ping.",
                }
            )

    except WebSocketDisconnect:
        logger.info("Client da ngat ket noi WebSocket /api/v1/ws/voice")
    except Exception as exc:
        logger.exception("Loi khong mong muon trong WebSocket: %s", exc)
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)


def _safe_parse_json(text_payload: str) -> Dict[str, Any]:
    """Parse control message JSON theo cách an toàn để tránh làm rơi kết nối."""
    try:
        parsed = json.loads(text_payload)
    except json.JSONDecodeError:
        return {}

    if not isinstance(parsed, dict):
        return {}

    return parsed
