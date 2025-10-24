"""
Base Server Configuration
Core server settings that apply to all tools
"""
import os
from typing import Optional
from pathlib import Path


class ServerConfig:
    """
    Core server configuration.
    Shared settings across all tools.
    """
    
    # Base Directory
    BASE_DIR: Path = Path(__file__).parent.parent
    OUTPUT_DIR: Path = BASE_DIR / "output"
    
    # Server Identity
    SERVER_NAME: str = os.getenv("MCP_SERVER_NAME", "Thinking Tools MCP Server")
    SERVER_VERSION: str = os.getenv("MCP_SERVER_VERSION", "1.0.0")
    SERVER_DESCRIPTION: str = "Advanced thinking and reasoning tools for problem-solving (Recursive Thinking, Sequential Thinking, Tree of Thoughts)"
    
    # Transport Configuration
    TRANSPORT_TYPE: str = os.getenv("MCP_TRANSPORT", "stdio")  # stdio, http, sse
    HTTP_HOST: str = os.getenv("MCP_HTTP_HOST", "127.0.0.1")
    HTTP_PORT: int = int(os.getenv("MCP_HTTP_PORT", "8000"))
    HTTP_PATH: str = os.getenv("MCP_HTTP_PATH", "/mcp")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("MCP_LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("MCP_LOG_FILE", None)
    
    # Authentication (if needed)
    AUTH_ENABLED: bool = os.getenv("MCP_AUTH_ENABLED", "false").lower() == "true"
    AUTH_PROVIDER: Optional[str] = os.getenv("MCP_AUTH_PROVIDER", None)
    
    @classmethod
    def ensure_output_directories(cls) -> None:
        """Ensure all output directories exist"""
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration settings"""
        valid_transports = ["stdio", "http", "sse"]
        if cls.TRANSPORT_TYPE not in valid_transports:
            raise ValueError(f"Invalid transport type. Must be one of: {valid_transports}")
        
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if cls.LOG_LEVEL not in valid_log_levels:
            raise ValueError(f"Invalid log level. Must be one of: {valid_log_levels}")
        
        # Ensure output directories exist
        cls.ensure_output_directories()
