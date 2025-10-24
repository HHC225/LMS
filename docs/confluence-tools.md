# Confluence Tools

Integration tools for managing Confluence pages, spaces, and content through REST API v2.

## 📋 Table of Contents

- [Overview](#overview)
- [Configuration](#configuration)
- [Available Tools](#available-tools)
- [Usage Examples](#usage-examples)
- [CQL Reference](#cql-reference)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

### Key Features

- **Page Management**: Create, read, update, and delete Confluence pages
- **Space Operations**: List and retrieve detailed information about spaces
- **Advanced Search**: Powerful search capabilities using CQL (Confluence Query Language)
- **Content Expansion**: Retrieve detailed information including body, version, and hierarchy
- **Version Control**: Safe page updates with optimistic locking

### Supported Features

- ✅ Bearer token authentication
- ✅ Storage format content (HTML)
- ✅ CQL search queries
- ✅ Pagination support
- ✅ Expansion options (body, version, space, ancestors)
- ✅ Comprehensive error handling (400, 401, 403, 404, 409, 500)

## Configuration

### 1. Create Configuration File

Copy the template file to create your configuration:

```bash
cp configs/confluence.py.template configs/confluence.py
```

### 2. Configure Confluence Credentials

Edit `configs/confluence.py` with your Confluence instance details:

```python
_config = ConfluenceConfig(
    # Confluence REST API base URL
    # Example: "https://your-domain.atlassian.net/wiki/rest/api/"
    base_url="https://your-confluence-instance.com/rest/api/",
    
    # API token (generate at https://id.atlassian.com/manage-profile/security/api-tokens)
    token="YOUR_API_TOKEN_HERE",
    
    # Optional: Username (email)
    username=None,
    
    # Optional: Default space key
    default_space=None,
    
    # Maximum search results (1-1000)
    max_results=50,
    
    # Request timeout (milliseconds)
    timeout=30000,
    
    # Debug mode
    debug=False,
    
    # Default expansion fields
    default_expand=[
        "body.storage",  # Page content (storage format)
        "version",       # Version information
        "space",         # Space details
        "ancestors"      # Parent page hierarchy
    ],
    
    # Default pagination size (1-100)
    page_size=25,
    
    # Content format: "storage", "view", "editor"
    content_format="storage"
)
```

### 3. Generate API Token

For Atlassian Cloud:
1. Visit https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Enter a label (e.g., "MCP Tools")
4. Copy the generated token and paste it into the `token` field in `configs/confluence.py`

### 4. Restart Server

After creating the configuration file, restart the MCP server to automatically register Confluence tools.

## Available Tools

### Page Management

#### 1. `confluence_create_page`
Create a new Confluence page with HTML content.

**Parameters:**
- `space_key` (string, required): Target space key
- `title` (string, required): Page title
- `content` (string, required): HTML content in storage format
- `parent_id` (string, optional): Parent page ID for hierarchy

**Example:**
```python
result = await confluence_create_page(
    space_key="TEAM",
    title="Project Documentation",
    content="<h1>Overview</h1><p>This is the project documentation.</p>",
    parent_id="123456789"
)
```

#### 2. `confluence_get_page`
Retrieve page details and content.

**Parameters:**
- `page_id` (string, required): Page ID
- `expand` (list, optional): Fields to expand (body.storage, version, space, ancestors)

**Example:**
```python
result = await confluence_get_page(
    page_id="123456789",
    expand=["body.storage", "version", "space"]
)
```

#### 3. `confluence_update_page`
Update an existing page with new content.

**Parameters:**
- `page_id` (string, required): Page ID
- `title` (string, required): New title
- `content` (string, required): New HTML content
- `version` (integer, required): Current version number (for optimistic locking)

**Example:**
```python
result = await confluence_update_page(
    page_id="123456789",
    title="Updated Documentation",
    content="<h1>Updated Content</h1><p>New information here.</p>",
    version=2
)
```

#### 4. `confluence_delete_page`
Delete a page permanently.

**Parameters:**
- `page_id` (string, required): Page ID to delete

**Example:**
```python
result = await confluence_delete_page(page_id="123456789")
```

### Space Operations

#### 5. `confluence_get_spaces`
List all spaces accessible to the authenticated user.

**Parameters:**
- `limit` (integer, optional): Maximum number of spaces to return (default: 25)
- `expand` (list, optional): Fields to expand (description, homepage, metadata)

**Example:**
```python
result = await confluence_get_spaces(limit=50, expand=["description"])
```

### Search

#### 6. `confluence_search_pages`
Search for pages using CQL (Confluence Query Language).

**Parameters:**
- `cql` (string, required): CQL query string
- `limit` (integer, optional): Maximum results (default: 25)
- `expand` (list, optional): Fields to expand

**Example:**
```python
# Search for pages in specific space
result = await confluence_search_pages(
    cql="space=TEAM AND type=page",
    limit=50
)

# Search by title
result = await confluence_search_pages(
    cql="title~'documentation' AND space=TEAM"
)

# Search by last modified date
result = await confluence_search_pages(
    cql="lastModified>='2024-01-01' AND space=TEAM ORDER BY lastModified DESC"
)
```

## Usage Examples

### Complete Workflow Example

```python
# 1. List available spaces
spaces = await confluence_get_spaces()

# 2. Create a new page
new_page = await confluence_create_page(
    space_key="TEAM",
    title="API Documentation",
    content="<h1>API Overview</h1><p>This document describes our APIs.</p>"
)

page_id = new_page["id"]

# 3. Retrieve and read the page
page_details = await confluence_get_page(
    page_id=page_id,
    expand=["body.storage", "version"]
)

current_version = page_details["version"]["number"]

# 4. Update the page
updated_page = await confluence_update_page(
    page_id=page_id,
    title="API Documentation - Updated",
    content="<h1>API Overview</h1><p>Updated API documentation with new endpoints.</p>",
    version=current_version
)

# 5. Search for related pages
search_results = await confluence_search_pages(
    cql="space=TEAM AND title~'API'"
)

# 6. Delete the page (if needed)
await confluence_delete_page(page_id=page_id)
```

## CQL Reference

### Basic Syntax

```
field operator value
```

### Common Operators

- `=`: Equals
- `!=`: Not equals
- `~`: Contains (for text fields)
- `>`, `>=`, `<`, `<=`: Comparison
- `IN`: Value in list
- `AND`, `OR`, `NOT`: Logical operators

### Useful Field Examples

```cql
# Search by space
space=TEAM

# Search by type
type=page

# Search by title
title~"documentation"

# Search by last modified
lastModified>="2024-01-01"

# Search by creator
creator=john.doe

# Combine conditions
space=TEAM AND type=page AND title~"API" ORDER BY lastModified DESC

# Search with label
label="important"

# Search by ancestor
ancestor=123456789
```

### Advanced Examples

```cql
# Pages modified in last 7 days
lastModified >= now("-7d") AND space=TEAM

# Pages created by specific user in specific space
space=TEAM AND creator=john.doe AND type=page

# Pages with specific label in multiple spaces
label="api" AND (space=TEAM OR space=DOCS)

# Pages under specific parent page
ancestor=123456789 AND type=page ORDER BY title ASC
```

## Best Practices

### 1. Content Format

Always use **storage format** (HTML) for page content:

```html
<!-- Good: Properly structured HTML -->
<h1>Title</h1>
<p>This is a paragraph with <strong>bold</strong> text.</p>
<ul>
  <li>Item 1</li>
  <li>Item 2</li>
</ul>

<!-- Avoid: Plain text without HTML tags -->
Title
This is a paragraph with bold text.
- Item 1
- Item 2
```

### 2. Version Control

Always retrieve the current version before updating:

```python
# 1. Get current version
page = await confluence_get_page(page_id="123", expand=["version"])
version = page["version"]["number"]

# 2. Update with correct version
await confluence_update_page(
    page_id="123",
    title="Updated Title",
    content="<p>New content</p>",
    version=version  # Use retrieved version
)
```

### 3. Error Handling

```python
try:
    result = await confluence_create_page(
        space_key="TEAM",
        title="New Page",
        content="<p>Content</p>"
    )
except Exception as e:
    if "409" in str(e):
        print("Page already exists or version conflict")
    elif "404" in str(e):
        print("Space or parent page not found")
    elif "403" in str(e):
        print("Permission denied")
    else:
        print(f"Error: {e}")
```

### 4. Pagination

For large result sets, use pagination:

```python
# Get pages in batches
limit = 50
start = 0

while True:
    results = await confluence_search_pages(
        cql=f"space=TEAM AND type=page",
        limit=limit
    )
    
    # Process results
    for page in results:
        print(page["title"])
    
    # Check if more results exist
    if len(results) < limit:
        break
    
    start += limit
```

### 5. Efficient Searching

Use specific CQL queries to minimize results:

```python
# Bad: Too broad
await confluence_search_pages(cql="type=page")

# Good: Specific scope
await confluence_search_pages(
    cql="space=TEAM AND lastModified>='2024-01-01' AND title~'API'"
)
```

## Troubleshooting

### Common Issues

#### 1. Authentication Errors (401)

**Problem:** "Unauthorized" error

**Solutions:**
- Verify API token is correct
- Check token hasn't expired
- Ensure user has access to Confluence instance

#### 2. Permission Errors (403)

**Problem:** "Forbidden" error

**Solutions:**
- Verify user has permission to access the space
- Check if user can create/edit/delete pages
- Confirm space key is correct

#### 3. Page Not Found (404)

**Problem:** "Page not found" error

**Solutions:**
- Verify page ID is correct
- Check if page has been deleted
- Ensure page exists in the specified space

#### 4. Version Conflict (409)

**Problem:** "Conflict - page has been updated" error

**Solutions:**
- Retrieve current version before updating
- Use optimistic locking with correct version number
- Handle conflicts by re-fetching and merging changes

#### 5. Invalid Content (400)

**Problem:** "Bad request - invalid content" error

**Solutions:**
- Ensure content is valid HTML in storage format
- Check for unclosed tags or malformed HTML
- Validate special characters are properly escaped

### Debug Mode

Enable debug mode for detailed logging:

```python
# In configs/confluence.py
_config = ConfluenceConfig(
    # ... other settings ...
    debug=True
)
```

This will log:
- API request URLs
- Request headers (token redacted)
- Response status codes
- Response bodies

### Testing Connection

Test your configuration:

```python
# Simple connection test
spaces = await confluence_get_spaces(limit=1)
print(f"Successfully connected! Found space: {spaces[0]['name']}")
```

### Common CQL Mistakes

```cql
# Wrong: Missing quotes around multi-word values
title=API Documentation

# Correct: Use quotes
title="API Documentation"

# Wrong: Invalid date format
lastModified>2024-01-01

# Correct: Use quotes for dates
lastModified>="2024-01-01"

# Wrong: Invalid field name
author=john.doe

# Correct: Use 'creator' not 'author'
creator=john.doe
```

## Additional Resources

- [Confluence REST API Documentation](https://developer.atlassian.com/cloud/confluence/rest/v2/intro/)
- [CQL (Confluence Query Language) Reference](https://developer.atlassian.com/cloud/confluence/advanced-searching-using-cql/)
- [Confluence Storage Format Documentation](https://confluence.atlassian.com/doc/confluence-storage-format-790796544.html)

## Support

For issues or questions:
1. Check this documentation first
2. Review error messages carefully
3. Enable debug mode for detailed logs
4. Verify your configuration settings
5. Test with simple queries first before complex ones
