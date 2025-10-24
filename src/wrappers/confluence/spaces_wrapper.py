"""
Confluence Spaces Wrapper Functions
MCP tool registration wrappers for Confluence space operations
"""

from typing import Optional, List
from src.tools.confluence import spaces_tool


async def confluence_get_spaces(
    space_key: Optional[str] = None,
    space_type: Optional[str] = None,
    status: str = "current",
    expand: Optional[List[str]] = None,
    limit: int = 25
) -> str:
    """
    Get Confluence spaces
    
    Args:
        space_key: Specific space key to retrieve (optional). If provided, returns single space.
        space_type: Space type filter - "global" (public) or "personal" (optional)
        status: Space status - "current" (active) or "archived" (default: "current")
        expand: List of fields to expand (optional)
                Available fields: "homepage", "description", "icon", "permissions"
        limit: Maximum number of results (1-100, default: 25)
        
    Returns:
        JSON string with space list or single space details
        
    Example:
        # Get all current spaces
        result = await confluence_get_spaces()
        
        # Get specific space
        result = await confluence_get_spaces(space_key="PROJ")
        
        # Get public spaces with homepage
        result = await confluence_get_spaces(
            space_type="global",
            expand=["homepage", "description"],
            limit=50
        )
        
        # Get archived spaces
        result = await confluence_get_spaces(status="archived")
    """
    return spaces_tool.execute(
        action="get_spaces",
        space_key=space_key,
        space_type=space_type,
        status=status,
        expand=expand,
        limit=limit
    )
