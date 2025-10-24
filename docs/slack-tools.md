# Slack Tools for FastMCP

## Overview

Eight essential Slack tools implemented in Python using FastMCP framework:

**Message Retrieval (3 tools):**
1. **Get Thread Content** - Retrieve entire Slack thread with all replies
2. **Get Single Message** - Retrieve a specific message without thread replies
3. **Get Channel History** - Retrieve channel message history with pagination

**Message Search (1 tool):**
4. **Search Threads** - Search Slack threads with intelligent relevance scoring ⭐ NEW!

**Message Posting (2 tools):**
5. **Post Message** - Send public messages to channels
6. **Post Ephemeral Message** - Send private messages to specific users

**Message Deletion (2 tools):**
7. **Delete Message** - Remove a single message from channel
8. **Bulk Delete Messages** - Remove multiple messages by date/timestamp range

## Architecture

```
Local_MCP_Server/
├── configs/
│   ├── slack.py.template                 # Template (commit to Git)
│   └── slack.py                          # Actual config (DO NOT commit)
├── src/
│   ├── tools/
│   │   └── slack/
│   │       ├── __init__.py
│   │       ├── slack_message_retrieval_tool.py   # Unified retrieval (single/thread/history)
│   │       ├── slack_message_posting_tool.py     # Unified posting (public/ephemeral)
│   │       ├── slack_thread_search_tool.py       # Thread search with relevance scoring ⭐ NEW
│   │       ├── delete_message_tool.py            # Message deletion tool (single/bulk)
│   │       └── digest_tool.py                    # Digest generation tool
│   └── wrappers/
│       └── slack/
│           ├── __init__.py
│           ├── slack_message_retrieval_wrapper.py    # get_single_message, get_thread_content, get_channel_history
│           ├── slack_message_posting_wrapper.py      # post_message, post_ephemeral_message
│           ├── slack_thread_search_wrapper.py        # search_threads ⭐ NEW
│           ├── delete_message_wrapper.py             # delete_message, bulk_delete_messages
│           └── digest_wrapper.py
└── main.py                                # Tool registration
```

## Key Design Decisions

### 1. **Unified Tool Architecture with Separated Wrappers**
- **Message Retrieval Tool**: Single tool (`SlackMessageRetrievalTool`) with three wrapper functions
  - `get_single_message`: Get single message only (`include_replies=False`)
  - `get_thread_content`: Get entire thread with all replies (`include_replies=True`)
  - `get_channel_history`: Get channel message history with pagination
- **Thread Search Tool**: Single tool (`SlackThreadSearchTool`) with one wrapper function ⭐ NEW
  - `search_threads`: Search threads with multi-factor relevance scoring
- **Message Posting Tool**: Single tool (`SlackMessagePostingTool`) with two wrapper functions
  - `post_message`: Post public message visible to all (`ephemeral=False`)
  - `post_ephemeral_message`: Post private message to specific user (`ephemeral=True`)
- **Message Deletion Tool**: Single tool (`DeleteMessageTool`) with two wrapper functions
  - `delete_message`: Delete single message by URL or channel+timestamp
  - `bulk_delete_messages`: Delete multiple messages by date/timestamp range

### 2. **No Separate API Client**
- Slack API calls are integrated directly into each tool
- Uses `aiohttp` for async HTTP requests
- Reduces abstraction layers and complexity

### 3. **Consistent with Existing Tools**
- Follows same pattern as Recursive Thinking, Sequential Thinking, etc.
- Config file (`slack.py`) placed directly in `configs/` directory
- Tools inherit from `BaseTool` class
- Wrappers provide FastMCP-compatible interfaces

### 4. **Comprehensive Documentation**
- Each wrapper function has detailed docstrings
- Includes usage examples, parameters, return values
- Documents requirements and error cases
- Provides best practices and use cases

## Configuration

### Environment Variables

```bash
# Required
export SLACK_BOT_TOKEN="xoxb-your-bot-token-here"

# Optional (for user-level operations)
export SLACK_USER_TOKEN="xoxp-your-user-token-here"
```

### Configuration File

Edit `configs/slack.py` to customize:

```python
@dataclass
class SlackConfig:
    bot_token: str                        # Bot token (xoxb-...)
    user_token: Optional[str] = None      # User token (optional)
    base_url: str = "https://slack.com/api"
    timeout: int = 30                     # Request timeout (seconds)
    retry_attempts: int = 3               # Retry count
    workspace_domain: str = "your-workspace.slack.com"
    default_user_id: str = "U00000000"   # For ephemeral messages
    ENABLE_SLACK_TOOLS: bool = True       # Enable/disable flag
```

## Usage Examples

