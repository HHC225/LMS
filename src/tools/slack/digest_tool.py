"""
Digest Generation Tool
Generates team digest from Slack conversations
"""
import asyncio
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
import aiohttp

from configs.slack import (
    get_slack_config,
    TEAM_USER_MAPPING,
    TEAM_MENTIONS,
    TEAM_USER_IDS,
    EXCLUDED_CHANNELS_FROM_DIGEST,
    MORNING_MEETING_EXCLUSION_PATTERNS,
    SEARCH_KEYWORDS,
    DIGEST_TARGET_CHANNEL,
    DIGEST_BOT_USERNAME,
    DIGEST_BOT_ICON,
    convert_mentions_to_slack_format
)
from src.utils.slack_user_cache import get_multiple_user_names
from src.utils.logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Digest Formatter Helper Class
# =============================================================================

class DigestFormatter:
    """Format digest data for Slack posting"""
    
    # Section divider
    SECTION_DIVIDER = "🔸🔸🔸🔸🔸🔸🔸🔸🔸🔸"
    
    @staticmethod
    def format_digest_message(digest_data: Dict[str, Any]) -> str:
        """
        Convert JSON digest structure to Slack message format
        
        Args:
            digest_data: Digest data dictionary with structure:
                {
                    "date": "YYYY年MM月DD日",
                    "majorTopics": [...],
                    "completedItems": [...],
                    "risksAndIssues": [...],
                    "actionItems": [...],
                    "maintenanceNotifications": [...]
                }
        
        Returns:
            Formatted Slack message text
        """
        sections = [
            DigestFormatter._create_header(digest_data.get("date", "Unknown Date")),
            DigestFormatter.SECTION_DIVIDER,
            DigestFormatter._create_completed_items_section(digest_data.get("completedItems", [])),
            DigestFormatter.SECTION_DIVIDER,
            DigestFormatter._create_major_topics_section(digest_data.get("majorTopics", [])),
            DigestFormatter.SECTION_DIVIDER,
            DigestFormatter._create_risks_section(digest_data.get("risksAndIssues", [])),
            DigestFormatter.SECTION_DIVIDER,
            DigestFormatter._create_action_items_section(digest_data.get("actionItems", [])),
            DigestFormatter.SECTION_DIVIDER,
            DigestFormatter._create_maintenance_section(digest_data.get("maintenanceNotifications", []))
        ]
        
        return "\n\n".join([s for s in sections if s.strip()])
    
    @staticmethod
    def format_error_message(error_data: Dict[str, Any]) -> str:
        """
        Format error information as Slack message
        
        Args:
            error_data: Error data dictionary with structure:
                {
                    "error": true,
                    "date": "YYYY-MM-DD",
                    "timestamp": "HH:MM:SS",
                    "errorMessage": "...",
                    "cause": [...],
                    "recommendations": [...]
                }
        
        Returns:
            Formatted error message
        """
        cause_list = "\n".join([f"• {c}" for c in error_data.get("cause", [])])
        rec_list = "\n".join([f"• {r}" for r in error_data.get("recommendations", [])])
        
        return f"""*🚨 Team Daily Digest - Error Occurred*

*📅 Analysis Period:* {error_data.get("date", "Unknown")}
*🕰 Occurrence Time:* {error_data.get("timestamp", "Unknown")}
*⚠️ Error Details:* {error_data.get("errorMessage", "Unknown error")}

*🔍 Possible Causes:*
{cause_list}

*📝 Recommendations:*
{rec_list}

Action required. Please contact the system administrator."""
    
    @staticmethod
    def _create_header(date: str) -> str:
        """Create header section"""
        return f"*📊 Team Daily Digest - {date}*"
    
    @staticmethod
    def _create_major_topics_section(topics: List[Dict[str, Any]]) -> str:
        """Create major topics section"""
        if not topics:
            return ""
        
        lines = ["*🎯 Major Topics(In Progress)*"]
        for topic in topics:
            priority_emoji = DigestFormatter._get_priority_emoji(topic.get("priority", "LOW"))
            title = topic.get("title", "No title")
            assignees = ", ".join(topic.get("assignees", []))
            
            lines.append(f"\n{priority_emoji} *{title}*")
            if assignees:
                lines.append(f"   Assigned: {assignees}")
            
            for detail in topic.get("details", []):
                lines.append(f"   • {detail}")
            
            # Limit to maximum 3 thread links
            limited_links = DigestFormatter._limit_thread_links(topic.get("threadLinks", []))
            for link in limited_links:
                lines.append(f"   📎 {link}")
        
        return "\n".join(lines)
    
    @staticmethod
    def _create_completed_items_section(items: List[Dict[str, Any]]) -> str:
        """Create completed items section"""
        if not items:
            return ""
        
        lines = ["*✅ Completed Items*"]
        for item in items:
            priority_emoji = DigestFormatter._get_priority_emoji(item.get("priority", "LOW"))
            title = item.get("title", "No title")
            assignees = ", ".join(item.get("assignees", []))
            
            lines.append(f"\n{priority_emoji} *{title}*")
            if assignees:
                lines.append(f"   Assigned: {assignees}")
            
            for detail in item.get("details", []):
                lines.append(f"   • {detail}")
            
            # Limit to maximum 3 thread links
            limited_links = DigestFormatter._limit_thread_links(item.get("threadLinks", []))
            for link in limited_links:
                lines.append(f"   📎 {link}")
        
        return "\n".join(lines)
    
    @staticmethod
    def _create_risks_section(items: List[Dict[str, Any]]) -> str:
        """Create risks and issues section"""
        if not items:
            return ""
        
        lines = ["*⚠️ Risks & Issues*"]
        for item in items:
            priority_emoji = DigestFormatter._get_priority_emoji(item.get("priority", "LOW"))
            title = item.get("title", "No title")
            assignees = ", ".join(item.get("assignees", []))
            
            lines.append(f"\n{priority_emoji} *{title}*")
            if assignees:
                lines.append(f"   Assigned: {assignees}")
            
            for detail in item.get("details", []):
                lines.append(f"   • {detail}")
            
            # Limit to maximum 3 thread links
            limited_links = DigestFormatter._limit_thread_links(item.get("threadLinks", []))
            for link in limited_links:
                lines.append(f"   📎 {link}")
        
        return "\n".join(lines)
    
    @staticmethod
    def _create_action_items_section(items: List[Dict[str, Any]]) -> str:
        """Create action items section"""
        if not items:
            return ""
        
        lines = ["*📋 Action Items*"]
        for item in items:
            priority_emoji = DigestFormatter._get_priority_emoji(item.get("priority", "LOW"))
            title = item.get("title", "No title")
            assignees = ", ".join(item.get("assignees", []))
            deadline = item.get("deadline")
            
            lines.append(f"\n{priority_emoji} *{title}*")
            if assignees:
                lines.append(f"   Assigned: {assignees}")
            if deadline:
                lines.append(f"   Deadline: {deadline}")
            
            for detail in item.get("details", []):
                lines.append(f"   • {detail}")
            
            # Limit to maximum 3 thread links
            limited_links = DigestFormatter._limit_thread_links(item.get("threadLinks", []))
            for link in limited_links:
                lines.append(f"   📎 {link}")
        
        return "\n".join(lines)
    
    @staticmethod
    def _create_maintenance_section(items: List[Dict[str, Any]]) -> str:
        """Create maintenance notifications section"""
        if not items:
            return ""
        
        lines = ["*🔧 Maintenance Notifications*"]
        for item in items:
            priority_emoji = DigestFormatter._get_priority_emoji(item.get("priority", "LOW"))
            title = item.get("title", "No title")
            assignees = ", ".join(item.get("assignees", []))
            
            lines.append(f"\n{priority_emoji} *{title}*")
            if assignees:
                lines.append(f"   Assigned: {assignees}")
            
            for detail in item.get("details", []):
                lines.append(f"   • {detail}")
            
            # Limit to maximum 3 thread links
            limited_links = DigestFormatter._limit_thread_links(item.get("threadLinks", []))
            for link in limited_links:
                lines.append(f"   📎 {link}")
        
        return "\n".join(lines)
    
    @staticmethod
    def _get_priority_emoji(priority: str) -> str:
        """Get emoji for priority level"""
        priority_upper = priority.upper()
        if priority_upper == "HIGH":
            return "🔴"
        elif priority_upper == "MEDIUM":
            return "🟡"
        else:  # LOW or default
            return "🟢"
    
    @staticmethod
    def _limit_thread_links(links: List[str], max_links: int = 3) -> List[str]:
        """
        Limit thread links to maximum number (most recent)
        
        Args:
            links: List of thread URLs
            max_links: Maximum number of links to keep (default: 3)
            
        Returns:
            Limited list of thread links
        """
        if not links:
            return []
        # Return up to max_links (assuming links are already in order)
        return links[:max_links]


