from gtts import gTTS
import os

def text_to_speech(text, output_filename="focusbuddy_reply.mp3"):
    """Biến văn bản thành giọng nói tiếng Việt"""
    try:
        # 1. Khởi tạo đối tượng gTTS với ngôn ngữ tiếng Việt (vi)
        tts = gTTS(text=text, lang='vi')
        
        # 2. Lưu thành file âm thanh
        tts.save(output_filename)
        
        # Trả về đường dẫn file để các module khác sử dụng
        return os.path.abspath(output_filename)
    except Exception as e:
        print(f"Lỗi khi tạo giọng nói: {str(e)}")
        return None

# --- TEST NHANH ---
if __name__ == "__main__":
    text_test = "Chào Như, mình là FocusBuddy đây. Chúc bạn học tập thật tốt nhé!"
    path = text_to_speech(text_test)
    if path:
        print(f"Thành công! File âm thanh đã được lưu tại: {path}")