### 1. Get Thread Content (with all replies)

```python
from src.wrappers.slack import get_thread_content

# Using Slack URL (recommended)
content = await get_thread_content(
    url="https://your-workspace.slack.com/archives/C1234567890/p1234567890123456?thread_ts=1234567890.123456"
)

# Using channel + timestamp
content = await get_thread_content(
    channel="C1234567890",
    timestamp="1234567890.123456"
)
```

**Output:**
```
📨 **Slack Thread Content**
Channel: C1234567890
Thread TS: 1234567890.123456
Total Messages: 5

============================================================

[1] 2025-01-15 09:30:45 - User: U1234567890
Message text here...
------------------------------------------------------------
[2] 2025-01-15 09:31:20 - User: U0987654321
Reply text here...
------------------------------------------------------------
```

### 2. Get Single Message (without replies)

```python
from src.wrappers.slack import get_single_message

# Using Slack URL (recommended)
message = await get_single_message(
    url="https://your-workspace.slack.com/archives/C1234567890/p1234567890123456"
)

# Using channel + timestamp
message = await get_single_message(
    channel="C1234567890",
    timestamp="1234567890.123456"
)
```

**Output:**
```
📬 **Single Slack Message**

Channel: C1234567890
Timestamp: 1234567890.123456
Time: 2025-01-15 09:30:45
User: U1234567890
📎 Thread replies: 3
📁 Attachments: 1 file(s)
  [1] report.pdf (PDF)
💬 Reactions: thumbsup (5), eyes (2)

============================================================

Message content here...

============================================================
```

**Use Cases:**
- Quick message lookup without loading entire thread
- Checking message metadata (reactions, attachments)
- Verifying message existence
- Getting message details for reference

### 3. Get Channel History

```python
from src.wrappers.slack import get_channel_history

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

# Get messages with Slack timestamp format (precise)
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

**Output (JSON format):**
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
      }
    ],
    "total_count": 150,
    "pages_processed": 2,
    "has_more": false
  }
}
```

**Features:**
- Automatic pagination (max 10 pages)
- Rate limiting (100ms delay between requests)
- Reverse chronological order (newest first)
- Precise timestamp range queries

**Use Cases:**
- Retrieve channel message history for analysis
- Search for messages in specific time period
- Export channel messages for backup
- Monitor channel activity patterns
- Find messages before/after specific timestamp

### 5. Post Public Message

```python
from src.wrappers.slack import post_message

# Simple message
result = await post_message(
    channel="C1234567890",
    text="Hello team! This is an announcement."
)

# Customized with emoji and username
result = await post_message(
    channel="C1234567890",
    text="*Daily Report* ✅\n\nAll tasks completed successfully!",
    username="Report Bot",
    icon_emoji=":chart_with_upwards_trend:"
)

# Reply to thread
result = await post_message(
    channel="C1234567890",
    text="Follow-up comment",
    thread_ts="1234567890.123456"
)
```

### 6. Post Private Message

```python
from src.wrappers.slack import post_ephemeral_message

# Simple private message
result = await post_ephemeral_message(
    channel="C1234567890",
    content="This is visible only to you."
)

# Detailed format with title
result = await post_ephemeral_message(
    channel="C1234567890",
    title="Analysis Report",
    content="Key findings:\n• Point 1\n• Point 2\n• Point 3",
    format_type='detailed'
)

# Specify target user (optional)
result = await post_ephemeral_message(
    channel="C1234567890",
    content="Personal notification",
    user="U1234567890"
)
```

### 4. Search Threads ⭐ NEW

```python
from src.wrappers.slack.slack_thread_search_wrapper import search_threads

# Basic search (summary format)
results = await search_threads(
    keyword="API design"
)

# Advanced search with filters
results = await search_threads(
    keyword="database optimization",
    channels=["C1234567890"],
    after_date="2024-01-01",
    before_date="2024-12-31",
    from_user="@john.doe",
    max_results=20,
    sort_by="relevance",
    output_format="detailed"
)

# Search with LLM analysis prompt
results = await search_threads(
    keyword="security review",
    include_llm_prompt=True,
    output_format="detailed"
)

# Get JSON output for programmatic use
results = await search_threads(
    keyword="deployment issues",
    output_format="json",
    max_results=50
)

# Get markdown format
results = await search_threads(
    keyword="performance optimization",
    output_format="markdown",
    top_n_detailed=5
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keyword` | str | (required) | Search keyword or phrase |
| `max_results` | int | 20 | Maximum results (max: 100) |
| `sort_by` | str | "relevance" | Sort by "relevance" or "timestamp" |
| `output_format` | str | "summary" | Output: summary/detailed/json/markdown |
| `channels` | List[str] | None | Channel IDs to search in |
| `exclude_channels` | List[str] | None | Channel IDs to exclude |
| `after_date` | str | None | After date (YYYY-MM-DD) |
| `before_date` | str | None | Before date (YYYY-MM-DD) |
| `from_user` | str | None | From specific user |
| `include_llm_prompt` | bool | False | Include LLM analysis prompt |
| `top_n_detailed` | int | 3 | Number of results with full content |

