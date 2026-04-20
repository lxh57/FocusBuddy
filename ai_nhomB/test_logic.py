from stt_module import speech_to_text
from chatbot_module import get_chatbot_response
from tts_module import text_to_speech  
import time

def run_ai_pipeline(audio_file):
    print(f"\n--- BẮT ĐẦU XỬ LÝ PIPELINE TOÀN DIỆN ---")
    total_start_time = time.time()
    
    # 1. Chạy Module STT (Speech-to-Text)
    print(f"1. Đang lắng nghe file: {audio_file}...")
    start_time = time.time()
    text_input = speech_to_text(audio_file)
    stt_time = time.time() - start_time
    
    print(f"   -> Văn bản nhận diện được: '{text_input}'")
    print(f"   (Thời gian xử lý STT: {stt_time:.2f}s)")
    
    if not text_input:
        print("Lỗi: Không nhận diện được âm thanh.")
        return

    # 2. Chạy Module Chatbot (Gemini)
    print(f"2. Đang gửi văn bản sang bộ não Gemini...")
    start_time = time.time()
    ai_reply = get_chatbot_response(text_input)
    chatbot_time = time.time() - start_time
    
    print(f"   -> FocusBuddy trả lời: {ai_reply}")
    print(f"   (Thời gian suy nghĩ: {chatbot_time:.2f}s)")

    # 3. Chạy Module TTS (Text-to-Speech) - MỚI BỔ SUNG
    print(f"3. Đang chuyển câu trả lời thành giọng nói...")
    start_time = time.time()
    # Bạn có thể đổi tên file output tùy ý ở đây
    audio_output_path = text_to_speech(ai_reply, output_filename="focusbuddy_reply.mp3")
    tts_time = time.time() - start_time

    if audio_output_path:
        print(f"   -> Đã tạo file phản hồi tại: {audio_output_path}")
        print(f"   (Thời gian xử lý TTS: {tts_time:.2f}s)")
    
    total_end_time = time.time() - total_start_time
    print(f"\n--- HOÀN TẤT TOÀN BỘ TRONG {total_end_time:.2f}s ---")
    print(f"--- BẠN CÓ THỂ MỞ FILE ĐỂ NGHE ---")

if __name__ == "__main__":
    # Đảm bảo file này tồn tại trong thư mục ai_nhomB
    file_test = "test_co_ban.wav" 
    run_ai_pipeline(file_test)