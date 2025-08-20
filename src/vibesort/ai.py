import os
from typing import TypeVar

from typing_extensions import Literal
from pydantic import BaseModel

try:  # pragma: no cover - exercised indirectly
    import openai  # type: ignore
except Exception:  # pragma: no cover - openai is optional
    openai = None  # type: ignore[assignment]


class VibesortResponse(BaseModel):
    sorted_array: list[int]


class VibesortRequest(BaseModel):
    array: list[int]
    order: Literal["asc", "desc"] = "asc"


def vibesort(array: list[int]) -> list[int]:
    """Sort ``array`` using GPT when available.

    Falls back to Python's built-in ``sorted`` when the OpenAI package or API
    key is missing, or if any error occurs while requesting the model. This
    makes the function usable in offline or testing environments where OpenAI
    isn't configured.
    """

    request = VibesortRequest(array=array)

    api_key = os.environ.get("OPENAI_API_KEY")
    if openai is None or api_key is None:
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
    if openai is None:
        raise RuntimeError("openai package is required for GPT sorting")

    api_key = os.environ["OPENAI_API_KEY"]
    client = openai.OpenAI(api_key=api_key)

    response = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": content}],
            }
        ],
        response_format=response_format,
    )
    return response.choices[0].message.parsed
