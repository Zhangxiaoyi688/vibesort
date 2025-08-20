import json
import os
from typing import TypeVar

from typing_extensions import Literal
from pydantic import BaseModel

try:  # pragma: no cover - exercised indirectly
    import openai  # type: ignore
except Exception:  # pragma: no cover - openai is optional
    openai = None  # type: ignore[assignment]

try:  # pragma: no cover - exercised indirectly
    from volcenginesdkarkruntime import Ark  # type: ignore
except Exception:  # pragma: no cover - Ark is optional
    Ark = None  # type: ignore[assignment]


class VibesortResponse(BaseModel):
    sorted_array: list[int]


class VibesortRequest(BaseModel):
    array: list[int]
    order: Literal["asc", "desc"] = "asc"


def vibesort(array: list[int]) -> list[int]:
    """Sort ``array`` using GPT when available.

    Attempts to use OpenAI or DouBao (Ark) when the corresponding SDK and API
    key are configured. Falls back to Python's built-in ``sorted`` if no model
    is available or any error occurs while requesting the model. This makes the
    function usable in offline or testing environments where an API isn't
    configured.
    """

    request = VibesortRequest(array=array)

    has_openai = openai is not None and os.environ.get("OPENAI_API_KEY")
    has_ark = Ark is not None and os.environ.get("ARK_API_KEY")
    if not (has_openai or has_ark):
        return sorted(request.array)

    try:
        return structured_output(
            content=request.model_dump_json(),
            response_format=VibesortResponse,
        ).sorted_array
    except Exception:  # pragma: no cover - network failure
        return sorted(request.array)


T = TypeVar("T", bound=BaseModel)


def structured_output(
    content: str,
    response_format: type[T],
    model: str = "gpt-4.1-mini",
) -> T:
    """Return a parsed response using OpenAI or DouBao."""

    if openai is not None and os.environ.get("OPENAI_API_KEY"):
        api_key = os.environ["OPENAI_API_KEY"]
        client = openai.OpenAI(api_key=api_key)
        response = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [{"type": "text", "text": content}],
                }
            ],
            response_format=response_format,
        )
        return response.choices[0].message.parsed

    if Ark is not None and os.environ.get("ARK_API_KEY"):
        api_key = os.environ["ARK_API_KEY"]
        ark_model = os.environ.get("ARK_MODEL", model)
        client = Ark(
            base_url="https://ark-cn-beijing.bytedance.net/api/v3",
            api_key=api_key,
        )
        response = client.chat.completions.create(
            model=ark_model,
            messages=[
                {
                    "role": "user",
                    "content": [{"type": "text", "text": content}],
                }
            ],
        )
        data = json.loads(response.choices[0].message["content"][0]["text"])
        return response_format.model_validate(data)

    raise RuntimeError("An AI SDK is required for GPT sorting")
