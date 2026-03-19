---
name: personalhub-bilibili
description: Configure and use Bilibili in PersonalizationMCP. Trigger when users need cookie-based credential setup, validation, video search, or BVID detail lookup.
---

Handle Bilibili credential setup and usage.

## Required input

- `BILIBILI_SESSDATA`
- `BILIBILI_BILI_JCT`

## Optional input

- `BILIBILI_BUVID3`

## Setup flow

1. Ask for missing required cookie fields only.
2. Write/update config.
3. Validate:

```bash
personalhub bilibili credentials
```

## Usage commands

```bash
personalhub bilibili search -k "<keyword>"
personalhub bilibili video --bvid <BVID>
```

## Output

Return `Ready` or `Needs setup`, then one next action.