# =============================================================================
# Main Digest Generator Tool
# =============================================================================


class DigestGeneratorTool:
    """
    Generate team digest from Slack messages
    Collects, analyzes, and posts digest automatically
    """
    
    def __init__(self):
        self.config = get_slack_config()
    
    async def generate_digest(self, date: Optional[str] = None) -> str:
        """
        Generate and post digest for specified date
        
        Args:
            date: Target date in YYYYMMDD format (optional, defaults to yesterday)
            
        Returns:
            LLM prompt for digest generation or success message
        """
        try:
            logger.info("🚀 Starting digest generation")
            
            # Calculate date range
            date_range = self._calculate_date_range(date)
            date_str = self._format_japanese_date(date_range["start"])
            
            # Log exact datetime range for debugging
            start_dt = date_range["start"]
            end_dt = date_range["end"]
            logger.info(f"📅 Target date: {date_str}")
            logger.info(f"⏰ Exact range (JST): {start_dt.strftime('%Y-%m-%d %H:%M:%S')} ~ {end_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"🔍 Slack search query date: on:{date_range['target_date_str']}")
            
            # Collect messages
            messages = await self._collect_team_messages(date_range)
            
            if not messages:
                return f"ℹ️ No messages found for {date_str}\n\nNo digest will be generated."
            
            logger.info(f"✅ Collected {len(messages)} messages")
            
            # Format messages for LLM
            formatted_messages = await self._format_messages_for_llm(messages)
            
            # Generate LLM prompt
            llm_prompt = self._generate_analysis_prompt(formatted_messages, date_str)
            
            # Return prompt for LLM to process
            # (In actual MCP execution, LLM will see this prompt and generate JSON response)
            return llm_prompt
            
        except Exception as e:
            logger.error(f"❌ Digest generation failed: {e}")
            return self._generate_error_prompt(str(e), date)
    
    async def post_digest(self, digest_json: str) -> str:
        """
        Parse digest JSON and post to Slack
        
        Args:
            digest_json: JSON string from LLM analysis
            
        Returns:
            Success/error message
        """
        try:
            logger.info("📤 Posting digest to Slack")
            
            # Parse JSON
            digest_data = json.loads(digest_json)
            
            # Check for error response
            if digest_data.get("error"):
                formatted_message = DigestFormatter.format_error_message(digest_data)
            else:
                formatted_message = DigestFormatter.format_digest_message(digest_data)
            
            # Convert mentions
            formatted_message = convert_mentions_to_slack_format(formatted_message)
            
            # Post to Slack
            result = await self._post_message(
                channel=DIGEST_TARGET_CHANNEL,
                text=formatted_message,
                username=DIGEST_BOT_USERNAME,
                icon_emoji=DIGEST_BOT_ICON
            )
            
            if result.get("ok"):
                logger.info(f"✅ Digest posted successfully: ts={result.get('ts')}")
                return f"""✅ Digest posted successfully to channel {DIGEST_TARGET_CHANNEL}

**Post Details:**
- Timestamp: {result.get('ts')}
- Message Length: {len(formatted_message)} characters
- Bot: {DIGEST_BOT_USERNAME}

**Preview:**
{formatted_message[:200]}..."""
            else:
                raise Exception(f"Slack API error: {result.get('error', 'Unknown error')}")
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing failed: {e}")
            return f"❌ Failed to parse digest JSON: {e}\n\nPlease ensure the LLM returns valid JSON."
        except Exception as e:
            logger.error(f"❌ Failed to post digest: {e}")
            return f"❌ Failed to post digest: {e}"
    
    async def _collect_team_messages(self, date_range: Dict[str, datetime]) -> List[Dict[str, Any]]:
        """
        Collect team-related messages within date range
        
        Args:
            date_range: Dictionary with 'start' and 'end' datetime objects
            
        Returns:
            List of filtered and deduplicated messages
        """
        all_messages: List[Dict[str, Any]] = []
        
        logger.info("🔍 Starting message collection")
        
        # Search by team mentions
        logger.info(f"👥 Searching team mentions ({len(TEAM_MENTIONS)} teams)")
        for mention_id in TEAM_MENTIONS:
            try:
                messages = await self._search_messages(mention_id, date_range)
                all_messages.extend(messages)
                logger.info(f"  ✓ {mention_id}: {len(messages)} messages")
                await asyncio.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"  ✗ {mention_id}: {e}")
        
        # Search by individual users
        logger.info(f"👤 Searching individual users ({len(TEAM_USER_IDS)} users)")
        for user_id in TEAM_USER_IDS:
            try:
                # Search for mentions of user
                mentions = await self._search_messages(f"<@{user_id}>", date_range)
                all_messages.extend(mentions)
                await asyncio.sleep(1)
                
                # Search for messages from user
                from_user = await self._search_messages(f"from:<@{user_id}>", date_range)
                all_messages.extend(from_user)
                await asyncio.sleep(1)
                
                logger.info(f"  ✓ {user_id}: {len(mentions) + len(from_user)} messages")
            except Exception as e:
                logger.error(f"  ✗ {user_id}: {e}")
        
        # Search by keywords
        logger.info(f"🔑 Searching keywords ({len(SEARCH_KEYWORDS)} keywords)")
        for keyword in SEARCH_KEYWORDS:
            try:
                messages = await self._search_messages(keyword, date_range)
                all_messages.extend(messages)
                logger.info(f"  ✓ '{keyword}': {len(messages)} messages")
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"  ✗ '{keyword}': {e}")
        
        logger.info(f"📊 Total collected: {len(all_messages)} messages")
        
        # Filter excluded messages
        filtered = self._filter_excluded_messages(all_messages)
        logger.info(f"🔒 After filtering: {len(filtered)} messages ({len(all_messages) - len(filtered)} excluded)")
        
        # Deduplicate
        deduplicated = self._deduplicate_messages(filtered)
        logger.info(f"🔄 After deduplication: {len(deduplicated)} messages ({len(filtered) - len(deduplicated)} duplicates)")
        
        # Enrich messages with missing thread_ts metadata
        enriched = await self._enrich_message_thread_metadata(deduplicated)
        logger.info(f"🔗 Thread metadata enrichment complete")
        
        return enriched
    
    async def _search_messages(
        self,
        query: str,
        date_range: Dict[str, datetime]
    ) -> List[Dict[str, Any]]:
        """
        Search messages using Slack API with accurate date filtering
        
        Args:
            query: Search query
            date_range: Date range for search (must include 'start', 'end', 'target_date_str')
            
        Returns:
            List of messages within the exact datetime range
        """
        url = f"{self.config.base_url}/search.messages"
        headers = {
            "Authorization": f"Bearer {self.config.user_token}",
            "Content-Type": "application/json"
        }
        
        # Use 'on:' parameter for exact date matching
        # This ensures we only get messages from the specific date
        target_date_str = date_range.get("target_date_str")
        
        # Build query with exact date
        full_query = f"{query} on:{target_date_str}"
        
        params = {
            "query": full_query,
            "sort": "timestamp",
            "sort_dir": "desc",
            "count": 100
        }
        
        logger.debug(f"Search query: {full_query}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                data = await response.json()
                
                if not data.get("ok"):
                    error = data.get("error", "Unknown error")
                    logger.warning(f"Search API error for query '{query}': {error}")
                    logger.debug(f"Full response: {data}")
                    return []
                
                matches = data.get("messages", {}).get("matches", [])
                total = data.get("messages", {}).get("total", 0)
                logger.debug(f"Query '{query}': {len(matches)}/{total} messages (before timestamp filtering)")
                
                # Additional timestamp filtering to ensure exact date range
                # Filter messages to only include those within start and end datetime
                start_ts = date_range["start"].timestamp()
                end_ts = date_range["end"].timestamp()
                
                filtered_matches = []
                for msg in matches:
                    msg_ts = float(msg.get("ts", "0"))
                    if start_ts <= msg_ts <= end_ts:
                        filtered_matches.append(msg)
                    else:
                        logger.debug(f"Filtered out message with ts={msg_ts} (outside range {start_ts}-{end_ts})")
                
                logger.debug(f"Query '{query}': {len(filtered_matches)}/{len(matches)} messages after timestamp filtering")
                
                return filtered_matches
    
    def _filter_excluded_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter out DMs, excluded channels, and morning meeting messages
        
        This method processes all collected messages and removes:
        1. Direct messages (DMs)
        2. Messages from excluded channels
        3. Messages containing morning meeting patterns
        
        Args:
            messages: List of all collected messages
            
        Returns:
            List of filtered messages
        """
        filtered = []
        excluded_count = {
            "dm": 0,
            "channel": 0,
            "morning_meeting": 0
        }
        
        for msg in messages:
            channel_id = self._get_channel_id(msg)
            
            # Filter 1: Exclude DMs
            if channel_id.startswith("D") or channel_id.startswith("M"):
                excluded_count["dm"] += 1
                logger.debug(f"Excluded DM: {channel_id}")
                continue
            
            # Filter 2: Exclude specific channels
            if channel_id in EXCLUDED_CHANNELS_FROM_DIGEST:
                excluded_count["channel"] += 1
                logger.debug(f"Excluded channel: {channel_id} - Message: {msg.get('text', '')[:50]}")
                continue
            
            # Filter 3: Exclude morning meeting messages
            if self._is_morning_meeting_message(msg):
                excluded_count["morning_meeting"] += 1
                logger.debug(f"Excluded morning meeting in {channel_id}: {msg.get('text', '')[:50]}")
                continue
            
            filtered.append(msg)
        
        # Log exclusion statistics
        total_excluded = sum(excluded_count.values())
        logger.info(f"📊 Exclusion breakdown: DMs={excluded_count['dm']}, "
                   f"Excluded channels={excluded_count['channel']}, "
                   f"Morning meetings={excluded_count['morning_meeting']}, "
                   f"Total excluded={total_excluded}")
        
        return filtered
    
    def _is_morning_meeting_message(self, message: Dict[str, Any]) -> bool:
        """
        Check if message contains morning meeting patterns
        
        Args:
            message: Message dictionary
            
        Returns:
            True if message matches any morning meeting pattern
        """
        text = message.get("text", "")
        
        # Check each exclusion pattern
        for pattern in MORNING_MEETING_EXCLUSION_PATTERNS:
            if pattern in text:
                logger.debug(f"Matched pattern '{pattern}' in text: {text[:100]}")
                return True
        
        return False
    
    def _deduplicate_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate messages based on channel-ts-user key"""
        seen: Set[str] = set()
        deduplicated = []
        
        for msg in messages:
            channel_id = self._get_channel_id(msg)
            ts = msg.get("ts", "")
            user = msg.get("user", "unknown")
            
            key = f"{channel_id}-{ts}-{user}"
            
            if key not in seen:
                seen.add(key)
                deduplicated.append(msg)
        
        return deduplicated
    
    async def _enrich_message_thread_metadata(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich messages with missing thread_ts by extracting from permalink
        
        The Slack search.messages API doesn't return thread_ts field directly,
        but the permalink URL contains the thread_ts parameter if the message is part of a thread.
        This method extracts thread_ts from permalink when available.
        
        Args:
            messages: List of messages from search.messages API
            
        Returns:
            List of messages with complete thread_ts metadata
        """
        enriched_count = 0
        
        for msg in messages:
            # Skip if already has thread_ts
            if msg.get("thread_ts"):
                continue
            
            # Extract thread_ts from permalink if available
            permalink = msg.get("permalink", "")
            if "?thread_ts=" in permalink or "&thread_ts=" in permalink:
                import re
                # Extract thread_ts parameter from URL
                # Format: ...?thread_ts=1234567890.123456 or ...&thread_ts=1234567890.123456
                match = re.search(r'[?&]thread_ts=([0-9]+\.[0-9]+)', permalink)
                if match:
                    thread_ts = match.group(1)
                    msg["thread_ts"] = thread_ts
                    enriched_count += 1
                    logger.debug(f"✅ Extracted thread_ts from permalink: {thread_ts}")
        
        if enriched_count > 0:
            logger.info(f"✅ Enriched {enriched_count} messages with thread_ts from permalink")
        else:
            logger.info("ℹ️ No messages needed thread_ts enrichment")
        
        return messages
    
    async def _format_messages_for_llm(self, messages: List[Dict[str, Any]]) -> str:
        """
        Format messages for LLM analysis with chronological thread grouping
        
        Messages are grouped by thread and sorted chronologically within each thread.
        The latest message in each thread is marked with [LATEST] to help LLM
        determine current status.
        
        Note: Thread links are generated from reply messages (which have thread_ts)
        rather than parent messages to ensure ?thread_ts= parameter is included.
        """
        
        # Resolve user names using shared cache
        user_ids = list(set(msg.get("user") for msg in messages if msg.get("user")))
        user_cache = await get_multiple_user_names(user_ids)
        
        # Group messages by thread
        threads: Dict[str, List[Dict[str, Any]]] = {}
        for msg in messages:
            # Thread key: use thread_ts if available, else use ts (for standalone messages)
            thread_key = msg.get("thread_ts") or msg.get("ts", "unknown")
            if thread_key not in threads:
                threads[thread_key] = []
            threads[thread_key].append(msg)
        
        # Sort each thread chronologically (oldest to newest)
        for thread_key in threads:
            threads[thread_key].sort(key=lambda m: float(m.get("ts", 0)))
        
        # Format threads
        formatted_threads = []
        
        for thread_key, thread_messages in threads.items():
            if not thread_messages:
                continue
            
            # Get first message preview for thread header
            first_msg = thread_messages[0]
            first_text = self._clean_slack_text(first_msg.get("text", ""))
            thread_preview = first_text[:50] + "..." if len(first_text) > 50 else first_text
            
            # Format thread header
            thread_lines = [f"{'=' * 60}"]
            thread_lines.append(f"🧵 Thread: {thread_preview}")
            thread_lines.append(f"{'=' * 60}")
            
            # Format each message in thread
            for idx, msg in enumerate(thread_messages):
                user_id = msg.get("user", "Unknown")
                user_name = user_cache.get(user_id, user_id)
                channel_id = self._get_channel_id(msg)
                text = self._clean_slack_text(msg.get("text", ""))
                ts = msg.get("ts", "")
                
                if not text.strip():
                    continue
                
                # Format timestamp
                timestamp_str = self._format_timestamp(ts)
                
                # Mark latest message
                is_latest = (idx == len(thread_messages) - 1)
                latest_marker = " [LATEST]" if is_latest else ""
                
                # Format message
                thread_lines.append(
                    f"[{timestamp_str}]{latest_marker} {user_name} (ch: {channel_id}): {text}"
                )
            
            # Add thread link at the end
            # Use permalink directly - it already contains ?thread_ts= if it's a thread
            permalink = first_msg.get("permalink", "")
            if permalink:
                thread_lines.append(f"📎 Thread Link: {permalink}")
            thread_lines.append(f"{'=' * 60}")
            
            formatted_threads.append("\n".join(thread_lines))
        
        return "\n\n".join(formatted_threads)
    
    def _clean_slack_text(self, text: str) -> str:
        """Clean Slack markup from text"""
        # Remove user mentions
        cleaned = re.sub(r'<@U\w+\|([^>]+)>', r'@\1', text)
        cleaned = re.sub(r'<@U\w+>', '@user', cleaned)
        
        # Remove channel mentions
        cleaned = re.sub(r'<#C\w+\|([^>]+)>', r'#\1', cleaned)
        cleaned = re.sub(r'<#C\w+>', '#channel', cleaned)
        
        # Remove team mentions
        cleaned = re.sub(r'<!subteam\^S\w+>', '@team', cleaned)
        
        # Simplify URLs
        cleaned = re.sub(r'<(https?://[^|>]+)\|([^>]+)>', r'\2', cleaned)
        cleaned = re.sub(r'https?://[^\s]+', '[Link]', cleaned)
        
        # Remove emoji codes
        cleaned = re.sub(r':[\\w-]+:', '', cleaned)
        
        # Clean up whitespace
        cleaned = re.sub(r'\n+', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned.strip()
    
    def _format_timestamp(self, ts: str) -> str:
        """
        Convert Slack timestamp to readable format
        
        Args:
            ts: Slack timestamp (format: "1234567890.123456")
            
        Returns:
            Formatted timestamp string "YYYY-MM-DD HH:MM:SS"
        """
        try:
            timestamp = float(ts)
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to parse timestamp '{ts}': {e}")
            return "Unknown Time"
    
    def _get_channel_id(self, msg: Dict[str, Any]) -> str:
        """
        Extract channel ID from message
        
        Args:
            msg: Message dictionary
            
        Returns:
            Channel ID string
        """
        channel = msg.get("channel")
        
        # If channel is a dictionary
        if isinstance(channel, dict):
            return channel.get("id", "unknown")
        
        # If channel is a string (channel ID directly)
        if isinstance(channel, str):
            return channel
        
        return "unknown"
    
    def _calculate_date_range(self, date_str: Optional[str] = None) -> Dict[str, datetime]:
        """
        Calculate date range for digest (JST timezone)
        
        Args:
            date_str: Target date in YYYYMMDD format
            
        Returns:
            Dictionary with 'start', 'end', and 'target_date_str' for Slack search
        """
        if date_str:
            # Parse YYYYMMDD format
            target_date = datetime.strptime(date_str, "%Y%m%d")
        else:
            # Default to yesterday
            target_date = datetime.now() - timedelta(days=1)
        
        # Set time range: 00:00:00 to 23:59:59 (JST)
        start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Format target date for Slack API 'on:' parameter
        target_date_str = target_date.strftime("%Y-%m-%d")
        
        return {
            "start": start,
            "end": end,
            "target_date_str": target_date_str
        }
    
    def _format_japanese_date(self, date: datetime) -> str:
        """Format date in a neutral format that works across languages"""
        return date.strftime("%Y-%m-%d")
    
    def _generate_analysis_prompt(self, formatted_messages: str, date_str: str) -> str:
        """
        Generate LLM analysis prompt for wrap-up meeting digest
        
        Purpose: Create clear and concise daily summary for wrap-up meeting
        Focus: What was done today, what needs attention, what's next
        """
        return f"""You are a digest generator for the team's daily wrap-up meeting.
Analyze the Slack message history and return a **structured JSON** with clear, concise summaries.

## 📅 Target Date
{date_str}

## 📝 Collected Messages
{formatted_messages}

## 🌍 Language Detection & Output

**CRITICAL**: Detect the primary language of the collected messages and generate the digest in **THE SAME LANGUAGE**.

- If messages are primarily in **Japanese** → Generate digest in Japanese
- If messages are primarily in **Korean** → Generate digest in Korean  
- If messages are primarily in **English** → Generate digest in English
- For mixed languages → Use the most frequently used language

**All text in the JSON (titles, details, etc.) must be in the detected language.**

## 🎯 Analysis Guidelines for Wrap-up Meeting

**Purpose**: Provide a clear, concise summary of what happened today for the wrap-up meeting.
**Focus**: Completed work, critical issues, and actions needed.
**Avoid**: Duplication, redundancy, and overly detailed information.

### 🔍 Status Determination Rules (CRITICAL):

**How to Determine Task Status:**
1. **Always read thread messages chronologically** (oldest → newest, as formatted above)
2. **Status MUST be based on the [LATEST] marked message ONLY**
3. **Ignore status indicators in earlier messages** if superseded by later messages

**Status Keywords:**

✅ **Completed Indicators** (for completedItems):
- Japanese: "完了", "完了しました", "完了済み", "リリース済み", "デプロイ済み", "解決済み", "修正済み", "終了", "反映済み"
- English: "completed", "finished", "done", "released", "deployed", "resolved", "fixed", "closed", "merged"
- Korean: "완료", "완료했습니다", "해결됨", "배포됨", "수정됨", "종료"

❌ **NOT Completed Indicators** (must NOT go to completedItems):
- Japanese: "進行中", "予定", "進行予定", "作業中", "対応中", "調査中", "検討中", "実施予定", "予定です", "します", "する予定"
- English: "in progress", "planned", "working on", "investigating", "scheduled", "will do", "going to", "planning to"
- Korean: "진행중", "예정", "작업중", "조사중", "검토중", "할 예정"

⚠️ **Partial Completion is NOT Full Completion:**
- "一部完了" (partially completed) → NOT completedItems
- "50%完了" (50% completed) → NOT completedItems  
- "Phase 1 completed, Phase 2 in progress" → NOT completedItems
- "XXXは完了、YYYは進行中" (XXX completed, YYY in progress) → NOT completedItems

**Decision Flow:**
1. Locate the [LATEST] message in each thread
2. If [LATEST] message contains NOT completed indicators → DO NOT put in completedItems
3. If [LATEST] message contains completed indicators AND no in-progress indicators → May go to completedItems
4. If uncertain or mixed signals → Default to NOT completed

### 📚 Status Classification Examples:

**Example 1 - Completed:**
```
[2025-10-20 10:00:00] User: APIの開発を開始します
[2025-10-20 15:00:00] [LATEST] User: APIの開発が完了しました
```
→ completedItems ✅

**Example 2 - NOT Completed (in progress):**
```
[2025-10-20 10:00:00] User: APIの開発を開始します  
[2025-10-20 14:00:00] User: APIの一部が完了しました
[2025-10-20 16:00:00] [LATEST] User: 残りは進行中です
```
→ majorTopics or risksAndIssues ❌ (NOT completedItems)

**Example 3 - NOT Completed (planned):**
```
[2025-10-20 11:00:00] [LATEST] User: 明日デプロイ予定です
```
→ actionItems or majorTopics ❌ (NOT completedItems)

### Analysis Rules:

1. **Completed Items (completedItems)**: 
   - ONLY items where the [LATEST] message shows **full completion**
   - The [LATEST] message MUST contain completion indicators (完了, deployed, etc.)
   - The [LATEST] message must NOT contain in-progress indicators (進行中, 予定, etc.)
   - Include: deployments, bug fixes, feature completions, releases
   - **EXCLUDE**: Partial completions, items still in progress, planned items
   - **CRITICAL**: If [LATEST] message says "進行中", "予定", or similar → DO NOT add to completedItems
   - Must show clear completion status (e.g., "deployed", "fixed", "released")
   - **CRITICAL**: If an item is completed, it should ONLY appear in completedItems, NOT in any other section

2. **Major Topics (majorTopics)**:
   - Important discussions or decisions that need team awareness
   - New features or projects being discussed (not yet started)
   - Cross-team coordination matters
   - **Exclude**: Completed items (those go to completedItems only)

3. **Risks and Issues (risksAndIssues)**:
   - Active problems that need attention
   - Blockers or concerns that could impact work
   - Technical issues under investigation
   - **Exclude**: Issues that were resolved (those go to completedItems)

4. **Action Items (actionItems)**:
   - Clear next steps with assignees
   - Items pending response or approval
   - Must-do items before next meeting
   - **Exclude**: General discussions without clear action

5. **Maintenance Notifications (maintenanceNotifications)**:
   - Scheduled maintenance or system changes
   - Infrastructure updates team should be aware of

### Key Requirements:

- **NO DUPLICATION**: Each message should appear in ONLY ONE category
- **Thread Links**: 
  - **CRITICAL**: You MUST use the EXACT thread links provided in the "📎 Thread Link:" lines
  - **DO NOT modify, regenerate, or create new links**
  - **DO NOT remove the ?thread_ts= parameter if it exists**
  - Copy the complete URL exactly as provided, including all query parameters
  - Maximum 3 most recent links per item
- **Concise Details**: Keep details brief and actionable
- **Clear Assignment**: Always specify assignees when known
- **Priority Accuracy**: HIGH=urgent/critical, MEDIUM=important, LOW=informational

## 📋 Required JSON Structure

Return **ONLY** valid JSON in this exact structure:

```json
{{
  "date": "{date_str}",
  "majorTopics": [
    {{
      "priority": "HIGH|MEDIUM|LOW",
      "title": "Topic title (plain text, no markdown) in detected language",
      "assignees": ["@acn-user1", "@acn-user2"],
      "details": ["Brief detail 1 in detected language", "Brief detail 2 in detected language"],
      "threadLinks": ["URL1", "URL2", "URL3"]
    }}
  ],
  "completedItems": [
    {{
      "priority": "HIGH|MEDIUM|LOW",
      "title": "Completed item title in detected language",
      "assignees": ["@acn-user"],
      "details": ["What was completed in detected language"],
      "threadLinks": ["URL1", "URL2", "URL3"]
    }}
  ],
  "risksAndIssues": [
    {{
      "priority": "HIGH|MEDIUM|LOW",
      "title": "Issue title in detected language",
      "assignees": ["@acn-user"],
      "details": ["Issue description in detected language"],
      "threadLinks": ["URL1", "URL2", "URL3"]
    }}
  ],
  "actionItems": [
    {{
      "priority": "HIGH|MEDIUM|LOW",
      "title": "Action item title in detected language",
      "assignees": ["@acn-user"],
      "deadline": "Deadline if specified",
      "details": ["Action description in detected language"],
      "threadLinks": ["URL1", "URL2", "URL3"]
    }}
  ],
  "maintenanceNotifications": [
    {{
      "priority": "HIGH|MEDIUM|LOW",
      "title": "Maintenance title in detected language",
      "assignees": ["@acn-user"],
      "details": ["Maintenance description in detected language"],
      "threadLinks": ["URL1", "URL2", "URL3"]
    }}
  ]
}}
```

## ⚠️ Critical Rules

1. **LANGUAGE MATCHING**: All digest content MUST be in the same language as the input messages
2. **NO DUPLICATION**: Never put the same content in multiple sections
3. **Completed vs In-Progress**: Completed items ONLY go to completedItems
4. **EXACT LINK COPYING**: 
   - **CRITICAL**: Copy thread links EXACTLY as provided in "📎 Thread Link:" lines
   - Include ALL query parameters (especially ?thread_ts=)
   - DO NOT modify, shorten, or regenerate links
   - Maximum 3 links per item
5. **Concise**: Keep details brief and focused on key information
6. **JSON Only**: Return only valid JSON, no explanatory text before or after
7. **Empty Arrays**: Use `[]` for sections with no items

Start analysis. Return **complete JSON only** (no additional text)."""
    
    def _generate_error_prompt(self, error_message: str, date: Optional[str] = None) -> str:
        """Generate error prompt for LLM"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        date_str = self._format_japanese_date(
            datetime.strptime(date, "%Y%m%d") if date else datetime.now()
        )
        
        return f"""ダイジェスト生成中にエラーが発生しました。以下のJSON形式でエラーレポートを生成してください:

```json
{{
  "error": true,
  "date": "{date_str}",
  "timestamp": "{timestamp}",
  "errorMessage": "{error_message}",
  "cause": [
    "考えられる原因1",
    "考えられる原因2"
  ],
  "recommendations": [
    "推奨事項1",
    "推奨事項2"
  ]
}}
```

JSONのみを返してください。"""
    
    async def _post_message(
        self,
        channel: str,
        text: str,
        username: Optional[str] = None,
        icon_emoji: Optional[str] = None
    ) -> Dict[str, Any]:
        """Post message to Slack"""
        url = f"{self.config.base_url}/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {self.config.bot_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "channel": channel,
            "text": text
        }
        
        if username:
            payload["username"] = username
        if icon_emoji:
            payload["icon_emoji"] = icon_emoji
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                return await response.json()
