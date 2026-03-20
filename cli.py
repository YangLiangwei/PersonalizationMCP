#!/usr/bin/env python3
"""PersonalizationMCP CLI entrypoint."""

from __future__ import annotations

import json
import os
import re
from typing import Any

import typer

from server import TOOL_PROFILES, create_mcp_server
from services.config_store import load_config_into_env, set_config_values
from services.status_service import build_personalization_status
from services.steam_service import SteamService
from services.youtube_service import YouTubeService
from services.spotify_service import SpotifyService
from services.reddit_service import RedditService
from services.bilibili_service import BilibiliService

app = typer.Typer(help="PersonalizationMCP command line tool")
steam_app = typer.Typer(help="Steam commands")
youtube_app = typer.Typer(help="YouTube commands")
spotify_app = typer.Typer(help="Spotify commands")
reddit_app = typer.Typer(help="Reddit commands")
bilibili_app = typer.Typer(help="Bilibili commands")

PLATFORM_REQUIREMENTS: dict[str, dict[str, list[str]]] = {
    "steam": {"required": ["STEAM_API_KEY", "STEAM_USER_ID"], "optional": []},
    "youtube": {"required": ["YOUTUBE_API_KEY"], "optional": []},
    "bilibili": {"required": ["BILIBILI_SESSDATA", "BILIBILI_BILI_JCT"], "optional": ["BILIBILI_BUVID3"]},
    "spotify": {
        "required": ["SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET"],
        "optional": ["SPOTIFY_REDIRECT_URI"],
    },
    "reddit": {
        "required": ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET"],
        "optional": ["REDDIT_REDIRECT_URI"],
    },
}


@app.command("profiles")
def list_profiles() -> None:
    """List available MCP tool exposure profiles."""
    typer.echo("Available profiles:")
    for name, allowlist in TOOL_PROFILES.items():
        if allowlist is None:
            typer.echo(f"- {name}: all tools exposed")
        else:
            typer.echo(f"- {name}: {len(allowlist)} tools")


@app.command("status")
def status() -> None:
    """Show personalization integration status (same as MCP tool output)."""
    typer.echo(build_personalization_status())


def _redact_text(text: str) -> str:
    # key=value style redaction
    text = re.sub(r"(?i)(api[_-]?key|client[_-]?secret|access[_-]?token|refresh[_-]?token|sessdata|bili[_-]?jct|buvid3)\s*=\s*[^,\s\n]+", r"\1=***", text)
    # bare long token-like strings
    text = re.sub(r"\b[A-Za-z0-9_-]{24,}\b", lambda m: m.group(0)[:6] + "***", text)
    return text


def _normalize_result(platform: str, action: str, raw: Any) -> dict[str, Any]:
    text = _redact_text(str(raw))
    lower = text.lower()
    ok = not any(x in lower for x in ["❌", "error", "not found", "not configured", "failed"])
    payload: dict[str, Any] = {
        "ok": ok,
        "platform": platform,
        "action": action,
        "message": text,
        "next_step": "" if ok else f"Complete {platform} required credentials and re-run `personalhub {platform} credentials`.",
    }
    return payload


def _emit(payload: dict[str, Any]) -> None:
    typer.echo(json.dumps(payload, ensure_ascii=False))


def _parse_set_values(values: list[str]) -> dict[str, str]:
    updates: dict[str, str] = {}
    for item in values:
        if "=" not in item:
            raise typer.BadParameter(f"Invalid --set value '{item}', expected KEY=VALUE")
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise typer.BadParameter(f"Invalid --set key in '{item}'")
        updates[key] = value
    return updates


def _normalize_platforms(platform: str, all_platforms: bool) -> list[str]:
    if all_platforms:
        return list(PLATFORM_REQUIREMENTS.keys())

    if not platform.strip():
        raise typer.BadParameter("Use --platform steam,youtube or --all")

    selected = [p.strip().lower() for p in platform.split(",") if p.strip()]
    invalid = [p for p in selected if p not in PLATFORM_REQUIREMENTS]
    if invalid:
        raise typer.BadParameter(f"Unknown platform(s): {', '.join(invalid)}")
    return selected


