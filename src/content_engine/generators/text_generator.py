"""Text generation via OpenRouter (OpenAI-compatible API)."""

from __future__ import annotations

import structlog
from openai import AsyncOpenAI

from src.config.settings import settings
from src.content_engine.prompts.post_prompts import PromptPair

log = structlog.get_logger()


class TextGenerator:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ):
        self.model = model or settings.openrouter_text_model
        self.client = AsyncOpenAI(
            api_key=api_key or settings.openrouter_api_key,
            base_url=base_url or settings.openrouter_base_url,
        )

    async def generate(
        self,
        prompt: PromptPair,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> tuple[str, dict]:
        """Generate text from a prompt pair.

        Returns:
            (generated_text, metadata) where metadata includes model, tokens, etc.
        """
        log.info("generating_text", model=self.model, system_len=len(prompt.system))

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompt.system},
                {"role": "user", "content": prompt.user},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        text = response.choices[0].message.content or ""
        metadata = {
            "model": self.model,
            "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
            "completion_tokens": response.usage.completion_tokens if response.usage else 0,
            "total_tokens": response.usage.total_tokens if response.usage else 0,
            "finish_reason": response.choices[0].finish_reason,
        }

        log.info(
            "text_generated",
            text_len=len(text),
            tokens=metadata.get("total_tokens"),
        )

        return text.strip(), metadata

    async def regenerate_with_feedback(
        self,
        original_prompt: PromptPair,
        original_text: str,
        feedback: str,
        temperature: float = 0.7,
    ) -> tuple[str, dict]:
        """Regenerate text incorporating admin feedback."""
        augmented_user = (
            f"{original_prompt.user}\n\n"
            f"---\n"
            f"Previous version (needs improvement):\n{original_text}\n\n"
            f"Feedback from editor:\n{feedback}\n\n"
            f"Please write an improved version addressing the feedback."
        )

        modified_prompt = PromptPair(
            system=original_prompt.system,
            user=augmented_user,
        )

        return await self.generate(modified_prompt, temperature=temperature)