**Relevance Scoring Algorithm:**

Multi-factor weighted scoring:
- **Native Score (30%)**: Slack's built-in relevance score
- **Keyword Frequency (20%)**: How often keyword appears
- **Recency (15%)**: How recent the message is
- **Engagement (25%)**: Number of replies and reactions
- **Title Match (10%)**: Keyword in first line

**Output Formats:**

1. **Summary (Default)**: Quick overview with top 5 results
```
🔍 Thread Search Results for "API design"

Found 15 matching threads

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🥇 Rank #1 - Relevance Score: 87.3
📍 Channel: #engineering
👤 User: @john.doe
📅 Date: 2024-10-15 14:30
💬 Replies: 12 | ⚡ Reactions: 8

📝 Discussion about RESTful API design patterns...

🔗 [View Thread](https://workspace.slack.com/archives/C123/p1234567890)
```

2. **Detailed**: Full thread content for top N results
3. **JSON**: Structured data format
```json
{
  "search_metadata": {
    "keyword": "API design",
    "total_results": 15,
    "timestamp": "2024-10-20T14:30:00"
  },
  "results": [...]
}
```
4. **Markdown**: Rich formatted output with tables

**Use Cases:**
- Find relevant discussions on specific topics
- Track decisions and action items
- Discover expertise and key contributors
- Research past solutions to similar problems
- Aggregate team knowledge
- Prepare summaries of ongoing discussions

**Key Features:**
- ✅ Multi-factor relevance scoring
- ✅ Advanced filtering (channels, dates, users)
- ✅ Multiple output formats
- ✅ LLM-ready analysis prompts
- ✅ Full thread content retrieval
- ✅ Channel name resolution
- ✅ Comprehensive error handling

**Performance:**
- Basic search: 1-2 seconds
- Detailed format: 3-5 seconds (fetches full threads)
- Channel name caching: Improves subsequent searches

### 7. Delete Message (Single Deletion)

```python
from src.wrappers.slack import delete_message

# Single deletion - Using URL (recommended)
result = await delete_message(
    url="https://your-workspace.slack.com/archives/C1234567890/p1234567890123456"
)

# Single deletion - Using channel + timestamp
result = await delete_message(
    channel="C1234567890",
    ts="1234567890.123456"
)
```

**Output:**
```
✅ Message deleted successfully

📋 **Deletion Details:**
- Channel: C1234567890
- Timestamp: 1234567890.123456
- Status: Deleted

💡 Deleted messages cannot be restored.
```

### 8. Bulk Delete Messages

```python
from src.wrappers.slack import bulk_delete_messages

# Preview mode (safe, shows what would be deleted)
result = await bulk_delete_messages(
    channel="G01G9JY2U3C",
    from_date="2025-10-20",
    to_date="2025-10-21",
    bot_only=True,
    preview=True,
    max_messages=100
)

# Execute deletion (DANGEROUS, cannot be undone!)
result = await bulk_delete_messages(
    channel="G01G9JY2U3C",
    from_date="2025-10-20",
    to_date="2025-10-21",
    bot_only=True,
    preview=False,  # ⚠️ Actually delete messages
    max_messages=100
)

# Delete all bot messages after specific timestamp (precise)
result = await bulk_delete_messages(
    channel="G01G9JY2U3C",
    from_date="1760948716.586639",  # Slack timestamp format
    bot_only=True,
    preview=False,
    max_messages=200
)

# Delete from specific timestamp (excluding the timestamp itself)
result = await bulk_delete_messages(
    channel="G01G9JY2U3C",
    from_date="1760948716.586640",  # Slightly larger than reference
    preview=False,
    max_messages=500
)
```

#### Bulk Deletion Parameters

- **channel** (required): Channel ID to delete messages from
- **from_date** (optional): Start date/timestamp (YYYY-MM-DD or Unix timestamp)
- **to_date** (optional): End date/timestamp (YYYY-MM-DD or Unix timestamp)
- **bot_only** (default: False): Delete only bot messages if True
- **preview** (default: True): Preview mode - shows what would be deleted without actually deleting
- **max_messages** (default: 100): Maximum number of messages to delete (safety limit)

#### Key Features

