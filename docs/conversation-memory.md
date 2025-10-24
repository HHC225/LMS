# Conversation Memory Tool

## Overview

The Conversation Memory Tool provides persistent storage and semantic retrieval of important conversation context using ChromaDB vector database. This tool enables AI assistants to maintain context across conversations, remember important decisions, and build a queryable knowledge base.

## Key Features

- **Automatic Embedding**: ChromaDB automatically generates embeddings for semantic search
- **Speaker Tracking**: Track who said what in conversations
- **Metadata Support**: Store additional context like topics, importance, timestamps
- **Semantic Search**: Find relevant conversations based on meaning, not just keywords
- **Persistent Storage**: Conversations are saved to disk and survive server restarts

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  LLM/GitHub Copilot                                 │
│  (Provides conversation context)                    │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  Conversation Memory Tool                           │
│  • Store full conversations                         │
│  • Query conversations (semantic search)            │
│  • Track speakers and metadata                      │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  ChromaDB Vector Database                           │
│  • Stores complete conversation text                │
│  • Automatic embeddings for semantic search         │
│  • Persistent storage on disk                       │
└─────────────────────────────────────────────────────┘
```

**Storage Strategy:**
- **Full Text Storage**: Complete conversation content is always stored to prevent information loss
- **Optional Summaries**: Summaries can be provided and are stored in metadata for quick reference
- **Semantic Search**: Vector embeddings are generated from full text for accurate semantic search

## Available Tools

### 1. conversation_memory_store

Store important conversation content in the vector database.

**Parameters:**
- `conversation_text` (required): Full conversation content to store (always stores complete text to prevent information loss)
- `speaker` (optional): Name of the speaker (e.g., "User", "GitHub Copilot")
- `summary` (optional): LLM-generated summary of the conversation (stored in metadata for quick reference only)
- `metadata` (optional): Additional metadata as dict
- `conversation_id` (optional): Unique identifier (auto-generated if not provided)

**Returns:**
- `success`: Boolean indicating success
- `conversation_id`: Unique ID for the stored conversation
- `metadata`: Stored metadata including timestamp
- `document_length`: Length of stored document

**Example Usage:**

```python
# Store a conversation (full text is always stored)
result = await conversation_memory_store(
    conversation_text="User: How should I design the API?\nCopilot: For this use case, REST would be better than GraphQL because...",
    speaker="GitHub Copilot",
    summary="Discussion about API design: Recommended REST over GraphQL for simple CRUD operations.",
    metadata={
        "topic": "API design",
        "context": "architecture planning",
        "importance": "high"
    }
)
```

**Important Notes:**
1. **Full text storage**: The complete `conversation_text` is always stored in the database to prevent information loss
2. **Summary as metadata**: If provided, the `summary` is stored in metadata for quick reference but does NOT replace the full text
3. **Semantic search**: ChromaDB's vector search works on the full conversation text, ensuring all information is searchable

**Best Practices:**
1. **Store complete conversations**: Don't worry about length - full context is preserved
2. **Include speaker info**: Track who provided the information
3. **Add meaningful metadata**: Use consistent keys like "topic", "context", "importance"
4. **Optional summaries**: Provide summaries for quick reference in metadata, but the full text is always available
5. **Store key decisions**: Focus on important information, not every message

### 2. conversation_memory_query

Query stored conversations using semantic search.

**Parameters:**
- `query_text` (required): Text to search for (semantic similarity)
- `n_results` (optional): Number of results to return (default: 5)
- `filter_metadata` (optional): Metadata filters as dict

**Returns:**
- `success`: Boolean indicating success
- `query`: Original query text
- `results`: Array of matching conversations with:
  - `id`: Conversation ID
  - `document`: Stored content/summary
  - `metadata`: Associated metadata
  - `distance`: Similarity score (lower = more similar)
- `count`: Number of results returned

**Example Usage:**

```python
# Find conversations about database design
result = await conversation_memory_query(
    query_text="How should I structure the database schema?",
    n_results=3,
    filter_metadata={"topic": "database"}
)

