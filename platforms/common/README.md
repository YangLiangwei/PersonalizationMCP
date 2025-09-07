# Common Platform Utilities

This module contains shared utilities and configurations used across all platform integrations.

## Files

- `platforms_config.py`: Centralized platform configuration management
- `README.md`: This documentation file

## Platform Configuration

The `platforms_config.py` module provides:

- **PlatformConfig**: Base configuration class for platform integrations
- **PLATFORMS**: Dictionary of all platform configurations
- **get_platform_status()**: Get status of all platforms
- **get_configured_platforms()**: Get list of properly configured platforms

## Usage

```python
from platforms.common.platforms_config import get_platform_status, get_configured_platforms

# Check which platforms are configured
status = get_platform_status()
configured = get_configured_platforms()

print(f"Configured platforms: {configured}")
```

## Adding New Platforms

To add a new platform:

1. Add a new `PlatformConfig` entry to the `PLATFORMS` dictionary
2. Specify required and optional environment variables
3. Set `enabled=True` when the platform is implemented
4. Create the platform-specific module in its own subdirectory
