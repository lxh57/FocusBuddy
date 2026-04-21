# API va Workflow - Version 1

## 1. Health Check
- Method: GET
- URL: /
- Ket qua mau:
  {
    "status": "success",
    "message": "Server FastAPI Nhom A dang chay on dinh tren laptop"
  }

## 2. HTTP Audio Processing
### 2.1 Xu ly audio
- Method: POST
- URL: /api/v1/voice/process
- Content-Type: multipart/form-data
- Form field:
  - file: audio file (webm/wav/mp3/...)

Response mau:
{
  "request_id": "uuid",
  "transcript": "Noi dung nhan dien",
  "reply_text": "Noi dung chatbot tra loi",
  "response_file": "uuid.mp3",
  "latency_ms": 2345.67
}

### 2.2 Tai file audio phan hoi
- Method: GET
- URL: /api/v1/voice/response/{response_file}
- Ket qua: file audio (thuong la mp3)

## 3. WebSocket Audio Processing
- URL: /api/v1/ws/voice

### 3.1 Control message tu client
1. start
   {"type":"start","format":"webm"}
2. binary audio chunks
   - Gui du lieu bytes trong luc ghi am
3. stop
   {"type":"stop"}

### 3.2 Message server tra ve
- ack start:
  {"type":"ack","message":"start_ok"}

- result khi xu ly xong:
  {
    "type":"result",
    "request_id":"uuid",
    "transcript":"...",
    "reply_text":"...",
    "latency_ms":1234.56,
    "response_file":"uuid.mp3",
    "audio_mime_type":"audio/mpeg",
    "audio_base64":"..."
  }

- error:
  {
    "type":"error",
    "message":"..."
  }

## 4. Workflow tong quan
1. Client bat dau ghi am va gui start.
2. Client gui cac chunk audio bytes qua WebSocket.
3. Client nhấn stop.
4. Server gop chunk -> tao request audio file.
5. Pipeline xu ly STT -> Chatbot -> TTS.
6. Server gui ket qua text + audio_base64 de client phat ngay.
7. File response dong thoi duoc luu trong runtime/response_audio de debug.
