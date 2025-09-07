"""
Platform Configuration
Centralized configuration for all platform integrations.
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class PlatformConfig:
    """Base configuration for a platform integration."""
    name: str
    enabled: bool
    required_env_vars: list
    optional_env_vars: list = None
    
    def is_configured(self) -> bool:
        """Check if all required environment variables are set."""
        return all(os.getenv(var) for var in self.required_env_vars)
    
    def get_config(self) -> Dict[str, Any]:
        """Get configuration values from environment variables."""
        config = {}
        
        # Required variables
        for var in self.required_env_vars:
            config[var.lower()] = os.getenv(var)
        
        # Optional variables
        if self.optional_env_vars:
            for var in self.optional_env_vars:
                value = os.getenv(var)
                if value:
                    config[var.lower()] = value
        
        return config

# Platform configurations
PLATFORMS = {
    "steam": PlatformConfig(
        name="Steam",
        enabled=True,
        required_env_vars=["STEAM_API_KEY", "STEAM_USER_ID"],
        optional_env_vars=[]
    ),
    
    "youtube": PlatformConfig(
        name="YouTube",
        enabled=True,
        required_env_vars=["YOUTUBE_API_KEY"],
        optional_env_vars=[]
    ),
    
    "bilibili": PlatformConfig(
        name="Bilibili",
        enabled=True,
        required_env_vars=["BILIBILI_SESSDATA", "BILIBILI_BILI_JCT"],
        optional_env_vars=["BILIBILI_BUVID3"]
    ),
    
    # Future platform integrations
    "spotify": PlatformConfig(
        name="Spotify",
        enabled=False,  # Not implemented yet
        required_env_vars=["SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET"],
        optional_env_vars=["SPOTIFY_REFRESH_TOKEN"]
    ),
    
    "twitter": PlatformConfig(
        name="Twitter/X",
        enabled=False,  # Not implemented yet
        required_env_vars=["TWITTER_API_KEY", "TWITTER_API_SECRET", "TWITTER_ACCESS_TOKEN"],
        optional_env_vars=["TWITTER_ACCESS_TOKEN_SECRET"]
    ),
    
    "github": PlatformConfig(
        name="GitHub",
        enabled=False,  # Not implemented yet
        required_env_vars=["GITHUB_TOKEN"],
        optional_env_vars=["GITHUB_USERNAME"]
    )
}

def get_platform_status() -> Dict[str, Dict[str, Any]]:
    """Get status of all platforms."""
    status = {}
    
    for platform_id, config in PLATFORMS.items():
        status[platform_id] = {
            "name": config.name,
            "enabled": config.enabled,
            "configured": config.is_configured(),
            "required_vars": config.required_env_vars,
            "missing_vars": [var for var in config.required_env_vars if not os.getenv(var)]
        }
    
    return status

def get_configured_platforms() -> list:
    """Get list of platforms that are both enabled and configured."""
    return [
        platform_id for platform_id, config in PLATFORMS.items()
        if config.enabled and config.is_configured()
    ]



