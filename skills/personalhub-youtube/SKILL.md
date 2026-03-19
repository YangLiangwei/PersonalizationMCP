---
name: personalhub-youtube
description: Use PersonalizationMCP YouTube CLI commands to validate configuration, search videos, and inspect trending content. Trigger when users ask for YouTube diagnostics, content discovery, or quick trend checks.
---

Use YouTube subcommands directly.

## Commands

```bash
personalhub youtube credentials
personalhub youtube search -q "<query>"
personalhub youtube trending --region-code US
```

## Workflow

1. Run `credentials` before data calls.
2. Use `search` for keyword requests.
3. Use `trending` for region-based trend checks.
4. Keep summaries compact with title/channel/view count.
