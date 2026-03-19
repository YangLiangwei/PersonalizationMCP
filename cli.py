#!/usr/bin/env python3
"""PersonalizationMCP CLI entrypoint."""

from __future__ import annotations

import os

import typer

from server import TOOL_PROFILES, build_personalization_status, create_mcp_server

app = typer.Typer(help="PersonalizationMCP command line tool")


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


def main() -> None:
    app()


if __name__ == "__main__":
    main()
