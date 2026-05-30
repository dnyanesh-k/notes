"""
LiteLLM gateway — single entry point for all LLM calls.

The agent and eval critic never talk to Groq/OpenAI directly.
Swap providers by changing LLM_MODEL — no code changes needed.

Examples:
    LLM_MODEL=groq/llama-3.3-70b-versatile   (default, needs GROQ_API_KEY)
    LLM_MODEL=openai/gpt-4o-mini             (needs OPENAI_API_KEY)

Optional fallback if primary fails:
    LLM_FALLBACK_MODEL=groq/llama-3.1-8b-instant
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from litellm import completion

_ROOT = Path(__file__).parent
load_dotenv(_ROOT / ".env")  # loads .env from mini-aria root; shell env vars still win

DEFAULT_AGENT_MODEL = "groq/llama-3.3-70b-versatile"
DEFAULT_CRITIC_MODEL = "groq/llama-3.3-70b-versatile"

# LiteLLM logs are noisy in a CLI demo — keep output clean
os.environ.setdefault("LITELLM_LOG", "ERROR")


def get_agent_model() -> str:
    return os.environ.get("LLM_MODEL", DEFAULT_AGENT_MODEL).strip()


def get_critic_model() -> str:
    return os.environ.get("LLM_CRITIC_MODEL", get_agent_model()).strip()


def get_fallback_model() -> str | None:
    fb = os.environ.get("LLM_FALLBACK_MODEL", "").strip()
    return fb or None


def _provider_for_model(model: str) -> str:
    return model.split("/", 1)[0] if "/" in model else "openai"


def _required_env_key(model: str) -> str:
    provider = _provider_for_model(model)
    return {
        "groq": "GROQ_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
    }.get(provider, f"{provider.upper()}_API_KEY")


def check_llm_env() -> None:
    """Exit with a helpful message if the API key for the chosen model is missing."""
    model = get_agent_model()
    key_name = _required_env_key(model)
    if not os.environ.get(key_name, "").strip():
        print(f"\nError: {key_name} is not set (required for LLM_MODEL={model}).")
        print("  1. Copy .env.example to .env")
        print(f"  2. Set {key_name} in .env")
        print("  Groq (free):  https://console.groq.com")
        print("  Or switch:    LLM_MODEL=openai/gpt-4o-mini  (+ OPENAI_API_KEY in .env)")
        sys.exit(1)


def chat_completion(
    *,
    model: str | None = None,
    messages: list[dict],
    tools: list[dict] | None = None,
    tool_choice: str | None = "auto",
    max_tokens: int = 2048,
    temperature: float = 0.1,
):
    """
    Route a chat completion through LiteLLM.
    Returns an OpenAI-compatible response (choices, usage, tool_calls).
    """
    model = model or get_agent_model()
    fallback = get_fallback_model()

    kwargs: dict = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if tools is not None:
        kwargs["tools"] = tools
        if tool_choice is not None:
            kwargs["tool_choice"] = tool_choice
    if fallback and fallback != model:
        kwargs["fallbacks"] = [fallback]

    return completion(**kwargs)
