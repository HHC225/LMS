"""
Slack Message Retrieval Tool
Provides unified interface for retrieving Slack messages (single or thread)
"""
import re
from typing import Optional, Dict, Any, List
from datetime import datetime
import aiohttp

from src.tools.base import BaseTool
from configs.slack import get_slack_config
from src.utils.slack_user_cache import get_user_display_name
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SlackMessageRetrievalTool(BaseTool):
    """
    Unified tool for retrieving Slack messages
    Supports both single message and full thread retrieval
    """
    
    def __init__(self):
        super().__init__(
            name="slack_message_retrieval",
            description="Retrieves Slack messages (single or thread)"
        )
        self.config = get_slack_config()
    
    async def execute(
        self,
        channel: Optional[str] = None,
        timestamp: Optional[str] = None,
        url: Optional[str] = None,
        include_replies: bool = False,
        **kwargs
    ) -> str:
        """
        Execute message retrieval
        
        Args:
            channel: Channel ID (required if url not provided)
            timestamp: Message timestamp (required if url not provided)
            url: Slack URL to extract channel and timestamp from
            include_replies: If True, retrieves entire thread. If False, single message only
            
        Returns:
            Formatted message or thread content
        """
        try:
            # Parse URL if provided
            if url:
                parsed = self._parse_slack_url(url)
                channel = parsed['channel']
                message_ts = parsed['message_ts']
                thread_ts = parsed['thread_ts']
                
                # Determine which timestamp to use
                if include_replies:
                    # For thread content: use thread_ts if exists, otherwise message_ts
                    timestamp = thread_ts or message_ts
                else:
                    # For single message: use message_ts (the specific message in URL)
                    timestamp = message_ts
                    # If this is a reply in a thread, we need the thread_ts to fetch it
                    if thread_ts and thread_ts != message_ts:
                        # This is a reply, fetch from thread
                        message = await self._fetch_single_reply(channel, thread_ts, message_ts)
                        formatted = await self._format_single_message(message, channel, message_ts)
                        return formatted
            else:
                message_ts = timestamp
                thread_ts = None
            
            if not channel or not timestamp:
                raise ValueError("Either url or (channel + timestamp) must be provided")
            
            # Normalize timestamp
            timestamp = self._normalize_timestamp(timestamp)
            
            if include_replies:
                # Retrieve entire thread
                messages = await self._fetch_thread_messages(channel, timestamp)
                formatted = await self._format_thread_content(messages, channel, timestamp)
            else:
                # Retrieve single message only (top-level message)
                message = await self._fetch_single_message(channel, timestamp)
                formatted = await self._format_single_message(message, channel, timestamp)
            
            return formatted
            
        except Exception as e:
            logger.error(f"Failed to retrieve message: {e}")
            return f"❌ Failed to retrieve message: {str(e)}"
    
    def _parse_slack_url(self, url: str) -> Dict[str, Optional[str]]:
        """
        Parse Slack URL to extract channel and timestamps
        
        Args:
            url: Slack message URL
            
        Returns:
            Dict with channel, message_ts, and thread_ts
        """
        # Pattern: https://workspace.slack.com/archives/CHANNEL/pTIMESTAMP?thread_ts=THREAD_TS
        pattern = r'https://[^/]+/archives/([^/]+)/p(\d+)(?:\?thread_ts=([\d.]+))?'
        match = re.search(pattern, url)
        
        if not match:
            raise ValueError(f"Invalid Slack URL format: {url}")
        
        channel = match.group(1)
        message_ts_raw = match.group(2)
        thread_ts = match.group(3)
        
        # Convert pTIMESTAMP to timestamp format
        message_ts = f"{message_ts_raw[:10]}.{message_ts_raw[10:]}"
        
        return {
            'channel': channel,
            'message_ts': message_ts,
            'thread_ts': thread_ts
        }
    
    def _normalize_timestamp(self, ts: str) -> str:
        """Normalize timestamp to Slack format"""
        if '.' not in ts and ts.isdigit():
            # Unix timestamp to Slack format
            return f"{ts[:10]}.{ts[10:]}" if len(ts) > 10 else f"{ts}.000000"
        return ts
    
    async def _fetch_single_message(
        self,
        channel: str,
        timestamp: str
    ) -> Dict[str, Any]:
        """
        Fetch a single message using Slack API
        Uses conversations.history with inclusive timestamps
        
        Args:
            channel: Channel ID
            timestamp: Message timestamp
            
        Returns:
            Message dictionary
        """
        url = f"{self.config.base_url}/conversations.history"
        
        # Use USER token for GET operations (better channel access)
        token = self.config.user_token if self.config.user_token else self.config.bot_token
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        params = {
            'channel': channel,
            'latest': timestamp,
            'oldest': timestamp,
            'inclusive': 'true',
            'limit': 1
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                data = await response.json()
                
                if not data.get('ok'):
                    error_msg = data.get('error', 'Unknown error')
                    raise Exception(f"Slack API error: {error_msg}")
                
                messages = data.get('messages', [])
                if not messages:
                    raise Exception(f"Message not found: {timestamp}")
                
                return messages[0]
    
    async def fetch_channel_history(
        self,
        channel: str,
        oldest: Optional[str] = None,
        latest: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Fetch channel message history with pagination support
        
        Args:
            channel: Channel ID
            oldest: Start timestamp (optional)
            latest: End timestamp (optional)
            limit: Maximum number of messages to retrieve (default: 100, max: 1000)
            
        Returns:
            Dict with messages, total count, pages processed, and has_more flag
        """
        url = f"{self.config.base_url}/conversations.history"
        
        # Use USER token for GET operations (better channel access)
        token = self.config.user_token if self.config.user_token else self.config.bot_token
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        all_messages = []
        cursor = None
        page_count = 0
        has_more = True
        max_pages = 10  # Maximum pages to prevent infinite loops
        
        async with aiohttp.ClientSession() as session:
            while has_more and page_count < max_pages and len(all_messages) < limit:
                params = {
                    'channel': channel,
                    'limit': min(100, limit - len(all_messages))  # Max 100 per request
                }
                
                if oldest:
                    params['oldest'] = oldest
                if latest:
                    params['latest'] = latest
                if cursor:
                    params['cursor'] = cursor
                
                async with session.get(url, headers=headers, params=params) as response:
                    data = await response.json()
                    
                    if not data.get('ok'):
                        error_msg = data.get('error', 'Unknown error')
                        raise Exception(f"Slack API error: {error_msg}")
                    
                    messages = data.get('messages', [])
                    if messages:
                        all_messages.extend(messages)
                    
                    has_more = data.get('has_more', False)
                    cursor = data.get('response_metadata', {}).get('next_cursor')
                    page_count += 1
                    
                    # Rate limiting: wait 100ms between requests
                    if has_more and page_count < max_pages:
                        await asyncio.sleep(0.1)
        
        return {
            'messages': all_messages,
            'total_count': len(all_messages),
            'pages_processed': page_count,
            'has_more': has_more
        }
    
    async def _fetch_single_reply(
        self,
        channel: str,
        thread_ts: str,
        message_ts: str
    ) -> Dict[str, Any]:
        """
        Fetch a single reply from a thread
        
        Args:
            channel: Channel ID
            thread_ts: Thread timestamp
            message_ts: Specific message timestamp to retrieve
            
        Returns:
            Message dictionary
        """
        # Fetch entire thread
        messages = await self._fetch_thread_messages(channel, thread_ts)
        
        # Find the specific message
        message_ts_normalized = self._normalize_timestamp(message_ts)
        for msg in messages:
            if msg.get('ts') == message_ts_normalized:
                return msg
        
        raise Exception(f"Reply not found: {message_ts} in thread {thread_ts}")
    
    async def _fetch_thread_messages(
        self,
        channel: str,
        thread_ts: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch all messages in a thread using Slack API
        Uses USER token for better channel access
        
        Args:
            channel: Channel ID
            thread_ts: Thread timestamp
            
        Returns:
            List of message dictionaries
        """
        url = f"{self.config.base_url}/conversations.replies"
        
        # Use USER token for GET operations (better channel access)
        token = self.config.user_token if self.config.user_token else self.config.bot_token
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        params = {
            'channel': channel,
            'ts': thread_ts,
            'limit': 1000
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                data = await response.json()
                
                if not data.get('ok'):
                    error_msg = data.get('error', 'Unknown error')
                    raise Exception(f"Slack API error: {error_msg}")
                
                return data.get('messages', [])
    
    async def _format_single_message(
        self,
        message: Dict[str, Any],
        channel: str,
        timestamp: str
    ) -> str:
        """
        Format single message for output
        
        Args:
            message: Message dictionary
            channel: Channel ID
            timestamp: Message timestamp
            
        Returns:
            Formatted string
        """
        msg_ts = message.get('ts', timestamp)
        user_id = message.get('user', 'Unknown')
        text = message.get('text', '')
        
        # Get user display name from shared cache
        user = await get_user_display_name(user_id)
        
        # Format timestamp to readable format
        try:
            dt = datetime.fromtimestamp(float(msg_ts))
            time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            time_str = msg_ts
        
        output = [
            "📬 **Single Slack Message**",
            "",
            f"Channel: {channel}",
            f"Timestamp: {msg_ts}",
            f"Time: {time_str}",
            f"User: {user}"
        ]
        
        # Check if message has thread replies
        reply_count = message.get('reply_count', 0)
        if reply_count > 0:
            output.append(f"📎 Thread replies: {reply_count}")
        
        # Extract attachments info if any
        attachments = message.get('files', [])
        if attachments:
            output.append(f"📁 Attachments: {len(attachments)} file(s)")
            for idx, file in enumerate(attachments, 1):
                file_name = file.get('name', 'Unknown')
                file_type = file.get('pretty_type', file.get('filetype', 'File'))
                output.append(f"  [{idx}] {file_name} ({file_type})")
        
        # Extract reactions if any
        reactions = message.get('reactions', [])
        if reactions:
            reaction_strs = []
            for reaction in reactions:
                emoji = reaction.get('name', '')
                count = reaction.get('count', 0)
                reaction_strs.append(f"{emoji} ({count})")
            output.append(f"💬 Reactions: {', '.join(reaction_strs)}")
        
        output.extend([
            "",
            "=" * 60,
            "",
            text,
            "",
            "=" * 60
        ])
        
        return "\n".join(output)
    
    async def _format_thread_content(
        self,
        messages: List[Dict[str, Any]],
        channel: str,
        thread_ts: str
    ) -> str:
        """
        Format thread messages for output
        
        Args:
            messages: List of message dictionaries
            channel: Channel ID
            thread_ts: Thread timestamp
            
        Returns:
            Formatted string
        """
        output = [
            "📨 **Slack Thread Content**",
            f"Channel: {channel}",
            f"Thread TS: {thread_ts}",
            f"Total Messages: {len(messages)}",
            "\n" + "=" * 60 + "\n"
        ]
        
        for idx, msg in enumerate(messages, 1):
            timestamp = msg.get('ts', '')
            user_id = msg.get('user', 'Unknown')
            text = msg.get('text', '')
            
            # Get user display name from shared cache
            user = await get_user_display_name(user_id)
            
            # Format timestamp to readable format
            try:
                dt = datetime.fromtimestamp(float(timestamp))
                time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                time_str = timestamp
            
            output.append(f"[{idx}] {time_str} - User: {user}")
            output.append(f"{text}")
            output.append("-" * 60)
        
        return "\n".join(output)
