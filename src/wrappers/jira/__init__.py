"""
JIRA Tool Wrappers
Unified wrapper functions for JIRA tools
"""
from .issues_wrapper import jira_search_issues, jira_get_issue_details, jira_create_issue
from .comments_wrapper import jira_get_comments, jira_add_comment, jira_update_comment, jira_delete_comment
from .attachments_wrapper import jira_list_attachments, jira_download_attachment
from .projects_wrapper import jira_get_projects
from .knowledge_wrapper import jira_search_knowledge

__all__ = [
    # Issues
    'jira_search_issues',
    'jira_get_issue_details',
    'jira_create_issue',
    # Comments
    'jira_get_comments',
    'jira_add_comment',
    'jira_update_comment',
    'jira_delete_comment',
    # Attachments
    'jira_list_attachments',
    'jira_download_attachment',
    # Projects
    'jira_get_projects',
    # Knowledge
    'jira_search_knowledge'
]
