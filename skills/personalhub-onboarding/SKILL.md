---
name: personalhub-onboarding
description: Unified onboarding entry for PersonalizationMCP credentials. Use when users want to set up one or more platforms from scratch, migrate credentials, or fix partial configuration across Steam, YouTube, Bilibili, Spotify, and Reddit.
---

Guide setup with one orchestration flow, then hand off to platform-specific skills.

## Workflow

1. Ask which platforms to configure (single or multi-select).
2. For each selected platform, invoke its platform skill flow (no nested skill execution required in one response; follow its checklist directly).
3. After each platform write/update, run:

```bash
personalhub <platform> credentials
```

4. End with 3 blocks:
- `Configured`
- `Needs input`
- `Next step`

## Rules

- Ask only minimum required fields first.
- Validate immediately after each platform is configured.
- Keep output short and actionable.
