"""
JIRA Knowledge Search Tool
Search for issues in knowledge base custom field
"""
import json
from typing import Optional
from datetime import datetime

from src.tools.base import BaseTool
from src.wrappers.jira import JiraApiClient, JiraApiError
from configs.jira import get_jira_config, validate_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class JiraKnowledgeSearchTool(BaseTool):
    """
    Tool for searching JIRA knowledge base
    """
    
    def __init__(self):
        super().__init__(
            name="jira_knowledge_search",
            description="Search for issues containing specific keywords in knowledge base custom field"
        )
        self.config = get_jira_config()
        validate_config(self.config)
        self.client = JiraApiClient(self.config)
    
    async def execute(
        self,
        keyword: str,
        project: Optional[str] = None,
        issue_type: Optional[str] = None,
        max_results: int = 25,
        start_at: int = 0,
        **kwargs
    ) -> str:
        """
        Search knowledge base for keyword
        
        Args:
            keyword: Search keyword (required)
            project: Project key to limit search (optional)
            issue_type: Issue type to limit search (optional)
            max_results: Maximum results per page (default: 25, max: 100)
            start_at: Starting index for pagination (default: 0)
            
        Returns:
            JSON string with search results
            
        Note:
            Automatically fetches all matching results across multiple pages
        """
        try:
            logger.info(f"Searching knowledge base for: {keyword}")
            
            # Validate inputs
            if not keyword or not keyword.strip():
                return json.dumps({
                    "success": False,
                    "error": "keyword cannot be empty"
                }, ensure_ascii=False, indent=2)
            
            if max_results < 1 or max_results > 100:
                return json.dumps({
                    "success": False,
                    "error": "max_results must be between 1 and 100"
                }, ensure_ascii=False, indent=2)
            
            # Get knowledge field ID
            knowledge_field_id = self.config.custom_fields.knowledge
            
            if knowledge_field_id == "customfield_XXXXX":
                return json.dumps({
                    "success": False,
                    "error": "Knowledge custom field is not configured. Please update configs/jira.py"
                }, ensure_ascii=False, indent=2)
            
            # Build JQL query
            jql_parts = []
            
            if project:
                jql_parts.append(f'project = {project}')
            
            if issue_type:
                jql_parts.append(f'issueType = "{issue_type}"')
            
            # Extract field number from customfield_XXXXX
            field_number = knowledge_field_id.replace('customfield_', '')
            jql_parts.append(f'cf[{field_number}] ~ "{keyword}"')
            
            jql = ' AND '.join(jql_parts)
            
            logger.info(f"Built JQL: {jql}")
            
            # Fetch all results across multiple pages
            all_issues = []
            current_start = start_at
            page_num = 1
            
            while True:
                logger.info(f"Fetching page {page_num}: start_at={current_start}")
                
                result = self.client.search_issues(
                    jql=jql,
                    start_at=current_start,
                    max_results=max_results
                )
                
                issues = result.get('issues', [])
                all_issues.extend(issues)
                
                total = result.get('total', 0)
                has_more = (current_start + len(issues)) < total
                
                logger.info(f"Page {page_num}: {len(issues)} issues, total so far: {len(all_issues)}/{total}")
                
                if not has_more:
                    break
                
                current_start += max_results
                page_num += 1
                
                # Safety limit
                if page_num > 50:
                    logger.warning(f"Reached page limit (50 pages)")
                    break
            
            # Format response
            formatted_result = self._format_knowledge_results(
                all_issues,
                keyword,
                knowledge_field_id,
                total
            )
            
            logger.info(f"Knowledge search completed: {len(all_issues)} total results")
            
            return json.dumps({
                "success": True,
                "data": formatted_result,
                "timestamp": datetime.now().isoformat()
            }, ensure_ascii=False, indent=2)
            
        except JiraApiError as e:
            logger.error(f"JIRA API error searching knowledge: {e.message}")
            return json.dumps({
                "success": False,
                "error": f"JIRA API Error: {e.message}",
                "status_code": e.status_code
            }, ensure_ascii=False, indent=2)
        
        except Exception as e:
            logger.error(f"Unexpected error searching knowledge: {str(e)}", exc_info=True)
            return json.dumps({
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }, ensure_ascii=False, indent=2)
    
    def _format_knowledge_results(
        self,
        issues: list,
        keyword: str,
        knowledge_field_id: str,
        total: int
    ) -> dict:
        """Format knowledge search results"""
        return {
            "query": {
                "keyword": keyword,
                "knowledge_field": knowledge_field_id
            },
            "summary": {
                "total": total,
                "returned": len(issues)
            },
            "issues": [
                {
                    "key": issue.get('key'),
                    "id": issue.get('id'),
                    "summary": issue.get('fields', {}).get('summary'),
                    "status": {
                        "name": issue.get('fields', {}).get('status', {}).get('name'),
                        "category": issue.get('fields', {}).get('status', {}).get('statusCategory', {}).get('name')
                    },
                    "issue_type": issue.get('fields', {}).get('issuetype', {}).get('name'),
                    "project": {
                        "key": issue.get('fields', {}).get('project', {}).get('key'),
                        "name": issue.get('fields', {}).get('project', {}).get('name')
                    },
                    "assignee": {
                        "display_name": issue.get('fields', {}).get('assignee', {}).get('displayName')
                    } if issue.get('fields', {}).get('assignee') else None,
                    "priority": {
                        "name": issue.get('fields', {}).get('priority', {}).get('name')
                    } if issue.get('fields', {}).get('priority') else None,
                    "created": issue.get('fields', {}).get('created'),
                    "updated": issue.get('fields', {}).get('updated'),
                    "labels": issue.get('fields', {}).get('labels', []),
                    "knowledge_preview": self._extract_knowledge_preview(
                        issue.get('fields', {}).get(knowledge_field_id),
                        keyword
                    )
                }
                for issue in issues
            ]
        }
    
    def _extract_knowledge_preview(self, knowledge_content: Optional[str], keyword: str) -> Optional[str]:
        """Extract preview of knowledge content around keyword"""
        if not knowledge_content:
            return None
        
        # Find keyword position (case-insensitive)
        lower_content = knowledge_content.lower()
        lower_keyword = keyword.lower()
        
        pos = lower_content.find(lower_keyword)
        if pos == -1:
            # Keyword not found, return first 200 chars
            return knowledge_content[:200] + "..." if len(knowledge_content) > 200 else knowledge_content
        
        # Extract content around keyword
        start = max(0, pos - 100)
        end = min(len(knowledge_content), pos + len(keyword) + 100)
        
        preview = knowledge_content[start:end]
        
        if start > 0:
            preview = "..." + preview
        if end < len(knowledge_content):
            preview = preview + "..."
        
        return preview


# Tool instance for FastMCP registration
jira_knowledge_tool = JiraKnowledgeSearchTool()