# Access results
for item in result["results"]:
    print(f"ID: {item['id']}")
    print(f"Content: {item['document']}")
    print(f"Speaker: {item['metadata'].get('speaker')}")
    print(f"Similarity: {item['distance']}")
```

**Search Tips:**
- Semantic search finds meaning, not exact words
- Use natural language queries
- Filter by metadata to narrow results
- Lower distance scores mean better matches

### 3. conversation_memory_list

List all stored conversation memories.

**Parameters:**
- `limit` (optional): Maximum number of conversations to return
- `offset` (optional): Number of conversations to skip (default: 0)

**Returns:**
- `success`: Boolean indicating success
- `conversations`: Array of all stored conversations
- `count`: Number of conversations returned
- `total_in_db`: Total conversations in database

**Example Usage:**

```python
# List first 10 conversations
result = await conversation_memory_list(limit=10)

# List all conversations
result = await conversation_memory_list()

# Pagination
result = await conversation_memory_list(limit=10, offset=20)
```

### 4. conversation_memory_get

Get a specific conversation by ID.

**Parameters:**
- `conversation_id` (required): ID of the conversation to retrieve

**Returns:**
- `success`: Boolean indicating success
- `conversation`: Object containing:
  - `id`: Conversation ID
  - `document`: Stored content/summary
  - `metadata`: Associated metadata

**Example Usage:**

```python
# Retrieve a specific conversation
result = await conversation_memory_get(
    conversation_id="conv_20241014_123456_789012"
)

if result["success"]:
    conv = result["conversation"]
    print(f"Content: {conv['document']}")
    print(f"Metadata: {conv['metadata']}")
```

**Use Cases:**
- Review existing conversation before updating
- Verify conversation content
- Check metadata of specific entry

### 5. conversation_memory_update

Update an existing conversation in the database.

**Parameters:**
- `conversation_id` (required): ID of the conversation to update
- `conversation_text` (optional): New conversation content
- `speaker` (optional): New speaker name
- `summary` (optional): New summary
- `metadata` (optional): New metadata dict
- `merge_metadata` (optional): If True, merge with existing metadata; if False, replace completely (default: True)

**Returns:**
- `success`: Boolean indicating success
- `conversation_id`: ID of updated conversation
- `message`: Confirmation message
- `metadata`: Updated metadata
- `document_length`: Length of updated document
- `was_merged`: Boolean indicating if metadata was merged

**Example Usage:**

```python
# Example 1: Update conversation text (summary stored in metadata if provided)
result = await conversation_memory_update(
    conversation_id="conv_20241014_123456_789012",
    conversation_text="Updated discussion about API design... [full updated conversation text here]",
    summary="Revised decision: Using GraphQL instead of REST for better flexibility",  # Stored in metadata
    merge_metadata=True
)

# Example 2: Add new metadata while keeping existing
result = await conversation_memory_update(
    conversation_id="conv_20241014_123456_789012",
    metadata={
        "status": "resolved",
        "reviewed_by": "team_lead"
    },
    merge_metadata=True  # Keeps existing metadata, adds/updates these fields
)

# Example 3: Replace all metadata
result = await conversation_memory_update(
    conversation_id="conv_20241014_123456_789012",
    metadata={
        "topic": "new_topic",
        "importance": "low"
    },
    merge_metadata=False  # Removes all existing metadata, replaces with new
)

# Example 4: Update text only (keeps metadata unchanged)
result = await conversation_memory_update(
    conversation_id="conv_20241014_123456_789012",
    conversation_text="Additional information added to the conversation...",
    # metadata not provided, so existing metadata is preserved
)
```

**Update Workflow:**

```python
# 1. Get existing conversation
get_result = await conversation_memory_get(
    conversation_id="conv_20241014_123456_789012"
)

# 2. Review and modify
existing_text = get_result["conversation"]["document"]
updated_text = existing_text + "\n\nAdditional notes: ..."