- ✅ **Thread-aware deletion**: Automatically includes thread replies when deleting parent messages
- ✅ **Smart filtering**: Filters both parent messages and thread replies by bot_only flag
- ✅ **Preview mode**: Safe preview shows all messages (including thread replies) before deletion
- ✅ **Rate limiting**: 100ms delay between API calls to prevent rate limit errors

**Important Note**: When a parent message has thread replies:
1. Tool retrieves parent messages first
2. For messages with `reply_count > 0`, fetches all thread replies
3. Applies filters (timestamp, bot_only) to both parents and replies
4. Deletes all matching messages including thread replies

This ensures complete cleanup when bot messages are in threads.

#### Bulk Deletion Response Example

```
📊 Bulk Message Deletion Result

✅ Deleted messages: 15
❌ Failed messages: 0

📋 Deleted Messages:
1. 🤖 Bot | 2025-10-07 16:58 | :bar_chart: チーム 日次ダイジェスト...
2. 🤖 Bot | 2025-10-08 16:45 | :bar_chart: チーム 日次ダイジェスト...
3. 🤖 Bot | 2025-10-09 17:02 | :bar_chart: チーム 日次ダイジェスト...
... and 12 more messages

✅ Deletion completed. Deleted messages cannot be restored.
```

## Requirements

### Python Dependencies

```bash
pip install aiohttp fastmcp
```

### Slack Bot Permissions

Required OAuth scopes for bot token:
- `channels:history` - Read channel messages
- `channels:read` - View channel information
- `chat:write` - Send messages
- `chat:write.public` - Send messages to channels without joining
- `groups:history` - Read private channel messages
- `groups:read` - View private channel information

## Error Handling

All tools provide detailed error messages with troubleshooting guidance:

```python
# Example error response
❌ Failed to post message

**Error Details:**
- Channel: C1234567890
- Error: channel_not_found

**Possible Causes:**
- Invalid channel ID
- Bot not in channel
- Missing permissions
- Network/API error

**Solutions:**
1. Verify channel ID
2. Invite bot to channel
3. Check network connection
4. Retry after a moment
```

## Testing

### Test Connection

```python
from configs.slack import get_slack_config, validate_slack_config

config = get_slack_config()
is_valid = validate_slack_config(config)
print(f"Configuration valid: {is_valid}")
```

### Test Tool Execution

```python
# Test message posting
from src.wrappers.slack import post_message

result = await post_message(
    channel="C1234567890",
    text="Test message from Slack tools"
)
print(result)
```

## Security & Configuration

### Template vs Actual Configuration

**IMPORTANT**: Never commit actual workspace credentials to Git!

1. **Template File** (`configs/slack.py.template`):
   - Generic template with placeholder values
   - Safe to commit to Git
   - Contains example configuration structure

2. **Actual Configuration** (`configs/slack.py`):
   - Contains real workspace credentials
   - Must be in `.gitignore`
   - Created by copying and editing template

### Setup Instructions

```bash
# 1. Copy template to actual config
cp configs/slack.py.template configs/slack.py

# 2. Edit slack.py with your actual values
# Replace:
#   - workspace_domain: "your-workspace.slack.com" → "actual-workspace.slack.com"
#   - default_user_id: "U00000000" → "U01234567"
#   - bot_token via environment variable

# 3. Verify .gitignore includes slack.py
echo "configs/slack.py" >> .gitignore
```

## Comparison with Previous Implementation

| Feature | Old (4 Separate Files) | New (2 Unified Files) |
|---------|------------------------|----------------------|
| Message Retrieval | `get_single_message_tool.py` + `get_thread_content_tool.py` | `slack_message_retrieval_tool.py` (unified) |
| Message Posting | `post_message_tool.py` + `post_ephemeral_tool.py` | `slack_message_posting_tool.py` (unified) |
| API Client | Integrated in each tool | Integrated in unified tools |
| Code Duplication | High (URL parsing, timestamp normalization duplicated) | Low (shared logic in single class) |
| Maintainability | Need to update multiple files for common changes | Update single file for common logic |
| File Count | 4 tool files + 4 wrapper files | 2 tool files + 2 wrapper files |

**Benefits of Unified Architecture:**
- ✅ **Reduced Code Duplication**: Common logic (URL parsing, timestamp handling) is shared
- ✅ **Easier Maintenance**: Update message retrieval logic in one place
- ✅ **Clearer Organization**: Related functionality grouped together
- ✅ **Flexible Interface**: Wrappers still provide separate functions for backward compatibility
- ✅ **Simpler Codebase**: Fewer files to manage and navigate

## Implementation Notes

### Why Unified Tools?

