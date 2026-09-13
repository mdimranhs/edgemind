import asyncio
from collections.abc import AsyncGenerator
from threading import Thread

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer

from app.interfaces.llm import BaseLLM
from app.models.chat import ChatMessage
from app.core.config import settings

GENERATION_KWARGS = dict(
    max_new_tokens=2048,
    temperature=0.7,
    top_p=0.9,
    do_sample=True,
)


class HuggingFaceLLMProvider(BaseLLM):

    def __init__(self) -> None:
        self.model_id = settings.hf_model
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = None
        self.model = None

    def load(self) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_id, use_fast=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto",
        )
        self.model.eval()

    async def warm(self) -> None:
        """Ensure the model weights and tokenizer are loaded."""
        self._ensure_loaded()

    def _ensure_loaded(self) -> None:
        if self.tokenizer is None or self.model is None:
            self.load()

    def _prepare_inputs(self, messages: list[ChatMessage]) -> dict:
        chat = [{"role": m.role, "content": m.content} for m in messages]
        prompt = self.tokenizer.apply_chat_template(
            chat, tokenize=False, add_generation_prompt=True
        )
        return self.tokenizer(prompt, return_tensors="pt").to(self.device)

    async def generate(self, messages: list[ChatMessage]) -> str:
        self._ensure_loaded()
        inputs = self._prepare_inputs(messages)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                **GENERATION_KWARGS,
            )

        decoded = self.tokenizer.decode(
            outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True
        )
        return decoded.strip()

    async def generate_stream(
        self, messages: list[ChatMessage],
    ) -> AsyncGenerator[str, None]:
        self._ensure_loaded()
        inputs = self._prepare_inputs(messages)

        streamer = TextIteratorStreamer(
            self.tokenizer, skip_prompt=True, skip_special_tokens=True,
        )
        gen_kwargs = dict(**inputs, **GENERATION_KWARGS, streamer=streamer)

        Thread(target=self.model.generate, kwargs=gen_kwargs).start()

        def _next_token() -> str | None:
            try:
                return next(streamer)
            except StopIteration:
                return None

        loop = asyncio.get_running_loop()
        while True:
            text = await loop.run_in_executor(None, _next_token)
            if text is None:
                break
            yield text
