"""
Report Generation Wrappers
"""
from .report_generator_wrapper import generate_report
from .html_builder_wrapper import build_report_from_json

__all__ = [
    "generate_report",
    "build_report_from_json",
]
