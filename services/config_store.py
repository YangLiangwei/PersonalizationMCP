"""Minimal config file loader/writer for PersonalizationMCP."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import dotenv_values


CONFIG_CANDIDATES = ("config", ".env")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_config_path(preferred: str | None = None) -> Path:
    root = _repo_root()
    if preferred:
        return (root / preferred).resolve()

    for name in CONFIG_CANDIDATES:
        p = root / name
        if p.exists():
            return p
    return (root / "config").resolve()


def load_config_into_env(config_path: str | None = None) -> Path:
    path = resolve_config_path(config_path)
    if not path.exists():
        return path

    values = dotenv_values(path)
    for key, value in values.items():
        if key and value is not None and not os.getenv(key):
            os.environ[key] = value
    return path


def set_config_values(updates: dict[str, str], config_path: str | None = None) -> Path:
    path = resolve_config_path(config_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    existing: dict[str, str] = {}
    if path.exists():
        for key, value in dotenv_values(path).items():
            if key and value is not None:
                existing[key] = value

    existing.update({k: v for k, v in updates.items() if v is not None})

    lines = [f"{k}={v}" for k, v in sorted(existing.items())]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    for key, value in updates.items():
        if value is not None:
            os.environ[key] = value
    return path


def missing_required(required_keys: list[str]) -> list[str]:
    return [k for k in required_keys if not os.getenv(k)]
