"""Khai báo schema trả về cho API Version 1."""

from __future__ import annotations

from pydantic import BaseModel, Field


class VoiceProcessResponse(BaseModel):
    """Thông tin phản hồi sau khi server xử lý xong một request audio."""

    request_id: str = Field(..., description="Mã định danh duy nhất của request")
    transcript: str = Field(..., description="Nội dung văn bản được nhận diện từ audio")
    reply_text: str = Field(..., description="Nội dung phản hồi dạng văn bản từ chatbot")
    response_file: str = Field(..., description="Tên file audio phản hồi trong runtime")
    latency_ms: float = Field(..., description="Tổng thời gian xử lý request (milliseconds)")
