from app.core.config import settings
from app.models.chat import ChatMessage

CHARS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // CHARS_PER_TOKEN)


def trim_history(
    messages: list[ChatMessage], budget: int | None = None,
) -> list[ChatMessage]:
    if not messages:
        return messages

    token_budget = budget if budget is not None else settings.max_prompt_tokens
    total = sum(estimate_tokens(m.content) for m in messages)
    if total <= token_budget:
        return messages

    trimmed = list(messages)
    while trimmed and total > token_budget:
        for i, m in enumerate(trimmed):
            if m.role != "system":
                total -= estimate_tokens(m.content)
                trimmed.pop(i)
                break
    return trimmed

