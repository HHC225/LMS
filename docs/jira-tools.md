# JIRA Tools

Python FastMCP-based JIRA integration tools for comprehensive issue and project management.

## 📋 Overview

This module provides JIRA REST API v2 integration for managing issues, comments, attachments, and projects. Fully migrated from TypeScript MCP server to Python implementation.

## ✨ Features

### Available Tools (11 total)

#### Issues Management (3 tools)
- `jira_search_issues` - Search issues using JQL
- `jira_get_issue_details` - Retrieve detailed issue information
- `jira_create_issue` - Create new issues

#### Comments Management (4 tools)
- `jira_get_comments` - List all comments on an issue
- `jira_add_comment` - Add a new comment
- `jira_update_comment` - Update existing comment
- `jira_delete_comment` - Delete a comment

#### Attachments Management (2 tools)
- `jira_list_attachments` - List all attachments on an issue
- `jira_download_attachment` - Download attachment files

#### Other Tools (2 tools)
- `jira_get_projects` - List available projects
- `jira_search_knowledge` - Search knowledge base

## 🚀 Getting Started

### 1. Create Configuration File

```bash
# Copy template
cp configs/jira.py.template configs/jira.py

# Edit configuration
vim configs/jira.py
```

### 2. Configure JIRA Authentication

```python
# configs/jira.py

@dataclass
class JiraConfig:
    # JIRA instance URL
    base_url: str = "https://your-company.atlassian.net/rest/api/2/"
    
    # API token (https://id.atlassian.com/manage-profile/security/api-tokens)
    auth_token: str = "YOUR_API_TOKEN_HERE"
    
    # Custom field IDs (adjust for your project)
    custom_fields: CustomFields = None
```

### 3. Configure Custom Fields (Optional)

If your project uses custom fields:

```python
@dataclass
class CustomFields:
    knowledge: str = "customfield_11219"       # Knowledge registration
    assigned_area: str = "customfield_11600"   # Assigned area
    incident_content: str = "customfield_11601"  # Incident content
    # ... additional fields
```

### 4. Generate API Token

For Atlassian Cloud:
1. Visit https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Enter a label (e.g., "MCP Tools")
4. Copy the token and paste it into `configs/jira.py`

### 5. Restart Server

After creating the configuration file, restart the MCP server to automatically register JIRA tools.

## 📖 Usage Examples

### Issues Management

#### Search Issues with JQL

```python
# Search for issues assigned to me that are not done
result = await jira_search_issues(
    jql="assignee = currentUser() AND status != Done"
)

# Search for bugs in specific project
result = await jira_search_issues(
    jql="project = MYPROJECT AND type = Bug",
    max_results=100
)

# Search for issues created in last 7 days
result = await jira_search_issues(
    jql="created >= -7d ORDER BY created DESC"
)
```

#### Get Issue Details

```python
# Get full issue details with all fields
result = await jira_get_issue_details(
    issue_key="PROJ-123"
)

# Access issue information
print(result["fields"]["summary"])
print(result["fields"]["status"]["name"])
print(result["fields"]["assignee"]["displayName"])
```

#### Create New Issue

```python
# Create a bug report
result = await jira_create_issue(
    project_key="PROJ",
    summary="Application crashes on startup",
    description="When launching the app, it immediately crashes with error code 500",
    issue_type="Bug",
    priority="High"
)

# Create a task
result = await jira_create_issue(
    project_key="PROJ",
    summary="Update documentation",
    description="Add API endpoint documentation for new features",
    issue_type="Task",
    assignee="john.doe@company.com"
)
```

### Comments Management

#### List Comments

```python
# Get all comments for an issue
result = await jira_get_comments(
    issue_key="PROJ-123"
)

# Access comment data
for comment in result["comments"]:
    print(f"{comment['author']['displayName']}: {comment['body']}")
```

#### Add Comment

```python
# Add a simple comment
result = await jira_add_comment(
    issue_key="PROJ-123",
    body="This issue has been reviewed and approved for implementation."
)

# Add a comment with formatting
result = await jira_add_comment(
    issue_key="PROJ-123",
    body="*Status Update*\n\nThe following items have been completed:\n* Database migration\n* API updates\n* Unit tests"
)
```

#### Update Comment

```python
# Update existing comment
result = await jira_update_comment(
    issue_key="PROJ-123",
    comment_id="10001",
    body="Updated: This issue has been reviewed and approved for immediate implementation."
)
```

#### Delete Comment

```python
# Delete a comment
result = await jira_delete_comment(
    issue_key="PROJ-123",
    comment_id="10001"
)
```

