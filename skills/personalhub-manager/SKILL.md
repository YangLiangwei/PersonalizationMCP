---
name: personalhub-manager
description: Manage all PersonalizationMCP platforms through one entry skill. Use when users ask for cross-platform status checks, centralized diagnostics, or unified summaries across Steam, YouTube, Bilibili, Spotify, and Reddit.
---

Act as a single orchestration layer for all platform skills.

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

1. Run `personalhub status` first for global view.
2. Run per-platform `credentials` only for platforms relevant to the request.
3. For a full audit, run all five credential checks.
4. Summarize in three blocks: `Ready`, `Needs setup`, `Next action`.
5. Keep output short and operational.

## Escalation

- If one platform fails, give only minimal fix steps for that platform.
- If multiple platforms fail, prioritize by user-stated importance.
