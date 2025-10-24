"""
Vibe Coding Tool Configuration
Interactive prompt refinement through iterative clarification
"""
import os


class VibeConfig:
    """
    Vibe Coding Tool Configuration
    Settings for interactive prompt refinement tool
    """
    
    # Enable/Disable Vibe Coding Tool
    ENABLE_VIBE_CODING: bool = os.getenv("ENABLE_VIBE_CODING", "true").lower() == "true"
    
    # Maximum refinement stages before auto-completion
    MAX_REFINEMENT_STAGES: int = int(os.getenv("VIBE_MAX_STAGES", "10"))
    
    # Number of alternative suggestions to provide (default: 5)
    NUM_SUGGESTIONS: int = int(os.getenv("VIBE_NUM_SUGGESTIONS", "5"))
    
    # Session timeout (in seconds, default: 1 hour)
    SESSION_TIMEOUT: int = int(os.getenv("VIBE_SESSION_TIMEOUT", "3600"))
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration settings"""
        if cls.NUM_SUGGESTIONS < 3 or cls.NUM_SUGGESTIONS > 10:
            raise ValueError("NUM_SUGGESTIONS must be between 3 and 10")
        
        if cls.MAX_REFINEMENT_STAGES < 1:
            raise ValueError("MAX_REFINEMENT_STAGES must be at least 1")


def get_vibe_config() -> VibeConfig:
    """
    Get validated Vibe Coding configuration.
    
    Returns:
        VibeConfig instance
    """
    VibeConfig.validate()
    return VibeConfig
