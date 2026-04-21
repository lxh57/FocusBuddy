# Architecture - NHOM_A Version 1

## 1. Muc tieu
Version 1 xu ly theo luong ghi am mot lan:
- Nguoi dung bam ghi am.
- Nguoi dung noi.
- Nguoi dung tat ghi am.
- Server nhan du lieu audio, xu ly qua STT -> Chatbot -> TTS.
- Server tra ve file audio phan hoi de phat lai.

## 2. Cau truc thu muc
- NHOM_A/src/main.py: Diem vao FastAPI, CORS, startup warmup.
- NHOM_A/src/logger.py: Logger dung chung toan he thong.
- NHOM_A/src/version_1/config.py: Duong dan va cau hinh runtime.
- NHOM_A/src/version_1/communication/router.py: API HTTP + WebSocket.
- NHOM_A/src/version_1/processing/pipeline.py: Dieu phoi STT -> Chatbot -> TTS.
- NHOM_A/src/version_1/processing/storage.py: Luu file request/response, base64.
- NHOM_A/src/version_1/integration/nhom_b_adapter.py: Goi module NHOM_B.
- NHOM_A/src/version_1/schemas.py: Response model cho API.
- NHOM_A/runtime/request_audio: Luu audio request.
- NHOM_A/runtime/response_audio: Luu audio response.

## 3. Thiet ke 3 lop
### Communication Layer
- HTTP endpoint nhan file audio va tra metadata.
- WebSocket endpoint nhan stream chunk audio va tra ket qua ngay khi client gui stop.
- Co co che ping/pong de client kiem tra ket noi.

### Processing Layer
- Chuan hoa du lieu dau vao.
- Luu request thanh file de de trace/log.
- Thuc thi pipeline bat dong bo de khong chan event loop.
- Bat loi tung buoc de tranh lam sap server.

### Integration Layer
- Import dong module cua NHOM_B (stt_module, chatbot_module, tts_module).
- Cach ly loi tich hop qua exception rieng NhomBIntegrationError.
- Warmup module o startup de giam do tre request dau tien.

## 4. Dinh huong toi uu toc do
- Preload module AI luc startup.
- Chay STT/Chatbot/TTS trong asyncio.to_thread.
- Giam I/O du thua: WebSocket tra ve base64 truc tiep sau khi co file response.
- Log latency_ms de theo doi hieu nang thuc te.

## 5. Luu y van hanh
- Neu chua co GOOGLE_API_KEY trong .env, chatbot co the loi.
- openai-whisper va torch co dung luong lon, can cai dat truoc khi chay.
- Runtime folder co the duoc clean dinh ky de tranh day o dia.
