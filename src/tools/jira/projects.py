"""
JIRA Projects Tool
Get list of accessible JIRA projects
"""
import json
from typing import Literal
from datetime import datetime

from src.tools.base import BaseTool
from src.wrappers.jira import JiraApiClient, JiraApiError
from configs.jira import get_jira_config, validate_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class JiraProjectsTool(BaseTool):
    """
    Tool for retrieving JIRA projects list
    """
    
    def __init__(self):
        super().__init__(
            name="jira_projects",
            description="Get list of accessible JIRA projects with details"
        )
        self.config = get_jira_config()
        validate_config(self.config)
        self.client = JiraApiClient(self.config)
    
    async def execute(
        self,
        include_archived: bool = False,
        sort_by: Literal['key', 'name', 'type'] = 'key',
        **kwargs
    ) -> str:
        """
        Get all accessible projects
        
        Args:
            include_archived: Include archived projects (default: False)
            sort_by: Sort order - 'key', 'name', or 'type' (default: 'key')
            
        Returns:
            JSON string with project list
        """
        try:
            logger.info("Getting projects list")
            
            # Get projects
            projects = self.client.get_projects()
            
            # Filter archived if needed
            if not include_archived:
                projects = [p for p in projects if not p.get('archived', False)]
            
            # Sort projects
            projects = self._sort_projects(projects, sort_by)
            
            # Format response
            formatted_result = self._format_projects(projects)
            
            logger.info(f"Projects retrieved: {len(projects)} projects")
            
            return json.dumps({
                "success": True,
                "data": formatted_result,
                "timestamp": datetime.now().isoformat()
            }, ensure_ascii=False, indent=2)
            
        except JiraApiError as e:
            logger.error(f"JIRA API error getting projects: {e.message}")
            return json.dumps({
                "success": False,
                "error": f"JIRA API Error: {e.message}",
                "status_code": e.status_code
            }, ensure_ascii=False, indent=2)
        
        except Exception as e:
            logger.error(f"Unexpected error getting projects: {str(e)}", exc_info=True)
            return json.dumps({
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }, ensure_ascii=False, indent=2)
    
    def _sort_projects(self, projects: list, sort_by: str) -> list:
        """Sort projects by specified field"""
        if sort_by == 'name':
            return sorted(projects, key=lambda p: p.get('name', '').lower())
        elif sort_by == 'type':
            return sorted(projects, key=lambda p: p.get('projectTypeKey', '').lower())
        else:  # key
            return sorted(projects, key=lambda p: p.get('key', '').lower())
    
    def _format_projects(self, projects: list) -> dict:
        """Format projects list"""
        # Calculate statistics
        project_types = {}
        for project in projects:
            ptype = project.get('projectTypeKey', 'unknown')
            project_types[ptype] = project_types.get(ptype, 0) + 1
        
        return {
            "summary": {
                "total": len(projects),
                "project_types": project_types
            },
            "projects": [
                {
                    "key": p.get('key'),
                    "id": p.get('id'),
                    "name": p.get('name'),
                    "description": p.get('description'),
                    "project_type": p.get('projectTypeKey'),
                    "lead": {
                        "account_id": p.get('lead', {}).get('accountId'),
                        "display_name": p.get('lead', {}).get('displayName'),
                        "email": p.get('lead', {}).get('emailAddress')
                    } if p.get('lead') else None,
                    "url": p.get('self'),
                    "avatar_urls": p.get('avatarUrls')
                }
                for p in projects
            ]
        }


# Tool instance for FastMCP registration
jira_projects_tool = JiraProjectsTool()
