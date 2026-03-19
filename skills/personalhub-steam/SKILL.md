---
name: personalhub-steam
description: Use PersonalizationMCP Steam CLI commands for game library, profile, and recent activity checks. Trigger when users ask about Steam setup, owned games, playtime, profile, or recent gaming behavior.
---

Use Steam subcommands directly.

## Commands

```bash
personalhub steam credentials
personalhub steam profile
personalhub steam library
```

## Workflow

1. Run `personalhub steam credentials` first.
2. If credentials pass, run `profile` or `library` as requested.
3. Highlight top findings only (e.g., total games, top playtime).
4. If credentials fail, return exact missing env vars.