### Attachments Management

#### List Attachments

```python
# Get all attachments for an issue
result = await jira_list_attachments(
    issue_key="PROJ-123"
)

# Access attachment information
for attachment in result["attachments"]:
    print(f"{attachment['filename']} ({attachment['size']} bytes)")
    print(f"Uploaded by {attachment['author']['displayName']}")
```

#### Download Attachment

```python
# Download attachment to local file
result = await jira_download_attachment(
    attachment_id="10000",
    save_path="/path/to/save/file.pdf"
)

# Or get download URL only
result = await jira_download_attachment(
    attachment_id="10000"
)
print(result["download_url"])
```

### Projects and Knowledge

#### List Projects

```python
# Get all accessible projects
result = await jira_get_projects()

# Access project data
for project in result["projects"]:
    print(f"{project['key']}: {project['name']}")
```

#### Search Knowledge Base

```python
# Search knowledge base for documentation
result = await jira_search_knowledge(
    query="API authentication",
    max_results=20
)

# Access knowledge articles
for article in result["results"]:
    print(f"{article['title']}: {article['url']}")
```

## 🔍 JQL (JIRA Query Language) Reference

### Basic Syntax

```
field operator value
```

### Common Operators

- `=`: Equals
- `!=`: Not equals
- `~`: Contains
- `>`, `>=`, `<`, `<=`: Comparison
- `IN`: Value in list
- `AND`, `OR`, `NOT`: Logical operators

### Useful Field Examples

```jql
# My open issues
assignee = currentUser() AND status != Done

# Project bugs
project = MYPROJECT AND type = Bug

# High priority issues
priority = High AND status = Open

# Recent issues
created >= -7d ORDER BY created DESC

# Specific status
status IN (Open, "In Progress", Reopened)

# Multiple conditions
project = PROJ AND type = Bug AND priority = High AND status != Done
```

### Advanced JQL Examples

```jql
# Issues due this week
duedate >= startOfWeek() AND duedate <= endOfWeek()

# Issues updated today
updated >= startOfDay()

# Issues without assignee
assignee IS EMPTY

# Issues with specific label
labels = "customer-facing"

# Issues in sprint
Sprint = "Sprint 23"

# Issues by reporter
reporter = john.doe@company.com

# Text search in summary and description
text ~ "authentication error"

# Complex query
project = PROJ AND (type = Bug OR type = "Technical Debt") 
    AND priority IN (High, Highest) 
    AND status != Done 
    AND assignee = currentUser()
    ORDER BY priority DESC, created ASC
```

## 📝 Best Practices

### 1. Issue Creation

Always provide clear, detailed information:

```python
# Good: Detailed issue
result = await jira_create_issue(
    project_key="PROJ",
    summary="Login API returns 500 error for users with special characters in email",
    description="""
    *Steps to Reproduce:*
    1. Navigate to login page
    2. Enter email with + symbol (e.g., user+test@example.com)
    3. Click login button
    
    *Expected Result:*
    User should be logged in successfully
    
    *Actual Result:*
    Server returns 500 Internal Server Error
    
    *Environment:*
    - Browser: Chrome 120
    - OS: Windows 11
    - API Version: 2.1.0
    """,
    issue_type="Bug",
    priority="High"
)

# Avoid: Vague issue
result = await jira_create_issue(
    project_key="PROJ",
    summary="Login not working",
    description="Fix login",
    issue_type="Bug"
)
```

### 2. Comment Formatting

Use Atlassian Document Format for better readability:

```python
# Use text formatting
result = await jira_add_comment(
    issue_key="PROJ-123",
    body="""
    *Update:* Issue has been resolved in PR #456
    
    *Testing Results:*
    - Unit tests: ✓ Passed
    - Integration tests: ✓ Passed
    - Manual testing: ✓ Passed
    
    *Next Steps:*
    # Deploy to staging environment
    # Perform smoke tests
    # Deploy to production
    
    cc: [~john.doe] [~jane.smith]
    """
)
```

### 3. Error Handling

```python
try:
    result = await jira_create_issue(
        project_key="PROJ",
        summary="New feature request",
        description="Detailed description",
        issue_type="Story"
    )
except Exception as e:
    if "400" in str(e):
        print("Invalid request - check field values")
    elif "401" in str(e):
        print("Authentication failed - check API token")
    elif "403" in str(e):
        print("Permission denied - check project access")
    elif "404" in str(e):
        print("Project or issue not found")
    else:
        print(f"Error: {e}")
```

