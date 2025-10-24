"""
JIRA Issues Management Wrappers for MCP Registration
Provides wrapper functions for JIRA issue operations
"""
from typing import Optional, List, Dict, Any
from fastmcp import Context
from src.tools.jira.issues import JiraIssuesManagementTool
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize tool instance
_issues_tool = JiraIssuesManagementTool()


async def jira_search_issues(
    jql: str,
    start_at: int = 0,
    max_results: Optional[int] = None,
    ctx: Context = None
) -> str:
    """
    Search for JIRA issues using JQL (JIRA Query Language)
    
    Filter issues by project, status, assignee, and other criteria using powerful JQL syntax.
    
    **Parameters:**
    - jql (str, required): JQL query string
    - start_at (int): Starting index for pagination (default: 0)
    - max_results (int): Maximum number of results to return (default: from config)
    
    **Example JQL Queries:**
    ```
    # Open issues in specific project
    "project = MYPROJECT AND status = Open"
    
    # High priority bugs assigned to me
    "assignee = currentUser() AND priority = High AND type = Bug"
    
    # Issues created in last 7 days
    "created >= -7d ORDER BY created DESC"
    
    # Search by keyword in summary/description
    "text ~ \"login issue\" AND project = AUTH"
    ```
    
    **Returns:**
    JSON string with search results including:
    - Query summary (total, returned, has_more)
    - Issue list with key details (summary, status, assignee, etc.)
    
    **Use Cases:**
    - Find all open bugs in a project
    - Track issues assigned to specific user
    - Monitor recently created/updated issues
    - Search for issues by keyword
    """
    if ctx:
        ctx.info(f"Searching JIRA issues with JQL: {jql}")
    
    result = await _issues_tool.execute(
        action="search",
        jql=jql,
        start_at=start_at,
        max_results=max_results
    )
    
    if ctx:
        ctx.info("Issue search completed")
    
    return result


async def jira_get_issue_details(
    issue_key: str,
    expand: Optional[List[str]] = None,
    include_history: bool = False,
    ctx: Context = None
) -> str:
    """
    Get detailed information about a specific JIRA issue
    
    Retrieves comprehensive issue details including all fields, metadata, and optionally change history.
    
    **Parameters:**
    - issue_key (str, required): Issue key (e.g., PROJECT-123, DEMO-456)
    - expand (list): Additional fields to expand (e.g., ["changelog", "comments", "attachments"])
    - include_history (bool): Whether to include change history (default: False)
    
    **Valid Expand Options:**
    - changelog: Change history
    - comments: All comments
    - attachments: Attachment details
    - worklog: Work log entries
    - transitions: Available transitions
    
    **Returns:**
    JSON string with comprehensive issue details including:
    - Basic info (key, summary, description)
    - Status and type information
    - People (assignee, reporter, creator)
    - Dates (created, updated, resolved)
    - Classification (labels, components)
    - Custom fields (if configured)
    - Change history (if requested)
    
    **Use Cases:**
    - Review full issue details
    - Track issue history and changes
    - Export issue information
    - Analyze custom field values
    """
    if ctx:
        ctx.info(f"Getting details for issue: {issue_key}")
    
    result = await _issues_tool.execute(
        action="get_details",
        issue_key=issue_key,
        expand=expand,
        include_history=include_history
    )
    
    if ctx:
        ctx.info("Issue details retrieved")
    
    return result


async def jira_create_issue(
    project: str,
    summary: str,
    issue_type: str = "Task",
    description: Optional[str] = None,
    assignee_account_id: Optional[str] = None,
    priority: Optional[str] = None,
    labels: Optional[List[str]] = None,
    custom_fields: Optional[Dict[str, Any]] = None,
    ctx: Context = None
) -> str:
    """
    Create a new JIRA issue
    
    Creates a new issue in the specified project with the provided details.
    
    **Parameters:**
    - project (str, required): Project key (e.g., "DEMO", "PROJECT")
    - summary (str, required): Issue summary/title (max 255 characters)
    - issue_type (str): Issue type (default: "Task", e.g., "Bug", "Story", "Epic")
    - description (str): Detailed description (optional)
    - assignee_account_id (str): Assignee's account ID (optional)
    - priority (str): Priority level (e.g., "Highest", "High", "Medium", "Low", "Lowest")
    - labels (list): List of labels (optional)
    - custom_fields (dict): Custom field values as dict (optional)
    
    **Example:**
    ```python
    result = await jira_create_issue(
        project="MYPROJECT",
        summary="Fix login bug",
        issue_type="Bug",
        description="Users unable to login with SSO",
        priority="High",
        labels=["security", "urgent"]
    )
    ```
    
    **Returns:**
    JSON string with created issue details including:
    - Issue key (e.g., PROJECT-123)
    - Issue ID
    - Web URL for viewing
    - Basic metadata
    
    **Use Cases:**
    - Report bugs or issues
    - Create tasks or stories
    - Log incidents
    - Track feature requests
    """
    if ctx:
        ctx.info(f"Creating issue in project: {project}")
    
    result = await _issues_tool.execute(
        action="create",
        project=project,
        summary=summary,
        issue_type=issue_type,
        description=description,
        assignee_account_id=assignee_account_id,
        priority=priority,
        labels=labels,
        custom_fields=custom_fields
    )
    
    if ctx:
        ctx.info("Issue created successfully")
    
    return result
