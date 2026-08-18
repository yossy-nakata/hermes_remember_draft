from dataclasses import dataclass

from openai import OpenAI


@dataclass(frozen=True)
class LlmConfig:
    base_url: str = "http://localhost:8080/v1"
    api_key: str = "local"
    model: str = "LFM2-24B-A2B-Q4_K_M"
    temperature: float = 0.2
    max_tokens: int = 4096


def complete_text(
    prompt: str,
    *,
    config: LlmConfig | None = None,
) -> str:
    config = config or LlmConfig()

    client = OpenAI(
        base_url=config.base_url,
        api_key=config.api_key,
    )

    response = client.chat.completions.create(
        model=config.model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )

    content = response.choices[0].message.content

    if content is None:
        raise RuntimeError("LLM response content is empty")

    return content