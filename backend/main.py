import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

# ==========================================
# 1. CẤU HÌNH LOGGING
# ==========================================
logging.basicConfig(
    level=logging.INFO, # Hiển thị từ mức INFO trở lên (INFO, WARNING, ERROR)
    format="%(asctime)s | %(levelname)-8s | %(message)s", # Định dạng: Thời gian | Mức độ | Nội dung
    datefmt="%Y-%m-%d %H:%M:%S"
)
# Tạo một "cuốn sổ" log riêng cho dự án
logger = logging.getLogger("FocusBuddy_Server")

# ==========================================
# 2. KHỞI TẠO APP
# ==========================================
app = FastAPI(title="Server Nhóm A", description="API xử lý giọng nói")

@app.get("/")
async def root():
    logger.info("Có client vừa gọi API Health Check (/)")
    return {"message": "Server FastAPI của Nhóm A đang hoạt động tốt!"}

# ==========================================
# 3. WEBSOCKET VỚI TRY...EXCEPT...FINALLY
# ==========================================
@app.websocket("/ws/audio")
async def websocket_audio_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Mạng lưới FocusBuddy: Một Client vừa kết nối thành công!")
    
    try:
        while True:
            # Chờ nhận luồng dữ liệu âm thanh từ client
            audio_data = await websocket.receive_bytes()
            logger.info(f"Đã nhận luồng âm thanh - Kích thước: {len(audio_data)} bytes")
            
            # Gửi trả lại đúng đoạn âm thanh (Echo Test tuần 1)
            await websocket.send_bytes(audio_data)
            logger.info("Đã phản hồi dữ liệu âm thanh về Client thành công.")
            
    except WebSocketDisconnect:
        # Bắt lỗi đặc thù khi Client chủ động ngắt mạng (Đây là điều bình thường, chỉ cần cảnh báo)
        logger.warning("Client đã ngắt kết nối WebSocket.")
        
    except Exception as e:
        # Bắt TẤT CẢ các lỗi bất ngờ khác (VD: lỗi phần cứng, dữ liệu rác, lỗi RAM...)
        logger.error(f"Có lỗi bất ngờ xảy ra trong quá trình truyền/nhận: {str(e)}")
        
    finally:
        # Khối này luôn chạy dù vòng lặp try thành công hay bị văng lỗi except
        logger.info("Đóng phiên làm việc của Client hiện tại.\n" + "-"*50)