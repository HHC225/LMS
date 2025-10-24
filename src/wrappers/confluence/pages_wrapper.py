"""
Confluence Pages Wrapper Functions
MCP tool registration wrappers for Confluence page operations
"""

from typing import Optional, List
from src.tools.confluence import pages_tool


async def confluence_create_page(
    title: str,
    space_key: str,
    content: str,
    parent_id: Optional[str] = None,
    page_type: str = "page"
) -> str:
    """
    Create new Confluence page
    
    Args:
        title: Page title
        space_key: Space key where page will be created
        content: Page content in storage format (HTML)
        parent_id: Parent page ID (optional)
        page_type: Page type - "page" or "blogpost" (default: "page")
        
    Returns:
        JSON string with creation results including page ID, title, space info, URL, and version
        
    Example:
        result = await confluence_create_page(
            title="Project Documentation",
            space_key="PROJ",
            content="<p>This is the project documentation.</p>",
            parent_id="123456"
        )
    """
    return pages_tool.execute(
        action="create",
        title=title,
        space_key=space_key,
        content=content,
        parent_id=parent_id,
        page_type=page_type
    )


async def confluence_get_page(
    page_id: str,
    expand: Optional[List[str]] = None
) -> str:
    """
    Get Confluence page details
    
    Args:
        page_id: Page ID to retrieve
        expand: List of fields to expand (optional)
                Available fields: "body.storage", "body.view", "version", "space", "ancestors"
                Default: ["body.storage", "version", "space", "ancestors"]
        
    Returns:
        JSON string with complete page details including title, content, version, space, and ancestors
        
    Example:
        # Get page with default expand
        result = await confluence_get_page(page_id="123456")
        
        # Get page with custom expand
        result = await confluence_get_page(
            page_id="123456",
            expand=["body.storage", "version", "space"]
        )
    """
    return pages_tool.execute(
        action="get",
        page_id=page_id,
        expand=expand
    )


async def confluence_update_page(
    page_id: str,
    title: str,
    content: str,
    version: int,
    version_message: Optional[str] = None,
    page_type: str = "page"
) -> str:
    """
    Update existing Confluence page
    
    Args:
        page_id: Page ID to update
        title: New page title
        content: New page content in storage format (HTML)
        version: Current version number (for optimistic locking)
        version_message: Version comment/message (optional)
        page_type: Page type - "page" or "blogpost" (default: "page")
        
    Returns:
        JSON string with update results including updated page info and new version number
        
    Example:
        result = await confluence_update_page(
            page_id="123456",
            title="Updated Project Documentation",
            content="<p>This is the updated project documentation.</p>",
            version=5,
            version_message="Updated documentation structure"
        )
    """
    return pages_tool.execute(
        action="update",
        page_id=page_id,
        title=title,
        content=content,
        version=version,
        version_message=version_message,
        page_type=page_type
    )


async def confluence_delete_page(page_id: str) -> str:
    """
    Delete Confluence page
    
    Args:
        page_id: Page ID to delete
        
    Returns:
        JSON string with deletion confirmation
        
    Example:
        result = await confluence_delete_page(page_id="123456")
        
    Warning:
        This action is permanent and cannot be undone. Deleted pages are moved to trash
        but may be permanently deleted after a retention period.
    """
    return pages_tool.execute(
        action="delete",
        page_id=page_id
    )
