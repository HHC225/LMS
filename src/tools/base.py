"""
Base classes for Recursive Thinking MCP tools.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from fastmcp import Context
import logging

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """
    Abstract base class for all MCP tools.
    Provides common structure and utilities.
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize base tool.
        
        Args:
            name: Tool name
            description: Tool description
        """
        self.name = name
        self.description = description
        logger.info(f"Initialized tool: {self.name}")
    
    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """
        Execute the tool logic.
        Must be implemented by subclasses.
        """
        pass
    
    async def log_execution(self, ctx: Optional[Context], message: str) -> None:
        """
        Log execution information to both logger and MCP context if available.
        
        Args:
            ctx: MCP context (optional)
            message: Log message
        """
        logger.info(f"[{self.name}] {message}")
        if ctx:
            await ctx.info(message)


class ReasoningTool(BaseTool):
    """
    Base class for reasoning-based tools.
    Extends BaseTool with reasoning-specific functionality.
    """
    
    def __init__(self, name: str, description: str):
        super().__init__(name, description)
        self.session_store: Dict[str, Any] = {}
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by ID"""
        return self.session_store.get(session_id)
    
    def create_session(self, session_id: str, data: Dict[str, Any]) -> None:
        """Create new session"""
        self.session_store[session_id] = data
    
    def update_session(self, session_id: str, data: Dict[str, Any]) -> None:
        """Update existing session"""
        if session_id in self.session_store:
            self.session_store[session_id].update(data)
    
    def delete_session(self, session_id: str) -> None:
        """Delete session"""
        if session_id in self.session_store:
            del self.session_store[session_id]
