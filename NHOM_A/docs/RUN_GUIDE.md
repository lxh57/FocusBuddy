# Huong dan chay NHOM_A Version 1

## 1. Cai dependencies
Tai thu muc goc FocusBuddy:
- pip install -r requirements.txt

## 2. Cau hinh bien moi truong
Can co file .env o muc goc FocusBuddy (hoac noi ma NHOM_B chatbot doc duoc):
- GOOGLE_API_KEY=your_key_here

## 3. Chay server
Di chuyen vao NHOM_A va chay:
- uvicorn src.main:app --reload

## 4. Test nhanh
### 4.1 Health check
- GET http://127.0.0.1:8000/

### 4.2 Test HTTP upload
- POST http://127.0.0.1:8000/api/v1/voice/process
- form-data key: file
- Lay response_file tu JSON va goi:
  GET http://127.0.0.1:8000/api/v1/voice/response/{response_file}

### 4.3 Test WebSocket
- Ket noi ws://127.0.0.1:8000/api/v1/ws/voice
- Gui {"type":"start","format":"webm"}
- Gui bytes audio chunk
- Gui {"type":"stop"}
- Nhan message result va phat audio_base64 tren client.

## 5. Giai thich toi uu da ap dung
- Warmup NHOM_B modules o startup.
- Chay STT/Chatbot/TTS trong thread rieng de giu server responsive.
- Tach rieng request_id cho moi phien xu ly de trace log nhanh.
- Co endpoint HTTP song song WebSocket de debug va fallback khi can.