1. **Related Functionality**: Single message and thread retrieval are variations of the same operation
2. **Code Reuse**: Both share URL parsing, timestamp normalization, and API call logic
3. **Simplified Maintenance**: Fix bugs or add features in one place instead of multiple files
4. **Clear Separation**: Public vs ephemeral posting is a configuration choice, not separate operations

### Backward Compatibility

The wrapper functions maintain the same interface as before:
- `get_single_message()` - Works exactly as before
- `get_thread_content()` - Works exactly as before
- `post_message()` - Works exactly as before
- `post_ephemeral_message()` - Works exactly as before

**No changes required in code using these functions!**

### Async Implementation

All tools use async/await pattern:
- `aiohttp` for non-blocking HTTP requests
- Compatible with FastMCP's async architecture
- Efficient for I/O-bound Slack API calls

### Error Messages

Designed for end-users:
- Clear problem description
- Possible causes listed
- Actionable solutions provided
- Context-specific guidance

## Troubleshooting

### Bot Token Issues

```bash
# Verify token format
echo $SLACK_BOT_TOKEN
# Should start with 'xoxb-'

# Test token validity
curl -X POST https://slack.com/api/auth.test \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN"
```

### Permission Errors

1. Check bot is in channel: `/invite @YourBotName`
2. Verify OAuth scopes in Slack App settings
3. Reinstall app if scopes changed

### Network Issues

1. Check firewall settings
2. Verify Slack API is accessible
3. Test with `curl` or `wget`

---

# Slack Digest Tool

Automated team digest generation from Slack conversations with LLM-powered analysis for daily wrap-up meetings.

## Overview

The Slack Digest tool automatically collects team-related messages from Slack channels, uses LLM to analyze and structure the information, and posts a formatted daily digest to a specified channel.

**Key Features:**
- 🔍 **Smart Collection**: Precise date range (JST timezone) with team mentions, users, and keywords
- 🧹 **Intelligent Filtering**: Excludes DMs, specific channels, and meeting notes
- 🤖 **LLM Analysis**: Anti-duplication logic with language auto-detection
- 📊 **Concise Formatting**: Optimized for wrap-up meetings (max 3 links per item)
- 🚀 **Automated Posting**: Direct posting to configured Slack channel
- 🌍 **Language Matching**: Digest language matches input message language

## Digest Configuration

### Team and Channel Setup

Edit `configs/slack.py` with your team's configuration:

```python
# Team User Mapping (for mention conversion)
TEAM_USER_MAPPING = {
    "@acn-username1": "U_USER_ID_1",
    "@acn-username2": "U_USER_ID_2",
}

# Team Group Mentions
TEAM_MENTIONS = [
    "S_TEAM_ID_1",  # Team mention IDs
    "S_TEAM_ID_2",
]

# Individual User IDs
TEAM_USER_IDS = list(TEAM_USER_MAPPING.values())

# Excluded Channels (won't be included in digest)
EXCLUDED_CHANNELS_FROM_DIGEST = {
    "C_CHANNEL_ID_1",
    "C_CHANNEL_ID_2",
}

# Exclusion Patterns (filter out meeting notes)
MORNING_MEETING_EXCLUSION_PATTERNS = [
    "Meeting notes",
    "Daily standup",
    "Team digest",
]

# Search Keywords
SEARCH_KEYWORDS = ["keyword1", "keyword2"]

# Posting Configuration
DIGEST_TARGET_CHANNEL = "G_CHANNEL_ID"
DIGEST_BOT_USERNAME = "Digest Bot"
DIGEST_BOT_ICON = ":robot_face:"
```

### Required Permissions

**Bot Token Scopes:**
- `chat:write` - Post messages
- `users:read` - Resolve user names
- `channels:read` - Access channel information

**User Token Scopes:**
- `search:read` - Search messages (requires user token, not bot token)

## Usage

### Basic Usage

```python
from src.wrappers.slack import generate_digest, post_digest

# Generate digest for yesterday (default)
prompt = await generate_digest()

# Generate digest for specific date (YYYYMMDD format)
prompt = await generate_digest(date="20251020")  # 2025-10-20 00:00:00 ~ 23:59:59 (JST)
```

### Complete Workflow

The digest generation follows a two-step process:

#### Step 1: Generate Analysis Prompt

```python
# Call generate_digest - returns LLM prompt
prompt = await generate_digest(date="20251020")

# The tool:
# 1. Collects messages from specified date (JST timezone)
# 2. Filters out excluded channels and patterns
# 3. Deduplicates messages
# 4. Formats for LLM analysis
# 5. Returns comprehensive prompt with language detection instructions
```

