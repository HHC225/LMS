"""
Slack User Cache Utility
Shared cache for resolving Slack user IDs to display names
"""
import asyncio
from typing import Dict
import aiohttp

from configs.slack import get_slack_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SlackUserCache:
    """
    Singleton cache for Slack user display names
    Shared across all Slack tools to avoid duplicate API calls
    """
    _instance = None
    _cache: Dict[str, str] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SlackUserCache, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.config = get_slack_config()
    
    async def get_user_display_name(self, user_id: str) -> str:
        """
        Get user's display name from Slack API
        Uses cache to avoid repeated API calls
        
        Args:
            user_id: User ID to lookup
            
        Returns:
            Display name (e.g., "john.doe" or "user.name") or user_id if not found
        """
        # Check cache first
        if user_id in self._cache:
            return self._cache[user_id]
        
        # Fetch from Slack API
        url = f"{self.config.base_url}/users.info"
        headers = {
            "Authorization": f"Bearer {self.config.bot_token}",
            "Content-Type": "application/json"
        }
        params = {"user": user_id}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    data = await response.json()
                    
                    if data.get("ok"):
                        user_info = data.get("user", {})
                        profile = user_info.get("profile", {})
                        # Try display_name first, fallback to real_name, then user_id
                        display_name = profile.get("display_name") or user_info.get("real_name") or user_id
                        
                        # Remove @ prefix if exists (to prevent mentions)
                        if display_name.startswith("@"):
                            display_name = display_name[1:]
                        
                        self._cache[user_id] = display_name
                        return display_name
                    else:
                        logger.warning(f"Failed to get user info for {user_id}: {data.get('error')}")
                        self._cache[user_id] = user_id
                        return user_id
        except Exception as e:
            logger.warning(f"Failed to resolve user {user_id}: {e}")
            self._cache[user_id] = user_id
            return user_id
    
    async def get_multiple_users(self, user_ids: list[str]) -> Dict[str, str]:
        """
        Get display names for multiple users efficiently
        
        Args:
            user_ids: List of user IDs to lookup
            
        Returns:
            Dict mapping user_id to display_name
        """
        # Filter out already cached users
        uncached_ids = [uid for uid in user_ids if uid not in self._cache]
        
        # Fetch uncached users with rate limiting
        if uncached_ids:
            tasks = []
            for user_id in uncached_ids:
                tasks.append(self.get_user_display_name(user_id))
                # Add small delay between requests to respect rate limits
                await asyncio.sleep(0.1)
            
            # Wait for all lookups to complete
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # Return all requested users from cache
        return {uid: self._cache.get(uid, uid) for uid in user_ids}
    
    def clear_cache(self):
        """Clear the user cache"""
        self._cache.clear()
        logger.info("Slack user cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "cached_users": len(self._cache),
            "cache_size_bytes": sum(len(k) + len(v) for k, v in self._cache.items())
        }


# Singleton instance
_user_cache = SlackUserCache()


async def get_user_display_name(user_id: str) -> str:
    """
    Convenience function to get user display name
    
    Args:
        user_id: User ID to lookup
        
    Returns:
        Display name or user_id if not found
    """
    return await _user_cache.get_user_display_name(user_id)


async def get_multiple_user_names(user_ids: list[str]) -> Dict[str, str]:
    """
    Convenience function to get multiple user display names
    
    Args:
        user_ids: List of user IDs to lookup
        
    Returns:
        Dict mapping user_id to display_name
    """
    return await _user_cache.get_multiple_users(user_ids)


def clear_user_cache():
    """Convenience function to clear the cache"""
    _user_cache.clear_cache()


def get_cache_stats() -> Dict[str, int]:
    """Convenience function to get cache stats"""
    return _user_cache.get_cache_stats()
