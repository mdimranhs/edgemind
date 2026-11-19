from typing import Literal

from pydantic import BaseModel, Field, field_validator
from app.core.config import settings


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

    @field_validator("content", mode="before")
    @classmethod
    def _clean_content(cls, value: object) -> str:
        if not isinstance(value, str):
            raise ValueError("Message content must be a string.")
        return value.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "")


class ChatRequest(BaseModel):
    session_id: str = Field(default="default", max_length=128)
    messages: list[ChatMessage] = Field(min_length=1)
    stream: bool = False

    @field_validator("messages")
    @classmethod
    def _validate_client_messages(cls, messages: list[ChatMessage]) -> list[ChatMessage]:
        if len(messages) > settings.max_history_messages:
            raise ValueError(
                f"Too many messages. Maximum allowed is {settings.max_history_messages}."
            )
        for idx, m in enumerate(messages):
            if m.role == "system":
                raise ValueError(
                    f"Message at index {idx} has role 'system'. Client-supplied system messages are not permitted."
                )
            if len(m.content) > settings.max_message_chars:
                raise ValueError(
                    f"Message at index {idx} exceeds maximum allowed length of {settings.max_message_chars} characters."
                )
        if messages[-1].role != "user":
            raise ValueError("The last message must be from the user.")
        return messages

