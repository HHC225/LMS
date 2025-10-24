"""
Thinking Tools MCP Server Configuration Package
Modular configuration management for scalable tool addition
"""
from .base import ServerConfig
from .reasoning import ReasoningConfig
from .memory import MemoryConfig
from .planning import PlanningConfig
from .slack import SlackConfig, get_slack_config
from .report import ReportConfig
from .vibe import VibeConfig, get_vibe_config

__all__ = [
    "ServerConfig",
    "ReasoningConfig",
    "MemoryConfig",
    "PlanningConfig",
    "SlackConfig",
    "get_slack_config",
    "ReportConfig",
    "VibeConfig",
    "get_vibe_config",
]

# Validate all configurations on import
ServerConfig.validate()
ReasoningConfig.validate()
MemoryConfig.validate()
PlanningConfig.validate()
ReportConfig.validate()
VibeConfig.validate()
