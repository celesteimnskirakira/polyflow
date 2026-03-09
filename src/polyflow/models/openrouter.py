"""
OpenRouter adapter — routes all models through https://openrouter.ai
using the OpenAI-compatible API, so one key covers Claude, Gemini, GPT-4.
"""
from openai import AsyncOpenAI
from .base import ModelAdapter

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Maps Polyflow model aliases to OpenRouter model IDs.
#
# Stable aliases always point to the latest recommended version of each
# family — existing workflows never break when models are updated here.
#
# Users can also use any full OpenRouter model ID directly in YAML:
#   model: openai/gpt-5.4
#   model: anthropic/claude-opus-4-6
#   model: google/gemini-3.1-pro
#
# Premium aliases (higher cost — see openrouter.ai/models for pricing):
#   claude-opus  → Claude Opus 4.6   (highest capability)
#   gpt-5        → GPT-5.4           (~$20/1M output tokens)
#   gemini-pro   → Gemini 3.1 Pro    (1M context window)
_MODEL_MAP: dict[str, str] = {
    # ── Stable aliases (recommended defaults) ────────────────────────────
    "claude":      "anthropic/claude-sonnet-4-6",
    "gemini":      "google/gemini-2.0-flash-001",
    "gpt-4":       "openai/gpt-4o",
    "codex":       "openai/gpt-4o",
    # ── Premium aliases (opt-in top tier) ────────────────────────────────
    "claude-opus": "anthropic/claude-opus-4-6",
    "gpt-5":       "openai/gpt-5.4",
    "gemini-pro":  "google/gemini-3.1-pro",
}


class OpenRouterAdapter(ModelAdapter):
    def __init__(self, model_key: str):
        super().__init__(model_key)
        self._openrouter_model = _MODEL_MAP.get(model_key, model_key)

    async def _call_api(self, prompt: str, api_key: str, timeout: int = 60) -> str:
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=OPENROUTER_BASE_URL,
            timeout=float(timeout),
        )
        response = await client.chat.completions.create(
            model=self._openrouter_model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
