"""
Slack Thread Search Tool
Advanced thread search with multi-factor relevance scoring
"""
import re
import time
import json
import aiohttp
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime

from src.tools.base import BaseTool
from src.tools.slack.slack_message_retrieval_tool import SlackMessageRetrievalTool
from configs.slack import get_slack_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SlackThreadSearchTool(BaseTool):
    """
    Advanced Slack thread search with intelligent relevance scoring
    """
    
    # Default weights for relevance scoring
    DEFAULT_WEIGHTS = {
        'native_score': 0.3,      # Slack's built-in relevance score
        'keyword_freq': 0.2,       # Keyword frequency in message
        'recency': 0.15,           # How recent the message is
        'engagement': 0.25,        # Replies + reactions
        'title_match': 0.1         # Keyword in first line
    }
    
    def __init__(self):
        super().__init__(
            name="slack_thread_search",
            description="Search Slack threads with advanced relevance scoring"
        )
        self.config = get_slack_config()
        self.retrieval_tool = SlackMessageRetrievalTool()
        self.channel_name_cache: Dict[str, str] = {}
    
    async def execute(
        self,
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
        **kwargs
    ) -> str:
        """
        Execute thread search with advanced filtering and scoring
        
        Args:
            keyword: Search keyword(s)
            max_results: Maximum number of results to return (default: 20)
            sort_by: Sort by 'relevance' or 'timestamp' (default: relevance)
            output_format: Output format - summary, detailed, json, markdown
            channels: List of channel IDs to search in (optional)
            exclude_channels: List of channel IDs to exclude (optional)
            after_date: Search after this date (YYYY-MM-DD format)
            before_date: Search before this date (YYYY-MM-DD format)
            from_user: Search messages from specific user
            include_llm_prompt: Include LLM analysis prompt in output
            top_n_detailed: Number of top results to fetch full content for
            
        Returns:
            Formatted search results
        """
        try:
            logger.info(f"Starting thread search for keyword: {keyword}")
            
            # Validate inputs
            if not keyword or not keyword.strip():
                return "❌ Error: Search keyword cannot be empty"
            
            # Build search query
            query = self._build_search_query(
                keyword=keyword,
                channels=channels,
                exclude_channels=exclude_channels,
                after_date=after_date,
                before_date=before_date,
                from_user=from_user
            )
            
            logger.info(f"Built search query: {query}")
            
            # Execute search
            search_results = await self._search_messages(query, max_results)
            
            if not search_results:
                return self._format_no_results(keyword)
            
            logger.info(f"Found {len(search_results)} results")
            
            # Calculate relevance scores
            scored_results = self._calculate_relevance_scores(search_results, keyword)
            
            # Sort results
            if sort_by == 'relevance':
                scored_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            else:  # timestamp
                scored_results.sort(key=lambda x: float(x.get('ts', 0)), reverse=True)
            
            # Limit results
            scored_results = scored_results[:max_results]
            
            # Fetch full thread content for top results
            if output_format in ['detailed', 'markdown']:
                scored_results = await self._fetch_top_thread_contents(
                    scored_results[:top_n_detailed]
                ) + scored_results[top_n_detailed:]
            
            # Fetch channel names
            await self._enrich_with_channel_names(scored_results)
            
            # Format output
            return await self._format_output(
                results=scored_results,
                keyword=keyword,
                output_format=output_format,
                include_llm_prompt=include_llm_prompt
            )
            
        except Exception as e:
            logger.error(f"Thread search failed: {e}", exc_info=True)
            return f"❌ Search Error: {str(e)}\n\nPlease check your search parameters and try again."
    
    def _build_search_query(
        self,
        keyword: str,
        channels: Optional[List[str]] = None,
        exclude_channels: Optional[List[str]] = None,
        after_date: Optional[str] = None,
        before_date: Optional[str] = None,
        from_user: Optional[str] = None
    ) -> str:
        """Build advanced Slack search query"""
        query_parts = [keyword.strip()]
        
        # Add channel filters
        if channels:
            for channel in channels:
                query_parts.append(f"in:{channel}")
        
        if exclude_channels:
            for channel in exclude_channels:
                query_parts.append(f"-in:{channel}")
        
        # Add date filters
        if after_date:
            query_parts.append(f"after:{after_date}")
        
        if before_date:
            query_parts.append(f"before:{before_date}")
        
        # Add user filter
        if from_user:
            query_parts.append(f"from:{from_user}")
        
        return " ".join(query_parts)
    
    async def _search_messages(
        self,
        query: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Execute Slack search API call"""
        url = f"{self.config.base_url}/search.messages"
        
        # Use user token for better search access
        token = self.config.user_token if self.config.user_token else self.config.bot_token
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'query': query,
            'count': min(max_results, 100),  # API limit
            'sort': 'score',
            'sort_dir': 'desc'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params, timeout=30) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Slack API error {response.status}: {error_text}")
                
                data = await response.json()
                
                if not data.get('ok'):
                    error = data.get('error', 'Unknown error')
                    raise Exception(f"Slack API error: {error}")
                
                messages = data.get('messages', {}).get('matches', [])
                return messages
    
    def _calculate_relevance_scores(
        self,
        messages: List[Dict[str, Any]],
        keyword: str,
        weights: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """Calculate multi-factor relevance scores for messages"""
        if weights is None:
            weights = self.DEFAULT_WEIGHTS
        
        keyword_lower = keyword.lower()
        current_time = time.time()
        
        for message in messages:
            score = 0.0
            
            # Factor 1: Slack's native relevance score
            native_score = message.get('score', 0)
            score += float(native_score) * weights['native_score']
            
            # Factor 2: Keyword frequency
            text = message.get('text', '').lower()
            keyword_count = text.count(keyword_lower)
            keyword_freq_score = min(keyword_count * 10, 50)
            score += keyword_freq_score * weights['keyword_freq']
            
            # Factor 3: Recency
            try:
                msg_timestamp = float(message.get('ts', 0))
                days_old = (current_time - msg_timestamp) / 86400
                recency_score = max(0, 100 - days_old)
                score += recency_score * weights['recency']
            except (ValueError, TypeError):
                pass
            
            # Factor 4: Thread engagement
            reply_count = message.get('reply_count', 0)
            reactions = message.get('reactions', [])
            reaction_count = sum(r.get('count', 0) for r in reactions)
            engagement_score = min(reply_count * 5 + reaction_count * 2, 100)
            score += engagement_score * weights['engagement']
            
            # Factor 5: Keyword in first line (title)
            first_line = text.split('\n')[0].lower() if text else ''
            if keyword_lower in first_line:
                score += 20 * weights['title_match']
            
            # Store calculated score
            message['relevance_score'] = round(score, 2)
            message['keyword_count'] = keyword_count
            message['engagement'] = {
                'replies': reply_count,
                'reactions': reaction_count
            }
        
        return messages
    
    async def _fetch_top_thread_contents(
        self,
        top_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Fetch full thread content for top results"""
        for result in top_results:
            try:
                channel = result.get('channel', {}).get('id')
                timestamp = result.get('ts')
                
                if channel and timestamp:
                    # Use retrieval tool to get full thread
                    thread_content = await self.retrieval_tool.execute(
                        channel=channel,
                        timestamp=timestamp,
                        include_replies=True
                    )
                    result['full_thread_content'] = thread_content
            except Exception as e:
                logger.warning(f"Failed to fetch thread content: {e}")
                result['full_thread_content'] = None
        
        return top_results
    
    async def _enrich_with_channel_names(
        self,
        results: List[Dict[str, Any]]
    ) -> None:
        """Enrich results with human-readable channel names"""
        for result in results:
            channel_id = result.get('channel', {}).get('id')
            if channel_id:
                result['channel_name'] = await self._get_channel_name(channel_id)
    
    async def _get_channel_name(self, channel_id: str) -> str:
        """Get channel name with caching"""
        if channel_id in self.channel_name_cache:
            return self.channel_name_cache[channel_id]
        
        try:
            url = f"{self.config.base_url}/conversations.info"
            token = self.config.user_token if self.config.user_token else self.config.bot_token
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            params = {'channel': channel_id}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('ok'):
                            name = data.get('channel', {}).get('name', channel_id)
                            self.channel_name_cache[channel_id] = name
                            return name
        except Exception as e:
            logger.warning(f"Failed to fetch channel name for {channel_id}: {e}")
        
        return channel_id
    
    def _format_no_results(self, keyword: str) -> str:
        """Format message when no results found"""
        return f"""🔍 No Results Found

Search keyword: "{keyword}"

**Suggestions to improve your search:**
- Try more general keywords
- Check spelling and try synonyms
- Use shorter keywords
- Try searching in English if applicable
- Remove date/channel filters to broaden search
"""
    
    async def _format_output(
        self,
        results: List[Dict[str, Any]],
        keyword: str,
        output_format: str,
        include_llm_prompt: bool
    ) -> str:
        """Format results based on output format"""
        if output_format == 'json':
            return self._format_json(results, keyword)
        elif output_format == 'markdown':
            return self._format_markdown(results, keyword, include_llm_prompt)
        elif output_format == 'detailed':
            return self._format_detailed(results, keyword, include_llm_prompt)
        else:  # summary
            return self._format_summary(results, keyword, include_llm_prompt)
    
    def _format_json(
        self,
        results: List[Dict[str, Any]],
        keyword: str
    ) -> str:
        """Format as JSON"""
        output = {
            'search_metadata': {
                'keyword': keyword,
                'total_results': len(results),
                'timestamp': datetime.now().isoformat()
            },
            'results': []
        }
        
        for idx, result in enumerate(results, 1):
            output['results'].append({
                'rank': idx,
                'relevance_score': result.get('relevance_score', 0),
                'channel_id': result.get('channel', {}).get('id'),
                'channel_name': result.get('channel_name', 'Unknown'),
                'timestamp': result.get('ts'),
                'user': result.get('user') or result.get('username', 'Unknown'),
                'text_preview': result.get('text', '')[:200],
                'permalink': result.get('permalink'),
                'replies': result.get('engagement', {}).get('replies', 0),
                'reactions': result.get('engagement', {}).get('reactions', 0),
                'keyword_count': result.get('keyword_count', 0)
            })
        
        return json.dumps(output, indent=2, ensure_ascii=False)
    
    def _format_summary(
        self,
        results: List[Dict[str, Any]],
        keyword: str,
        include_llm_prompt: bool
    ) -> str:
        """Format as summary (default)"""
        output = [
            f"🔍 **Thread Search Results for \"{keyword}\"**",
            "",
            f"Found **{len(results)}** matching threads",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            ""
        ]
        
        for idx, result in enumerate(results[:5], 1):
            # Medal emoji for top 3
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(idx, f"#{idx}")
            
            score = result.get('relevance_score', 0)
            channel = result.get('channel_name', 'Unknown')
            user = result.get('user') or result.get('username', 'Unknown')
            timestamp = result.get('ts', '')
            
            # Format timestamp
            try:
                dt = datetime.fromtimestamp(float(timestamp))
                time_str = dt.strftime('%Y-%m-%d %H:%M')
            except:
                time_str = 'Unknown time'
            
            replies = result.get('engagement', {}).get('replies', 0)
            reactions = result.get('engagement', {}).get('reactions', 0)
            text = result.get('text', '')
            text_preview = text[:150] + "..." if len(text) > 150 else text
            permalink = result.get('permalink', '')
            
            output.extend([
                f"{medal} **Rank #{idx}** - Relevance Score: **{score}**",
                f"📍 Channel: #{channel}",
                f"👤 User: {user}",
                f"📅 Date: {time_str}",
                f"💬 Replies: {replies} | ⚡ Reactions: {reactions}",
                "",
                f"📝 {text_preview}",
                "",
                f"🔗 [View Thread]({permalink})",
                "",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                ""
            ])
        
        if len(results) > 5:
            output.append(f"\n... and {len(results) - 5} more results")
        
        if include_llm_prompt:
            output.extend([
                "",
                "",
                self._generate_llm_prompt(results, keyword)
            ])
        
        return "\n".join(output)
    
    def _format_detailed(
        self,
        results: List[Dict[str, Any]],
        keyword: str,
        include_llm_prompt: bool
    ) -> str:
        """Format with detailed thread content"""
        output = [
            f"🔍 **Detailed Thread Search Results for \"{keyword}\"**",
            "",
            f"Found **{len(results)}** matching threads",
            f"Showing top results with full thread content",
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            ""
        ]
        
        for idx, result in enumerate(results, 1):
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(idx, f"#{idx}")
            score = result.get('relevance_score', 0)
            channel = result.get('channel_name', 'Unknown')
            
            output.extend([
                f"{medal} **Rank #{idx}** - Relevance Score: **{score}**",
                f"📍 Channel: #{channel}",
                ""
            ])
            
            # Include full thread content if available
            if result.get('full_thread_content'):
                output.extend([
                    "**Full Thread Content:**",
                    "",
                    result['full_thread_content'],
                    ""
                ])
            else:
                text = result.get('text', '')
                output.extend([
                    f"**Message:** {text}",
                    ""
                ])
            
            output.extend([
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                ""
            ])
        
        if include_llm_prompt:
            output.extend([
                "",
                self._generate_llm_prompt(results, keyword)
            ])
        
        return "\n".join(output)
    
    def _format_markdown(
        self,
        results: List[Dict[str, Any]],
        keyword: str,
        include_llm_prompt: bool
    ) -> str:
        """Format as rich markdown"""
        output = [
            f"# 🔍 Thread Search Results",
            "",
            f"**Search Query:** `{keyword}`  ",
            f"**Total Results:** {len(results)}  ",
            f"**Search Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            ""
        ]
        
        for idx, result in enumerate(results, 1):
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(idx, f"**#{idx}**")
            score = result.get('relevance_score', 0)
            channel = result.get('channel_name', 'Unknown')
            user = result.get('user') or result.get('username', 'Unknown')
            timestamp = result.get('ts', '')
            
            try:
                dt = datetime.fromtimestamp(float(timestamp))
                time_str = dt.strftime('%Y-%m-%d %H:%M')
            except:
                time_str = 'Unknown'
            
            replies = result.get('engagement', {}).get('replies', 0)
            reactions = result.get('engagement', {}).get('reactions', 0)
            permalink = result.get('permalink', '')
            
            output.extend([
                f"## {medal} Result #{idx}",
                "",
                f"| Metric | Value |",
                f"|--------|-------|",
                f"| **Relevance Score** | {score} |",
                f"| **Channel** | #{channel} |",
                f"| **User** | {user} |",
                f"| **Date** | {time_str} |",
                f"| **Replies** | {replies} |",
                f"| **Reactions** | {reactions} |",
                "",
                "### Message Content",
                "",
                "```",
                result.get('text', 'No content'),
                "```",
                "",
                f"🔗 [View Full Thread]({permalink})",
                "",
                "---",
                ""
            ])
        
        if include_llm_prompt:
            output.extend([
                "",
                self._generate_llm_prompt(results, keyword)
            ])
        
        return "\n".join(output)
    
    def _generate_llm_prompt(
        self,
        results: List[Dict[str, Any]],
        keyword: str
    ) -> str:
        """Generate LLM analysis prompt"""
        return f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 **LLM Analysis Request**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You are a Slack conversation analysis expert. Please analyze the search results above for the keyword "{keyword}".

**Your Analysis Should Include:**

1. **Relevance Assessment**
   - How relevant are the top results to the search query?
   - Are there common themes across multiple threads?

2. **Key Insights**
   - What are the main topics being discussed?
   - Who are the key participants?
   - What decisions or conclusions were reached?

3. **Summary of Top 3 Threads**
   - For each of the top 3 threads, provide:
     * Main topic and context
     * Key discussion points
     * Participants and their roles
     * Any action items or decisions

4. **Recommendations**
   - What should someone searching for "{keyword}" know?
   - Are there follow-up searches that might be useful?
   - What patterns or trends do you notice?

**Format your analysis in a clear, structured way that's easy to read and actionable.**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
