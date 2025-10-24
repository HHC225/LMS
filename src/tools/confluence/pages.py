"""
Confluence Pages Tool
Unified tool for Confluence page management operations
"""

import json
import requests
from typing import Dict, Any, Optional, List
from configs.confluence import get_confluence_config


class PagesToolManagement:
    """
    Confluence Pages Management Tool
    
    Handles page operations: create, get, update, delete
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
        Execute page action
        
        Args:
            action: Action to perform (create, get, update, delete)
            **kwargs: Action-specific parameters
            
        Returns:
            JSON string with action results
        """
        action_map = {
            "create": self._create_page,
            "get": self._get_page,
            "update": self._update_page,
            "delete": self._delete_page
        }
        
        if action not in action_map:
            return json.dumps({
                "success": False,
                "message": f"Unknown action: {action}. Available actions: {', '.join(action_map.keys())}"
            }, ensure_ascii=False)
        
        try:
            result = action_map[action](**kwargs)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({
                "success": False,
                "message": f"Error executing {action} action",
                "error": str(e)
            }, ensure_ascii=False)
    
    def _create_page(
        self,
        title: str,
        space_key: str,
        content: str,
        parent_id: Optional[str] = None,
        page_type: str = "page"
    ) -> Dict[str, Any]:
        """
        Create new Confluence page
        
        Args:
            title: Page title
            space_key: Space key where page will be created
            content: Page content in storage format (HTML)
            parent_id: Parent page ID (optional)
            page_type: Page type (page or blogpost)
            
        Returns:
            Dictionary with creation results
        """
        # Validate required parameters
        if not title or not space_key or not content:
            return {
                "success": False,
                "message": "Missing required parameters: title, space_key, and content are required"
            }
        
        # Build request payload
        payload = {
            "type": page_type,
            "title": title,
            "space": {
                "key": space_key
            },
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            }
        }
        
        # Add parent if specified
        if parent_id:
            payload["ancestors"] = [{"id": parent_id}]
        
        try:
            response = requests.post(
                f"{self.base_url}/content",
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "message": f"Page '{title}' created successfully",
                    "data": {
                        "id": data.get("id"),
                        "title": data.get("title"),
                        "type": data.get("type"),
                        "space": {
                            "id": data.get("space", {}).get("id"),
                            "key": data.get("space", {}).get("key"),
                            "name": data.get("space", {}).get("name")
                        },
                        "version": {
                            "number": data.get("version", {}).get("number")
                        },
                        "url": f"{self.base_url.replace('/rest/api/', '')}{data.get('_links', {}).get('webui', '')}",
                        "parent_id": parent_id
                    }
                }
            elif response.status_code == 400:
                return {
                    "success": False,
                    "message": "Invalid page data provided",
                    "error": response.json().get("message", "Bad request")
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
                    "message": f"No permission to create pages in space '{space_key}'",
                    "error": "Forbidden"
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "message": f"Space '{space_key}' or parent page not found",
                    "error": "Not found"
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
    
    def _get_page(
        self,
        page_id: str,
        expand: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get Confluence page details
        
        Args:
            page_id: Page ID to retrieve
            expand: List of fields to expand (optional)
            
        Returns:
            Dictionary with page details
        """
        if not page_id:
            return {
                "success": False,
                "message": "page_id is required"
            }
        
        # Use config default expand if not specified
        if expand is None:
            expand = self.config.default_expand
        
        params = {
            "expand": ",".join(expand)
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/content/{page_id}",
                headers=self.headers,
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Build result with expanded data
                result = {
                    "id": data.get("id"),
                    "type": data.get("type"),
                    "status": data.get("status"),
                    "title": data.get("title"),
                    "space": {
                        "id": data.get("space", {}).get("id"),
                        "key": data.get("space", {}).get("key"),
                        "name": data.get("space", {}).get("name"),
                        "type": data.get("space", {}).get("type")
                    },
                    "version": {
                        "number": data.get("version", {}).get("number"),
                        "when": data.get("version", {}).get("when"),
                        "by": data.get("version", {}).get("by", {}).get("displayName", "Unknown")
                    }
                }
                
                # Add body if expanded
                if "body" in expand and "body" in data:
                    body_data = data["body"]
                    result["body"] = {}
                    if "storage" in body_data:
                        result["body"]["storage"] = body_data["storage"].get("value")
                    if "view" in body_data:
                        result["body"]["view"] = body_data["view"].get("value")
                
                # Add ancestors if expanded
                if "ancestors" in expand and "ancestors" in data:
                    result["ancestors"] = [
                        {
                            "id": ancestor.get("id"),
                            "type": ancestor.get("type"),
                            "title": ancestor.get("title")
                        }
                        for ancestor in data["ancestors"]
                    ]
                
                # Add links
                result["links"] = {
                    "self": data.get("_links", {}).get("self"),
                    "webui": data.get("_links", {}).get("webui"),
                    "edit": data.get("_links", {}).get("edit")
                }
                
                return {
                    "success": True,
                    "message": f"Page '{data.get('title')}' retrieved successfully",
                    "data": result
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
                    "message": f"No permission to view page '{page_id}'",
                    "error": "Forbidden"
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "message": f"Page '{page_id}' not found",
                    "error": "Not found"
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
    
    def _update_page(
        self,
        page_id: str,
        title: str,
        content: str,
        version: int,
        version_message: Optional[str] = None,
        page_type: str = "page"
    ) -> Dict[str, Any]:
        """
        Update existing Confluence page
        
        Args:
            page_id: Page ID to update
            title: New page title
            content: New page content in storage format
            version: Current version number (for optimistic locking)
            version_message: Version comment (optional)
            page_type: Page type (page or blogpost)
            
        Returns:
            Dictionary with update results
        """
        # Validate required parameters
        if not page_id or not title or not content or version is None:
            return {
                "success": False,
                "message": "Missing required parameters: page_id, title, content, and version are required"
            }
        
        # Build request payload
        payload = {
            "id": page_id,
            "type": page_type,
            "title": title,
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            },
            "version": {
                "number": version + 1
            }
        }
        
        # Add version message if provided
        if version_message:
            payload["version"]["message"] = version_message
        
        try:
            response = requests.put(
                f"{self.base_url}/content/{page_id}",
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "message": f"Page '{title}' updated successfully",
                    "data": {
                        "id": data.get("id"),
                        "title": data.get("title"),
                        "type": data.get("type"),
                        "space": {
                            "id": data.get("space", {}).get("id"),
                            "key": data.get("space", {}).get("key"),
                            "name": data.get("space", {}).get("name")
                        },
                        "version": {
                            "number": data.get("version", {}).get("number"),
                            "when": data.get("version", {}).get("when"),
                            "by": data.get("version", {}).get("by", {}).get("displayName", "Unknown"),
                            "message": version_message
                        },
                        "url": f"{self.base_url.replace('/rest/api/', '')}{data.get('_links', {}).get('webui', '')}"
                    }
                }
            elif response.status_code == 400:
                return {
                    "success": False,
                    "message": "Invalid update data provided",
                    "error": response.json().get("message", "Bad request")
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
                    "message": f"No permission to update page '{page_id}'",
                    "error": "Forbidden"
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "message": f"Page '{page_id}' not found",
                    "error": "Not found"
                }
            elif response.status_code == 409:
                return {
                    "success": False,
                    "message": "Version conflict. Page was modified by another user. Please refresh and try again",
                    "error": "Conflict"
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
    
    def _delete_page(self, page_id: str) -> Dict[str, Any]:
        """
        Delete Confluence page
        
        Args:
            page_id: Page ID to delete
            
        Returns:
            Dictionary with deletion results
        """
        if not page_id:
            return {
                "success": False,
                "message": "page_id is required"
            }
        
        try:
            response = requests.delete(
                f"{self.base_url}/content/{page_id}",
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code == 204:
                return {
                    "success": True,
                    "message": f"Page '{page_id}' deleted successfully",
                    "data": {
                        "page_id": page_id,
                        "deleted": True
                    }
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
                    "message": f"No permission to delete page '{page_id}'",
                    "error": "Forbidden"
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "message": f"Page '{page_id}' not found",
                    "error": "Not found"
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


# Create singleton instance
pages_tool = PagesToolManagement()
