---
name: personalhub-reddit
description: Use PersonalizationMCP Reddit CLI commands for credential checks, token status, and subscribed subreddit retrieval. Trigger when users ask about Reddit setup, auth status, or community subscriptions.
---

Use Reddit subcommands directly.

## Commands

```bash
personalhub reddit credentials
personalhub reddit token-status
personalhub reddit subreddits --limit 20
```

## Workflow

1. Run `credentials` first.
2. Run `token-status` for OAuth validation.
3. Use `subreddits` for account scope and interest checks.
4. If auth fails, output minimal fix steps only.
