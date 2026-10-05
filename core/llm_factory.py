# core/llm_factory.py
import os
from langchain_ollama import ChatOllama

# Default configuration
DEFAULT_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "300"))

# Model registry: map friendly names to actual Ollama model tags
MODEL_REGISTRY = {
        "deepseek": os.getenv("DEEPSEEK_MODEL", "deepseek-coder:latest"),
    "qwen": os.getenv("QWEN_MODEL", "qwen2.5:7b-instruct"),
}


def get_llm(
    model_key: str,
    temperature: float = 0.2,
    base_url: str | None = None,
    timeout: int | None = None,
) -> ChatOllama:
    """
    Factory function to create a configured LLM instance.

    Args:
        model_key: Friendly name from MODEL_REGISTRY ("deepseek" or "dolphin")
        temperature: Creativity level (0.0 = deterministic, 1.0 = creative)
        base_url: Override Ollama server URL if needed
        timeout: Request timeout in seconds

    Returns:
        Configured ChatOllama instance

    Raises:
        ValueError: If model_key is not in MODEL_REGISTRY
    """
    if model_key not in MODEL_REGISTRY:
        raise ValueError(
            f"Unknown model key: '{model_key}'. "
            f"Available: {list(MODEL_REGISTRY.keys())}"
        )

    return ChatOllama(
        model=MODEL_REGISTRY[model_key],
        base_url=base_url or DEFAULT_BASE_URL,
        temperature=temperature,
        timeout=timeout or DEFAULT_TIMEOUT,
    )


def get_deepseek() -> ChatOllama:
    """Convenience wrapper for DeepSeek Coder."""
    return get_llm("deepseek", temperature=0.2)


def get_qwen() -> ChatOllama:
    """Convenience wrapper for Qwen."""
    return get_llm("qwen", temperature=0.3)
