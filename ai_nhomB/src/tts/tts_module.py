"""
TTS Module - Chuyển đổi văn bản thành giọng nói.

Refactored từ: ai_nhomB/tts_module.py
Thay đổi:
    - Chuyển sang class TextToSpeech
    - Output path lấy từ config
    - Thêm logging
"""

import os
from gtts import gTTS
from src.utils.logger import setup_logger


class TextToSpeech:
    """Class quản lý Text-to-Speech với gTTS."""

    def __init__(self, config: dict):
        """
        Khởi tạo TTS module.

        Args:
            config: Dict config chứa tts.language, tts.output_dir
        """
        self.logger = setup_logger("TTS", config)
        tts_config = config.get("tts", {})

        self.language = tts_config.get("language", "vi")
        self.output_dir = tts_config.get("output_dir", "outputs/audio")

        # Đảm bảo thư mục output tồn tại
        os.makedirs(self.output_dir, exist_ok=True)
        self.logger.info("TTS module đã sẵn sàng.")

    def speak(self, text: str, filename: str = "focusbuddy_reply.mp3") -> str:
        """
        Chuyển văn bản thành file âm thanh.

        Args:
            text: Văn bản cần chuyển thành giọng nói.
            filename: Tên file output (mặc định: focusbuddy_reply.mp3).

        Returns:
            Đường dẫn tuyệt đối tới file audio, hoặc None nếu lỗi.
        """
        try:
            output_path = os.path.join(self.output_dir, filename)
            tts = gTTS(text=text, lang=self.language)
            tts.save(output_path)

            abs_path = os.path.abspath(output_path)
            self.logger.info(f"Đã tạo file audio: {abs_path}")
            return abs_path
        except Exception as e:
            self.logger.error(f"Lỗi khi tạo giọng nói: {e}")
            return None