def _run_credentials_check(platform: str) -> dict[str, Any]:
    if platform == "steam":
        raw = SteamService.credentials_status()
    elif platform == "youtube":
        raw = YouTubeService.credentials_status()
    elif platform == "bilibili":
        raw = BilibiliService.credentials_status()
    elif platform == "spotify":
        raw = SpotifyService.credentials_status()
    elif platform == "reddit":
        raw = RedditService.credentials_status()
    else:
        raw = "Unsupported platform"
    return _normalize_result(platform, "credentials", raw)


@app.command("onboarding")
def onboarding(
    platform: str = typer.Option("", help="Comma-separated platforms: steam,youtube,bilibili,spotify,reddit"),
    all_platforms: bool = typer.Option(False, "--all", help="Configure all platforms"),
    set_values: list[str] = typer.Option(None, "--set", help="Set KEY=VALUE (repeatable, non-interactive friendly)"),
    dry_run: bool = typer.Option(False, help="Only show missing fields, do not write config"),
    config_file: str = typer.Option("", help="Config file path relative to project root (default: config)"),
) -> None:
    """Interactive credentials onboarding for one or more platforms."""
    load_config_into_env(config_file or None)
    preset_updates = _parse_set_values(set_values or [])
    if preset_updates and not dry_run:
        set_config_values(preset_updates, config_file or None)
    targets = _normalize_platforms(platform, all_platforms)

    configured: list[str] = []
    needs_input: list[str] = []

    for p in targets:
        req = PLATFORM_REQUIREMENTS[p]
        updates: dict[str, str] = {}

        typer.echo(f"\n[{p}] setup")
        for key in req["required"]:
            current = os.getenv(key, "")
            if current:
                typer.echo(f"- {key}: already set")
                continue
            if dry_run:
                needs_input.append(f"{p}:{key}")
                continue
            value = typer.prompt(f"Enter {key}").strip()
            if not value:
                needs_input.append(f"{p}:{key}")
            else:
                updates[key] = value

        for key in req["optional"]:
            current = os.getenv(key, "")
            if current or dry_run:
                continue
            value = typer.prompt(f"Enter {key} (optional)", default="", show_default=False).strip()
            if value:
                updates[key] = value

        if updates and not dry_run:
            set_config_values(updates, config_file or None)

        result = _run_credentials_check(p)
        typer.echo(f"- credentials: {result['message']}")

        if not result["ok"]:
            needs_input.append(p)
        else:
            configured.append(p)

    typer.echo("\nConfigured:")
    typer.echo(", ".join(sorted(set(configured))) if configured else "(none)")
    typer.echo("Needs input:")
    typer.echo(", ".join(sorted(set(needs_input))) if needs_input else "(none)")
    typer.echo("Next step:")
    typer.echo("Run `personalhub status` to verify global readiness.")


@app.command("serve")
def serve(
    profile: str = typer.Option("safe", help="Tool exposure profile: full|safe|minimal"),
    allow_tool: list[str] = typer.Option(None, "--allow-tool", help="Extra tool(s) to expose"),
) -> None:
    """Run MCP server with explicit tool exposure controls."""
    if profile not in TOOL_PROFILES:
        raise typer.BadParameter(f"Unknown profile '{profile}'. Use 'profiles' to list available values.")

    extra = allow_tool or []
    os.environ["MCP_TOOL_PROFILE"] = profile
    if extra:
        os.environ["MCP_EXTRA_ALLOWED_TOOLS"] = ",".join(extra)

    typer.echo(f"Starting PersonalizationMCP with profile='{profile}'")
    if extra:
        typer.echo(f"Extra allowed tools: {', '.join(extra)}")

    create_mcp_server(profile=profile, extra_allowed_tools=extra).run()


