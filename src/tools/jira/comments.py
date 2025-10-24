"""
JIRA Comments Management Tool
Unified interface for JIRA comment operations (get, add, update, delete)
"""
import json
import re
from typing import Optional, Dict
from datetime import datetime

from src.tools.base import BaseTool
from src.wrappers.jira import JiraApiClient, JiraApiError
from configs.jira import get_jira_config, validate_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class JiraCommentsManagementTool(BaseTool):
    """
    Unified tool for JIRA comment management
    Supports get, add, update, and delete operations
    """
    
    def __init__(self):
        super().__init__(
            name="jira_comments",
            description="Manage JIRA issue comments (get, add, update, delete)"
        )
        self.config = get_jira_config()
        validate_config(self.config)
        self.client = JiraApiClient(self.config)
    
    async def execute(
        self,
        action: str,
        issue_key: str,
        **kwargs
    ) -> str:
        """
        Execute comment management action
        
        Args:
            action: Action to perform - 'get', 'add', 'update', or 'delete'
            issue_key: Issue key (required for all actions)
            **kwargs: Action-specific parameters
            
        Actions:
            get: Get comments list
                - start_at (int): Starting index
                - max_results (int): Maximum results
            
            add: Add new comment
                - body (str, required): Comment text
                - visibility (dict): Visibility settings
            
            update: Update existing comment
                - comment_id (str, required): Comment ID
                - body (str, required): New comment text
                - visibility (dict): Visibility settings
            
            delete: Delete comment
                - comment_id (str, required): Comment ID
            
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
            
            if action == "get":
                return await self._get_comments(issue_key, **kwargs)
            elif action == "add":
                return await self._add_comment(issue_key, **kwargs)
            elif action == "update":
                return await self._update_comment(issue_key, **kwargs)
            elif action == "delete":
                return await self._delete_comment(issue_key, **kwargs)
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid action: {action}. Valid actions: get, add, update, delete"
                }, ensure_ascii=False, indent=2)
        
        except Exception as e:
            logger.error(f"Error in comments management: {str(e)}", exc_info=True)
            return json.dumps({
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }, ensure_ascii=False, indent=2)
    
    async def _get_comments(
        self,
        issue_key: str,
        start_at: int = 0,
        max_results: int = 50,
        **kwargs
    ) -> str:
        """Get comments list"""
        try:
            logger.info(f"Getting comments for: {issue_key}")
            
            if start_at < 0:
                return json.dumps({
                    "success": False,
                    "error": "start_at must be 0 or greater"
                }, ensure_ascii=False, indent=2)
            
            if max_results < 1 or max_results > 100:
                return json.dumps({
                    "success": False,
                    "error": "max_results must be between 1 and 100"
                }, ensure_ascii=False, indent=2)
            
            comments_response = self.client.get_comments(
                issue_key=issue_key,
                start_at=start_at,
                max_results=max_results
            )
            
            formatted_result = self._format_comments(comments_response, issue_key)
            
            logger.info(f"Comments retrieved: {len(comments_response.get('comments', []))} comments")
            
            return json.dumps({
                "success": True,
                "action": "get",
                "data": formatted_result,
                "timestamp": datetime.now().isoformat()
            }, ensure_ascii=False, indent=2)
            
        except JiraApiError as e:
            logger.error(f"JIRA API error getting comments: {e.message}")
            return json.dumps({
                "success": False,
                "error": f"JIRA API Error: {e.message}",
                "status_code": e.status_code
            }, ensure_ascii=False, indent=2)
    
    async def _add_comment(
        self,
        issue_key: str,
        body: str,
        visibility: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> str:
        """Add new comment"""
        try:
            logger.info(f"Adding comment to: {issue_key}")
            
            # Validate body
            if not body or not isinstance(body, str) or not body.strip():
                return json.dumps({
                    "success": False,
                    "error": "body is required and cannot be empty"
                }, ensure_ascii=False, indent=2)
            
            if len(body) > 32767:
                return json.dumps({
                    "success": False,
                    "error": "body must be 32767 characters or less"
                }, ensure_ascii=False, indent=2)
            
            # Validate visibility if provided
            if visibility:
                validation_error = self._validate_visibility(visibility)
                if validation_error:
                    return json.dumps({
                        "success": False,
                        "error": validation_error
                    }, ensure_ascii=False, indent=2)
            
            comment = self.client.add_comment(
                issue_key=issue_key,
                body=body,
                visibility=visibility
            )
            
            formatted_result = self._format_comment(comment, issue_key)
            
            logger.info(f"Comment added: {comment.get('id')}")
            
            return json.dumps({
                "success": True,
                "action": "add",
                "data": formatted_result,
                "message": f"Comment added to {issue_key}",
                "timestamp": datetime.now().isoformat()
            }, ensure_ascii=False, indent=2)
            
        except JiraApiError as e:
            logger.error(f"JIRA API error adding comment: {e.message}")
            return json.dumps({
                "success": False,
                "error": f"JIRA API Error: {e.message}",
                "status_code": e.status_code
            }, ensure_ascii=False, indent=2)
    
    async def _update_comment(
        self,
        issue_key: str,
        comment_id: str,
        body: str,
        visibility: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> str:
        """Update existing comment"""
        try:
            logger.info(f"Updating comment {comment_id} on: {issue_key}")
            
            if not comment_id:
                return json.dumps({
                    "success": False,
                    "error": "comment_id is required"
                }, ensure_ascii=False, indent=2)
            
            if not body or not isinstance(body, str) or not body.strip():
                return json.dumps({
                    "success": False,
                    "error": "body is required and cannot be empty"
                }, ensure_ascii=False, indent=2)
            
            if len(body) > 32767:
                return json.dumps({
                    "success": False,
                    "error": "body must be 32767 characters or less"
                }, ensure_ascii=False, indent=2)
            
            if visibility:
                validation_error = self._validate_visibility(visibility)
                if validation_error:
                    return json.dumps({
                        "success": False,
                        "error": validation_error
                    }, ensure_ascii=False, indent=2)
            
            comment = self.client.update_comment(
                issue_key=issue_key,
                comment_id=comment_id,
                body=body,
                visibility=visibility
            )
            
            formatted_result = self._format_comment(comment, issue_key)
            
            logger.info(f"Comment updated: {comment_id}")
            
            return json.dumps({
                "success": True,
                "action": "update",
                "data": formatted_result,
                "message": f"Comment {comment_id} updated on {issue_key}",
                "timestamp": datetime.now().isoformat()
            }, ensure_ascii=False, indent=2)
            
        except JiraApiError as e:
            logger.error(f"JIRA API error updating comment: {e.message}")
            return json.dumps({
                "success": False,
                "error": f"JIRA API Error: {e.message}",
                "status_code": e.status_code
            }, ensure_ascii=False, indent=2)
    
    async def _delete_comment(
        self,
        issue_key: str,
        comment_id: str,
        **kwargs
    ) -> str:
        """Delete comment"""
        try:
            logger.info(f"Deleting comment {comment_id} from: {issue_key}")
            
            if not comment_id:
                return json.dumps({
                    "success": False,
                    "error": "comment_id is required"
                }, ensure_ascii=False, indent=2)
            
            self.client.delete_comment(
                issue_key=issue_key,
                comment_id=comment_id
            )
            
            logger.info(f"Comment deleted: {comment_id}")
            
            return json.dumps({
                "success": True,
                "action": "delete",
                "data": {
                    "issue_key": issue_key,
                    "comment_id": comment_id,
                    "deleted": True
                },
                "message": f"Comment {comment_id} deleted from {issue_key}",
                "timestamp": datetime.now().isoformat()
            }, ensure_ascii=False, indent=2)
            
        except JiraApiError as e:
            logger.error(f"JIRA API error deleting comment: {e.message}")
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
    
    def _validate_visibility(self, visibility: dict) -> Optional[str]:
        """Validate visibility settings"""
        if not isinstance(visibility, dict):
            return "visibility must be a dict with 'type' and 'value' keys"
        
        if 'type' not in visibility or 'value' not in visibility:
            return "visibility must have 'type' and 'value' keys"
        
        if visibility['type'] not in ['group', 'role']:
            return "visibility type must be 'group' or 'role'"
        
        return None
    
    def _format_comments(self, comments_response: dict, issue_key: str) -> dict:
        """Format comments list"""
        comments = comments_response.get('comments', [])
        
        return {
            "issue_key": issue_key,
            "summary": {
                "total": comments_response.get('total', 0),
                "start_at": comments_response.get('startAt', 0),
                "max_results": comments_response.get('maxResults', 0),
                "returned": len(comments)
            },
            "comments": [
                {
                    "id": c.get('id'),
                    "body": c.get('body'),
                    "author": {
                        "account_id": c.get('author', {}).get('accountId'),
                        "display_name": c.get('author', {}).get('displayName'),
                        "email": c.get('author', {}).get('emailAddress')
                    } if c.get('author') else None,
                    "created": c.get('created'),
                    "updated": c.get('updated'),
                    "visibility": c.get('visibility')
                }
                for c in comments
            ]
        }
    
    def _format_comment(self, comment: dict, issue_key: str) -> dict:
        """Format single comment"""
        return {
            "issue_key": issue_key,
            "comment_id": comment.get('id'),
            "body": comment.get('body'),
            "author": {
                "account_id": comment.get('author', {}).get('accountId'),
                "display_name": comment.get('author', {}).get('displayName'),
                "email": comment.get('author', {}).get('emailAddress')
            } if comment.get('author') else None,
            "created": comment.get('created'),
            "updated": comment.get('updated'),
            "visibility": comment.get('visibility'),
            "self": comment.get('self')
        }


# Tool instance for FastMCP registration
jira_comments_tool = JiraCommentsManagementTool()
