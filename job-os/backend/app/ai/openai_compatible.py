import json
import urllib.error
import urllib.request

from app.ai.errors import AIProviderError


class OpenAICompatibleProvider:
    """Chat Completions client for OpenAI and compatible gateways."""

    def __init__(
        self,
        *,
        api_key: str | None,
        base_url: str,
        model: str,
        timeout_seconds: float,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def complete(self, *, system: str, user: str) -> str:
        payload = {
            "model": self.model,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json",
                **({"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}),
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise AIProviderError(
                f"AI provider returned HTTP {exc.code}: {detail[:300]}"
            ) from exc
        except urllib.error.URLError as exc:
            raise AIProviderError("Could not reach the AI provider.") from exc
        except json.JSONDecodeError as exc:
            raise AIProviderError("AI provider returned a non-JSON response.") from exc

        try:
            content = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AIProviderError("AI provider response was missing message content.") from exc
        if not isinstance(content, str) or not content.strip():
            raise AIProviderError("AI provider returned an empty message.")
        return content
