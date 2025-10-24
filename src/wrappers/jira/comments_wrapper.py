"""
JIRA Comments Management Wrappers for MCP Registration
Provides wrapper functions for JIRA comment operations
"""
from typing import Optional, Dict
from fastmcp import Context
from src.tools.jira.comments import JiraCommentsManagementTool
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize tool instance
_comments_tool = JiraCommentsManagementTool()


async def jira_get_comments(
    issue_key: str,
    start_at: int = 0,
    max_results: int = 50,
    ctx: Context = None
) -> str:
    """
    Get all comments from a JIRA issue
    
    Retrieves comments list with author information, timestamps, and visibility settings.
    
    **Parameters:**
    - issue_key (str, required): Issue key (e.g., PROJECT-123)
    - start_at (int): Starting index for pagination (default: 0)
    - max_results (int): Maximum comments to return (default: 50, max: 100)
    
    **Returns:**
    JSON string with comments list including:
    - Summary (total count, pagination info)
    - Comment details (id, body, author, timestamps)
    
    **Use Cases:**
    - Review issue discussions
    - Export comment history
    - Track communication timeline
    """
    if ctx:
        ctx.info(f"Getting comments for: {issue_key}")
    
    result = await _comments_tool.execute(
        action="get",
        issue_key=issue_key,
        start_at=start_at,
        max_results=max_results
    )
    
    if ctx:
        ctx.info("Comments retrieved")
    
    return result


async def jira_add_comment(
    issue_key: str,
    body: str,
    visibility: Optional[Dict[str, str]] = None,
    ctx: Context = None
) -> str:
    """
    Add a new comment to a JIRA issue
    
    Posts a comment with optional visibility restrictions (private comments).
    
    **Parameters:**
    - issue_key (str, required): Issue key (e.g., PROJECT-123)
    - body (str, required): Comment text (max 32767 characters)
    - visibility (dict): Visibility settings for private comments (optional)
      Format: {"type": "group" or "role", "value": "group-name" or "role-name"}
    
    **Example:**
    ```python
    # Public comment
    result = await jira_add_comment(
        issue_key="PROJECT-123",
        body="This issue has been resolved"
    )
    
    # Private comment (group visibility)
    result = await jira_add_comment(
        issue_key="PROJECT-123",
        body="Internal discussion notes",
        visibility={"type": "group", "value": "jira-developers"}
    )
    
    # Private comment (role visibility)
    result = await jira_add_comment(
        issue_key="PROJECT-123",
        body="Admin-only information",
        visibility={"type": "role", "value": "Administrators"}
    )
    ```
    
    **Returns:**
    JSON string with created comment details
    
    **Use Cases:**
    - Add progress updates
    - Document decisions
    - Communicate with team
    - Add internal notes
    """
    if ctx:
        ctx.info(f"Adding comment to: {issue_key}")
    
    result = await _comments_tool.execute(
        action="add",
        issue_key=issue_key,
        body=body,
        visibility=visibility
    )
    
    if ctx:
        ctx.info("Comment added")
    
    return result


async def jira_update_comment(
    issue_key: str,
    comment_id: str,
    body: str,
    visibility: Optional[Dict[str, str]] = None,
    ctx: Context = None
) -> str:
    """
    Update an existing comment on a JIRA issue
    
    Modifies comment text and/or visibility settings.
    
    **Parameters:**
    - issue_key (str, required): Issue key (e.g., PROJECT-123)
    - comment_id (str, required): Comment ID to update
    - body (str, required): New comment text (max 32767 characters)
    - visibility (dict): Visibility settings (optional)
    
    **Returns:**
    JSON string with updated comment details
    
    **Use Cases:**
    - Correct typos or mistakes
    - Update information
    - Change visibility settings
    """
    if ctx:
        ctx.info(f"Updating comment {comment_id} on: {issue_key}")
    
    result = await _comments_tool.execute(
        action="update",
        issue_key=issue_key,
        comment_id=comment_id,
        body=body,
        visibility=visibility
    )
    
    if ctx:
        ctx.info("Comment updated")
    
    return result


async def jira_delete_comment(
    issue_key: str,
    comment_id: str,
    ctx: Context = None
) -> str:
    """
    Delete a comment from a JIRA issue
    
    Permanently removes a comment. This action cannot be undone!
    
    **Parameters:**
    - issue_key (str, required): Issue key (e.g., PROJECT-123)
    - comment_id (str, required): Comment ID to delete
    
    **Returns:**
    JSON string with deletion confirmation
    
    **Warning:**
    ⚠️ This action is permanent and cannot be undone!
    
    **Use Cases:**
    - Remove spam or inappropriate content
    - Delete duplicate comments
    - Clean up test data
    """
    if ctx:
        ctx.info(f"Deleting comment {comment_id} from: {issue_key}")
    
    result = await _comments_tool.execute(
        action="delete",
        issue_key=issue_key,
        comment_id=comment_id
    )
    
    if ctx:
        ctx.info("Comment deleted")
    
    return result
