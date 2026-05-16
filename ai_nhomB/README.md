# 🤖 FocusBuddy - AI Study Assistant

FocusBuddy là trợ lý học tập AI thông minh, giúp sinh viên tập trung và học tập hiệu quả hơn.

## ✨ Tính năng

- **Speech-to-Text (STT)**: Nhận diện giọng nói tiếng Việt bằng Whisper
- **AI Chatbot**: Trả lời câu hỏi học tập thông minh bằng Gemini
- **Text-to-Speech (TTS)**: Chuyển câu trả lời thành giọng nói bằng gTTS
- **Pipeline tự động**: STT → Chatbot → TTS trong một lệnh duy nhất

## 📁 Cấu trúc project

```
FocusBuddy/
├── configs/              # Cấu hình theo version
│   ├── v1.yaml
│   └── v2.yaml
├── data/
│   ├── raw/              # Dữ liệu thô (audio input)
│   └── processed/        # Dữ liệu đã xử lý
├── models/
│   ├── v1/               # Model artifacts version 1
│   ├── v2/               # Model artifacts version 2
│   └── whisper/          # Whisper model cache
├── src/
│   ├── inference/        # Pipeline dự đoán
│   │   └── predict.py    # ChatbotInference + run_pipeline()
│   ├── stt/              # Speech-to-Text
│   │   └── whisper_module.py
│   ├── tts/              # Text-to-Speech
│   │   └── tts_module.py
│   ├── train/            # Training (skeleton)
│   │   └── train.py
│   └── utils/            # Utilities
│       ├── config.py     # Config loader
│       └── logger.py     # Logging module
├── outputs/
│   ├── logs/             # Log files theo version
│   └── metrics/          # Training metrics
├── notebooks/            # Jupyter notebooks
├── main.py               # Entry point
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 Cài đặt

### 1. Clone project

```bash
git clone <repo_url>
cd FocusBuddy
```

### 2. Tạo môi trường ảo

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình API key

```bash
# Copy file mẫu
cp .env.example .env

# Mở file .env và thêm API key
# GOOGLE_API_KEY=your_actual_api_key
```

## 📖 Hướng dẫn sử dụng

### Chạy Inference (Dự đoán)

#### Mode giọng nói (Audio → AI → Giọng nói)

```bash
python main.py --version v1 --audio data/raw/question.wav
```

#### Mode text (Text → AI → Giọng nói)

```bash
python main.py --version v1 --text "Giúp mình lập kế hoạch học tập cho kỳ thi"
```

#### Dùng version khác

```bash
python main.py --version v2 --text "Làm sao để tập trung hơn?"
```

### Chạy Training (Skeleton)

```bash
python main.py --mode train --version v1
```

### Xem help

```bash
python main.py --help
```

## ⚙️ Quản lý version

Mỗi version có file config riêng trong `configs/`:

| File | Mô tả |
|------|--------|
| `configs/v1.yaml` | Config mặc định (Whisper small + Gemini Flash) |
| `configs/v2.yaml` | Template cho version 2 (Whisper medium) |

Để tạo version mới:
1. Copy `configs/v1.yaml` → `configs/v3.yaml`
2. Chỉnh sửa các tham số
3. Chạy: `python main.py --version v3 --text "test"`

## 📊 Outputs

- **Logs**: `outputs/logs/<version>/YYYY-MM-DD.log`
- **Audio**: `outputs/audio/focusbuddy_reply.mp3`
- **Metrics**: `outputs/metrics/<version>/training_metrics.json`

## 🛠️ Tech Stack

| Thành phần | Công nghệ |
|-----------|-----------|
| STT | OpenAI Whisper |
| Chatbot | Google Gemini API |
| TTS | gTTS |
| Config | YAML |
| Logging | Python logging |

## 👥 Nhóm phát triển

Nhóm B - FocusBuddy AI Study Assistant
