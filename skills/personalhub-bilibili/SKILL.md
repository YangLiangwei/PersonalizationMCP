---
name: personalhub-bilibili
description: Use PersonalizationMCP Bilibili CLI commands for credential checks, video search, and video detail lookup. Trigger when users ask about Bilibili setup, BVID details, or keyword-based content discovery.
---

Use Bilibili subcommands directly.

## Commands

```bash
personalhub bilibili credentials
personalhub bilibili search -k "<keyword>"
personalhub bilibili video --bvid <BVID>
```

## Workflow

1. Run `credentials` first.
2. Use `search` for discovery tasks.
3. Use `video` when BVID is provided.
4. If cookies are invalid, state refresh is required.
