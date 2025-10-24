"""
Delete Message Tool
Deletes messages from Slack channels - supports single and bulk deletion
"""
import re
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
import aiohttp

from src.tools.base import BaseTool
from configs.slack import get_slack_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DeleteMessageTool(BaseTool):
    """
    Tool to delete messages from Slack channels
    
    Features:
    - Single message deletion by URL or channel+timestamp
    - Bulk deletion by date range
    - Bot-only message filtering
    - Preview mode for safety
    - Maximum deletion limit protection
    
    Can only delete messages sent by the bot or messages the bot has permission to delete
    """
    
    def __init__(self):
        super().__init__(
            name="delete_message",
            description="Delete message(s) from Slack channel - supports single and bulk deletion"
        )
        self.config = get_slack_config()
    
    async def execute(
        self,
        channel: Optional[str] = None,
        ts: Optional[str] = None,
        url: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        bot_only: bool = False,
        preview: bool = True,
        max_messages: int = 100,
        **kwargs
    ) -> str:
        """
        Execute message deletion (single or bulk)
        
        Single deletion parameters:
            channel: Channel ID (required if url not provided)
            ts: Message timestamp (required if url not provided)
            url: Slack message URL to extract channel and timestamp
            
        Bulk deletion parameters:
            channel: Channel ID (required)
            from_date: Start date (YYYY-MM-DD or timestamp, optional)
            to_date: End date (YYYY-MM-DD or timestamp, optional)
            bot_only: Delete only bot messages (default: False)
            preview: Preview mode - shows what would be deleted (default: True)
            max_messages: Maximum number of messages to delete (default: 100)
            
        Returns:
            Success/failure message with details
        """
        try:
            # Determine if this is bulk deletion or single deletion
            is_bulk = from_date is not None or to_date is not None
            
            if is_bulk:
                return await self._execute_bulk_delete(
                    channel=channel,
                    from_date=from_date,
                    to_date=to_date,
                    bot_only=bot_only,
                    preview=preview,
                    max_messages=max_messages
                )
            else:
                return await self._execute_single_delete(
                    channel=channel,
                    ts=ts,
                    url=url
                )
            
        except Exception as e:
            logger.error(f"Failed to delete message(s): {e}")
            return self._format_error_response(str(e), channel, ts)
    
    async def _execute_single_delete(
        self,
        channel: Optional[str],
        ts: Optional[str],
        url: Optional[str]
    ) -> str:
        """
        Execute single message deletion
        
        Args:
            channel: Channel ID
            ts: Message timestamp
            url: Slack message URL
            
        Returns:
            Formatted result string
        """
        # Parse URL if provided
        if url:
            parsed = self._parse_slack_url(url)
            channel = parsed['channel']
            ts = parsed['ts']
        
        if not channel or not ts:
            raise ValueError("Either url or (channel + ts) must be provided")
        
        # Validate timestamp format
        if not re.match(r'^\d+\.\d+$', ts):
            raise ValueError(f"Invalid timestamp format: {ts}. Expected format: 1234567890.123456")
        
        # Delete message via Slack API
        await self._delete_message(channel, ts)
        
        return self._format_success_response(channel, ts)
    
    async def _execute_bulk_delete(
        self,
        channel: Optional[str],
        from_date: Optional[str],
        to_date: Optional[str],
        bot_only: bool,
        preview: bool,
        max_messages: int
    ) -> str:
        """
        Execute bulk message deletion
        
        Args:
            channel: Channel ID
            from_date: Start date (YYYY-MM-DD or timestamp)
            to_date: End date (YYYY-MM-DD or timestamp)
            bot_only: Delete only bot messages
            preview: Preview mode
            max_messages: Maximum deletion limit
            
        Returns:
            Formatted result string
        """
        if not channel:
            raise ValueError("Channel ID is required for bulk deletion")
        
        # Convert dates to timestamps
        from_ts = self._date_to_timestamp(from_date) if from_date else None
        to_ts = self._date_to_timestamp(to_date) if to_date else None
        
        # If from_ts is a Slack timestamp (has decimal point), subtract 0.000001 to include the exact timestamp
        # This ensures the specified timestamp itself is included in the deletion range
        if from_ts and '.' in from_ts:
            from_ts = str(float(from_ts) - 0.000001)
            logger.info(f"Adjusted from_ts to include exact timestamp: {from_ts}")
        
        logger.info(f"Bulk delete: channel={channel}, from={from_ts}, to={to_ts}, bot_only={bot_only}")
        
        # Get channel history
        messages = await self._get_channel_history(channel, from_ts, to_ts)
        
        logger.info(f"Retrieved {len(messages)} messages from channel history")
        
        # Filter messages
        filtered_messages = self._filter_messages(messages, from_ts, to_ts, bot_only)
        
        logger.info(f"Filtered to {len(filtered_messages)} messages")
        
        # Check maximum limit
        if len(filtered_messages) > max_messages:
            return self._format_over_limit_response(
                len(filtered_messages),
                max_messages,
                channel,
                from_date,
                to_date,
                bot_only
            )
        
        if len(filtered_messages) == 0:
            return self._format_no_messages_response(channel, from_date, to_date, bot_only)
        
        # Preview mode
        if preview:
            return self._format_bulk_result(filtered_messages, [], is_preview=True)
        
        # Execute deletion
        deleted_messages = []
        failed_messages = []
        
        logger.info(f"Starting deletion of {len(filtered_messages)} messages")
        
        for msg_info in filtered_messages:
            try:
                await self._delete_message(channel, msg_info['ts'])
                deleted_messages.append(msg_info)
                logger.info(f"✅ Deleted: {msg_info['ts']}")
            except Exception as e:
                error_msg = self._parse_deletion_error(str(e))
                failed_messages.append({
                    'message': msg_info,
                    'error': error_msg
                })
                logger.warning(f"❌ Failed to delete {msg_info['ts']}: {error_msg}")
            
            # Rate limiting: wait 100ms between deletions
            await asyncio.sleep(0.1)
        
        return self._format_bulk_result(deleted_messages, failed_messages, is_preview=False)
    
    def _date_to_timestamp(self, date_str: str) -> str:
        """
        Convert date string to Slack timestamp
        
        Args:
            date_str: Date string (YYYY-MM-DD or timestamp)
            
        Returns:
            Timestamp string
        """
        # Check if already timestamp format
        if re.match(r'^\d+(\.\d+)?$', date_str):
            return date_str
        
        try:
            # Parse YYYY-MM-DD format
            if 'T' in date_str:
                # ISO format with time
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                # YYYY-MM-DD format - parse as UTC midnight
                dt = datetime.strptime(date_str, '%Y-%m-%d')
            
            timestamp = dt.timestamp()
            return str(timestamp)
            
        except Exception as e:
            raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD or timestamp. Error: {e}")
    
    async def _get_channel_history(
        self,
        channel: str,
        oldest: Optional[str],
        latest: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Get channel message history from Slack API
        Includes both parent messages and thread replies
        
        Args:
            channel: Channel ID
            oldest: Oldest timestamp
            latest: Latest timestamp
            
        Returns:
            List of message dictionaries (including thread replies)
        """
        url = f"{self.config.base_url}/conversations.history"
        headers = {
            'Authorization': f'Bearer {self.config.bot_token}',
            'Content-Type': 'application/json'
        }
        
        all_messages = []
        cursor = None
        
        async with aiohttp.ClientSession() as session:
            # Step 1: Get parent messages
            while True:
                params = {
                    'channel': channel,
                    'limit': 1000  # Maximum per request
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
                        raise Exception(f"Failed to get channel history: {error_msg}")
                    
                    messages = data.get('messages', [])
                    all_messages.extend(messages)
                    
                    # Check for more pages
                    if not data.get('has_more'):
                        break
                    
                    cursor = data.get('response_metadata', {}).get('next_cursor')
                    if not cursor:
                        break
                    
                    # Rate limiting
                    await asyncio.sleep(0.1)
            
            # Step 2: Get thread replies for messages that have replies
            messages_with_replies = [msg for msg in all_messages if msg.get('reply_count', 0) > 0]
            
            logger.info(f"Found {len(messages_with_replies)} parent messages with replies")
            
            for parent_msg in messages_with_replies:
                thread_ts = parent_msg['ts']
                
                try:
                    # Get thread replies
                    replies = await self._get_thread_replies(session, headers, channel, thread_ts)
                    
                    # Add replies to all_messages (skip first message as it's the parent)
                    if len(replies) > 1:
                        all_messages.extend(replies[1:])
                        logger.info(f"Added {len(replies) - 1} replies from thread {thread_ts}")
                    
                except Exception as e:
                    logger.warning(f"Failed to get replies for thread {thread_ts}: {e}")
                
                # Rate limiting
                await asyncio.sleep(0.1)
        
        return all_messages
    
    async def _get_thread_replies(
        self,
        session: aiohttp.ClientSession,
        headers: Dict[str, str],
        channel: str,
        thread_ts: str
    ) -> List[Dict[str, Any]]:
        """
        Get all replies in a thread
        
        Args:
            session: aiohttp session
            headers: HTTP headers
            channel: Channel ID
            thread_ts: Thread timestamp
            
        Returns:
            List of reply messages (including parent)
        """
        url = f"{self.config.base_url}/conversations.replies"
        params = {
            'channel': channel,
            'ts': thread_ts,
            'limit': 1000
        }
        
        async with session.get(url, headers=headers, params=params) as response:
            data = await response.json()
            
            if not data.get('ok'):
                error_msg = data.get('error', 'Unknown error')
                raise Exception(f"Failed to get thread replies: {error_msg}")
            
            return data.get('messages', [])
    
    def _filter_messages(
        self,
        messages: List[Dict[str, Any]],
        from_ts: Optional[str],
        to_ts: Optional[str],
        bot_only: bool
    ) -> List[Dict[str, Any]]:
        """
        Filter messages by criteria
        
        Args:
            messages: List of message dictionaries
            from_ts: Start timestamp
            to_ts: End timestamp
            bot_only: Filter for bot messages only
            
        Returns:
            List of filtered message info dictionaries
        """
        filtered = []
        
        for msg in messages:
            msg_ts = float(msg.get('ts', 0))
            
            # Check timestamp range
            if from_ts and msg_ts < float(from_ts):
                continue
            if to_ts and msg_ts > float(to_ts):
                continue
            
            # Check bot filter
            if bot_only and not msg.get('bot_id'):
                continue
            
            # Extract message info
            text = msg.get('text', '')
            if len(text) > 100:
                text = text[:100] + '...'
            
            filtered.append({
                'ts': msg['ts'],
                'user': msg.get('user'),
                'bot_id': msg.get('bot_id'),
                'text': text,
                'created': datetime.fromtimestamp(msg_ts)
            })
        
        return filtered
    
    def _parse_deletion_error(self, error: str) -> str:
        """
        Parse deletion error message
        
        Args:
            error: Error message
            
        Returns:
            Parsed error string
        """
        if 'cant_delete_message' in error:
            return 'No permission to delete'
        elif 'message_not_found' in error:
            return 'Message not found'
        elif 'channel_not_found' in error:
            return 'Channel not found'
        else:
            return error[:50]
    
    def _format_bulk_result(
        self,
        deleted_messages: List[Dict[str, Any]],
        failed_messages: List[Dict[str, Any]],
        is_preview: bool
    ) -> str:
        """
        Format bulk deletion result
        
        Args:
            deleted_messages: List of deleted message info
            failed_messages: List of failed deletions
            is_preview: Preview mode flag
            
        Returns:
            Formatted result string
        """
        action = 'Preview' if is_preview else 'Deletion'
        lines = [f"📊 Bulk Message {action} Result\n"]
        
        lines.append(f"✅ {action}{' targets' if is_preview else 'd'} messages: {len(deleted_messages)}")
        if failed_messages:
            lines.append(f"❌ Failed messages: {len(failed_messages)}")
        lines.append("")
        
        # Show deleted messages (max 10)
        if deleted_messages:
            lines.append(f"📋 {action}{' Target' if is_preview else 'd'} Messages:")
            for i, msg in enumerate(deleted_messages[:10]):
                msg_type = '🤖 Bot' if msg.get('bot_id') else '👤 User'
                date_str = msg['created'].strftime('%Y-%m-%d %H:%M')
                lines.append(f"{i+1}. {msg_type} | {date_str} | {msg['text']}")
            
            if len(deleted_messages) > 10:
                lines.append(f"... and {len(deleted_messages) - 10} more messages")
            lines.append("")
        
        # Show failed messages (max 5)
        if failed_messages:
            lines.append("❌ Failed Messages:")
            for i, failed in enumerate(failed_messages[:5]):
                msg = failed['message']
                error = failed['error']
                date_str = msg['created'].strftime('%Y-%m-%d %H:%M')
                lines.append(f"{i+1}. {date_str} | {error}")
            
            if len(failed_messages) > 5:
                lines.append(f"... and {len(failed_messages) - 5} more failures")
            lines.append("")
        
        if is_preview:
            lines.append("💡 To actually delete these messages, set preview=false and run again.")
            lines.append("⚠️ Deleted messages cannot be restored.")
        else:
            lines.append("✅ Deletion completed. Deleted messages cannot be restored.")
        
        return "\n".join(lines)
    
    def _format_over_limit_response(
        self,
        found_count: int,
        max_count: int,
        channel: str,
        from_date: Optional[str],
        to_date: Optional[str],
        bot_only: bool
    ) -> str:
        """Format over limit response"""
        lines = [
            "⚠️ Too many messages to delete\n",
            f"🔍 Messages found: {found_count}",
            f"📊 Maximum allowed: {max_count}\n",
            "💡 **Options:**",
            "  - Increase max_messages parameter",
            "  - Narrow the date range",
            "  - Use more specific filters\n",
            "**Current filters:**",
            f"  - Channel: {channel}",
            f"  - From: {from_date or 'No limit'}",
            f"  - To: {to_date or 'No limit'}",
            f"  - Bot only: {'Yes' if bot_only else 'No'}"
        ]
        return "\n".join(lines)
    
    def _format_no_messages_response(
        self,
        channel: str,
        from_date: Optional[str],
        to_date: Optional[str],
        bot_only: bool
    ) -> str:
        """Format no messages found response"""
        lines = [
            "📭 No messages to delete\n",
            "🔍 **Search criteria:**",
            f"  - Channel: {channel}",
            f"  - From: {from_date or 'No limit'}",
            f"  - To: {to_date or 'No limit'}",
            f"  - Bot messages only: {'Yes' if bot_only else 'No'}\n",
            "💡 **Try:**",
            "  - Adjust the date range",
            "  - Change the bot_only filter",
            "  - Verify the channel ID"
        ]
        return "\n".join(lines)
    
    def _parse_slack_url(self, url: str) -> dict:
        """
        Parse Slack URL to extract channel and timestamp
        
        Args:
            url: Slack message URL
            
        Returns:
            Dict with channel and ts
        """
        # Pattern: https://workspace.slack.com/archives/CHANNEL/pTIMESTAMP
        pattern = r'https://[^/]+/archives/([^/]+)/p(\d+)'
        match = re.search(pattern, url)
        
        if not match:
            raise ValueError(f"Invalid Slack URL format: {url}")
        
        channel = match.group(1)
        timestamp_raw = match.group(2)
        
        # Convert pTIMESTAMP to timestamp format
        timestamp = f"{timestamp_raw[:10]}.{timestamp_raw[10:]}"
        
        return {
            'channel': channel,
            'ts': timestamp
        }
    
    async def _delete_message(self, channel: str, ts: str) -> None:
        """
        Delete message via Slack API
        
        Args:
            channel: Channel ID
            ts: Message timestamp
        """
        url = f"{self.config.base_url}/chat.delete"
        headers = {
            'Authorization': f'Bearer {self.config.bot_token}',
            'Content-Type': 'application/json'
        }
        payload = {
            'channel': channel,
            'ts': ts
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                data = await response.json()
                
                if not data.get('ok'):
                    error_msg = data.get('error', 'Unknown error')
                    raise Exception(f"Slack API error: {error_msg}")
    
    def _format_success_response(self, channel: str, ts: str) -> str:
        """Format success response"""
        return f"""✅ Message deleted successfully

📋 **Deletion Details:**
- Channel: {channel}
- Timestamp: {ts}
- Status: Deleted

💡 Deleted messages cannot be restored."""
    
    def _format_error_response(
        self,
        error: str,
        channel: Optional[str],
        ts: Optional[str]
    ) -> str:
        """Format error response"""
        error_details = []
        
        if 'message_not_found' in error:
            error_details.append("🔍 **Error:** Message not found")
            error_details.append("**Check:**")
            error_details.append("  - Verify channel ID is correct")
            error_details.append("  - Verify timestamp is correct")
            error_details.append("  - Message may already be deleted")
        elif 'cant_delete_message' in error:
            error_details.append("🚫 **Error:** No permission to delete this message")
            error_details.append("**Check:**")
            error_details.append("  - Message must be sent by bot")
            error_details.append("  - Bot must have delete permissions")
        elif 'channel_not_found' in error:
            error_details.append("🔍 **Error:** Channel not found")
            error_details.append("**Check:**")
            error_details.append("  - Verify channel ID is correct")
            error_details.append("  - Bot must be in channel")
        else:
            error_details.append(f"🔍 **Error:** {error}")
            error_details.append("**Common Causes:**")
            error_details.append("  - Network connection issues")
            error_details.append("  - Slack API authentication issues")
            error_details.append("  - Insufficient permissions")
        
        result = [
            "❌ Failed to delete message\n",
            f"Channel: {channel or 'N/A'}",
            f"Timestamp: {ts or 'N/A'}",
            ""
        ]
        result.extend(error_details)
        
        return "\n".join(result)