#### Step 2: LLM Processing and Posting

The LLM will:
1. **Detect language** of collected messages (Japanese/Korean/English)
2. Analyze content based on guidelines
3. Generate structured JSON in **the same language**
4. Return JSON to `post_digest` tool
5. Formatted digest is posted to Slack

```python
# LLM generates JSON and system calls post_digest automatically
result = await post_digest(digest_json=llm_generated_json)
```

### JSON Structure

The LLM must return JSON in this exact format (in detected language):

```json
{
  "date": "2025-10-20",
  "completedItems": [
    {
      "priority": "HIGH",
      "title": "Completed task title (in detected language)",
      "assignees": ["@acn-user1"],
      "details": ["What was completed (in detected language)"],
      "threadLinks": ["URL1", "URL2", "URL3"]
    }
  ],
  "majorTopics": [
    {
      "priority": "MEDIUM",
      "title": "Important discussion topic (in detected language)",
      "assignees": ["@acn-user1", "@acn-user2"],
      "details": ["Brief detail 1", "Brief detail 2"],
      "threadLinks": ["URL1", "URL2", "URL3"]
    }
  ],
  "risksAndIssues": [
    {
      "priority": "HIGH",
      "title": "Issue title (in detected language)",
      "assignees": ["@acn-user"],
      "details": ["Issue description"],
      "threadLinks": ["URL1", "URL2", "URL3"]
    }
  ],
  "actionItems": [
    {
      "priority": "MEDIUM",
      "title": "Action item title (in detected language)",
      "assignees": ["@acn-user"],
      "deadline": "Deadline if specified",
      "details": ["Action description"],
      "threadLinks": ["URL1", "URL2", "URL3"]
    }
  ],
  "maintenanceNotifications": [
    {
      "priority": "LOW",
      "title": "Maintenance title (in detected language)",
      "assignees": ["@acn-user"],
      "details": ["Maintenance description"],
      "threadLinks": ["URL1", "URL2", "URL3"]
    }
  ]
}
```

## Digest Categories

The tool organizes information into 5 categories (no duplication):

1. **✅ Completed Items** (`completedItems`)
   - ONLY items that were **fully completed today**
   - Deployments, bug fixes, feature completions, releases
   - **If completed, appears ONLY here, not in other sections**

2. **🎯 Major Topics** (`majorTopics`)
   - Important discussions or decisions
   - New features or projects being discussed (not yet started)
   - Cross-team coordination matters
   - **Excludes completed items**

3. **⚠️ Risks & Issues** (`risksAndIssues`)
   - Active problems that need attention
   - Blockers or concerns that could impact work
   - Technical issues under investigation
   - **Excludes resolved issues**

4. **📋 Action Items** (`actionItems`)
   - Clear next steps with assignees
   - Items pending response or approval
   - Must-do items before next meeting
   - **Excludes general discussions**

5. **🔧 Maintenance Notifications** (`maintenanceNotifications`)
   - Scheduled maintenance or system changes
   - Infrastructure updates team should be aware of

## Design Philosophy

**Purpose**: Clear and concise daily summary for wrap-up meetings

**Key Principles**:
- ✅ **No duplication**: Each item appears in exactly one category
- ✅ **Completed first**: Highlights what was accomplished today
- ✅ **Maximum 3 links**: Keeps digest concise and readable
- ✅ **Clear assignment**: Always shows who's responsible
- ✅ **Language matching**: Digest language matches input message language
- ✅ **Wrap-up focused**: Designed for end-of-day team meetings
- ✅ **Chronological thread grouping**: Messages grouped and sorted by thread with timestamps
- ✅ **Latest-message status**: Task status determined from the most recent message in each thread

## Message Formatting and Status Determination

### Thread Grouping and Chronological Sorting

Messages are organized to provide clear temporal context to the LLM:

**Grouping Strategy:**
1. Messages are grouped by thread using `thread_ts` (or `ts` for standalone messages)
2. Within each thread, messages are sorted chronologically (oldest → newest)
3. Each message includes timestamp in format: `[YYYY-MM-DD HH:MM:SS]`
4. The latest message in each thread is marked with `[LATEST]`
5. Thread links are included once per thread (not per message)

**Example Thread Format:**
```
============================================================
🧵 Thread: APIの開発について...
============================================================
[2025-10-20 10:00:00] User1 (ch: C1234567): APIの開発を開始します
[2025-10-20 14:00:00] User2 (ch: C1234567): テストが一部完了しました
[2025-10-20 16:30:00] [LATEST] User1 (ch: C1234567): 残りは明日完了予定です
📎 Thread Link: https://workspace.slack.com/archives/...
============================================================
```

