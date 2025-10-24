"""
Confluence Search Wrapper Functions
MCP tool registration wrappers for Confluence search operations
"""

from typing import Optional, List
from src.tools.confluence import search_tool


async def confluence_search_pages(
    query: Optional[str] = None,
    space_key: Optional[str] = None,
    title: Optional[str] = None,
    cql: Optional[str] = None,
    expand: Optional[List[str]] = None,
    limit: int = 25,
    start: int = 0
) -> str:
    """
    Search Confluence pages using CQL (Confluence Query Language)
    
    Args:
        query: General search query (searches both title and content)
        space_key: Filter results by space key
        title: Filter by title using partial match
        cql: Custom CQL query (overrides other search parameters)
             CQL examples:
             - 'type=page AND space="PROJ" AND title~"design"'
             - 'text~"documentation" AND created >= "2024-01-01"'
             - 'creator=currentUser() AND lastmodified >= startOfMonth()'
        expand: List of fields to expand (optional)
                Available fields: "body.storage", "body.view", "version", "space", "ancestors"
                Default: ["body.storage", "version", "space", "ancestors"]
        limit: Maximum number of results (1-100, default: 25)
        start: Starting offset for pagination (default: 0)
        
    Returns:
        JSON string with search results including pages, pagination info, and search criteria
        
    Example:
        # Simple text search
        result = await confluence_search_pages(query="project documentation")
        
        # Search in specific space
        result = await confluence_search_pages(
            query="API",
            space_key="DEV"
        )
        
        # Search by title
        result = await confluence_search_pages(title="meeting notes")
        
        # Custom CQL query
        result = await confluence_search_pages(
            cql='type=page AND space="PROJ" AND created >= "2024-01-01"',
            expand=["body.storage", "version"],
            limit=50
        )
        
        # Pagination
        result = await confluence_search_pages(
            query="documentation",
            limit=10,
            start=20  # Get results 21-30
        )
        
    CQL Reference:
        Field operators:
        - = : Exact match
        - != : Not equal
        - ~ : Contains (partial match)
        - !~ : Does not contain
        
        Date operators:
        - >= : Greater than or equal
        - <= : Less than or equal
        
        Functions:
        - currentUser() : Current authenticated user
        - now() : Current date/time
        - startOfDay(), startOfWeek(), startOfMonth(), startOfYear()
        - endOfDay(), endOfWeek(), endOfMonth(), endOfYear()
        
        Common fields:
        - type : Content type (page, blogpost, comment, attachment)
        - space : Space key
        - title : Page title
        - text : Page content
        - creator : User who created the content
        - created : Creation date
        - contributor : User who modified the content
        - lastmodified : Last modification date
    """
    return search_tool.execute(
        action="search_pages",
        query=query,
        space_key=space_key,
        title=title,
        cql=cql,
        expand=expand,
        limit=limit,
        start=start
    )
