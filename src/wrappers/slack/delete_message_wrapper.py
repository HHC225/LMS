"""
Delete Message Wrapper for MCP Registration
Separated into single message deletion and bulk deletion functions
"""
from typing import Optional
from fastmcp import Context
from src.tools.slack.delete_message_tool import DeleteMessageTool

# Initialize tool instance
_delete_message_tool = DeleteMessageTool()


async def delete_message(
    channel: Optional[str] = None,
    ts: Optional[str] = None,
    url: Optional[str] = None,
    ctx: Context = None
) -> str:
    """
    Delete message from Slack channel
    
    Deletes a message from Slack channel. Can only delete messages sent by the bot
    or messages the bot has explicit permission to delete.
    
    **Parameters:**
    Method 1 - Using URL (recommended):
    - url: Slack message URL (e.g., https://workspace.slack.com/archives/CHANNEL/pTIMESTAMP)
    
    Method 2 - Using channel + timestamp:
    - channel: Channel ID (e.g., C1234567890)
    - ts: Message timestamp (e.g., 1234567890.123456)
    
    **Returns:**
    Success confirmation or detailed error message
    
    **Example:**
    ```python
    # Delete using URL
    result = await delete_message(
        url="https://workspace.slack.com/archives/C1234567890/p1234567890123456"
    )
    
    # Delete using channel + timestamp
    result = await delete_message(
        channel="C1234567890",
        ts="1234567890.123456"
    )
    ```
    
    **Use Cases:**
    - Remove incorrectly sent messages
    - Delete messages sent to wrong channel
    - Clean up test messages
    - Remove outdated information
    - Delete spam or inappropriate content (if bot has permission)
    
    **Requirements:**
    - Bot must have sent the message OR
    - Bot must have explicit delete permission
    - Valid channel ID and timestamp
    - Bot must be in channel
    
    **Important Warnings:**
    ⚠️ Deleted messages CANNOT be restored
    ⚠️ Deletion is permanent and immediate
    ⚠️ Consider archiving important messages before deletion
    
    **Error Cases:**
    - message_not_found: Message doesn't exist or already deleted
    - cant_delete_message: No permission to delete (not sent by bot)
    - channel_not_found: Invalid channel ID or bot not in channel
    - invalid_auth: Bot token authentication failed
    
    **Best Practices:**
    1. Verify message details before deletion
    2. Use URL method for accuracy
    3. Check bot permissions first
    4. Log important deletions
    5. Have backup/recovery plan for critical data
    """
    return await _delete_message_tool.execute(
        channel=channel,
        ts=ts,
        url=url,
        ctx=ctx
    )


async def bulk_delete_messages(
    channel: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    bot_only: bool = False,
    preview: bool = True,
    max_messages: int = 100,
    ctx: Context = None
) -> str:
    """
    Bulk delete messages from Slack channel by date/timestamp range
    
    Deletes multiple messages within a date/timestamp range. Always use preview mode first
    to verify what will be deleted before actually deleting.
    
    **Parameters:**
    - channel: Channel ID (required, e.g., C1234567890)
    - from_date: Start date/timestamp (optional)
      * YYYY-MM-DD format: starts from midnight (00:00:00) of that date
      * Slack timestamp format: 1234567890.123456 (precise to microsecond)
    - to_date: End date/timestamp (optional)
      * YYYY-MM-DD format: ends at midnight (00:00:00) of that date
      * Slack timestamp format: 1234567890.123456 (precise to microsecond)
    - bot_only: Delete only bot messages (default: False)
    - preview: Preview mode - shows what would be deleted without deleting (default: True)
    - max_messages: Maximum number of messages to delete (default: 100)
    
    **IMPORTANT:** 
    - When using Slack timestamps (e.g., 1760948716.586639), messages from that exact
      timestamp onwards will be included
    - Using YYYY-MM-DD format starts from midnight (00:00:00) and may include messages
      you don't intend to delete
    - Always use preview=True first to verify the deletion range
    
    **Returns:**
    Formatted result with deleted/preview message list and statistics
    
    **Examples:**
    ```python
    # Preview deletion from specific timestamp
    result = await bulk_delete_messages(
        channel="C1234567890",
        from_date="1760948716.586639",
        preview=True
    )
    
    # Delete all messages in date range (actual deletion)
    result = await bulk_delete_messages(
        channel="C1234567890",
        from_date="2025-10-20",
        to_date="2025-10-21",
        preview=False,
        max_messages=500
    )
    
    # Delete only bot messages from specific date
    result = await bulk_delete_messages(
        channel="C1234567890",
        from_date="2025-10-20",
        bot_only=True,
        preview=False
    )
    
    # Delete all messages after specific timestamp (excluding the timestamp itself)
    result = await bulk_delete_messages(
        channel="C1234567890",
        from_date="1760948716.586640",  # Slightly larger than reference timestamp
        preview=False
    )
    ```
    
    **Use Cases:**
    - Bulk cleanup of test messages
    - Remove bot messages from specific period
    - Clean up spam or inappropriate content
    - Archive old messages by deleting
    - Reset channel to specific point in time
    
    **Requirements:**
    - Bot must have sent the messages OR have explicit delete permission
    - Valid channel ID
    - Bot must be in channel
    
    **Important Warnings:**
    ⚠️ Deleted messages CANNOT be restored
    ⚠️ Deletion is permanent and immediate
    ⚠️ ALWAYS use preview=True first to verify deletion targets
    ⚠️ Be careful with date ranges to avoid unintended deletions
    
    **Error Cases:**
    - channel_not_found: Invalid channel ID or bot not in channel
    - invalid_auth: Bot token authentication failed
    - cant_delete_message: No permission to delete some messages
    
    **Best Practices:**
    1. ALWAYS preview first with preview=True
    2. Use Slack timestamp format for precise deletion ranges
    3. Start with small max_messages value for testing
    4. Verify the deletion range carefully
    5. Consider backing up important messages before deletion
    6. Use bot_only=True if you only want to delete bot messages
    7. Log important bulk deletions for audit trail
    """
    return await _delete_message_tool.execute(
        channel=channel,
        from_date=from_date,
        to_date=to_date,
        bot_only=bot_only,
        preview=preview,
        max_messages=max_messages,
        ctx=ctx
    )
