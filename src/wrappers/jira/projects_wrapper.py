"""
JIRA Projects Wrapper for MCP Registration
Provides wrapper function for JIRA projects retrieval
"""
from typing import Literal
from fastmcp import Context
from src.tools.jira.projects import JiraProjectsTool
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize tool instance
_projects_tool = JiraProjectsTool()


async def jira_get_projects(
    include_archived: bool = False,
    sort_by: Literal['key', 'name', 'type'] = 'key',
    ctx: Context = None
) -> str:
    """
    Get list of all accessible JIRA projects
    
    Retrieves comprehensive project information including keys, names, descriptions, and leads.
    
    **Parameters:**
    - include_archived (bool): Include archived projects (default: False)
    - sort_by (str): Sort order - 'key', 'name', or 'type' (default: 'key')
    
    **Returns:**
    JSON string with project list including:
    - Summary (total count, project types breakdown)
    - Project details (key, name, description, type, lead, avatar)
    
    **Use Cases:**
    - List available projects for issue creation
    - Find project keys for JQL queries
    - Review project metadata
    - Generate project inventory
    
    **Example:**
    ```python
    # Get active projects sorted by name
    result = await jira_get_projects(
        include_archived=False,
        sort_by="name"
    )
    ```
    """
    if ctx:
        ctx.info("Getting JIRA projects list")
    
    result = await _projects_tool.execute(
        include_archived=include_archived,
        sort_by=sort_by
    )
    
    if ctx:
        ctx.info("Projects list retrieved")
    
    return result
