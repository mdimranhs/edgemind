from pathlib import Path

from app.models.chat import ChatMessage

SYSTEM_IDENTITY_PATH = (
    Path(__file__).resolve().parent.parent.parent / "knowledge" / "system_identity.md"
)

SYSTEM_POLICY = """Operational policy:
- Be a helpful, accurate, and concise assistant for any question.
- When the knowledge base has relevant information about Md Imran Hossain or EdgeMind, prefer it over generic answers.
- If you don't know something, say so plainly rather than guessing.
- Keep answers concise unless the user asks for more detail.
- Do not reveal internal filenames or implementation details unless explicitly asked.
"""


def load_system_identity() -> str:
    try:
        return SYSTEM_IDENTITY_PATH.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return (
            "You are EdgeMind, a helpful AI assistant. "
            "Be direct, concise, factual, and grounded. If you do not know, say so. "
            "Use the knowledge base when available for questions about Md Imran Hossain, "
            "and use your general knowledge for all other topics."
        )


class PromptBuilder:

    def build(
        self, messages: list[ChatMessage], context: str | None = None,
    ) -> list[ChatMessage]:
        result = [
            ChatMessage(role="system", content=load_system_identity()),
            ChatMessage(role="system", content=SYSTEM_POLICY),
        ]
        if context and messages:
            last = messages[-1]
            result.extend(messages[:-1])
            result.append(
                ChatMessage(
                    role=last.role,
                    content=f"[Current information: {context}]\n\nNow, using the above as your source: {last.content}",
                )
            )
        else:
            result.extend(messages)
        return result


prompt_builder = PromptBuilder()
