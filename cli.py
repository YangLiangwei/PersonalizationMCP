#!/usr/bin/env python3
"""PersonalizationMCP CLI entrypoint."""

from __future__ import annotations

import os

import typer

from server import TOOL_PROFILES, create_mcp_server
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
    typer.echo(RedditService.credentials_status())


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
    app()


if __name__ == "__main__":
    main()
