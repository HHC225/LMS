"""
Report Generator Configuration
Settings for IT report generation tool
"""
import os
from pathlib import Path
from .base import ServerConfig


class ReportConfig:
    """
    Configuration for report generation tools.
    Converts raw IT content into professional HTML reports.
    """
    
    # ============================================================================
    # FEATURE FLAGS
    # ============================================================================
    
    # Enable Report Generator
    ENABLE_REPORT_GENERATOR: bool = os.getenv(
        "ENABLE_REPORT_GENERATOR", "true"
    ).lower() == "true"
    
    # ============================================================================
    # REPORT SPECIFIC SETTINGS
    # ============================================================================
    
    # Report output directory
    REPORT_OUTPUT_DIR: Path = ServerConfig.OUTPUT_DIR / "reports"
    
    # Templates directory (inside src/tools/report)
    REPORT_TEMPLATES_DIR: Path = ServerConfig.BASE_DIR / "src" / "tools" / "report" / "templates"
    
    # Default report format
    REPORT_DEFAULT_FORMAT: str = os.getenv("REPORT_DEFAULT_FORMAT", "html")
    
    # Enable auto-opening of generated reports
    REPORT_AUTO_OPEN: bool = os.getenv(
        "REPORT_AUTO_OPEN", "false"
    ).lower() == "true"
    
    # Report filename pattern
    REPORT_FILENAME_PATTERN: str = os.getenv(
        "REPORT_FILENAME_PATTERN", "{report_type}_{timestamp}.html"
    )
    
    # Maximum content length for reports (in characters)
    REPORT_MAX_CONTENT_LENGTH: int = int(os.getenv(
        "REPORT_MAX_CONTENT_LENGTH", "50000"
    ))
    
    # Enable JSON validation
    REPORT_VALIDATE_JSON: bool = os.getenv(
        "REPORT_VALIDATE_JSON", "true"
    ).lower() == "true"
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure all required directories exist"""
        cls.REPORT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.REPORT_TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration settings"""
        # Ensure directories exist
        cls.ensure_directories()
        
        # Validate max content length
        if cls.REPORT_MAX_CONTENT_LENGTH <= 0:
            raise ValueError("REPORT_MAX_CONTENT_LENGTH must be positive")
        
        # Validate format
        valid_formats = ["html", "pdf", "markdown"]
        if cls.REPORT_DEFAULT_FORMAT not in valid_formats:
            raise ValueError(f"Invalid report format. Must be one of: {valid_formats}")