### 4. Efficient Searching

Use specific JQL queries to minimize results:

```python
# Bad: Too broad, returns too many results
result = await jira_search_issues(jql="type = Bug")

# Good: Specific scope
result = await jira_search_issues(
    jql="project = MYPROJECT AND type = Bug AND status = Open AND priority = High",
    max_results=50
)
```

### 5. Pagination

For large result sets, use pagination:

```python
# Search with pagination
start_at = 0
max_results = 50

while True:
    result = await jira_search_issues(
        jql="project = MYPROJECT",
        start_at=start_at,
        max_results=max_results
    )
    
    # Process results
    for issue in result["issues"]:
        print(f"{issue['key']}: {issue['fields']['summary']}")
    
    # Check if more results exist
    if len(result["issues"]) < max_results:
        break
    
    start_at += max_results
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Authentication Errors (401)

**Problem:** "Unauthorized" error

**Solutions:**
- Verify API token is correct
- Check token hasn't expired
- Ensure token has necessary permissions
- Regenerate token if needed

#### 2. Permission Errors (403)

**Problem:** "Forbidden" error

**Solutions:**
- Verify user has access to the project
- Check project permissions in JIRA
- Ensure user can perform the requested action (create, edit, delete)
- Confirm project key is correct

#### 3. Issue Not Found (404)

**Problem:** "Issue not found" error

**Solutions:**
- Verify issue key is correct (e.g., "PROJ-123")
- Check if issue has been deleted
- Ensure issue exists in the specified project
- Confirm you have permission to view the issue

#### 4. Invalid Field (400)

**Problem:** "Bad request - invalid field" error

**Solutions:**
- Check required fields are provided
- Verify field names match project configuration
- Ensure custom field IDs are correct
- Validate field value types and formats

#### 5. Custom Fields

**Problem:** Custom fields not working

**Solutions:**
1. Find custom field IDs in JIRA:
   - Go to Settings → Issues → Custom Fields
   - Note the field ID (e.g., customfield_10001)
   
2. Update `configs/jira.py`:
   ```python
   custom_fields = CustomFields(
       knowledge="customfield_10001",
       assigned_area="customfield_10002"
   )
   ```

### Debug Tips

#### Enable Detailed Logging

```python
# Add debug logging in your code
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Test Connection

```python
# Simple connection test
try:
    projects = await jira_get_projects()
    print(f"Successfully connected! Found {len(projects['projects'])} projects.")
except Exception as e:
    print(f"Connection failed: {e}")
```

#### Verify Custom Fields

```python
# Get issue to see all available fields
result = await jira_get_issue_details(issue_key="PROJ-123")

# Print all field keys
for field_key in result["fields"].keys():
    print(field_key)
```

### Common JQL Mistakes

```jql
# Wrong: Missing quotes for multi-word values
summary = API Documentation Error

# Correct: Use quotes
summary = "API Documentation Error"

# Wrong: Invalid date format
created >= 2024-01-01

# Correct: Use proper date format
created >= "2024-01-01"

# Wrong: Invalid field name
owner = john.doe

# Correct: Use 'assignee' not 'owner'
assignee = john.doe

# Wrong: Missing project context
type = Bug

# Better: Include project for specificity
project = MYPROJECT AND type = Bug
```

## 📚 Additional Resources

- [JIRA REST API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v2/)
- [JQL Reference Guide](https://support.atlassian.com/jira-software-cloud/docs/use-advanced-search-with-jira-query-language-jql/)
- [Atlassian Document Format](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/)

## 💡 Tips & Tricks

### 1. Quick Issue Search

```python
# Find my open bugs
await jira_search_issues(
    jql="assignee = currentUser() AND type = Bug AND status != Done"
)
```

### 2. Batch Operations

```python
# Get multiple issues efficiently
issue_keys = ["PROJ-123", "PROJ-124", "PROJ-125"]
jql = f"key IN ({','.join(issue_keys)})"
result = await jira_search_issues(jql=jql)
```

### 3. Monitor Recent Activity

```python
# Issues updated in last hour
await jira_search_issues(
    jql="updated >= -1h ORDER BY updated DESC"
)
```

### 4. Filter by Custom Field

```python
# Assuming custom field for "Team"
await jira_search_issues(
    jql='project = PROJ AND "Team[Dropdown]" = "Backend Team"'
)
```

## Support

For issues or questions:
1. Check this documentation first
2. Review error messages carefully
3. Verify your configuration settings
4. Test with simple queries before complex ones
5. Check JIRA permissions and project access