# 3. Update with changes
update_result = await conversation_memory_update(
    conversation_id="conv_20241014_123456_789012",
    conversation_text=updated_text,
    metadata={"last_updated": "2024-10-14", "status": "revised"},
    merge_metadata=True
)
```

**Automatic Metadata Updates:**

When updating a conversation, these fields are automatically set:
- `timestamp`: Updated to current time (ISO 8601 format)
- `updated`: Set to `True`
- `has_summary`: Set to `True` if summary is provided
- `summary`: The summary text (stored in metadata for quick reference)
- `character_count`: Updated if conversation_text is provided

**Note**: The full `conversation_text` is always stored as the main document, while `summary` (if provided) is stored in metadata for convenience.

**Use Cases:**
- Append new information to existing conversation
- Correct mistakes in stored content
- Update conversation status or metadata
- Mark conversations as resolved/in-progress
- Add review or approval information

### 6. conversation_memory_delete

Delete a specific conversation from the database.

**Parameters:**
- `conversation_id` (required): ID of the conversation to delete

**Returns:**
- `success`: Boolean indicating success
- `message`: Confirmation message

**Example Usage:**

```python
result = await conversation_memory_delete(
    conversation_id="conv_20241014_123456_789012"
)
```

### 7. conversation_memory_clear

Clear all conversations from the database.

**⚠️ WARNING**: This permanently deletes all stored conversation memories.

**Returns:**
- `success`: Boolean indicating success
- `message`: Confirmation message with count of deleted items

**Example Usage:**

```python
# Clear all conversations (use with caution!)
result = await conversation_memory_clear()
```

## Workflow Examples

### Example 1: Building Context During Development

```python
# Session 1: API Design Discussion
await conversation_memory_store(
    conversation_text="Full conversation about API endpoints...",
    speaker="GitHub Copilot",
    summary="Designed REST API with 5 endpoints: users, posts, comments, auth, and profile. Using JWT for authentication.",
    metadata={"topic": "API design", "phase": "planning"}
)

# Session 2: Later, Query Context
result = await conversation_memory_query(
    query_text="What authentication method did we decide to use?"
)
# Returns: Previous conversation about JWT authentication
```

### Example 2: Decision Tracking

```python
# Store important decisions
await conversation_memory_store(
    conversation_text="...",
    speaker="User",
    summary="Decision: Use PostgreSQL instead of MongoDB due to complex relationships and ACID requirements.",
    metadata={
        "topic": "database",
        "type": "decision",
        "importance": "high"
    }
)

# Later, find all decisions
result = await conversation_memory_query(
    query_text="database decisions",
    filter_metadata={"type": "decision"}
)
```

### Example 3: Knowledge Base Building

```python
# Store best practices
await conversation_memory_store(
    conversation_text="...",
    speaker="GitHub Copilot",
    summary="Best practice: Always validate input at API boundary, use DTOs for data transfer, and handle errors with consistent error codes.",
    metadata={
        "category": "best-practices",
        "topic": "API development"
    }
)

# Retrieve relevant best practices when needed
result = await conversation_memory_query(
    query_text="API input validation best practices",
    filter_metadata={"category": "best-practices"}
)
```

### Example 4: Updating Decisions

```python
# Initial decision stored
store_result = await conversation_memory_store(
    conversation_text="Discussion about database choice...",
    speaker="Team",
    summary="Decision: Use MongoDB for flexible schema",
    metadata={"topic": "database", "status": "decided"}
)

# Later, requirements change - update the decision
conv_id = store_result["conversation_id"]

# Get current content to review
get_result = await conversation_memory_get(conversation_id=conv_id)
print(f"Current: {get_result['conversation']['document']}")

# Update with new decision
await conversation_memory_update(
    conversation_id=conv_id,
    conversation_text="Discussion about database choice... [Updated] After review, switching to PostgreSQL due to complex relationships.",
    summary="Decision (Updated): Use PostgreSQL for relational data integrity and complex joins",
    metadata={
        "status": "updated",
        "updated_reason": "requirements_change",
        "previous_decision": "MongoDB"
    },
    merge_metadata=True  # Keeps original topic and adds new fields
)
```

### Example 5: Progressive Information Gathering

```python
# Day 1: Initial information
result = await conversation_memory_store(
    conversation_text="Research on caching strategies...",
    speaker="Developer",
    summary="Researched Redis and Memcached options",
    metadata={"topic": "caching", "phase": "research", "completeness": "partial"}
)
conv_id = result["conversation_id"]

