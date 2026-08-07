import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator


_UI_ARTIFACTS = (
    "[object Object]",
    "Dismiss",
)


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

    @field_validator("content", mode="before")
    @classmethod
    def _clean_content(cls, value: object) -> str:
        text = "" if value is None else str(value)
        for artifact in _UI_ARTIFACTS:
            text = text.replace(artifact, " ")
        text = re.sub(r"\s+", " ", text).strip()
        return text


class ChatRequest(BaseModel):
    session_id: str = "default"
    messages: list[ChatMessage] = Field(default_factory=list)
    stream: bool = False
