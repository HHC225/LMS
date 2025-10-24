"""
Memory Tools Configuration
Settings for Conversation Memory and related storage
"""
import os
from pathlib import Path
from .base import ServerConfig


class MemoryConfig:
    """
    Configuration for memory and conversation storage tools.
    ChromaDB and conversation management settings.
    """
    
    # ============================================================================
    # FEATURE FLAGS
    # ============================================================================
    
    # Conversation Memory Tools
    ENABLE_CONVERSATION_MEMORY: bool = os.getenv(
        "ENABLE_CONVERSATION_MEMORY", "true"
    ).lower() == "true"
    
    # ============================================================================
    # CONVERSATION MEMORY SPECIFIC SETTINGS
    # ============================================================================
    
    # ChromaDB storage path
    CONVERSATION_MEMORY_DB_PATH: Path = ServerConfig.OUTPUT_DIR / "chroma_db"
    
    # Default number of results to return
    CONVERSATION_MEMORY_DEFAULT_RESULTS: int = int(
        os.getenv("CONVERSATION_MEMORY_DEFAULT_RESULTS", "5")
    )
    
    # Maximum results allowed
    CONVERSATION_MEMORY_MAX_RESULTS: int = int(
        os.getenv("CONVERSATION_MEMORY_MAX_RESULTS", "50")
    )
    
    # Collection name for ChromaDB
    CONVERSATION_MEMORY_COLLECTION_NAME: str = os.getenv(
        "CONVERSATION_MEMORY_COLLECTION_NAME", "conversations"
    )
    
    # Enable embedding persistence
    CONVERSATION_MEMORY_PERSIST: bool = os.getenv(
        "CONVERSATION_MEMORY_PERSIST", "true"
    ).lower() == "true"
    
    @classmethod
    def validate(cls) -> None:
        """Validate memory configuration settings"""
        if cls.CONVERSATION_MEMORY_DEFAULT_RESULTS < 1:
            raise ValueError("CONVERSATION_MEMORY_DEFAULT_RESULTS must be at least 1")
        
        if cls.CONVERSATION_MEMORY_MAX_RESULTS < cls.CONVERSATION_MEMORY_DEFAULT_RESULTS:
            raise ValueError("CONVERSATION_MEMORY_MAX_RESULTS must be >= DEFAULT_RESULTS")
        
        # Ensure ChromaDB directory exists
        cls.CONVERSATION_MEMORY_DB_PATH.mkdir(parents=True, exist_ok=True)