# Day 2: Add findings
get_result = await conversation_memory_get(conversation_id=conv_id)
existing_text = get_result["conversation"]["document"]

await conversation_memory_update(
    conversation_id=conv_id,
    conversation_text=existing_text + "\n\n[Day 2] Performance test results: Redis outperforms Memcached by 20% in our use case.",
    metadata={"completeness": "in-progress", "test_date": "2024-10-15"},
    merge_metadata=True
)

# Day 3: Final decision
get_result = await conversation_memory_get(conversation_id=conv_id)
final_text = get_result["conversation"]["document"] + "\n\n[Day 3] Final decision: Implementing Redis with cluster mode."

await conversation_memory_update(
    conversation_id=conv_id,
    conversation_text=final_text,
    summary="Caching research and decision: Selected Redis with cluster mode after testing showed 20% better performance",
    metadata={"completeness": "complete", "status": "implemented"},
    merge_metadata=True
)
```

## Configuration

In `config.py` or `.env` file:

```python
# Enable/disable conversation memory tools
ENABLE_CONVERSATION_MEMORY_TOOLS=true

# Database storage path
CONVERSATION_MEMORY_DB_PATH=./chroma_db

# Default number of query results
CONVERSATION_MEMORY_DEFAULT_RESULTS=5
```

## Technical Details

### Storage Location

Conversations are stored in the ChromaDB database at:
- Default: `./chroma_db` (relative to server root)
- Configurable via `CONVERSATION_MEMORY_DB_PATH`

### Embedding Model

ChromaDB uses its default embedding model (`all-MiniLM-L6-v2`) which:
- Generates 384-dimensional embeddings
- Supports semantic similarity search
- Works offline (no API calls needed)
- Fast and efficient for most use cases

### Metadata Schema

Automatically added metadata:
- `timestamp`: ISO format datetime
- `has_summary`: Boolean indicating if summary was provided
- `character_count`: Length of original conversation

User-provided metadata:
- `speaker`: Who provided the information
- `topic`, `context`, `importance`: Recommended fields
- Any custom fields you define

## Best Practices

### 1. Summarization Strategy

**Let the LLM summarize before storing:**

```
Good prompt to LLM:
"Please summarize our conversation about database design in 2-3 sentences, 
focusing on the key decisions and recommendations."

Then store the summary with conversation_memory_store.
```

### 2. Consistent Speaker Names

Use consistent speaker identifiers:
- ✅ "User", "GitHub Copilot", "Assistant"
- ❌ "user", "Me", "Copilot", "AI"

### 3. Metadata Organization

Use consistent metadata keys:

```python
# Recommended metadata structure
metadata = {
    "topic": "category name",           # Main topic
    "context": "specific situation",    # Specific context
    "type": "decision|discussion|info", # Type of conversation
    "importance": "low|medium|high",    # Importance level
    "phase": "planning|development",    # Project phase
}
```

### 4. Query Optimization

- **Use natural language**: "How should I handle errors?" vs "error handling"
- **Be specific**: Include context in queries
- **Use filters**: Narrow results with metadata filters
- **Adjust n_results**: Start with 3-5, increase if needed

### 5. Maintenance

Periodically review and clean up:
- Delete outdated conversations
- Update important conversations if decisions change
- Archive old project contexts before starting new projects

**Update vs Delete-and-Recreate:**

✅ **Use update when:**
- Adding information to existing conversation
- Correcting mistakes
- Updating status/metadata
- Preserving conversation history and ID

❌ **Avoid delete-and-recreate when:**
- Other parts of your system reference the conversation_id
- You want to maintain conversation history
- Only partial updates are needed

**Example: Update instead of delete-recreate**

```python
# ❌ Old approach: Delete and recreate
await conversation_memory_delete(conversation_id=old_id)
await conversation_memory_store(
    conversation_text=new_text,
    speaker=speaker,
    ...
)  # This creates a NEW conversation_id!

