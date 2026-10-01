from app.ai.errors import AIProviderNotConfigured
from app.ai.openai_compatible import OpenAICompatibleProvider
from app.ai.provider import AIProvider
from app.config import settings


def get_ai_provider() -> AIProvider:
    provider = settings.ai_provider.strip().lower()
    if provider in {"", "none"}:
        raise AIProviderNotConfigured(
            "AI provider is not configured. Set AI_PROVIDER=openai_compatible "
            "and AI_API_KEY to extract requirements from a job description."
        )
    if provider in {"openai", "openai_compatible"}:
        return OpenAICompatibleProvider(
            api_key=settings.ai_api_key,
            base_url=settings.ai_base_url,
            model=settings.ai_model,
            timeout_seconds=settings.ai_timeout_seconds,
        )
    raise AIProviderNotConfigured(
        f"Unknown AI provider '{settings.ai_provider}'. "
        "Use AI_PROVIDER=openai_compatible or AI_PROVIDER=none."
    )
