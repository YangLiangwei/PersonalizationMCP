---
name: personalhub-spotify
description: Use PersonalizationMCP Spotify CLI commands for credential validation, OAuth token status, and recent listening checks. Trigger when users ask about Spotify setup, token health, or recently played tracks.
---

Use Spotify subcommands directly.

## Commands

```bash
personalhub spotify credentials
personalhub spotify token-status
personalhub spotify recent --limit 20
```

## Workflow

1. Run `credentials` first.
2. Run `token-status` before user-data queries.
3. Use `recent` to summarize listening behavior.
4. On auth failure, report the exact failing step.
