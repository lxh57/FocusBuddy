import asyncio
import websockets
import os

# Tên file bạn muốn gửi đi (phải nằm cùng thư mục)
FILE_TO_SEND = "test_audio.wav"
# Tên file sẽ được lưu sau khi server trả về
FILE_TO_SAVE = "received_audio.wav"

async def test_websocket_audio():
    uri = "ws://localhost:8000/ws/audio"
    
    # Kết nối tới server
    async with websockets.connect(uri, max_size=None) as websocket:
        print(f"Đã kết nối tới Server: {uri}")
        
        # Kiểm tra xem file có tồn tại không
        if not os.path.exists(FILE_TO_SEND):
            print(f"Lỗi: Không tìm thấy file '{FILE_TO_SEND}'!")
            return
            
        # 1. Đọc file âm thanh dưới dạng nhị phân (rb)
        with open(FILE_TO_SEND, "rb") as f:
            audio_data = f.read()
            
        # 2. Gửi dữ liệu âm thanh (bytes) lên server
        print(f"Đang gửi file '{FILE_TO_SEND}' ({len(audio_data)} bytes)...")
        await websocket.send(audio_data)
        
        # 3. Chờ nhận dữ liệu (bytes) trả về từ server
        print("Đang chờ phản hồi từ server...")
        response_data = await websocket.recv()
        
        # 4. Lưu dữ liệu trả về thành một file mới
        with open(FILE_TO_SAVE, "wb") as f:
            f.write(response_data)
            
        print(f"Hoàn tất! Đã lưu file phản hồi thành '{FILE_TO_SAVE}' ({len(response_data)} bytes).")
        
        # So sánh kích thước để xác nhận Echo hoạt động đúng
        if len(audio_data) == len(response_data):
            print("=> TEST THÀNH CÔNG: Kích thước file gửi và nhận hoàn toàn khớp nhau!")
        else:
            print("=> TEST THẤT BẠI: Kích thước file không khớp.")

# Khởi chạy hàm bất đồng bộ
asyncio.run(test_websocket_audio())