@steam_app.command("credentials")
def steam_credentials() -> None:
    """Check Steam credential status."""
    _emit(_normalize_result("steam", "credentials", SteamService.credentials_status()))


@steam_app.command("library")
def steam_library(steamid: str = typer.Option(None, help="Steam ID (defaults to STEAM_USER_ID)")) -> None:
    """Show Steam game library summary."""
    typer.echo(SteamService.get_library(steamid=steamid))


@steam_app.command("profile")
def steam_profile(steamid: str = typer.Option(None, help="Steam ID (defaults to STEAM_USER_ID)")) -> None:
    """Show Steam profile summary."""
    typer.echo(SteamService.get_profile(steamid=steamid))


app.add_typer(steam_app, name="steam")


@youtube_app.command("credentials")
def youtube_credentials() -> None:
    """Check YouTube credential status."""
    _emit(_normalize_result("youtube", "credentials", YouTubeService.credentials_status()))


@youtube_app.command("search")
def youtube_search(
    query: str = typer.Option(..., "--query", "-q", help="Search query"),
    max_results: int = typer.Option(10, help="Max results (<=50)"),
) -> None:
    """Search YouTube videos."""
    typer.echo(YouTubeService.search_videos(query=query, max_results=max_results))


@youtube_app.command("trending")
def youtube_trending(
    region_code: str = typer.Option("US", help="Region code"),
    max_results: int = typer.Option(10, help="Max results (<=50)"),
) -> None:
    """Show YouTube trending videos."""
    typer.echo(YouTubeService.get_trending(region_code=region_code, max_results=max_results))


app.add_typer(youtube_app, name="youtube")


@spotify_app.command("credentials")
def spotify_credentials() -> None:
    """Check Spotify credential status."""
    typer.echo(SpotifyService.credentials_status())


@spotify_app.command("token-status")
def spotify_token_status() -> None:
    """Show Spotify OAuth token status."""
    typer.echo(SpotifyService.token_status())


@spotify_app.command("recent")
def spotify_recent(limit: int = typer.Option(20, help="Number of recently played tracks (<=50)")) -> None:
    """Show recently played Spotify tracks."""
    typer.echo(SpotifyService.get_recently_played(limit=limit))


app.add_typer(spotify_app, name="spotify")


@reddit_app.command("credentials")
def reddit_credentials() -> None:
    """Check Reddit credential status."""
    _emit(_normalize_result("reddit", "credentials", RedditService.credentials_status()))


@reddit_app.command("token-status")
def reddit_token_status() -> None:
    """Show Reddit OAuth token status."""
    typer.echo(RedditService.token_status())


@reddit_app.command("subreddits")
def reddit_subreddits(limit: int = typer.Option(20, help="Number of subscribed subreddits (<=100)")) -> None:
    """Show subscribed Reddit communities."""
    typer.echo(RedditService.get_user_subreddits(limit=limit))


app.add_typer(reddit_app, name="reddit")


@bilibili_app.command("credentials")
def bilibili_credentials() -> None:
    """Check Bilibili credential status."""
    typer.echo(BilibiliService.credentials_status())


@bilibili_app.command("search")
def bilibili_search(
    keyword: str = typer.Option(..., "--keyword", "-k", help="Search keyword"),
    page: int = typer.Option(1, help="Page number"),
    order: str = typer.Option("totalrank", help="Sort order"),
) -> None:
    """Search Bilibili videos."""
    typer.echo(BilibiliService.search_videos(keyword=keyword, page=page, order=order))


@bilibili_app.command("video")
def bilibili_video_info(bvid: str = typer.Option(..., "--bvid", help="Bilibili video BVID")) -> None:
    """Get Bilibili video details."""
    typer.echo(BilibiliService.get_video_info(bvid=bvid))


app.add_typer(bilibili_app, name="bilibili")


def main() -> None:
    load_config_into_env()
    app()


if __name__ == "__main__":
    main()


