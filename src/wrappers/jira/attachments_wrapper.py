"""
JIRA Attachments Management Wrappers for MCP Registration
Provides wrapper functions for JIRA attachment operations
"""
from typing import Optional
from fastmcp import Context
from src.tools.jira.attachments import JiraAttachmentsManagementTool
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize tool instance
_attachments_tool = JiraAttachmentsManagementTool()


async def jira_list_attachments(
    issue_key: str,
    ctx: Context = None
) -> str:
    """
    Get list of all attachments for a JIRA issue
    
    Retrieves attachment metadata including filename, size, author, and download URLs.
    
    **Parameters:**
    - issue_key (str, required): Issue key (e.g., PROJECT-123)
    
    **Returns:**
    JSON string with attachment list including:
    - Total attachment count
    - Attachment details (id, filename, size, mime type, author, URLs)
    
    **Use Cases:**
    - Check what files are attached to an issue
    - Find specific attachments before downloading
    - Review attachment metadata
    - Export attachment inventory
    """
    if ctx:
        ctx.info(f"Listing attachments for: {issue_key}")
    
    result = await _attachments_tool.execute(
        action="list",
        issue_key=issue_key
    )
    
    if ctx:
        ctx.info("Attachments listed")
    
    return result


async def jira_download_attachment(
    issue_key: str,
    attachment_id: Optional[str] = None,
    content_url: Optional[str] = None,
    output_path: Optional[str] = None,
    filename: Optional[str] = None,
    ctx: Context = None
) -> str:
    """
    Download an attachment from a JIRA issue
    
    Downloads attachment to local filesystem. Can specify by attachment ID or direct URL.
    
    **Parameters:**
    - issue_key (str, required): Issue key (e.g., PROJECT-123)
    - attachment_id (str): Attachment ID (optional if content_url provided)
    - content_url (str): Direct content URL (optional if attachment_id provided)
    - output_path (str): Full output path including filename (optional)
    - filename (str): Filename to save as (optional, used with default dir)
    
    **Note:**
    If neither output_path nor filename is specified, the original filename will be used
    in the default download directory (./download)
    
    **Example:**
    ```python
    # Download by attachment ID
    result = await jira_download_attachment(
        issue_key="PROJECT-123",
        attachment_id="10001",
        filename="downloaded_file.pdf"
    )
    
    # Download by URL to specific path
    result = await jira_download_attachment(
        issue_key="PROJECT-123",
        content_url="https://jira.example.com/secure/attachment/10001/file.pdf",
        output_path="/path/to/save/file.pdf"
    )
    ```
    
    **Returns:**
    JSON string with download result including:
    - Saved file path
    - File size (bytes and human-readable)
    - Filename
    
    **Use Cases:**
    - Download logs for analysis
    - Save screenshots or documentation
    - Backup attachments
    - Access referenced files
    """
    if ctx:
        ctx.info(f"Downloading attachment from: {issue_key}")
    
    result = await _attachments_tool.execute(
        action="download",
        issue_key=issue_key,
        attachment_id=attachment_id,
        content_url=content_url,
        output_path=output_path,
        filename=filename
    )
    
    if ctx:
        ctx.info("Attachment downloaded")
    
    return result
