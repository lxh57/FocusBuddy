import whisper
import torch

# Khởi tạo model một lần duy nhất để tiết kiệm RAM/GPU
device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("small", device=device) 

def speech_to_text(audio_path):
    """Hàm chuyển đổi âm thanh thành văn bản"""
    if not audio_path:
        return ""
    
    # Thực hiện nhận diện
    result = model.transcribe(audio_path, language="vi")
    return result["text"].strip()