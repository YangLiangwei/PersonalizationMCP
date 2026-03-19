---
name: personalhub-spotify
description: Configure and use Spotify in PersonalizationMCP. Trigger when users need Spotify API credential setup, token validation, or recent listening summaries.
---

Handle Spotify credential setup and usage.

## Required input

- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_CLIENT_SECRET`

## Optional input

- `SPOTIFY_REDIRECT_URI`

## Setup flow

1. Ask for required fields first.
2. Write/update config.
3. Validate:

```bash
personalhub spotify credentials
personalhub spotify token-status
```

## Usage command

```bash
personalhub spotify recent --limit 20
```

## Output

Return `Ready` or `Needs setup`, then one next action.
