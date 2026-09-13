from pathlib import Path

from app.models.chat import ChatMessage

SYSTEM_IDENTITY_PATH = (
    Path(__file__).resolve().parent.parent.parent / "knowledge" / "system_identity.md"
)

SYSTEM_POLICY = """Operational policy:
- Base personal answers on the knowledge base and conversation context.
- Prefer documented preferences over generic recommendations when they conflict.
- If the answer is not supported by the available context, say so plainly.
- Keep answers concise unless the user asks for more detail.
- Do not reveal internal filenames or implementation details unless explicitly asked.
- Do not answer questions about people, events, or topics unrelated to Md Imran Hossain or EdgeMind. If asked, say the topic is outside your scope.
"""


def load_system_identity() -> str:
    try:
        return SYSTEM_IDENTITY_PATH.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return (
            "You are EdgeMind, the personal AI assistant for Md Imran Hossain. "
            "Be direct, concise, factual, and grounded. If you do not know, say so. "
            "Prefer the knowledge base when it is available, and do not fabricate facts."
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
            if messages:
                last = messages[-1]
                result.extend(messages[:-1])
                result.append(
                    ChatMessage(
                        role=last.role,
                        content=f"[No relevant information found in the knowledge base.]\n\nAnswer only if the question is about Md Imran Hossain or EdgeMind. If it is about a different person, place, event, or topic, reply: \"That topic is outside my scope. I can only answer questions about Md Imran Hossain and EdgeMind.\"\n\n{last.content}",
                    )
                )
            else:
                result.extend(messages)
        return result


prompt_builder = PromptBuilder()
