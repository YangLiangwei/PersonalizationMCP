#!/usr/bin/env python3
"""PersonalizationMCP CLI entrypoint."""

from __future__ import annotations

import os

import typer

from server import TOOL_PROFILES, create_mcp_server
from services.status_service import build_personalization_status
from services.steam_service import SteamService
from services.youtube_service import YouTubeService

app = typer.Typer(help="PersonalizationMCP command line tool")
steam_app = typer.Typer(help="Steam commands")
youtube_app = typer.Typer(help="YouTube commands")


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
    typer.echo(SteamService.credentials_status())


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
    typer.echo(YouTubeService.credentials_status())


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


def main() -> None:
    app()


if __name__ == "__main__":
    main()