### Status Determination Rules

The LLM is instructed to determine task status using these critical rules:

**1. Latest-Message Priority:**
- Status MUST be determined from the `[LATEST]` marked message only
- Earlier messages are for context but do not determine final status
- If latest message says "進行中" (in progress), the task is NOT completed

**2. Status Keywords Recognition:**

**Completed Indicators** (for completedItems):
- Japanese: "完了", "完了しました", "完了済み", "リリース済み", "デプロイ済み", "解決済み"
- English: "completed", "finished", "done", "released", "deployed", "resolved", "fixed"
- Korean: "완료", "완료했습니다", "해결됨", "배포됨"

**NOT Completed Indicators** (must NOT go to completedItems):
- Japanese: "進行中", "予定", "進行予定", "作業中", "対応中", "調査中", "実施予定"
- English: "in progress", "planned", "working on", "investigating", "scheduled", "will do"
- Korean: "진행중", "예정", "작업중", "조사중"

**3. Partial Completion Handling:**
- "一部完了" (partially completed) → NOT completedItems
- "Phase 1 done, Phase 2 in progress" → NOT completedItems
- Only full task completion goes to completedItems

**4. Decision Examples:**

✅ **Completed** (goes to completedItems):
```
[10:00:00] User: タスク開始
[15:00:00] [LATEST] User: タスク完了しました
```

❌ **NOT Completed** (goes to majorTopics or risksAndIssues):
```
[10:00:00] User: タスク開始
[14:00:00] User: 一部完了
[16:00:00] [LATEST] User: 残りは進行中です  ← "進行中" means NOT completed
```

❌ **Planned** (goes to actionItems):
```
[11:00:00] [LATEST] User: 明日デプロイ予定です  ← "予定" means NOT completed
```

This approach ensures that:
- Task status accurately reflects the latest information
- Partial progress is not mistaken for full completion
- In-progress and planned tasks are correctly categorized
- The digest shows the true current state of work

## Message Collection Process

### 1. Date Range Calculation

```python
# For date "20251020":
# Start: 2025-10-20 00:00:00 (JST)
# End:   2025-10-20 23:59:59 (JST)

# Slack API uses 'on:YYYY-MM-DD' parameter
# Additional timestamp filtering ensures exact range
```

### 2. Search Strategies

```python
# Team Mentions
for team_id in TEAM_MENTIONS:
    search_messages(f"{team_id} on:{target_date}")

# Individual Users  
for user_id in TEAM_USER_IDS:
    search_messages(f"<@{user_id}> on:{target_date}")        # Mentioned
    search_messages(f"from:<@{user_id}> on:{target_date}")   # Sent by user

# Keywords
for keyword in SEARCH_KEYWORDS:
    search_messages(f"{keyword} on:{target_date}")
```

### 3. Filtering

Messages are filtered to exclude:
- **Direct Messages**: Channel IDs starting with 'D' or 'M'
- **Excluded Channels**: Configured in `EXCLUDED_CHANNELS_FROM_DIGEST`
- **Meeting Notes**: Matching `MORNING_MEETING_EXCLUSION_PATTERNS`
- **Out of range**: Messages outside exact timestamp range

### 4. Deduplication

Duplicates are removed using key: `{channel_id}-{timestamp}-{user_id}`

### 5. Thread Link Generation

Complete thread links include reply timestamps:
```
https://workspace.slack.com/archives/CHANNEL/pTIMESTAMP?thread_ts=THREAD_TS
```

## Output Format

### Slack Message Format

The posted digest uses this format (language matches input):

```
*📊 Team Daily Digest - 2025-10-20*

🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸

*✅ Completed Items*

🔴 *High Priority Task*
   Assigned: @acn-user1, @acn-user2
   • Detail point 1
   • Detail point 2
   📎 https://slack.com/archives/...
   📎 https://slack.com/archives/...
   📎 https://slack.com/archives/...

🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸

*🎯 Major Topics*
...

🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸

*⚠️ Risks & Issues*
...

🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸

*📋 Action Items*
...

🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸

*🔧 Maintenance Notifications*
...
```

### Priority Indicators

- 🔴 **HIGH**: Urgent or critical items
- 🟡 **MEDIUM**: Important but not urgent
- 🟢 **LOW**: Minor or informational items

## Language Auto-Detection

The LLM automatically detects the primary language of collected messages:

- **Japanese messages** → Japanese digest
- **Korean messages** → Korean digest
- **English messages** → English digest
- **Mixed languages** → Most frequently used language

**Example**:
```json
{
  "date": "2025年10月20日",
  "completedItems": [
    {
      "title": "API開発完了",
      "details": ["本番環境にデプロイしました"]
    }
  ]
}
```

