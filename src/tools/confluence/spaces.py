"""
Confluence Spaces Tool
Tool for managing Confluence spaces
"""

import json
import requests
from typing import Dict, Any, Optional, List
from configs.confluence import get_confluence_config


class SpacesToolManagement:
    """
    Confluence Spaces Management Tool
    
    Handles space operations: get_spaces
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
        Execute space action
        
        Args:
            action: Action to perform (get_spaces)
            **kwargs: Action-specific parameters
            
        Returns:
            JSON string with action results
        """
        if action == "get_spaces":
            result = self._get_spaces(**kwargs)
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            return json.dumps({
                "success": False,
                "message": f"Unknown action: {action}. Available actions: get_spaces"
            }, ensure_ascii=False)
    
    def _get_spaces(
        self,
        space_key: Optional[str] = None,
        space_type: Optional[str] = None,
        status: str = "current",
        expand: Optional[List[str]] = None,
        limit: int = 25
    ) -> Dict[str, Any]:
        """
        Get Confluence spaces
        
        Args:
            space_key: Specific space key to retrieve (optional)
            space_type: Space type filter (global or personal)
            status: Space status (current or archived)
            expand: List of fields to expand (optional)
            limit: Maximum number of results (1-100)
            
        Returns:
            Dictionary with space list or single space details
        """
        # If specific space key is requested
        if space_key:
            return self._get_single_space(space_key, expand)
        
        # Build query parameters
        params = {
            "limit": limit,
            "status": status
        }
        
        if space_type:
            params["type"] = space_type
        
        if expand:
            params["expand"] = ",".join(expand)
        
        try:
            response = requests.get(
                f"{self.base_url}/space",
                headers=self.headers,
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                spaces = []
                
                for space in data.get("results", []):
                    space_info = {
                        "id": space.get("id"),
                        "key": space.get("key"),
                        "name": space.get("name"),
                        "type": space.get("type"),
                        "status": space.get("status")
                    }
                    
                    # Add homepage if expanded
                    if "homepage" in space:
                        space_info["homepage"] = {
                            "id": space["homepage"].get("id"),
                            "title": space["homepage"].get("title"),
                            "url": space["homepage"].get("_links", {}).get("webui")
                        }
                    
                    # Add description if expanded
                    if "description" in space and space["description"]:
                        desc_plain = space["description"].get("plain", {})
                        if desc_plain:
                            space_info["description"] = desc_plain.get("value", "")
                    
                    spaces.append(space_info)
                
                return {
                    "success": True,
                    "message": f"Retrieved {len(spaces)} space(s)",
                    "data": {
                        "spaces": spaces,
                        "pagination": {
                            "start": data.get("start", 0),
                            "limit": data.get("limit", limit),
                            "size": data.get("size", len(spaces)),
                            "total": len(spaces)
                        }
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
                    "message": "No permission to view spaces",
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
    
    def _get_single_space(
        self,
        space_key: str,
        expand: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get single space by key
        
        Args:
            space_key: Space key to retrieve
            expand: List of fields to expand
            
        Returns:
            Dictionary with space details
        """
        params = {}
        if expand:
            params["expand"] = ",".join(expand)
        
        try:
            response = requests.get(
                f"{self.base_url}/space/{space_key}",
                headers=self.headers,
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                space = response.json()
                
                space_info = {
                    "id": space.get("id"),
                    "key": space.get("key"),
                    "name": space.get("name"),
                    "type": space.get("type"),
                    "status": space.get("status")
                }
                
                # Add homepage if expanded
                if "homepage" in space:
                    space_info["homepage"] = {
                        "id": space["homepage"].get("id"),
                        "title": space["homepage"].get("title"),
                        "url": space["homepage"].get("_links", {}).get("webui")
                    }
                
                # Add description if expanded
                if "description" in space and space["description"]:
                    desc_plain = space["description"].get("plain", {})
                    if desc_plain:
                        space_info["description"] = desc_plain.get("value", "")
                
                return {
                    "success": True,
                    "message": f"Space '{space_key}' retrieved successfully",
                    "data": space_info
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
                    "message": f"No permission to view space '{space_key}'",
                    "error": "Forbidden"
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "message": f"Space '{space_key}' not found",
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
spaces_tool = SpacesToolManagement()
