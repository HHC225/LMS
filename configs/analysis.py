"""
Code Analysis Tools Configuration
Settings for Code Analysis tool
"""
import os
from pathlib import Path
from .base import ServerConfig


class AnalysisConfig:
    """
    Configuration for code analysis tools.
    Source code analysis and documentation generation settings.
    """
    
    # ============================================================================
    # FEATURE FLAGS
    # ============================================================================
    
    # Code Analysis Tools
    ENABLE_CODE_ANALYSIS: bool = os.getenv(
        "ENABLE_CODE_ANALYSIS", "true"
    ).lower() == "true"
    
    # Feature Flow Analysis Tools
    ENABLE_FEATURE_FLOW_ANALYSIS: bool = os.getenv(
        "ENABLE_FEATURE_FLOW_ANALYSIS", "true"
    ).lower() == "true"
    
    # ============================================================================
    # ANALYSIS SPECIFIC SETTINGS
    # ============================================================================
    
    # Analysis output directory
    ANALYSIS_OUTPUT_DIR: Path = ServerConfig.OUTPUT_DIR / "analysis"
    
    # Default lines per step (for step calculation)
    ANALYSIS_LINES_PER_STEP: int = int(os.getenv("ANALYSIS_LINES_PER_STEP", "300"))
    
    # Minimum lines per step
    ANALYSIS_MIN_LINES_PER_STEP: int = int(os.getenv("ANALYSIS_MIN_LINES_PER_STEP", "100"))
    
    # Maximum lines per step
    ANALYSIS_MAX_LINES_PER_STEP: int = int(os.getenv("ANALYSIS_MAX_LINES_PER_STEP", "500"))
    
    # Default output format
    ANALYSIS_DEFAULT_FORMAT: str = os.getenv("ANALYSIS_DEFAULT_FORMAT", "markdown")
    
    # Enable auto-versioning of analysis files
    ANALYSIS_AUTO_VERSION: bool = os.getenv(
        "ANALYSIS_AUTO_VERSION", "true"
    ).lower() == "true"
    
    # Supported file extensions
    ANALYSIS_SUPPORTED_EXTENSIONS: list = [
        '.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', 
        '.rb', '.php', '.cs', '.swift', '.kt', '.rs'
    ]
    
    # ============================================================================
    # VALIDATION
    # ============================================================================
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration settings"""
        if cls.ANALYSIS_LINES_PER_STEP < cls.ANALYSIS_MIN_LINES_PER_STEP:
            raise ValueError(
                f"ANALYSIS_LINES_PER_STEP ({cls.ANALYSIS_LINES_PER_STEP}) "
                f"must be >= ANALYSIS_MIN_LINES_PER_STEP ({cls.ANALYSIS_MIN_LINES_PER_STEP})"
            )
        
        if cls.ANALYSIS_LINES_PER_STEP > cls.ANALYSIS_MAX_LINES_PER_STEP:
            raise ValueError(
                f"ANALYSIS_LINES_PER_STEP ({cls.ANALYSIS_LINES_PER_STEP}) "
                f"must be <= ANALYSIS_MAX_LINES_PER_STEP ({cls.ANALYSIS_MAX_LINES_PER_STEP})"
            )
        
        return True


# Validate on module load
AnalysisConfig.validate()
