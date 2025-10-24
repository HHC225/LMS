"""
Confluence Search Tool
Tool for searching Confluence pages using CQL
"""

import json
import requests
from typing import Dict, Any, Optional, List
from configs.confluence import get_confluence_config


class SearchToolManagement:
    """
    Confluence Search Management Tool
    
    Handles page search operations using CQL (Confluence Query Language)
    """
    
    def __init__(self):
        """Initialize with Confluence configuration"""
        self.config = get_confluence_config()
        self.base_url = self.config.base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {self.config.token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.timeout = self.config.timeout / 1000  # Convert milliseconds to seconds
    
    def execute(self, action: str, **kwargs) -> str:
        """
        Execute search action
        
        Args:
            action: Action to perform (search_pages)
            **kwargs: Action-specific parameters
            
        Returns:
            JSON string with action results
        """
        if action == "search_pages":
            result = self._search_pages(**kwargs)
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            return json.dumps({
                "success": False,
                "message": f"Unknown action: {action}. Available actions: search_pages"
            }, ensure_ascii=False)
    
    def _search_pages(
        self,
        query: Optional[str] = None,
        space_key: Optional[str] = None,
        title: Optional[str] = None,
        cql: Optional[str] = None,
        expand: Optional[List[str]] = None,
        limit: int = 25,
        start: int = 0
    ) -> Dict[str, Any]:
        """
        Search Confluence pages
        
        Args:
            query: General search query (searches title and content)
            space_key: Filter by space key
            title: Filter by title (partial match)
            cql: Custom CQL query (overrides other filters)
            expand: List of fields to expand
            limit: Maximum number of results (1-100)
            start: Starting offset for pagination
            
        Returns:
            Dictionary with search results
        """
        # Build CQL query
        if cql:
            # Use custom CQL if provided
            search_cql = cql
        else:
            # Build CQL from parameters
            cql_parts = ["type=page"]
            
            if space_key:
                cql_parts.append(f'space="{space_key}"')
            
            if title:
                cql_parts.append(f'title~"{title}"')
            
            if query:
                cql_parts.append(f'(title~"{query}" OR text~"{query}")')
            
            search_cql = " AND ".join(cql_parts)
        
        # Build query parameters
        params = {
            "cql": search_cql,
            "start": start,
            "limit": limit
        }
        
        # Add expand parameters
        if expand:
            params["expand"] = ",".join(expand)
        else:
            params["expand"] = ",".join(self.config.default_expand)
        
        try:
            response = requests.get(
                f"{self.base_url}/content/search",
                headers=self.headers,
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                pages = []
                
                for page in data.get("results", []):
                    page_info = {
                        "id": page.get("id"),
                        "type": page.get("type"),
                        "status": page.get("status"),
                        "title": page.get("title")
                    }
                    
                    # Add space information
                    if "space" in page:
                        page_info["space"] = {
                            "id": page["space"].get("id"),
                            "key": page["space"].get("key"),
                            "name": page["space"].get("name"),
                            "type": page["space"].get("type")
                        }
                    
                    # Add version information
                    if "version" in page:
                        page_info["version"] = {
                            "number": page["version"].get("number"),
                            "when": page["version"].get("when")
                        }
                        if "by" in page["version"]:
                            page_info["version"]["by"] = page["version"]["by"].get("displayName", "Unknown")
                    
                    # Add body content if expanded
                    if "body" in page:
                        page_info["body"] = {}
                        
                        # Storage format (HTML)
                        if "storage" in page["body"] and "value" in page["body"]["storage"]:
                            storage_value = page["body"]["storage"]["value"]
                            page_info["body"]["storage_preview"] = self._strip_html(storage_value)[:300]
                        
                        # View format (rendered HTML)
                        if "view" in page["body"] and "value" in page["body"]["view"]:
                            view_value = page["body"]["view"]["value"]
                            page_info["body"]["view_preview"] = self._strip_html(view_value)[:300]
                    
                    # Add ancestors if expanded
                    if "ancestors" in page:
                        page_info["ancestors"] = [
                            {
                                "id": ancestor.get("id"),
                                "type": ancestor.get("type"),
                                "title": ancestor.get("title")
                            }
                            for ancestor in page["ancestors"]
                        ]
                    
                    # Add links
                    if "_links" in page:
                        page_info["links"] = {
                            "self": page["_links"].get("self"),
                            "webui": page["_links"].get("webui"),
                            "edit": page["_links"].get("edit")
                        }
                    
                    pages.append(page_info)
                
                return {
                    "success": True,
                    "message": f"Found {len(pages)} page(s)",
                    "data": {
                        "pages": pages,
                        "pagination": {
                            "start": data.get("start", start),
                            "limit": data.get("limit", limit),
                            "size": data.get("size", len(pages)),
                            "total_size": len(pages),
                            "has_next": "_links" in data and "next" in data["_links"],
                            "has_prev": "_links" in data and "prev" in data["_links"]
                        },
                        "search_criteria": {
                            "cql": search_cql,
                            "query": query,
                            "space_key": space_key,
                            "title": title
                        }
                    }
                }
            elif response.status_code == 400:
                return {
                    "success": False,
                    "message": "Invalid CQL query",
                    "error": response.json().get("message", "Bad request - check your query syntax")
                }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "message": "Authentication failed. Please check your API token",
                    "error": "Unauthorized"
                }
            elif response.status_code == 403:
                return {
                    "success": False,
                    "message": "No permission to search pages",
                    "error": "Forbidden"
                }
            else:
                return {
                    "success": False,
                    "message": f"Confluence API error: {response.status_code}",
                    "error": response.text
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "message": "Request timeout",
                "error": f"Request exceeded {self.timeout}s timeout"
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": "Network error occurred",
                "error": str(e)
            }
    
    def _strip_html(self, html: str) -> str:
        """
        Remove HTML tags from string
        
        Args:
            html: HTML string
            
        Returns:
            Plain text string
        """
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', html).strip()


# Create singleton instance
search_tool = SearchToolManagement()
