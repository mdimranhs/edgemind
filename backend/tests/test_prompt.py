import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.models.chat import ChatMessage
from app.services.prompt import SYSTEM_POLICY, load_system_identity, prompt_builder


class PromptTests(unittest.TestCase):
    def test_prompt_includes_identity_and_policy(self) -> None:
        prompt = prompt_builder.build([ChatMessage(role="user", content="Hello")])

        self.assertGreaterEqual(len(prompt), 3)
        self.assertEqual(prompt[0].role, "system")
        self.assertEqual(prompt[1].role, "system")
        self.assertIn("EdgeMind", prompt[0].content)
        self.assertIn("Operational policy", prompt[1].content)
        self.assertIn("Base personal answers on the knowledge base", prompt[1].content)
        self.assertIn("Who EdgeMind Is", prompt[0].content)
        self.assertIn("confidence and uncertainty", prompt[0].content.lower())


if __name__ == "__main__":
    unittest.main()