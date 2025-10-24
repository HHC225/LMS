"""
JIRA Knowledge Search Wrapper for MCP Registration
Provides wrapper function for JIRA knowledge base search
"""
from typing import Optional
from fastmcp import Context
from src.tools.jira.knowledge import JiraKnowledgeSearchTool
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize tool instance
_knowledge_tool = JiraKnowledgeSearchTool()


async def jira_search_knowledge(
    keyword: str,
    project: Optional[str] = None,
    issue_type: Optional[str] = None,
    max_results: int = 25,
    start_at: int = 0,
    ctx: Context = None
) -> str:
    """
    Search for issues containing specific keywords in knowledge base custom field
    
    Searches the configured knowledge base custom field for matching keywords.
    Automatically fetches all results across multiple pages.
    
    **Parameters:**
    - keyword (str, required): Search keyword
    - project (str): Project key to limit search (optional)
    - issue_type (str): Issue type to limit search (optional)
    - max_results (int): Maximum results per page (default: 25, max: 100)
    - start_at (int): Starting index for pagination (default: 0)
    
    **Returns:**
    JSON string with search results including:
    - Query information and field used
    - Summary (total found, total returned)
    - Issue list with knowledge content preview
    
    **Example:**
    ```python
    # Search all projects
    result = await jira_search_knowledge(
        keyword="database connection"
    )
    
    # Search specific project and type
    result = await jira_search_knowledge(
        keyword="login error",
        project="SUPPORT",
        issue_type="Incident"
    )
    ```
    
    **Use Cases:**
    - Find troubleshooting procedures
    - Search incident response guides
    - Locate configuration documentation
    - Access team knowledge base
    
    **Note:**
    This tool automatically fetches all matching results across multiple pages
    (up to 50 pages safety limit).
    
    **Configuration Required:**
    The knowledge custom field must be configured in configs/jira.py.
    If not configured, an error will be returned with setup instructions.
    """
    if ctx:
        ctx.info(f"Searching knowledge base for: {keyword}")
    
    result = await _knowledge_tool.execute(
        keyword=keyword,
        project=project,
        issue_type=issue_type,
        max_results=max_results,
        start_at=start_at
    )
    
    if ctx:
        ctx.info("Knowledge search completed")
    
    return result
