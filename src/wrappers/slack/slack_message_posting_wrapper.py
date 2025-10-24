"""
Slack Message Posting Wrappers for MCP Registration
Provides unified interface for posting messages to Slack (public or ephemeral)
"""
from fastmcp import Context
from src.tools.slack.slack_message_posting_tool import SlackMessagePostingTool

# Initialize tool instance
_posting_tool = SlackMessagePostingTool()


async def post_message(
    channel: str,
    text: str,
    username: str = None,
    icon_emoji: str = None,
    thread_ts: str = None,
    ctx: Context = None
) -> str:
    """
    Post public message to Slack channel
    
    Posts a message that all channel members can see.
    Ideal for team announcements, reports, and shared information.
    
    **Parameters:**
    - channel: Channel ID (required, e.g., C1234567890 or G01G9JY2U3C)
    - text: Message content (required)
    - username: Display name (optional, for bot customization)
    - icon_emoji: Icon emoji (optional, e.g., :robot_face:)
    - thread_ts: Thread timestamp for replying to existing thread (optional)
    
    **Returns:**
    Success confirmation with message timestamp and details
    
    **Example:**
    ```python
    # Simple message
    result = await post_message(
        channel="C1234567890",
        text="Hello team! This is an announcement."
    )
    
    # Customized message with emoji and username
    result = await post_message(
        channel="C1234567890",
        text="Daily report completed successfully ✅",
        username="Report Bot",
        icon_emoji=":chart_with_upwards_trend:"
    )
    
    # Reply to thread
    result = await post_message(
        channel="C1234567890",
        text="This is a follow-up comment",
        thread_ts="1234567890.123456"
    )
    ```
    
    **Use Cases:**
    - Team announcements
    - Daily digest reports
    - Status updates
    - Automated notifications
    - Scheduled messages
    
    **Requirements:**
    - Bot must be invited to the channel
    - Bot token must have chat:write permission
    - Channel ID must be valid
    
    **Note:**
    Message formatting supports Slack markdown:
    - *bold text*
    - _italic text_
    - `code`
    - ```code block```
    - > quote
    - • bullet list
    """
    if ctx:
        ctx.info(f"Posting public message to channel: {channel}")
    
    result = await _posting_tool.execute(
        channel=channel,
        text=text,
        ephemeral=False,
        username=username,
        icon_emoji=icon_emoji,
        thread_ts=thread_ts
    )
    
    if ctx:
        ctx.info("Public message posted successfully")
    
    return result


async def post_ephemeral_message(
    channel: str,
    content: str,
    title: str = None,
    thread_ts: str = None,
    format_type: str = 'detailed',
    user: str = None,
    ctx: Context = None
) -> str:
    """
    Post private message visible only to specific user
    
    Posts an ephemeral (temporary) message that only the specified user can see.
    Perfect for private analysis results, personal notifications, or sensitive information.
    
    **Parameters:**
    - channel: Channel ID (required, e.g., C1234567890)
    - content: Message content (required)
    - title: Message title (optional, adds header)
    - thread_ts: Thread timestamp for replying in thread (optional)
    - format_type: Display format - 'simple' or 'detailed' (default: 'detailed')
    - user: Target user ID (optional, uses default_user_id from config if not provided)
    
    **Returns:**
    Success confirmation with post details
    
    **Example:**
    ```python
    # Simple private message
    result = await post_ephemeral_message(
        channel="C1234567890",
        content="This is a private analysis result for you only."
    )
    
    # Detailed format with title
    result = await post_ephemeral_message(
        channel="C1234567890",
        title="Thread Analysis Report",
        content="Analysis results:\n- Key point 1\n- Key point 2\n- Key point 3",
        format_type='detailed'
    )
    
    # Reply to specific user in thread
    result = await post_ephemeral_message(
        channel="C1234567890",
        content="Here's the information you requested",
        thread_ts="1234567890.123456",
        user="U1234567890"
    )
    ```
    
    **Use Cases:**
    - Private analysis results
    - Personal search results
    - Individual notifications
    - Sensitive information sharing
    - User-specific feedback
    - Testing bot responses
    
    **Requirements:**
    - MUST use bot token (user token will fail)
    - Bot must be in channel
    - Target user must be channel member
    - default_user_id must be configured if user not specified
    
    **Important Notes:**
    - Message is temporary and disappears on page reload
    - Only visible to specified user
    - Cannot be seen by other channel members
    - Ideal for private bot interactions
    
    **Format Types:**
    - 'simple': Plain text with optional title
    - 'detailed': Structured format with enhanced readability
    """
    if ctx:
        ctx.info(f"Posting ephemeral message to channel: {channel}, user: {user or 'default'}")
    
    result = await _posting_tool.execute(
        channel=channel,
        content=content,
        ephemeral=True,
        title=title,
        thread_ts=thread_ts,
        format_type=format_type,
        user=user
    )
    
    if ctx:
        ctx.info("Ephemeral message posted successfully")
    
    return result
