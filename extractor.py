import json
import re
from typing import Any

import httpx

from config import (
    LLM_MAX_INPUT_CHARS,
    LLM_MAX_TOKENS,
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
)

BOOLEAN_FIELDS = [
    "trains_on_input",
    "soc2_certified",
    "hipaa_compliant",
    "gdpr_compliant",
    "iso_27001",
    "breach_mentions",
]

EXTRACTION_PROMPT = """
Read this privacy policy and security document. Extract the following fields:

1. data_retention  – How long user data is retained (e.g. "30 days", "deleted on request"). Return as a string.
2. trains_on_input – Does the service train models on user inputs? Return true or false.
3. soc2_certified  – SOC 2 certified? Return true or false.
4. hipaa_compliant – HIPAA compliant? Return true or false.
5. gdpr_compliant  – GDPR compliant? Return true or false.
6. iso_27001       – ISO 27001 certified? Return true or false.
7. breach_mentions – Any data breach incidents mentioned? Return true or false.

Rules:
- Boolean fields must be exactly true or false (no quotes, no "unknown").
- If you cannot determine a boolean field, use false.
- Return ONLY a valid JSON object. No markdown, no extra text.

Document:
{document}

Example output:
{{"data_retention": "90 days", "trains_on_input": false, "soc2_certified": true, "hipaa_compliant": false, "gdpr_compliant": true, "iso_27001": false, "breach_mentions": false}}
"""


def _parse_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        lower = value.lower().strip()
        if lower in ("true", "yes", "1"):
            return True
        if lower in ("false", "no", "0"):
            return False
    return None


async def extract_fields(pages: dict[str, str]) -> dict[str, Any]:
    """
    Sends scraped page content to the LLM and returns structured fields.

    Returns an empty dict if extraction fails.
    """
    combined_text = "\n\n".join(pages.values())[:LLM_MAX_INPUT_CHARS]
    if not combined_text:
        return {}

    prompt = EXTRACTION_PROMPT.format(document=combined_text)

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://your-site.com",
                    "X-Title": "AI Tool Risk Profiler",
                },
                json={
                    "model": OPENROUTER_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": LLM_MAX_TOKENS,
                },
            )

        if response.status_code != 200:
            print(f"[llm] OpenRouter error {response.status_code}: {response.text}")
            return {}

        raw = response.json()
        if not raw.get("choices"):
            print(f"[llm] Unexpected response shape: {raw}")
            return {}

        text = raw["choices"][0]["message"]["content"].strip()
        text = text.replace("```json", "").replace("```", "").strip()

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            text = match.group()

        fields: dict[str, Any] = json.loads(text)

    except json.JSONDecodeError as exc:
        print(f"[llm] JSON parse error: {exc}")
        return {}
    except Exception as exc:
        print(f"[llm] Extraction failed: {exc}")
        return {}

    # Normalise boolean fields
    for field in BOOLEAN_FIELDS:
        fields[field] = _parse_bool(fields.get(field))

    fields.setdefault("data_retention", "Not specified")

    return fields