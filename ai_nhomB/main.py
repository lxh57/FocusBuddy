"""
FocusBuddy - AI Study Assistant
================================
Entry point chính cho toàn bộ ứng dụng.

Sử dụng:
    # Mode giọng nói (STT → Chatbot → TTS)
    python main.py --version v1 --audio path/to/audio.wav

    # Mode text (Chatbot → TTS)
    python main.py --version v1 --text "Giúp mình lập kế hoạch học tập"

    # Chạy training (skeleton)
    python main.py --mode train --version v1
"""

import argparse
import sys

from src.utils.config import load_config
from src.utils.logger import setup_logger
from src.inference.predict import run_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="FocusBuddy - AI Study Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:
  python main.py --version v1 --audio data/raw/question.wav
  python main.py --version v1 --text "Làm sao để tập trung học bài?"
  python main.py --mode train --version v1
        """
    )

    parser.add_argument(
        "--version", "-v",
        type=str,
        default="v1",
        help="Version config (v1, v2, ...). Mặc định: v1"
    )
    parser.add_argument(
        "--mode", "-m",
        type=str,
        choices=["inference", "train"],
        default="inference",
        help="Chế độ: inference (mặc định) hoặc train"
    )
    parser.add_argument(
        "--audio", "-a",
        type=str,
        default=None,
        help="Đường dẫn file audio cho mode giọng nói"
    )
    parser.add_argument(
        "--text", "-t",
        type=str,
        default=None,
        help="Văn bản trực tiếp (bỏ qua STT)"
    )

    args = parser.parse_args()

    # Load config theo version
    try:
        config = load_config(args.version)
    except FileNotFoundError as e:
        print(f"Lỗi: {e}")
        sys.exit(1)

    logger = setup_logger("Main", config)
    logger.info(f"FocusBuddy khởi động - Version: {args.version}, Mode: {args.mode}")

    # --- Mode Training ---
    if args.mode == "train":
        from src.train.train import train
        train(args.version)
        return

    # --- Mode Inference ---
    if not args.audio and not args.text:
        logger.error("Cần cung cấp --audio hoặc --text cho mode inference.")
        parser.print_help()
        sys.exit(1)

    result = run_pipeline(
        config=config,
        audio_path=args.audio,
        text_input=args.text
    )

    # Hiển thị kết quả
    print("\n" + "=" * 60)
    print("KẾT QUẢ FOCUSBUDDY")
    print("=" * 60)
    print(f"Đầu vào: {result['input_text']}")
    print(f"\nFocusBuddy: {result['ai_reply']}")
    if result["audio_output"]:
        print(f"\nFile audio: {result['audio_output']}")
    print(f"\nThời gian xử lý: {result['timing'].get('total', 0)}s")
    print("=" * 60)


if __name__ == "__main__":
    main()
