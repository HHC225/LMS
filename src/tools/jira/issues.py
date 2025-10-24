"""
JIRA Issues Management Tool
Unified interface for JIRA issue operations (search, get_details, create)
"""
import json
import re
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.tools.base import BaseTool
from src.wrappers.jira import JiraApiClient, JiraApiError
from configs.jira import get_jira_config, validate_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class JiraIssuesManagementTool(BaseTool):
    """
    Unified tool for JIRA issue management
    Supports search, get details, and create operations
    """
    
    def __init__(self):
        super().__init__(
            name="jira_issues",
            description="Manage JIRA issues (search, get details, create)"
        )
        self.config = get_jira_config()
        validate_config(self.config)
        self.client = JiraApiClient(self.config)
    
    async def execute(
        self,
        action: str,
        **kwargs
    ) -> str:
        """
        Execute issue management action
        
        Args:
            action: Action to perform - 'search', 'get_details', or 'create'
            **kwargs: Action-specific parameters
            
        Actions:
            search: Search issues using JQL
                - jql (str, required): JQL query
                - start_at (int): Starting index
                - max_results (int): Maximum results
            
            get_details: Get issue details by key
                - issue_key (str, required): Issue key (e.g., PROJECT-123)
                - expand (list): Fields to expand
                - include_history (bool): Include change history
            
            create: Create new issue
                - project (str, required): Project key
                - summary (str, required): Issue summary
                - issue_type (str): Issue type (default: Task)
                - description (str): Description
                - assignee_account_id (str): Assignee
                - priority (str): Priority level
                - labels (list): Labels
                - custom_fields (dict): Custom fields
            
        Returns:
            JSON string with action results
        """
        try:
            if action == "search":
                return await self._search_issues(**kwargs)
            elif action == "get_details":
                return await self._get_issue_details(**kwargs)
            elif action == "create":
                return await self._create_issue(**kwargs)
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid action: {action}. Valid actions: search, get_details, create"
                }, ensure_ascii=False, indent=2)
        
        except Exception as e:
            logger.error(f"Error in issues management: {str(e)}", exc_info=True)
            return json.dumps({
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }, ensure_ascii=False, indent=2)
    
    async def _search_issues(
        self,
        jql: str,
        start_at: int = 0,
        max_results: Optional[int] = None,
        **kwargs
    ) -> str:
        """Search issues using JQL"""
        try:
            logger.info(f"Searching issues with JQL: {jql}")
            
            # Validate inputs
            if not jql or not jql.strip():
                return json.dumps({
                    "success": False,
                    "error": "JQL query cannot be empty"
                }, ensure_ascii=False, indent=2)
            
            if start_at < 0:
                return json.dumps({
                    "success": False,
                    "error": "start_at must be 0 or greater"
                }, ensure_ascii=False, indent=2)
            
            if max_results is not None and (max_results < 1 or max_results > 1000):
                return json.dumps({
                    "success": False,
                    "error": "max_results must be between 1 and 1000"
                }, ensure_ascii=False, indent=2)
            
            # Execute search
            result = self.client.search_issues(
                jql=jql.strip(),
                start_at=start_at,
                max_results=max_results
            )
            
            # Format response
            formatted_result = self._format_search_result(result, jql)
            
            logger.info(f"Search completed: {result['total']} total, {len(result['issues'])} returned")
            
            return json.dumps({
                "success": True,
                "action": "search",
                "data": formatted_result,
                "timestamp": datetime.now().isoformat()
            }, ensure_ascii=False, indent=2)
            
        except JiraApiError as e:
            logger.error(f"JIRA API error during search: {e.message}")
            return json.dumps({
                "success": False,
                "error": f"JIRA API Error: {e.message}",
                "status_code": e.status_code
            }, ensure_ascii=False, indent=2)
    
    async def _get_issue_details(
        self,
        issue_key: str,
        expand: Optional[List[str]] = None,
        include_history: bool = False,
        **kwargs
    ) -> str:
        """Get issue details by key"""
        try:
            logger.info(f"Getting issue details: {issue_key}")
            
            # Validate issue key format
            if not issue_key or not self._is_valid_issue_key(issue_key):
                return json.dumps({
                    "success": False,
                    "error": "Invalid issue key format. Expected format: PROJECT-123"
                }, ensure_ascii=False, indent=2)
            
            # Prepare expand fields
            expand_fields = expand or []
            if include_history and 'changelog' not in expand_fields:
                expand_fields.append('changelog')
            
            # Get issue details
            issue = self.client.get_issue(
                issue_key=issue_key,
                expand=expand_fields if expand_fields else None
            )
            
            # Format response
            formatted_result = self._format_issue_details(issue, include_history)
            
            logger.info(f"Issue details retrieved: {issue_key}")
            
            return json.dumps({
                "success": True,
                "action": "get_details",
                "data": formatted_result,
                "timestamp": datetime.now().isoformat()
            }, ensure_ascii=False, indent=2)
            
        except JiraApiError as e:
            logger.error(f"JIRA API error getting issue details: {e.message}")
            return json.dumps({
                "success": False,
                "error": f"JIRA API Error: {e.message}",
                "status_code": e.status_code
            }, ensure_ascii=False, indent=2)
    
    async def _create_issue(
        self,
        project: str,
        summary: str,
        issue_type: str = "Task",
        description: Optional[str] = None,
        assignee_account_id: Optional[str] = None,
        priority: Optional[str] = None,
        labels: Optional[List[str]] = None,
        custom_fields: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """Create new issue"""
        try:
            logger.info(f"Creating issue: {project} - {summary}")
            
            # Validate inputs
            validation_error = self._validate_create_inputs(project, summary, issue_type, priority)
            if validation_error:
                return json.dumps({
                    "success": False,
                    "error": validation_error
                }, ensure_ascii=False, indent=2)
            
            # Build issue fields
            fields = {
                "project": {"key": project},
                "summary": summary,
                "issuetype": {"name": issue_type}
            }
            
            # Add optional fields
            if description:
                fields["description"] = description
            if assignee_account_id:
                fields["assignee"] = {"accountId": assignee_account_id}
            if priority:
                fields["priority"] = {"name": priority}
            if labels:
                fields["labels"] = labels
            if custom_fields:
                fields.update(custom_fields)
            
            # Create issue
            created_issue = self.client.create_issue(fields=fields)
            
            # Format response
            formatted_result = self._format_created_issue(created_issue)
            
            logger.info(f"Issue created successfully: {created_issue.get('key')}")
            
            return json.dumps({
                "success": True,
                "action": "create",
                "data": formatted_result,
                "message": f"Issue {created_issue.get('key')} created successfully",
                "timestamp": datetime.now().isoformat()
            }, ensure_ascii=False, indent=2)
            
        except JiraApiError as e:
            logger.error(f"JIRA API error creating issue: {e.message}")
            return json.dumps({
                "success": False,
                "error": f"JIRA API Error: {e.message}",
                "status_code": e.status_code,
                "details": e.response_data
            }, ensure_ascii=False, indent=2)
    
    # Helper methods
    def _is_valid_issue_key(self, issue_key: str) -> bool:
        """Validate issue key format (PROJECT-123)"""
        pattern = r'^[A-Z][A-Z0-9]*-[0-9]+$'
        return bool(re.match(pattern, issue_key))
    
    def _validate_create_inputs(
        self,
        project: str,
        summary: str,
        issue_type: str,
        priority: Optional[str]
    ) -> Optional[str]:
        """Validate create issue inputs"""
        if not project or not isinstance(project, str):
            return "project is required and must be a string"
        
        if not re.match(r'^[A-Z][A-Z0-9]*$', project):
            return "project must contain only uppercase letters and numbers"
        
        if not summary or not isinstance(summary, str) or not summary.strip():
            return "summary is required and cannot be empty"
        
        if len(summary) > 255:
            return "summary must be 255 characters or less"
        
        if not issue_type or not isinstance(issue_type, str):
            return "issue_type must be a string"
        
        if priority:
            valid_priorities = ["Highest", "High", "Medium", "Low", "Lowest"]
            if priority not in valid_priorities:
                return f"priority must be one of: {', '.join(valid_priorities)}"
        
        return None
    
    def _format_search_result(self, result: dict, jql: str) -> dict:
        """Format search result"""
        issues = result.get('issues', [])
        
        return {
            "query": {"jql": jql, "executed_at": datetime.now().isoformat()},
            "summary": {
                "total": result.get('total', 0),
                "start_at": result.get('startAt', 0),
                "max_results": result.get('maxResults', 0),
                "returned": len(issues),
                "has_more": result.get('startAt', 0) + len(issues) < result.get('total', 0)
            },
            "issues": [self._format_issue_summary(issue) for issue in issues]
        }
    
    def _format_issue_summary(self, issue: dict) -> dict:
        """Format issue summary for list"""
        fields = issue.get('fields', {})
        return {
            "key": issue.get('key'),
            "id": issue.get('id'),
            "summary": fields.get('summary'),
            "description": self._truncate_text(fields.get('description'), 200),
            "status": {
                "name": fields.get('status', {}).get('name'),
                "category": fields.get('status', {}).get('statusCategory', {}).get('name')
            },
            "issue_type": fields.get('issuetype', {}).get('name'),
            "project": {
                "key": fields.get('project', {}).get('key'),
                "name": fields.get('project', {}).get('name')
            },
            "assignee": self._format_user(fields.get('assignee')),
            "priority": fields.get('priority', {}).get('name') if fields.get('priority') else None,
            "created": fields.get('created'),
            "updated": fields.get('updated')
        }
    
    def _format_issue_details(self, issue: dict, include_history: bool) -> dict:
        """Format detailed issue information"""
        fields = issue.get('fields', {})
        
        result = {
            "basic": {
                "key": issue.get('key'),
                "id": issue.get('id'),
                "self": issue.get('self'),
                "summary": fields.get('summary'),
                "description": fields.get('description')
            },
            "status": {
                "name": fields.get('status', {}).get('name'),
                "category": fields.get('status', {}).get('statusCategory', {}).get('name')
            },
            "issue_type": fields.get('issuetype', {}).get('name'),
            "project": {
                "key": fields.get('project', {}).get('key'),
                "name": fields.get('project', {}).get('name')
            },
            "people": {
                "assignee": self._format_user(fields.get('assignee')),
                "reporter": self._format_user(fields.get('reporter')),
                "creator": self._format_user(fields.get('creator'))
            },
            "priority": fields.get('priority', {}).get('name') if fields.get('priority') else None,
            "dates": {
                "created": fields.get('created'),
                "updated": fields.get('updated'),
                "resolved": fields.get('resolutiondate'),
                "due_date": fields.get('duedate')
            },
            "classification": {
                "labels": fields.get('labels', []),
                "components": [c.get('name') for c in fields.get('components', [])]
            },
            "links": {
                "attachments_count": len(fields.get('attachment', [])),
                "comments_count": fields.get('comment', {}).get('total', 0)
            }
        }
        
        # Add custom fields if configured
        if self.config.custom_fields:
            result["custom_fields"] = self._extract_custom_fields(fields)
        
        # Add change history if requested
        if include_history and 'changelog' in issue:
            result["history"] = self._format_changelog(issue.get('changelog'))
        
        return result
    
    def _format_created_issue(self, issue: dict) -> dict:
        """Format created issue response"""
        return {
            "key": issue.get('key'),
            "id": issue.get('id'),
            "self": issue.get('self'),
            "web_url": self._build_web_url(issue.get('key'))
        }
    
    def _format_user(self, user: Optional[dict]) -> Optional[dict]:
        """Format user information"""
        if not user:
            return None
        return {
            "account_id": user.get('accountId'),
            "display_name": user.get('displayName'),
            "email": user.get('emailAddress')
        }
    
    def _extract_custom_fields(self, fields: dict) -> dict:
        """Extract configured custom field values"""
        custom_fields = {}
        cf_config = self.config.custom_fields
        
        if cf_config.knowledge != "customfield_XXXXX":
            custom_fields["knowledge"] = fields.get(cf_config.knowledge)
        if cf_config.assigned_area != "customfield_XXXXX":
            custom_fields["assigned_area"] = fields.get(cf_config.assigned_area)
        if cf_config.incident_content != "customfield_XXXXX":
            custom_fields["incident_content"] = fields.get(cf_config.incident_content)
        if cf_config.temporary_response != "customfield_XXXXX":
            custom_fields["temporary_response"] = fields.get(cf_config.temporary_response)
        if cf_config.permanent_response != "customfield_XXXXX":
            custom_fields["permanent_response"] = fields.get(cf_config.permanent_response)
        if cf_config.impact_scope != "customfield_XXXXX":
            custom_fields["impact_scope"] = fields.get(cf_config.impact_scope)
        
        return custom_fields
    
    def _format_changelog(self, changelog: dict) -> List[dict]:
        """Format change history"""
        histories = changelog.get('histories', [])
        return [
            {
                "id": h.get('id'),
                "author": self._format_user(h.get('author')),
                "created": h.get('created'),
                "items": [
                    {
                        "field": item.get('field'),
                        "from": item.get('fromString'),
                        "to": item.get('toString')
                    }
                    for item in h.get('items', [])
                ]
            }
            for h in histories[:10]
        ]
    
    def _truncate_text(self, text: Optional[str], max_length: int = 200) -> Optional[str]:
        """Truncate text to specified length"""
        if not text:
            return None
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
    
    def _build_web_url(self, issue_key: str) -> str:
        """Build web URL for issue"""
        base_url = self.config.base_url.replace('/rest/api/2/', '')
        return f"{base_url}/browse/{issue_key}"


# Tool instance for FastMCP registration
jira_issues_tool = JiraIssuesManagementTool()