## Troubleshooting

### Common Issues

#### 1. No Messages Found

**Cause**: Date range or search configuration issue

**Solution**:
- Check if messages exist for the target date
- Verify `SEARCH_KEYWORDS` are correct
- Ensure user IDs and team mentions are valid
- Check date format is YYYYMMDD

#### 2. Wrong Date Range

**Cause**: Timezone or date calculation issue

**Solution**:
- Verify date format is YYYYMMDD (e.g., "20251020")
- Check logs for "Exact range (JST)" output
- Ensure Slack API 'on:' parameter is correct

#### 3. Search API Error

**Cause**: Missing or invalid user token

**Solution**:
- Verify `SLACK_USER_TOKEN` is set (not bot token)
- Ensure token has `search:read` scope
- Check token hasn't expired

#### 4. Duplicate Content

**Cause**: Same item appearing in multiple categories

**Solution**:
- Review LLM prompt emphasizes "NO DUPLICATION"
- Check if completed items are only in completedItems
- Verify LLM is following categorization rules

#### 5. Too Many Thread Links

**Cause**: More than 3 links per item

**Solution**:
- Verify `_limit_thread_links` is working
- Check LLM prompt specifies "Maximum 3 links"
- Review formatter is applying link limit

#### 6. Wrong Language Output

**Cause**: Language detection not working

**Solution**:
- Verify collected messages contain clear language indicators
- Check LLM prompt includes language detection section
- Review "LANGUAGE MATCHING" rule in prompt

## API Reference

### generate_digest()

```python
async def generate_digest(date: Optional[str] = None) -> str
```

**Parameters:**
- `date` (optional): Target date in YYYYMMDD format (e.g., "20251020")

**Returns:**
- LLM analysis prompt with collected messages and analysis instructions

**Date Range:**
- If `date="20251020"`: 2025-10-20 00:00:00 ~ 23:59:59 (JST)
- If `date=None`: Yesterday 00:00:00 ~ 23:59:59 (JST)

**Raises:**
- Connection errors if Slack API fails
- Configuration errors if tokens invalid

### post_digest()

```python
async def post_digest(digest_json: str) -> str
```

**Parameters:**
- `digest_json`: JSON string from LLM analysis (in detected language)

**Returns:**
- Success message with post details

**Raises:**
- `json.JSONDecodeError`: Invalid JSON format
- API errors if posting fails

## Best Practices

1. **Date Specification**: Always use YYYYMMDD format (e.g., "20251020")
2. **Token Security**: Never commit `configs/slack.py` to git
3. **Channel Selection**: Use private channels for sensitive information
4. **Regular Updates**: Keep user mappings and exclusion lists current
5. **No Duplication**: Ensure LLM follows anti-duplication rules
6. **Link Limit**: Maximum 3 thread links per item for readability
7. **Language Consistency**: Verify digest language matches input messages

## Examples

### Example 1: Daily Automated Digest

```python
import asyncio
from src.wrappers.slack.digest_wrapper import generate_digest

async def daily_digest():
    # Generate for yesterday
    result = await generate_digest()
    print(result)

asyncio.run(daily_digest())
```

### Example 2: Specific Date Digest

```python
# Generate digest for October 20, 2025
result = await generate_digest(date="20251020")

# Date range will be:
# 2025-10-20 00:00:00 ~ 2025-10-20 23:59:59 (JST)
```

### Example 3: Weekly Review

```python
from datetime import datetime, timedelta

# Generate digest for each day of last week
for i in range(7):
    target_date = (datetime.now() - timedelta(days=i+1)).strftime("%Y%m%d")
    print(f"Generating digest for {target_date}")
    result = await generate_digest(date=target_date)
```

---

## Future Enhancements

Possible additions for all Slack tools:
- Bulk message operations
- Advanced search filters
- Reaction management
- File upload support
- Channel history retrieval
- Enhanced rate limiting
- Retry with exponential backoff
- Digest scheduling and automation
- Custom digest templates
- Multi-language support enhancement

## License

Same as parent project

## Contributing

Follow the existing tool pattern:
1. Create tool class in `src/tools/slack/`
2. Add wrapper function in `src/wrappers/slack/`
3. Register in `main.py`
4. Add comprehensive docstrings
5. Test thoroughly
6. Update this documentation
7. Never commit actual credentials

## Support

For issues or questions:
1. Check logs in console output (look for 🔍 🚀 ✅ ❌ emoji markers)
2. Verify configuration in `configs/slack.py`
3. Test Slack API directly with curl
4. Review error messages carefully
5. Check date format and timezone
6. Verify token permissions and scopes

