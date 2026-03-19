---
name: personalhub-reddit
description: Configure and use Reddit in PersonalizationMCP. Trigger when users need Reddit app credential setup, OAuth validation, or subscribed community checks.
---

Handle Reddit credential setup and usage.

## Required input

- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`

## Optional input

- `REDDIT_REDIRECT_URI`

## Setup flow

1. Ask for required fields first.
2. Write/update config.
3. Validate:

```bash
personalhub reddit credentials
personalhub reddit token-status
```

## Usage command

```bash
personalhub reddit subreddits --limit 20
```

## Output

Return `Ready` or `Needs setup`, then one next action.
