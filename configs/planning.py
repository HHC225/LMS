"""
Planning Tools Configuration
Settings for Planning and WBS Execution tools
"""
import os
from pathlib import Path
from .base import ServerConfig


class PlanningConfig:
    """
    Configuration for planning and project management tools.
    WBS generation and execution tracking settings.
    """
    
    # ============================================================================
    # FEATURE FLAGS
    # ============================================================================
    
    # Planning Tools
    ENABLE_PLANNING: bool = os.getenv(
        "ENABLE_PLANNING", "true"
    ).lower() == "true"
    
    # WBS Execution Tools
    ENABLE_WBS_EXECUTION: bool = os.getenv(
        "ENABLE_WBS_EXECUTION", "true"
    ).lower() == "true"
    
    # ============================================================================
    # PLANNING SPECIFIC SETTINGS
    # ============================================================================
    
    # Planning output directory
    PLANNING_OUTPUT_DIR: Path = ServerConfig.OUTPUT_DIR / "planning"
    
    # Default WBS filename
    PLANNING_WBS_FILENAME: str = os.getenv("PLANNING_WBS_FILENAME", "WBS.md")
    
    # Planning format
    PLANNING_DEFAULT_FORMAT: str = os.getenv("PLANNING_DEFAULT_FORMAT", "markdown")
    
    # Enable auto-versioning
    PLANNING_AUTO_VERSION: bool = os.getenv(
        "PLANNING_AUTO_VERSION", "true"
    ).lower() == "true"
    
    # ============================================================================
    # WBS EXECUTION SPECIFIC SETTINGS
    # ============================================================================
    
    # WBS execution tracking directory
    WBS_EXECUTION_TRACKING_DIR: Path = PLANNING_OUTPUT_DIR / "execution"
    
    # Default status tracking format
    WBS_EXECUTION_STATUS_FORMAT: str = os.getenv(
        "WBS_EXECUTION_STATUS_FORMAT", "json"
    )
    
    # Enable progress reporting
    WBS_EXECUTION_ENABLE_PROGRESS: bool = os.getenv(
        "WBS_EXECUTION_ENABLE_PROGRESS", "true"
    ).lower() == "true"
    
    @classmethod
    def validate(cls) -> None:
        """Validate planning configuration settings"""
        valid_formats = ["markdown", "json", "yaml"]
        if cls.PLANNING_DEFAULT_FORMAT not in valid_formats:
            raise ValueError(f"PLANNING_DEFAULT_FORMAT must be one of: {valid_formats}")
        
        valid_status_formats = ["json", "yaml", "markdown"]
        if cls.WBS_EXECUTION_STATUS_FORMAT not in valid_status_formats:
            raise ValueError(f"WBS_EXECUTION_STATUS_FORMAT must be one of: {valid_status_formats}")
        
        # Ensure planning directories exist
        cls.PLANNING_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.WBS_EXECUTION_TRACKING_DIR.mkdir(parents=True, exist_ok=True)
