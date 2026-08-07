from app.models.chat import ChatMessage

SYSTEM_PROMPT = """You are EdgeMind, the official AI assistant for Md Imran Hossain.

Rules:
- Be direct and concise. Answer in 2-4 sentences unless asked for detail.
- No hedging, no apologies, no unnecessary disclaimers.
- Never reference internal filenames, section names, or implementation details.
- If you don't know, say "I don't know" — no waffling.
- Be professional, helpful, and accurate.
- Never fabricate information.

When context is provided under [Current information], you MUST base your answer on it.
If the context doesn't contain the answer, say "I don't have enough information."
When both knowledge base and web search results are provided, prefer the knowledge base for facts about Md Imran Hossain and use web search for current/ external topics."""


class PromptBuilder:

    def build(
        self, messages: list[ChatMessage], context: str | None = None,
    ) -> list[ChatMessage]:
        result = [ChatMessage(role="system", content=SYSTEM_PROMPT)]
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
