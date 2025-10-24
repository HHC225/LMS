"""
Slack Message Retrieval Wrappers for MCP Registration
Provides unified interface for retrieving Slack messages (single or thread)
"""
from fastmcp import Context
from src.tools.slack.slack_message_retrieval_tool import SlackMessageRetrievalTool
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize tool instance
_retrieval_tool = SlackMessageRetrievalTool()


async def get_single_message(
    channel: str = None,
    timestamp: str = None,
    url: str = None,
    ctx: Context = None
) -> str:
    """
    Retrieve a single Slack message without thread replies
    
    Retrieves only the specified message without any thread replies.
    Useful for getting specific message content or checking message details.
    
    **Usage:**
    - Provide Slack URL (recommended): Automatically extracts channel and timestamp
    - Or provide channel + timestamp: Manual specification
    
    **Parameters:**
    - url: Slack URL (e.g., https://workspace.slack.com/archives/CHANNEL/pTIMESTAMP)
    - channel: Channel ID (e.g., C1234567890) - required if url not provided
    - timestamp: Message timestamp (e.g., 1234567890.123456) - required if url not provided
    
    **Returns:**
    Formatted single message with metadata (reactions, attachments, thread info)
    
    **Example:**
    ```python
    # Using URL
    message = await get_single_message(
        url="https://workspace.slack.com/archives/C1234567890/p1234567890123456"
    )
    
    # Using channel + timestamp
    message = await get_single_message(
        channel="C1234567890",
        timestamp="1234567890.123456"
    )
    ```
    
    **Use Cases:**
    - Getting specific message content
    - Checking message metadata (reactions, attachments)
    - Verifying message existence
    - Quick message lookup without thread context
    
    **Note:**
    - If you need all thread replies, use `get_thread_content` instead
    - This tool only returns the single specified message
    """
    if ctx:
        ctx.info(f"Retrieving single message - Channel: {channel or 'from URL'}, TS: {timestamp or 'from URL'}")
    
    result = await _retrieval_tool.execute(
        channel=channel,
        timestamp=timestamp,
        url=url,
        include_replies=False
    )
    
    if ctx:
        ctx.info("Single message retrieval completed")
    
    return result


async def get_thread_content(
    channel: str = None,
    timestamp: str = None,
    url: str = None,
    ctx: Context = None
) -> str:
    """
    Retrieve Slack thread content for analysis
    
    Retrieves all messages in a Slack thread including replies.
    Useful for analyzing discussion context and history.
    
    **Usage:**
    - Provide Slack URL (recommended): Automatically extracts channel and timestamp
    - Or provide channel + timestamp: Manual specification
    
    **Parameters:**
    - url: Slack URL (e.g., https://workspace.slack.com/archives/CHANNEL/pTIMESTAMP?thread_ts=THREAD_TS)
    - channel: Channel ID (e.g., C1234567890) - required if url not provided
    - timestamp: Thread timestamp (e.g., 1234567890.123456) - required if url not provided
    
    **Returns:**
    Formatted thread content with all messages, timestamps, and user information
    
    **Example:**
    ```python
    # Using URL
    content = await get_thread_content(
        url="https://workspace.slack.com/archives/C1234567890/p1234567890123456?thread_ts=1234567890.123456"
    )
    
    # Using channel + timestamp
    content = await get_thread_content(
        channel="C1234567890",
        timestamp="1234567890.123456"
    )
    ```
    
    **Use Cases:**
    - Analyzing team discussions
    - Reviewing decision-making threads
    - Extracting key information from conversations
    - Tracking issue resolution progress
    """
    if ctx:
        ctx.info(f"Retrieving thread content - Channel: {channel or 'from URL'}, TS: {timestamp or 'from URL'}")
    
    result = await _retrieval_tool.execute(
        channel=channel,
        timestamp=timestamp,
        url=url,
        include_replies=True
    )
    
    if ctx:
        ctx.info("Thread content retrieval completed")
    
    return result


async def get_channel_history(
    channel: str,
    oldest: str = None,
    latest: str = None,
    limit: int = 100,
    ctx: Context = None
) -> str:
    """
    Retrieve Slack channel message history
    
    Retrieves message history from a Slack channel with optional time range filtering.
    Supports pagination to retrieve large message sets.
    
    **Parameters:**
    - channel: Channel ID (required, e.g., C1234567890 or G01G9JY2U3C)
    - oldest: Start timestamp (optional, UNIX timestamp or Slack timestamp format)
      * UNIX timestamp: 1693756800
      * Slack timestamp: 1693756800.123456
    - latest: End timestamp (optional, UNIX timestamp or Slack timestamp format)
      * UNIX timestamp: 1693843200
      * Slack timestamp: 1693843200.123456
    - limit: Maximum number of messages to retrieve (default: 100, max: 1000)
    
    **Returns:**
    JSON string with message list, total count, and pagination info
    
    **Examples:**
    ```python
    # Get recent 100 messages
    result = await get_channel_history(
        channel="C1234567890"
    )
    
    # Get messages in specific time range
    result = await get_channel_history(
        channel="C1234567890",
        oldest="1693756800",
        latest="1693843200"
    )
    
    # Get messages with Slack timestamp format
    result = await get_channel_history(
        channel="C1234567890",
        oldest="1760948716.586639",
        limit=500
    )
    
    # Get up to 1000 messages
    result = await get_channel_history(
        channel="C1234567890",
        limit=1000
    )
    ```
    
    **Use Cases:**
    - Retrieve channel message history for analysis
    - Search for messages in specific time period
    - Export channel messages for backup
    - Monitor channel activity patterns
    - Find messages before/after specific timestamp
    
    **Response Format:**
    ```json
    {
        "success": true,
        "data": {
            "messages": [
                {
                    "type": "message",
                    "ts": "1693756800.123456",
                    "user": "U1234567890",
                    "text": "Message content",
                    "reply_count": 3,
                    "reactions": [...]
                },
                ...
            ],
            "total_count": 150,
            "pages_processed": 2,
            "has_more": false
        }
    }
    ```
    
    **Important Notes:**
    - Messages are returned in reverse chronological order (newest first)
    - Maximum 100 messages per API request (automatic pagination)
    - Rate limiting: 100ms delay between paginated requests
    - Default max_pages is 10 to prevent infinite loops
    - Use precise Slack timestamp format for exact time range queries
    
    **Requirements:**
    - Bot must be a member of the channel
    - Bot token must have channels:history or groups:history permission
    - User token provides better access to private channels
    
    **Error Cases:**
    - channel_not_found: Invalid channel ID or bot not in channel
    - invalid_auth: Bot token authentication failed
    - missing_scope: Insufficient permissions
    """
    if ctx:
        ctx.info(f"Retrieving channel history - Channel: {channel}, Range: {oldest or 'start'} to {latest or 'now'}, Limit: {limit}")
    
    try:
        result = await _retrieval_tool.fetch_channel_history(
            channel=channel,
            oldest=oldest,
            latest=latest,
            limit=limit
        )
        
        if ctx:
            ctx.info(f"Channel history retrieved: {result['total_count']} messages, {result['pages_processed']} pages")
        
        # Return formatted JSON string
        import json
        return json.dumps({
            'success': True,
            'data': result
        }, indent=2, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Failed to retrieve channel history: {e}")
        import json
        return json.dumps({
            'success': False,
            'error': str(e)
        }, indent=2, ensure_ascii=False)
