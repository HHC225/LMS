"""
Slack Message Posting Tool
Provides unified interface for posting messages to Slack (public or ephemeral)
"""
from typing import Optional
import aiohttp

from src.tools.base import BaseTool
from configs.slack import get_slack_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SlackMessagePostingTool(BaseTool):
    """
    Unified tool for posting messages to Slack
    Supports both public messages and ephemeral (private) messages
    """
    
    def __init__(self):
        super().__init__(
            name="slack_message_posting",
            description="Posts messages to Slack (public or ephemeral)"
        )
        self.config = get_slack_config()
    
    async def execute(
        self,
        channel: str,
        text: str = None,
        content: str = None,
        ephemeral: bool = False,
        user: Optional[str] = None,
        username: Optional[str] = None,
        icon_emoji: Optional[str] = None,
        thread_ts: Optional[str] = None,
        title: Optional[str] = None,
        format_type: str = 'detailed',
        **kwargs
    ) -> str:
        """
        Execute message posting
        
        Args:
            channel: Channel ID (required)
            text: Message text for public messages (use either text or content)
            content: Message content for ephemeral messages (use either text or content)
            ephemeral: If True, posts ephemeral message. If False, posts public message
            user: User ID for ephemeral messages (uses default_user_id if not provided)
            username: Display name for public messages (optional)
            icon_emoji: Icon emoji for public messages (optional, e.g., :robot_face:)
            thread_ts: Thread timestamp for reply (optional)
            title: Message title for ephemeral messages (optional)
            format_type: Display format for ephemeral messages ('simple' or 'detailed')
            
        Returns:
            Success/failure message with details
        """
        try:
            if not channel:
                raise ValueError("'channel' is required parameter")
            
            message_text = text or content
            if not message_text:
                raise ValueError("Either 'text' or 'content' is required parameter")
            
            if ephemeral:
                # Post ephemeral (private) message
                result = await self._post_ephemeral_message(
                    channel=channel,
                    content=message_text,
                    title=title,
                    thread_ts=thread_ts,
                    format_type=format_type,
                    user=user
                )
            else:
                # Post public message
                result = await self._post_public_message(
                    channel=channel,
                    text=message_text,
                    username=username,
                    icon_emoji=icon_emoji,
                    thread_ts=thread_ts
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to post message: {e}")
            return self._format_error_response(str(e), channel, ephemeral)
    
    async def _post_public_message(
        self,
        channel: str,
        text: str,
        username: Optional[str] = None,
        icon_emoji: Optional[str] = None,
        thread_ts: Optional[str] = None
    ) -> str:
        """
        Post public message to channel
        
        Args:
            channel: Channel ID
            text: Message text
            username: Display name (optional)
            icon_emoji: Icon emoji (optional)
            thread_ts: Thread timestamp (optional)
            
        Returns:
            Success message
        """
        # Prepare message payload
        payload = {
            'channel': channel,
            'text': text
        }
        
        if username:
            payload['username'] = username
        if icon_emoji:
            payload['icon_emoji'] = icon_emoji
        if thread_ts:
            payload['thread_ts'] = thread_ts
        
        # Send message via Slack API
        url = f"{self.config.base_url}/chat.postMessage"
        headers = {
            'Authorization': f'Bearer {self.config.bot_token}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                data = await response.json()
                
                if not data.get('ok'):
                    error_msg = data.get('error', 'Unknown error')
                    raise Exception(f"Slack API error: {error_msg}")
                
                timestamp = data.get('ts', 'N/A')
                preview = text[:100] + '...' if len(text) > 100 else text
                
                return f"""✅ Public message posted successfully

**Post Details:**
- Channel: {channel}
- Timestamp: {timestamp}
- Message Length: {len(text)} characters
- Message Type: Public

**Message Preview:**
{preview}"""
    
    async def _post_ephemeral_message(
        self,
        channel: str,
        content: str,
        title: Optional[str] = None,
        thread_ts: Optional[str] = None,
        format_type: str = 'detailed',
        user: Optional[str] = None
    ) -> str:
        """
        Post ephemeral (private) message to specific user
        
        Args:
            channel: Channel ID
            content: Message content
            title: Message title (optional)
            thread_ts: Thread timestamp (optional)
            format_type: Display format ('simple' or 'detailed')
            user: User ID (optional, uses default_user_id from config)
            
        Returns:
            Success message
        """
        # Use default user if not specified
        target_user = user or self.config.default_user_id
        
        if not target_user:
            raise ValueError("User ID not specified and default_user_id not configured")
        
        # Format message text
        message_text = self._format_ephemeral_message(content, title, format_type)
        
        # Prepare payload
        payload = {
            'channel': channel,
            'user': target_user,
            'text': message_text
        }
        
        if thread_ts:
            payload['thread_ts'] = thread_ts
        
        # Send ephemeral message via Slack API
        url = f"{self.config.base_url}/chat.postEphemeral"
        headers = {
            'Authorization': f'Bearer {self.config.bot_token}',
            'Content-Type': 'application/json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                data = await response.json()
                
                if not data.get('ok'):
                    error_msg = data.get('error', 'Unknown error')
                    raise Exception(f"Slack API error: {error_msg}")
                
                return f"""✅ Ephemeral message posted successfully

**Post Details:**
- Channel: {channel}
- Target User: {target_user}
- Message Type: Private (Ephemeral)

**Note:** This message is only visible to the specified user."""
    
    def _format_ephemeral_message(
        self,
        content: str,
        title: Optional[str],
        format_type: str
    ) -> str:
        """
        Format ephemeral message content based on type
        
        Args:
            content: Main content
            title: Optional title
            format_type: 'simple' or 'detailed'
            
        Returns:
            Formatted message text
        """
        if format_type == 'simple':
            return f"{title}\n\n{content}" if title else content
        else:
            # Detailed format with structure
            parts = []
            if title:
                parts.append(f"*{title}*")
                parts.append("")
            parts.append(content)
            return "\n".join(parts)
    
    def _format_error_response(self, error: str, channel: str, ephemeral: bool) -> str:
        """Format error response"""
        message_type = "ephemeral" if ephemeral else "public"
        
        base_message = f"""❌ Failed to post {message_type} message

**Error Details:**
- Channel: {channel}
- Error: {error}
"""
        
        if ephemeral:
            base_message += """
**Possible Causes:**
- Bot token required (user token won't work)
- Bot not in channel
- User not in channel
- Invalid user ID

**Solutions:**
1. Verify bot token is configured
2. Invite bot to channel
3. Verify user is channel member
4. Check default_user_id in config"""
        else:
            base_message += """
**Possible Causes:**
- Invalid channel ID
- Bot not in channel
- Missing permissions
- Network/API error

**Solutions:**
1. Verify channel ID
2. Invite bot to channel
3. Check network connection
4. Retry after a moment"""
        
        return base_message
