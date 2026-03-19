---
name: personalhub-steam
description: Configure and use Steam in PersonalizationMCP. Trigger when users need Steam credential setup, validation, game library lookup, profile checks, or recent activity summaries.
---

Handle Steam credential setup and usage.

## Required input

- `STEAM_API_KEY`
- `STEAM_USER_ID`

## Setup flow

1. Ask for missing required values only.
2. Write/update config entries.
3. Validate:

```bash
personalhub steam credentials
```

## Usage commands

```bash
personalhub steam profile
personalhub steam library
```

## Output

Return `Ready` or `Needs setup`, then one next action.
