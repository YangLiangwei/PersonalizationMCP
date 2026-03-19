---
name: personalhub-status
description: Check PersonalizationMCP integration health and MCP tool exposure profile. Use when users ask whether setup/config is correct, whether credentials are ready, or to quickly diagnose platform readiness before deeper tasks.
---

Run status checks first.

## Commands

```bash
personalhub status
personalhub profiles
```

## Workflow

1. Run `personalhub status` to inspect platform readiness.
2. Run `personalhub profiles` when tool exposure confusion exists.
3. Report only failing or missing items first.
4. Propose the smallest next action.

## Output Style

- Keep output short.
- Group by platform.
- End with one concrete next step.
