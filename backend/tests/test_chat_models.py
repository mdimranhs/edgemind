import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.models.chat import ChatMessage, ChatRequest


class ChatModelTests(unittest.TestCase):
    def test_chat_message_sanitizes_ui_artifacts(self) -> None:
        message = ChatMessage(
            role="user",
            content="Md IMran Hossain can I hire hime [object Object] Dismiss",
        )

        self.assertEqual(message.content, "Md IMran Hossain can I hire hime")

    def test_chat_request_uses_independent_message_lists(self) -> None:
        first = ChatRequest()
        second = ChatRequest()

        first.messages.append(ChatMessage(role="user", content="Hello"))

        self.assertEqual(len(first.messages), 1)
        self.assertEqual(len(second.messages), 0)


if __name__ == "__main__":
    unittest.main()
