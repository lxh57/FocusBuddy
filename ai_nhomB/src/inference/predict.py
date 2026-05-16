"""
Inference Module - Pipeline dự đoán: STT → Chatbot → TTS

Refactored từ: ai_nhomB/chatbot_module.py + ai_nhomB/test_logic.py
Thay đổi:
    - Tách chatbot logic thành class ChatbotInference
    - Pipeline run_pipeline() kết hợp tất cả modules
    - Config-driven, logging, đo thời gian xử lý
"""

import os
import time
import google.generativeai as genai
from dotenv import load_dotenv

from src.stt.whisper_module import WhisperSTT
from src.tts.tts_module import TextToSpeech
from src.utils.logger import setup_logger


class ChatbotInference:
    """Class quản lý Gemini chatbot cho FocusBuddy."""

    def __init__(self, config: dict):
        """
        Khởi tạo Gemini model với config.

        Args:
            config: Dict config chứa chatbot.model_name, chatbot.system_prompt
        """
        self.logger = setup_logger("Chatbot", config)
        chatbot_config = config.get("chatbot", {})

        # Load API key từ .env
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            self.logger.error("Không tìm thấy GOOGLE_API_KEY trong .env")
            raise ValueError(
                "Thiếu GOOGLE_API_KEY. Hãy tạo file .env với nội dung:\n"
                "GOOGLE_API_KEY=your_api_key_here"
            )

        genai.configure(api_key=api_key)

        model_name = chatbot_config.get("model_name", "gemini-2.5-flash")
        system_prompt = chatbot_config.get("system_prompt", "")

        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt
        )
        self.logger.info(f"Chatbot Gemini ({model_name}) đã sẵn sàng.")

    def get_response(self, user_text: str) -> str:
        """
        Gửi văn bản tới Gemini và nhận phản hồi.

        Args:
            user_text: Câu hỏi/tin nhắn từ người dùng.

        Returns:
            Phản hồi đã được làm sạch (bỏ markdown).
        """
        try:
            self.logger.info(f"User: {user_text}")
            response = self.model.generate_content(user_text)
            reply = response.text

            # Làm sạch markdown (giữ nguyên logic gốc)
            clean_reply = reply.replace("**", "").replace("*", "").strip()
            self.logger.info(f"FocusBuddy: {clean_reply[:100]}...")
            return clean_reply
        except Exception as e:
            self.logger.error(f"Lỗi kết nối Gemini: {e}")
            return f"Lỗi kết nối bộ não: {str(e)}"


def run_pipeline(config: dict, audio_path: str = None, text_input: str = None) -> dict:
    """
    Chạy pipeline đầy đủ: STT → Chatbot → TTS

    Args:
        config: Dict config từ YAML.
        audio_path: Đường dẫn file audio (mode giọng nói).
        text_input: Văn bản trực tiếp (mode text, bỏ qua STT).

    Returns:
        Dict chứa kết quả:
        {
            "input_text": str,
            "ai_reply": str,
            "audio_output": str or None,
            "timing": {
                "stt": float,
                "chatbot": float,
                "tts": float,
                "total": float
            }
        }
    """
    logger = setup_logger("Pipeline", config)
    logger.info("=" * 50)
    logger.info("BẮT ĐẦU PIPELINE FOCUSBUDDY")
    logger.info("=" * 50)

    total_start = time.time()
    result = {
        "input_text": "",
        "ai_reply": "",
        "audio_output": None,
        "timing": {}
    }

    # --- Bước 1: Speech-to-Text (nếu có audio) ---
    if audio_path:
        logger.info(f"[1/3] STT - Đang nhận diện: {audio_path}")
        start = time.time()
        stt = WhisperSTT(config)
        result["input_text"] = stt.transcribe(audio_path)
        result["timing"]["stt"] = round(time.time() - start, 2)
        logger.info(f"STT hoàn tất trong {result['timing']['stt']}s")

        if not result["input_text"]:
            logger.error("Không nhận diện được âm thanh. Dừng pipeline.")
            return result
    elif text_input:
        result["input_text"] = text_input
        result["timing"]["stt"] = 0
        logger.info(f"[1/3] STT - Bỏ qua (mode text): '{text_input}'")
    else:
        logger.error("Không có đầu vào (audio hoặc text).")
        return result

    # --- Bước 2: Chatbot AI ---
    logger.info("[2/3] Chatbot - Đang xử lý...")
    start = time.time()
    chatbot = ChatbotInference(config)
    result["ai_reply"] = chatbot.get_response(result["input_text"])
    result["timing"]["chatbot"] = round(time.time() - start, 2)
    logger.info(f"Chatbot hoàn tất trong {result['timing']['chatbot']}s")

    # --- Bước 3: Text-to-Speech ---
    logger.info("[3/3] TTS - Đang tạo giọng nói...")
    start = time.time()
    tts = TextToSpeech(config)
    result["audio_output"] = tts.speak(result["ai_reply"])
    result["timing"]["tts"] = round(time.time() - start, 2)
    logger.info(f"TTS hoàn tất trong {result['timing']['tts']}s")

    # --- Tổng kết ---
    result["timing"]["total"] = round(time.time() - total_start, 2)
    logger.info("=" * 50)
    logger.info(f"PIPELINE HOÀN TẤT trong {result['timing']['total']}s")
    logger.info("=" * 50)

    return result
