---
name: personalhub-youtube
description: Configure and use YouTube in PersonalizationMCP. Trigger when users need YouTube API setup, credential validation, search/trending usage, or OAuth troubleshooting.
---

Handle YouTube credential setup and usage.

## Required input

- `YOUTUBE_API_KEY`

## Optional input

- OAuth tokens (for personal data access)

## Setup flow

1. Ask for `YOUTUBE_API_KEY` first.
2. Write/update config.
3. Validate:

```bash
personalhub youtube credentials
```

## Usage commands

```bash
personalhub youtube search -q "<query>"
personalhub youtube trending --region-code US
```

## Output

Return `Ready` or `Needs setup`, then one next action.
