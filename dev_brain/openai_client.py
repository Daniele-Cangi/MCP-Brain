from __future__ import annotations

import os
from openai import OpenAI


def get_openai_client() -> OpenAI:
    """
    Return a shared OpenAI client for all Dev Brain runtime calls.

    API key resolution priority:
    - QDB_CODEX_API_KEY
    - OPENAI_API_KEY

    If neither is set, raise a clear RuntimeError.
    """
    api_key = os.environ.get("QDB_CODEX_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Environment variable QDB_CODEX_API_KEY or OPENAI_API_KEY is not set."
        )

    # For QDB we use the default OpenAI API endpoint.
    # No base_url override for Gemini or other providers.
    return OpenAI(api_key=api_key)
