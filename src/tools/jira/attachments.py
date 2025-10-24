"""
JIRA Attachments Management Tool
Unified interface for JIRA attachment operations (list, download)
"""
import json
import re
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

from src.tools.base import BaseTool
from src.wrappers.jira import JiraApiClient, JiraApiError
from configs.jira import get_jira_config, validate_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class JiraAttachmentsManagementTool(BaseTool):
    """
    Unified tool for JIRA attachment management
    Supports list and download operations
    """
    
    def __init__(self):
        super().__init__(
            name="jira_attachments",
            description="Manage JIRA issue attachments (list, download)"
        )
        self.config = get_jira_config()
        validate_config(self.config)
        self.client = JiraApiClient(self.config)
        self.default_download_dir = Path("./download")
    
    async def execute(
        self,
        action: str,
        issue_key: str,
        **kwargs
    ) -> str:
        """
        Execute attachment management action
        
        Args:
            action: Action to perform - 'list' or 'download'
            issue_key: Issue key (required)
            **kwargs: Action-specific parameters
            
        Actions:
            list: List attachments for issue
                (no additional parameters required)
            
            download: Download attachment
                - attachment_id (str): Attachment ID (optional if content_url provided)
                - content_url (str): Direct content URL (optional if attachment_id provided)
                - output_path (str): Full output path
                - filename (str): Filename to save as
            
        Returns:
            JSON string with action results
        """
        try:
            # Validate issue key
            if not issue_key or not self._is_valid_issue_key(issue_key):
                return json.dumps({
                    "success": False,
                    "error": "Invalid issue key format. Expected format: PROJECT-123"
                }, ensure_ascii=False, indent=2)
            
            if action == "list":
                return await self._list_attachments(issue_key, **kwargs)
            elif action == "download":
                return await self._download_attachment(issue_key, **kwargs)
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid action: {action}. Valid actions: list, download"
                }, ensure_ascii=False, indent=2)
        
        except Exception as e:
            logger.error(f"Error in attachments management: {str(e)}", exc_info=True)
            return json.dumps({
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }, ensure_ascii=False, indent=2)
    
    async def _list_attachments(self, issue_key: str, **kwargs) -> str:
        """List attachments for issue"""
        try:
            logger.info(f"Listing attachments for: {issue_key}")
            
            issue = self.client.get_issue(issue_key, expand=['attachment'])
            attachments = issue.get('fields', {}).get('attachment', [])
            
            formatted_result = self._format_attachments(attachments, issue_key)
            
            logger.info(f"Attachments listed: {len(attachments)} attachments")
            
            return json.dumps({
                "success": True,
                "action": "list",
                "data": formatted_result,
                "timestamp": datetime.now().isoformat()
            }, ensure_ascii=False, indent=2)
            
        except JiraApiError as e:
            logger.error(f"JIRA API error listing attachments: {e.message}")
            return json.dumps({
                "success": False,
                "error": f"JIRA API Error: {e.message}",
                "status_code": e.status_code
            }, ensure_ascii=False, indent=2)
    
    async def _download_attachment(
        self,
        issue_key: str,
        attachment_id: Optional[str] = None,
        content_url: Optional[str] = None,
        output_path: Optional[str] = None,
        filename: Optional[str] = None,
        **kwargs
    ) -> str:
        """Download attachment"""
        try:
            logger.info(f"Downloading attachment for: {issue_key}")
            
            if not attachment_id and not content_url:
                return json.dumps({
                    "success": False,
                    "error": "Either attachment_id or content_url must be provided"
                }, ensure_ascii=False, indent=2)
            
            # Get attachment info if needed
            if attachment_id:
                attachment_info = await self._get_attachment_info(issue_key, attachment_id)
                if not attachment_info:
                    return json.dumps({
                        "success": False,
                        "error": f"Attachment {attachment_id} not found in issue {issue_key}"
                    }, ensure_ascii=False, indent=2)
                
                content_url = attachment_info['content_url']
                original_filename = attachment_info['filename']
            else:
                original_filename = self._extract_filename_from_url(content_url)
            
            # Determine save path
            if output_path:
                save_path = Path(output_path)
            elif filename:
                self.default_download_dir.mkdir(parents=True, exist_ok=True)
                save_path = self.default_download_dir / filename
            else:
                self.default_download_dir.mkdir(parents=True, exist_ok=True)
                save_path = self.default_download_dir / original_filename
            
            # Download file
            logger.info(f"Downloading from: {content_url}")
            file_content = self.client.download_attachment(content_url)
            
            # Save file
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'wb') as f:
                f.write(file_content)
            
            file_size = len(file_content)
            
            logger.info(f"Attachment downloaded: {save_path} ({file_size} bytes)")
            
            return json.dumps({
                "success": True,
                "action": "download",
                "data": {
                    "issue_key": issue_key,
                    "filename": save_path.name,
                    "saved_path": str(save_path.absolute()),
                    "size": file_size,
                    "size_readable": self._format_file_size(file_size)
                },
                "message": f"Attachment downloaded to {save_path}",
                "timestamp": datetime.now().isoformat()
            }, ensure_ascii=False, indent=2)
            
        except JiraApiError as e:
            logger.error(f"JIRA API error downloading attachment: {e.message}")
            return json.dumps({
                "success": False,
                "error": f"JIRA API Error: {e.message}",
                "status_code": e.status_code
            }, ensure_ascii=False, indent=2)
    
    # Helper methods
    def _is_valid_issue_key(self, issue_key: str) -> bool:
        """Validate issue key format"""
        pattern = r'^[A-Z][A-Z0-9]*-[0-9]+$'
        return bool(re.match(pattern, issue_key))
    
    async def _get_attachment_info(self, issue_key: str, attachment_id: str) -> Optional[dict]:
        """Get attachment info by ID"""
        try:
            issue = self.client.get_issue(issue_key, expand=['attachment'])
            attachments = issue.get('fields', {}).get('attachment', [])
            
            for att in attachments:
                if att.get('id') == attachment_id:
                    return {
                        'content_url': att.get('content'),
                        'filename': att.get('filename')
                    }
            return None
        except Exception as e:
            logger.error(f"Error getting attachment info: {str(e)}")
            return None
    
    def _extract_filename_from_url(self, url: str) -> str:
        """Extract filename from URL"""
        from urllib.parse import urlparse, unquote
        
        path = urlparse(url).path
        filename = unquote(path.split('/')[-1])
        
        if not filename:
            filename = f"attachment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return filename
    
    def _format_attachments(self, attachments: list, issue_key: str) -> dict:
        """Format attachments list"""
        return {
            "issue_key": issue_key,
            "total_count": len(attachments),
            "attachments": [
                {
                    "id": att.get('id'),
                    "filename": att.get('filename'),
                    "size": att.get('size'),
                    "size_readable": self._format_file_size(att.get('size', 0)),
                    "mime_type": att.get('mimeType'),
                    "created": att.get('created'),
                    "author": {
                        "display_name": att.get('author', {}).get('displayName'),
                        "email": att.get('author', {}).get('emailAddress')
                    } if att.get('author') else None,
                    "content_url": att.get('content'),
                    "thumbnail_url": att.get('thumbnail')
                }
                for att in attachments
            ]
        }
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        if size_bytes == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.2f} {units[unit_index]}"


# Tool instance for FastMCP registration
jira_attachments_tool = JiraAttachmentsManagementTool()