# ✅ Better approach: Update existing
await conversation_memory_update(
    conversation_id=old_id,  # Same ID preserved
    conversation_text=new_text,
    merge_metadata=True  # Keeps existing metadata
)
```

### 6. Metadata Merging Strategy

Choose the right merge strategy:

```python
# Strategy 1: Merge (default) - Add/update specific fields
await conversation_memory_update(
    conversation_id=conv_id,
    metadata={"status": "resolved", "reviewer": "John"},
    merge_metadata=True  # Keeps all other existing metadata
)

# Strategy 2: Replace - Complete metadata overwrite
await conversation_memory_update(
    conversation_id=conv_id,
    metadata={"topic": "new_topic", "importance": "low"},
    merge_metadata=False  # Removes all previous metadata
)

# Strategy 3: Selective field updates - Update only specific fields
get_result = await conversation_memory_get(conversation_id=conv_id)
current_meta = get_result["conversation"]["metadata"]
current_meta["status"] = "in_progress"  # Modify specific field
current_meta["updated_by"] = "Alice"   # Add new field

await conversation_memory_update(
    conversation_id=conv_id,
    metadata=current_meta,
    merge_metadata=False  # Use modified metadata
)
```

## Common Use Cases

### 1. Context Retention
Store and retrieve context across multiple conversation sessions.

### 2. Decision Log with Updates
Maintain a searchable log of important technical decisions that can be updated when requirements change.

```python
# Initial decision
result = await conversation_memory_store(...)
decision_id = result["conversation_id"]

# Later update when decision changes
await conversation_memory_update(
    conversation_id=decision_id,
    summary="Updated decision: ...",
    metadata={"status": "revised", "revision_date": "2024-10-15"}
)
```

### 3. Knowledge Base
Build a project-specific knowledge base of patterns and solutions.

### 4. Best Practices Library
Store and query best practices and recommendations.

### 5. Architecture Documentation
Track architectural decisions and their rationale.

### 6. Progressive Documentation
Build documentation incrementally by updating conversations as more information becomes available.

```python
# Start with initial notes
result = await conversation_memory_store(
    summary="Initial API design notes",
    metadata={"completeness": "draft"}
)

# Add details over time
await conversation_memory_update(
    conversation_id=result["conversation_id"],
    summary="Complete API design with authentication flow",
    metadata={"completeness": "final", "reviewed": True},
    merge_metadata=True
)
```

### 7. Status Tracking
Track the status of conversations and decisions over time.

```python
# Mark as in-progress
await conversation_memory_update(
    conversation_id=conv_id,
    metadata={"status": "in_progress", "assignee": "John"},
    merge_metadata=True
)

# Later mark as complete
await conversation_memory_update(
    conversation_id=conv_id,
    metadata={"status": "completed", "completion_date": "2024-10-15"},
    merge_metadata=True
)
```

## Troubleshooting

### Database Location Issues

```python
# Check database path
import os
print(os.path.abspath("./chroma_db"))

# Use absolute path in config
CONVERSATION_MEMORY_DB_PATH="/absolute/path/to/chroma_db"
```

### Query Returns No Results

1. Verify conversations are stored: Use `conversation_memory_list()`
2. Try broader queries: Use more general language
3. Check metadata filters: Remove or adjust filters
4. Increase n_results: Try higher numbers

### Storage Fails

1. Check disk space
2. Verify write permissions
3. Check database path exists
4. Review logs for errors

## API Reference

See inline documentation in tool definitions for complete parameter details and return types.

## Related Tools

- **Recursive Thinking**: Use conversation memory to inform deep analysis
- **Sequential Thinking**: Reference past conversations in thought process
- **Tree of Thoughts**: Store exploration paths and decisions

## Limits and Considerations

- **Storage**: ChromaDB stores embeddings on disk; consider disk space for large deployments
- **Search Speed**: Query performance is excellent for up to 100K conversations
- **Embedding Model**: Default model is good for English; consider custom models for other languages
- **Context Length**: Store summaries for long conversations to improve relevance

---

**Next Steps:**
- [Troubleshooting Guide](troubleshooting.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Back to Main README](../README.md)
