"""
Confluence Wrappers Package
"""

from .pages_wrapper import (
    confluence_create_page,
    confluence_get_page,
    confluence_update_page,
    confluence_delete_page
)
from .spaces_wrapper import confluence_get_spaces
from .search_wrapper import confluence_search_pages

__all__ = [
    "confluence_create_page",
    "confluence_get_page",
    "confluence_update_page",
    "confluence_delete_page",
    "confluence_get_spaces",
    "confluence_search_pages"
]
