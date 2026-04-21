"""Adapter tích hợp các module AI của NHOM_B vào backend NHOM_A."""

from __future__ import annotations

import importlib
import math
import struct
import sys
import wave
from pathlib import Path
from types import ModuleType
from typing import Callable, Dict, Optional, cast

from src.logger import logger
from src.version_1.config import NHOM_B_AI_ROOT


class NhomBIntegrationError(RuntimeError):
    """Lỗi xảy ra trong quá trình gọi module của NHOM_B."""


_ModuleFunctions = Dict[str, Callable[..., object]]
_MODULE_FUNCTIONS: Optional[_ModuleFunctions] = None


def _fallback_speech_to_text(_: str) -> str:
    """Fallback STT khi môi trường chưa sẵn sàng model Whisper."""
    logger.warning("STT fallback dang duoc su dung vi module NHOM_B chua san sang.")
    return ""


def _fallback_chatbot_response(user_text: str) -> str:
    """Fallback chatbot giúp pipeline vẫn phản hồi thay vì trả lỗi 500."""
    if user_text.strip():
        return (
            "He thong tam thoi dang o che do du phong. "
            "Minh da ghi nhan noi dung cua ban va se tra loi day du hon khi AI san sang."
        )
    return "Minh chua nghe ro noi dung. Ban thu ghi am lai giup minh nhe."


def _synthesize_fallback_wav(output_filename: str) -> Path:
    """Tao file WAV ngan de client luon nhan duoc audio response hop le."""
    output_path = Path(output_filename).with_suffix(".wav")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    sample_rate = 16000
    duration_seconds = 0.35
    frequency = 440.0
    amplitude = 8000
    total_frames = int(sample_rate * duration_seconds)

    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for frame_idx in range(total_frames):
            sample = int(amplitude * math.sin(2.0 * math.pi * frequency * frame_idx / sample_rate))
            wav_file.writeframes(struct.pack("<h", sample))

    return output_path


def _fallback_text_to_speech(_: str, output_filename: str) -> Path:
    """Fallback TTS khi gTTS hoac module NHOM_B khong hoat dong."""
    logger.warning("TTS fallback dang duoc su dung vi module NHOM_B chua san sang.")
    return _synthesize_fallback_wav(output_filename)


def _bootstrap_import_path() -> None:
    """Thêm đường dẫn NHOM_B/ai_nhomB vào sys.path để import module động."""
    ai_path = str(NHOM_B_AI_ROOT)
    if ai_path not in sys.path:
        sys.path.insert(0, ai_path)


def _get_callable(module: ModuleType, function_name: str) -> Callable[..., object]:
    """Kiểm tra và trả về function callable từ module của NHOM_B."""
    candidate = getattr(module, function_name, None)
    if not callable(candidate):
        raise NhomBIntegrationError(
            f"Module {module.__name__} không có hàm callable '{function_name}'."
        )
    return cast(Callable[..., object], candidate)


def _load_module_functions() -> _ModuleFunctions:
    """Import một lần và cache các hàm trọng yếu để giảm độ trễ các request sau."""
    global _MODULE_FUNCTIONS

    if _MODULE_FUNCTIONS is not None:
        return _MODULE_FUNCTIONS

    _bootstrap_import_path()

    stt_callable: Callable[..., object] = _fallback_speech_to_text
    chatbot_callable: Callable[..., object] = _fallback_chatbot_response
    tts_callable: Callable[..., object] = _fallback_text_to_speech

    try:
        stt_module = importlib.import_module("stt_module")
        stt_callable = _get_callable(stt_module, "speech_to_text")
    except Exception as exc:
        logger.warning(
            "Khong nap duoc stt_module tu %s. Ly do: %s",
            Path(NHOM_B_AI_ROOT),
            exc,
        )

    try:
        chatbot_module = importlib.import_module("chatbot_module")
        chatbot_callable = _get_callable(chatbot_module, "get_chatbot_response")
    except Exception as exc:
        logger.warning(
            "Khong nap duoc chatbot_module tu %s. Ly do: %s",
            Path(NHOM_B_AI_ROOT),
            exc,
        )

    try:
        tts_module = importlib.import_module("tts_module")
        tts_callable = _get_callable(tts_module, "text_to_speech")
    except Exception as exc:
        logger.warning(
            "Khong nap duoc tts_module tu %s. Ly do: %s",
            Path(NHOM_B_AI_ROOT),
            exc,
        )

    _MODULE_FUNCTIONS = {
        "speech_to_text": stt_callable,
        "get_chatbot_response": chatbot_callable,
        "text_to_speech": tts_callable,
    }

    logger.info("Da khoi tao xong adapter NHOM_B cho Version 1 (co the dang o che do fallback).")
    return _MODULE_FUNCTIONS


def warmup_nhom_b_integration() -> None:
    """Preload module để request đầu tiên phản hồi nhanh hơn."""
    _load_module_functions()


def speech_to_text(audio_path: str) -> str:
    """Gọi STT của NHOM_B để chuyển file audio sang text."""
    try:
        module_functions = _load_module_functions()
        raw_text = module_functions["speech_to_text"](audio_path)
    except Exception as exc:
        logger.warning("Loi khi goi speech_to_text, chuyen ve transcript rong. Ly do: %s", exc)
        return ""

    return str(raw_text or "").strip()


def get_chatbot_response(user_text: str) -> str:
    """Gọi chatbot của NHOM_B để tạo phản hồi văn bản."""
    safe_input = user_text.strip() or "Nguoi dung gui audio nhung chua nhan dien duoc noi dung."

    try:
        module_functions = _load_module_functions()
        raw_reply = module_functions["get_chatbot_response"](safe_input)
    except Exception as exc:
        logger.warning("Loi khi goi get_chatbot_response, dung fallback text. Ly do: %s", exc)
        raw_reply = _fallback_chatbot_response(safe_input)

    reply_text = str(raw_reply or "").strip()
    if not reply_text:
        return "Minh chua nghe ro noi dung vua gui. Ban co the thu lai mot lan nua khong?"

    return reply_text


def text_to_speech(text: str, output_filename: str) -> Path:
    """Gọi TTS của NHOM_B để sinh file audio phản hồi."""
    try:
        module_functions = _load_module_functions()
        raw_result = module_functions["text_to_speech"](text, output_filename)
    except Exception as exc:
        logger.warning("Loi khi goi text_to_speech, dung fallback WAV. Ly do: %s", exc)
        return _fallback_text_to_speech(text, output_filename)

    if raw_result is None:
        logger.warning("NHOM_B text_to_speech tra ve None, dung fallback WAV.")
        return _fallback_text_to_speech(text, output_filename)

    response_path = Path(str(raw_result))
    if not response_path.exists():
        logger.warning("File audio response khong ton tai sau TTS, dung fallback WAV.")
        return _fallback_text_to_speech(text, output_filename)

    return response_path
