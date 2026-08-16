"""Cliente de Anthropic configurado desde el .env de la raíz."""

from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path

import anthropic
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent

load_dotenv(ROOT / ".env")

MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-5")
MODEL_FAST = os.getenv("CLAUDE_MODEL_FAST", "claude-haiku-4-5")
MODEL_LEGACY = os.getenv("CLAUDE_MODEL_LEGACY", "claude-haiku-4-5")
MAX_TOKENS = int(os.getenv("CLAUDE_MAX_TOKENS", "4096"))


@lru_cache(maxsize=1)
def get_client() -> anthropic.Anthropic:
    if not os.getenv("ANTHROPIC_API_KEY"):
        sys.exit(
            "Falta ANTHROPIC_API_KEY.\n"
            f"Copia {ROOT / '.env.example'} a {ROOT / '.env'} y añade la clave."
        )
    return anthropic.Anthropic()


@lru_cache(maxsize=1)
def get_async_client() -> anthropic.AsyncAnthropic:
    """La uso en el módulo 03 para lanzar evals en paralelo."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        sys.exit("Falta ANTHROPIC_API_KEY. Revisar el .env.")
    return anthropic.AsyncAnthropic()
