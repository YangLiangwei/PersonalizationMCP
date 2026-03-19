---
name: personalhub-manager
description: Central manager for PersonalizationMCP operations across all platforms. Use for cross-platform health checks, unified summaries, and day-2 maintenance after initial onboarding.
---

Use this as the operational control skill.

## Commands

```bash
personalhub status
personalhub steam credentials
personalhub youtube credentials
personalhub bilibili credentials
personalhub spotify credentials
personalhub reddit credentials
```

## Workflow

1. Run `personalhub status` first.
2. Run platform `credentials` checks only where needed.
3. Summarize in: `Ready`, `Needs setup`, `Next action`.
4. Keep output concise.

## Boundary

- For first-time setup, use `personalhub-onboarding` flow.
