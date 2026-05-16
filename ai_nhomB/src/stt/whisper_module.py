"""
Whisper STT Module - Chuyển đổi giọng nói thành văn bản.

Refactored từ: ai_nhomB/stt_module.py
Thay đổi:
    - Chuyển từ global variable sang class WhisperSTT
    - Config-driven: model size, device, language đọc từ YAML
    - Thêm logging thay print()
"""

import whisper
import torch
from src.utils.logger import setup_logger


class WhisperSTT:
    """Class quản lý Whisper model cho Speech-to-Text."""

    def __init__(self, config: dict):
        """
        Khởi tạo Whisper model.

        Args:
            config: Dict config chứa stt.model_name, stt.device, stt.language
        """
        self.logger = setup_logger("STT", config)
        stt_config = config.get("stt", {})

        self.model_name = stt_config.get("model_name", "small")
        self.language = stt_config.get("language", "vi")

        # Xác định device
        device_setting = stt_config.get("device", "auto")
        if device_setting == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device_setting

        self.logger.info(f"Đang tải Whisper model '{self.model_name}' trên {self.device}...")
        self.model = whisper.load_model(self.model_name, device=self.device)
        self.logger.info("Whisper model đã sẵn sàng.")

    def transcribe(self, audio_path: str) -> str:
        """
        Chuyển đổi file âm thanh thành văn bản.

        Args:
            audio_path: Đường dẫn tới file audio (.wav, .mp3, ...)

        Returns:
            Văn bản đã nhận diện, hoặc chuỗi rỗng nếu lỗi.
        """
        if not audio_path:
            self.logger.warning("Không có file audio đầu vào.")
            return ""

        try:
            self.logger.info(f"Đang nhận diện giọng nói từ: {audio_path}")
            result = self.model.transcribe(audio_path, language=self.language)
            text = result["text"].strip()
            self.logger.info(f"Kết quả STT: '{text}'")
            return text
        except Exception as e:
            self.logger.error(f"Lỗi nhận diện giọng nói: {e}")
            return ""
