"""
Reasoning Tools Configuration
Settings for Recursive Thinking, Sequential Thinking, and Tree of Thoughts
"""
import os
from .base import ServerConfig


class ReasoningConfig:
    """
    Configuration for all reasoning tools.
    Centralized settings for thinking and reasoning functionalities.
    """
    
    # ============================================================================
    # FEATURE FLAGS
    # ============================================================================
    
    # Recursive Thinking Tools
    ENABLE_RECURSIVE_THINKING: bool = os.getenv(
        "ENABLE_RECURSIVE_THINKING", "true"
    ).lower() == "true"
    
    # Sequential Thinking Tools
    ENABLE_SEQUENTIAL_THINKING: bool = os.getenv(
        "ENABLE_SEQUENTIAL_THINKING", "true"
    ).lower() == "true"
    
    # Tree of Thoughts Tools
    ENABLE_TREE_OF_THOUGHTS: bool = os.getenv(
        "ENABLE_TREE_OF_THOUGHTS", "true"
    ).lower() == "true"
    
    # Verbalized Sampling Tools
    ENABLE_VERBALIZED_SAMPLING: bool = os.getenv(
        "ENABLE_VERBALIZED_SAMPLING", "true"
    ).lower() == "true"
    
    # Counterfactual Reasoning Tools
    ENABLE_COUNTERFACTUAL_REASONING: bool = os.getenv(
        "ENABLE_COUNTERFACTUAL_REASONING", "true"
    ).lower() == "true"
    
    # ============================================================================
    # RECURSIVE THINKING SPECIFIC SETTINGS
    # ============================================================================
    
    # Default number of latent reasoning updates
    RECURSIVE_THINKING_DEFAULT_LATENT_UPDATES: int = int(
        os.getenv("RECURSIVE_THINKING_DEFAULT_LATENT_UPDATES", "4")
    )
    
    # Default maximum improvement iterations
    RECURSIVE_THINKING_DEFAULT_MAX_IMPROVEMENTS: int = int(
        os.getenv("RECURSIVE_THINKING_DEFAULT_MAX_IMPROVEMENTS", "16")
    )
    
    # Session timeout in seconds
    RECURSIVE_THINKING_SESSION_TIMEOUT: int = int(
        os.getenv("RECURSIVE_THINKING_SESSION_TIMEOUT", "3600")
    )
    
    # ============================================================================
    # SEQUENTIAL THINKING SPECIFIC SETTINGS
    # ============================================================================
    
    # Maximum thoughts allowed
    SEQUENTIAL_THINKING_MAX_THOUGHTS: int = int(
        os.getenv("SEQUENTIAL_THINKING_MAX_THOUGHTS", "100")
    )
    
    # Session timeout in seconds
    SEQUENTIAL_THINKING_SESSION_TIMEOUT: int = int(
        os.getenv("SEQUENTIAL_THINKING_SESSION_TIMEOUT", "3600")
    )
    
    # ============================================================================
    # TREE OF THOUGHTS SPECIFIC SETTINGS
    # ============================================================================
    
    # Maximum tree depth
    TREE_OF_THOUGHTS_MAX_DEPTH: int = int(
        os.getenv("TREE_OF_THOUGHTS_MAX_DEPTH", "10")
    )
    
    # Maximum branches per node
    TREE_OF_THOUGHTS_MAX_BRANCHES: int = int(
        os.getenv("TREE_OF_THOUGHTS_MAX_BRANCHES", "5")
    )
    
    # Session timeout in seconds
    TREE_OF_THOUGHTS_SESSION_TIMEOUT: int = int(
        os.getenv("TREE_OF_THOUGHTS_SESSION_TIMEOUT", "3600")
    )
    
    @classmethod
    def validate(cls) -> None:
        """Validate reasoning configuration settings"""
        # Validate Recursive Thinking settings
        if cls.RECURSIVE_THINKING_DEFAULT_LATENT_UPDATES < 1:
            raise ValueError("RECURSIVE_THINKING_DEFAULT_LATENT_UPDATES must be at least 1")
        
        if cls.RECURSIVE_THINKING_DEFAULT_MAX_IMPROVEMENTS < 1:
            raise ValueError("RECURSIVE_THINKING_DEFAULT_MAX_IMPROVEMENTS must be at least 1")
        
        if cls.RECURSIVE_THINKING_SESSION_TIMEOUT < 1:
            raise ValueError("RECURSIVE_THINKING_SESSION_TIMEOUT must be at least 1")
        
        # Validate Sequential Thinking settings
        if cls.SEQUENTIAL_THINKING_MAX_THOUGHTS < 1:
            raise ValueError("SEQUENTIAL_THINKING_MAX_THOUGHTS must be at least 1")
        
        # Validate Tree of Thoughts settings
        if cls.TREE_OF_THOUGHTS_MAX_DEPTH < 1:
            raise ValueError("TREE_OF_THOUGHTS_MAX_DEPTH must be at least 1")
        
        if cls.TREE_OF_THOUGHTS_MAX_BRANCHES < 1:
            raise ValueError("TREE_OF_THOUGHTS_MAX_BRANCHES must be at least 1")
