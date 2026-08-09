from litellm import completion


class AuthError(Exception):
    """Raised when the provider rejects the API Key."""


class APIError(Exception):
    """Raised when an LLM API request fails."""


PROVIDER_MODELS = {
    "openai": "gpt-4o-mini",
    "gemini": "gemini/gemini-2.5-flash",
}


def call_llm(provider: str, model: str, query: str, api_key: str) -> dict:

    if provider not in PROVIDER_MODELS:
        raise APIError(f"Unsupported provider: {provider}")

    try:
        response = completion(
            model=model, messages=[{"role": "user", "content": query}], api_key=api_key
        )

    except Exception as exc:
        error_name = type(exc).__name__.lower()

        if "auth" in error_name or "authentication" in error_name:
            raise AuthError(str(exc)) from exc

        raise APIError(str(exc)) from exc

    content = response.choices[0].message.content

    usage = getattr(response, "usage", None)
    tokens_used = getattr(usage, "total_tokens", None)

    return {
        "provider": provider,
        "model": model,
        "query": query,
        "response": content,
        "tokens_used": tokens_used,
    }
