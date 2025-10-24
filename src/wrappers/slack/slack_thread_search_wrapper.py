"""
Slack Thread Search Wrapper for MCP Registration
Provides intelligent thread search with relevance scoring
"""
from fastmcp import Context
from typing import Optional, List, Literal
from src.tools.slack.slack_thread_search_tool import SlackThreadSearchTool
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize tool instance
_search_tool = SlackThreadSearchTool()


async def search_threads(
    keyword: str,
    max_results: int = 20,
    sort_by: Literal['relevance', 'timestamp'] = 'relevance',
    output_format: Literal['summary', 'detailed', 'json', 'markdown'] = 'summary',
    channels: Optional[List[str]] = None,
    exclude_channels: Optional[List[str]] = None,
    after_date: Optional[str] = None,
    before_date: Optional[str] = None,
    from_user: Optional[str] = None,
    include_llm_prompt: bool = False,
    top_n_detailed: int = 3,
    ctx: Context = None
) -> str:
    """
    Search Slack threads with intelligent relevance scoring
    
    Searches across Slack workspace for threads matching the keyword, ranks results
    using multi-factor relevance scoring, and returns formatted results.
    
    **Key Features:**
    - Multi-factor relevance scoring (native score, keyword frequency, recency, engagement)
    - Advanced search filters (channels, dates, users)
    - Multiple output formats (summary, detailed, json, markdown)
    - Optional LLM analysis prompt generation
    - Full thread content retrieval for top results
    
    **Parameters:**
    - keyword: Search keyword or phrase (required)
      Example: "API design", "database performance"
    
    - max_results: Maximum number of results to return (default: 20, max: 100)
    
    - sort_by: Sort results by 'relevance' or 'timestamp' (default: relevance)
      * relevance: Uses multi-factor scoring algorithm
      * timestamp: Most recent first
    
    - output_format: Choose output format (default: summary)
      * summary: Quick overview with top 5 results
      * detailed: Full thread content for top results
      * json: Structured JSON for programmatic use
      * markdown: Rich markdown formatting
    
    - channels: List of channel IDs to search in (optional)
      Example: ["C1234567890", "C0987654321"]
    
    - exclude_channels: List of channel IDs to exclude (optional)
      Example: ["C1111111111"]
    
    - after_date: Search messages after this date (optional)
      Format: YYYY-MM-DD
      Example: "2024-01-01"
    
    - before_date: Search messages before this date (optional)
      Format: YYYY-MM-DD
      Example: "2024-12-31"
    
    - from_user: Search messages from specific user (optional)
      Example: "@john.doe" or "U1234567890"
    
    - include_llm_prompt: Include LLM analysis prompt in output (default: False)
      When True, adds a prompt asking LLM to analyze the search results
    
    - top_n_detailed: Number of top results to fetch full content for (default: 3)
      Only used when output_format is 'detailed' or 'markdown'
    
    **Returns:**
    Formatted search results based on output_format parameter
    
    **Relevance Scoring Algorithm:**
    Results are scored using weighted factors:
    - Native score (30%): Slack's built-in relevance score
    - Keyword frequency (20%): How often keyword appears
    - Recency (15%): How recent the message is
    - Engagement (25%): Number of replies and reactions
    - Title match (10%): Keyword in first line of message
    
    **Example Usage:**
    
    ```python
    # Basic search
    results = await search_threads(
        keyword="database optimization"
    )
    
    # Advanced search with filters
    results = await search_threads(
        keyword="API design patterns",
        channels=["C1234567890"],
        after_date="2024-01-01",
        sort_by="relevance",
        output_format="detailed",
        include_llm_prompt=True
    )
    
    # Search in specific channel, exclude DMs
    results = await search_threads(
        keyword="security review",
        channels=["C1234567890"],
        from_user="@security.team",
        max_results=10
    )
    
    # Get JSON output for programmatic processing
    results = await search_threads(
        keyword="deployment issues",
        output_format="json",
        max_results=50
    )
    ```
    
    **Use Cases:**
    - Find relevant discussions on a topic
    - Track decisions and action items
    - Discover expertise and key contributors
    - Research past solutions to similar problems
    - Aggregate team knowledge on specific subjects
    - Prepare summaries of ongoing discussions
    
    **Output Formats:**
    
    1. **Summary** (Default): Quick overview with top 5 results
       - Rank, relevance score, channel, user, date
       - Message preview (150 chars)
       - Reply and reaction counts
       - Permalink to full thread
    
    2. **Detailed**: Full thread content for top N results
       - Everything from summary format
       - Complete thread conversation
       - All participants and timestamps
       - Useful for deep analysis
    
    3. **JSON**: Structured data format
       - All metadata preserved
       - Easy to parse programmatically
       - Includes search metadata and timestamp
    
    4. **Markdown**: Rich formatted output
       - Tables with metrics
       - Collapsible sections
       - Copy-paste friendly
       - Good for documentation
    
    **Tips for Better Results:**
    - Use specific keywords (not too broad)
    - Combine with channel filters for focused search
    - Use date ranges to find recent discussions
    - Try both 'relevance' and 'timestamp' sorting
    - Enable LLM prompt for intelligent analysis
    
    **Error Handling:**
    - Empty keyword: Returns error message
    - No results: Returns helpful search tips
    - API errors: Returns detailed error with suggestions
    - Partial failures: Returns available results with warning
    
    **Performance Notes:**
    - Basic search: Fast (1-2 seconds)
    - Detailed format: Slower due to thread content fetching
    - Large result sets: May take longer to process
    - Channel name lookup: Cached for better performance
    """
    if ctx:
        ctx.info(f"Searching threads for keyword: {keyword}")
        ctx.info(f"Filters - sort: {sort_by}, format: {output_format}, max: {max_results}")
    
    try:
        result = await _search_tool.execute(
            keyword=keyword,
            max_results=max_results,
            sort_by=sort_by,
            output_format=output_format,
            channels=channels,
            exclude_channels=exclude_channels,
            after_date=after_date,
            before_date=before_date,
            from_user=from_user,
            include_llm_prompt=include_llm_prompt,
            top_n_detailed=top_n_detailed
        )
        
        if ctx:
            ctx.info("Thread search completed successfully")
        
        return result
        
    except Exception as e:
        logger.error(f"Thread search wrapper error: {e}", exc_info=True)
        if ctx:
            ctx.error(f"Thread search failed: {e}")
        
        return f"""❌ **Thread Search Error**

An error occurred while searching: {str(e)}

**Troubleshooting:**
- Check that your keyword is valid
- Verify channel IDs if using channel filters
- Ensure date format is YYYY-MM-DD
- Check Slack API permissions
- Try simplifying your search query

Please try again or contact support if the issue persists.
"""
