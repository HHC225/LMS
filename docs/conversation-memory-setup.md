# Conversation Memory Tool - Setup Guide

## Quick Setup

### 1. Install ChromaDB

ChromaDB is already included in the `requirements.txt` file. If you followed the main installation guide, it's already installed.

To install manually or update to latest version:

```bash
cd /Users/username/Desktop/MCP/Local_MCP_Server
uv pip install chromadb
```

### 2. Verify Installation

```bash
python3 -c "import chromadb; print(f'ChromaDB version: {chromadb.__version__}')"
```

Expected output:
```
ChromaDB version: 1.1.1
```

### 3. Configure Environment (Optional)

Create or edit `.env` file:

```bash
# Enable Conversation Memory Tools
ENABLE_CONVERSATION_MEMORY_TOOLS=true

# Database storage path (default: ./chroma_db)
CONVERSATION_MEMORY_DB_PATH=./chroma_db

# Default number of query results (default: 5)
CONVERSATION_MEMORY_DEFAULT_RESULTS=5
```

### 4. Start the Server

```bash
python3 main.py
```

You should see:
```
INFO: Registering Conversation Memory tools...
INFO: Conversation Memory tools registered successfully
```

### 5. Test the Tool

Use your MCP client (Claude Desktop, VSCode Copilot, etc.) to test:

```python
# Store a conversation
await conversation_memory_store(
    conversation_text="Discussed API design patterns for RESTful services",
    speaker="GitHub Copilot",
    summary="Recommended REST over GraphQL for simple CRUD operations",
    metadata={"topic": "API design"}
)

# Query stored conversations
result = await conversation_memory_query(
    query_text="What did we discuss about API design?",
    n_results=3
)

print(result)
```

## Available Tools

The Conversation Memory Tool provides 7 operations:

| Tool | Purpose | Example Use Case |
|------|---------|------------------|
| `conversation_memory_store` | Save new conversation | Store initial decision or discussion |
| `conversation_memory_query` | Semantic search | Find past conversations by meaning |
| `conversation_memory_list` | Browse all conversations | Review stored entries |
| `conversation_memory_get` | Retrieve by ID | Get specific conversation for review |
| `conversation_memory_update` | Modify existing entry | Update decisions, add info, fix mistakes |
| `conversation_memory_delete` | Remove single entry | Clean up specific conversation |
| `conversation_memory_clear` | Remove all entries | Reset database (use with caution) |

**Key Features:**
- ✅ **Automatic embeddings** - No manual embedding required
- 🔍 **Semantic search** - Find by meaning, not just keywords
- 🔄 **Update support** - Modify conversations without losing ID
- 📊 **Metadata filtering** - Combine search with filters
- 💾 **Persistent storage** - Data survives server restarts

## File Structure

After setup, your project structure will include:

```
Local_MCP_Server/
├── tools/
│   ├── memory/                          # NEW: Memory tools directory
│   │   ├── __init__.py
│   │   └── conversation_memory_tool.py  # Conversation Memory implementation
│   └── reasoning/
│       ├── recursive_thinking_tool.py
│       ├── sequential_thinking_tool.py
│       └── tree_of_thoughts_tool.py
├── chroma_db/                           # NEW: ChromaDB storage (auto-created)
│   ├── chroma.sqlite3                   # Vector database
│   └── ...
├── requirements.txt                      # Updated with chromadb
├── main.py                              # Server with Conversation Memory tools
└── config.py                            # Configuration settings
```

## Database Location

By default, the ChromaDB database is stored at:
```
./chroma_db/
```

This directory contains:
- `chroma.sqlite3`: SQLite database for metadata
- Collection data and embeddings
- Automatic persistence (survives server restarts)

**Important**: The `chroma_db/` directory is added to `.gitignore` to prevent committing database files.

## Storage Requirements

- **Typical usage**: ~10-50MB per 1000 conversations
- **Embedding size**: 384 dimensions per document
- **Recommended**: 1GB+ free disk space for production use

## How It Works

### 1. Automatic Embedding

ChromaDB automatically generates embeddings using the default model:
- Model: `all-MiniLM-L6-v2` (sentence-transformers)
- Dimensions: 384
- Language: Optimized for English
- Speed: Fast, runs locally (no API calls)

```python
# No manual embedding needed!
await conversation_memory_store(
    conversation_text="Your text here",
    summary="Summary here"
)
# ChromaDB automatically creates embeddings
```

### 2. Semantic Search

Search by meaning, not just keywords:

```python
# Query: "database design"
# Will find conversations about:
# - "schema planning"
# - "SQL structure"
# - "data modeling"
# Even if exact words don't match!
```

### 3. Metadata Filtering

Combine semantic search with filters:

```python
await conversation_memory_query(
    query_text="API patterns",
    filter_metadata={"speaker": "GitHub Copilot"}
)
# Returns only conversations from GitHub Copilot about API patterns
```

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_CONVERSATION_MEMORY_TOOLS` | `true` | Enable/disable the tool |
| `CONVERSATION_MEMORY_DB_PATH` | `./chroma_db` | Database storage location |
| `CONVERSATION_MEMORY_DEFAULT_RESULTS` | `5` | Default query result count |

### Custom Database Path

Use absolute path for shared database:

```bash
# .env file
CONVERSATION_MEMORY_DB_PATH=/Users/username/shared/conversations_db
```

Or relative to project:

```bash
# .env file
CONVERSATION_MEMORY_DB_PATH=./data/chroma_db
```

## Usage Examples

### Example 1: Store Important Decision

```python
result = await conversation_memory_store(
    conversation_text="""
    User: Should we use PostgreSQL or MongoDB?
    Copilot: For this project, I recommend PostgreSQL because:
    1. Complex relationships between users, orders, and products
    2. ACID compliance needed for financial transactions
    3. Strong ecosystem and tooling
    """,
    speaker="GitHub Copilot",
    summary="Decision: Use PostgreSQL for complex relationships and ACID requirements",
    metadata={
        "topic": "database",
        "type": "decision",
        "importance": "high",
        "date": "2025-10-14"
    }
)

print(f"Stored with ID: {result['conversation_id']}")
```

### Example 2: Query Past Decisions

```python
# Find database-related decisions
result = await conversation_memory_query(
    query_text="What database did we choose?",
    n_results=3,
    filter_metadata={"type": "decision", "topic": "database"}
)

for item in result['results']:
    print(f"ID: {item['id']}")
    print(f"Content: {item['document']}")
    print(f"Speaker: {item['metadata'].get('speaker')}")
    print(f"Date: {item['metadata'].get('date')}")
    print("---")
```

### Example 3: List All Conversations

```python
# Get all stored conversations
result = await conversation_memory_list(limit=10)

print(f"Total conversations: {result['total_in_db']}")
print(f"Showing: {result['count']}")

for conv in result['conversations']:
    print(f"- {conv['id']}: {conv['document'][:100]}...")
```

### Example 4: Update Existing Conversation

```python
# Store initial decision
result = await conversation_memory_store(
    conversation_text="Initial API design discussion...",
    speaker="Team",
    summary="Decision: Use REST API",
    metadata={"topic": "API", "status": "decided"}
)
conv_id = result["conversation_id"]

# Later, retrieve and review
get_result = await conversation_memory_get(conversation_id=conv_id)
print(f"Current: {get_result['conversation']['document']}")

# Update when requirements change
await conversation_memory_update(
    conversation_id=conv_id,
    conversation_text="Initial API design discussion... [Updated] Switched to GraphQL for better flexibility",
    summary="Decision (Updated): Use GraphQL API for flexible querying",
    metadata={"status": "revised", "revision_date": "2025-10-15"},
    merge_metadata=True  # Keeps existing metadata, adds new fields
)

print("Conversation updated successfully!")
```

### Example 5: Progressive Documentation

```python
# Day 1: Start documentation
result = await conversation_memory_store(
    conversation_text="Research on authentication methods...",
    summary="Initial research: JWT vs OAuth comparison",
    metadata={"completeness": "draft", "version": "1.0"}
)
doc_id = result["conversation_id"]

# Day 2: Add test results
get_result = await conversation_memory_get(conversation_id=doc_id)
existing = get_result["conversation"]["document"]

await conversation_memory_update(
    conversation_id=doc_id,
    conversation_text=existing + "\n\n[Day 2] Performance tests completed. JWT shows 15% better performance.",
    metadata={"completeness": "in-progress", "version": "1.1"},
    merge_metadata=True
)

# Day 3: Finalize
get_result = await conversation_memory_get(conversation_id=doc_id)
final = get_result["conversation"]["document"] + "\n\n[Day 3] Final decision: Implementing JWT"

await conversation_memory_update(
    conversation_id=doc_id,
    conversation_text=final,
    summary="Complete authentication research and decision: JWT selected for performance and simplicity",
    metadata={"completeness": "final", "version": "2.0", "implemented": True},
    merge_metadata=True
)
```

### Example 6: Clean Up Old Conversations

```python
# Delete specific conversation
await conversation_memory_delete(
    conversation_id="conv_20241014_123456_789012"
)

# Or clear all (use carefully!)
# result = await conversation_memory_clear()
```

## Best Practices

### 1. Summarization Strategy

**Always let the LLM summarize before storing:**

❌ **Bad**: Store raw conversation
```python
conversation_text = "User: hi\nCopilot: hello\nUser: how are you\n..."
# Too much noise, poor search results
```

✅ **Good**: Store LLM-generated summary
```python
summary = "Discussed API authentication methods. Decided on JWT with 24-hour expiration."
# Clear, concise, searchable
```

### 2. Consistent Metadata

Use consistent keys across all conversations:

```python
# Recommended metadata structure
metadata = {
    "speaker": "GitHub Copilot" | "User" | "Assistant",
    "topic": "api" | "database" | "testing" | etc.,
    "type": "decision" | "discussion" | "question" | "answer",
    "importance": "low" | "medium" | "high",
    "project": "project_name",
    "phase": "planning" | "development" | "testing"
}
```

### 3. Regular Maintenance

```python
# Weekly: Review and clean up
result = await conversation_memory_list()

# Monthly: Archive old projects
# (manually backup chroma_db/, then clear)
```

### 4. Update vs Delete-Recreate

**Always prefer update over delete-recreate:**

❌ **Bad**: Delete and create new (loses conversation ID)
```python
await conversation_memory_delete(conversation_id=old_id)
result = await conversation_memory_store(
    conversation_text=new_text,
    ...
)
# Problem: New ID created, references broken!
```

✅ **Good**: Update existing (preserves ID)
```python
await conversation_memory_update(
    conversation_id=old_id,
    conversation_text=new_text,
    merge_metadata=True
)
# Same ID maintained, references preserved
```

### 5. Metadata Merge Strategy

**Choose the right merge strategy for your use case:**

```python
# Merge (default): Add/update specific fields
await conversation_memory_update(
    conversation_id=conv_id,
    metadata={"status": "resolved"},
    merge_metadata=True  # Keeps all other metadata
)

# Replace: Complete metadata overwrite
await conversation_memory_update(
    conversation_id=conv_id,
    metadata={"topic": "new_topic"},
    merge_metadata=False  # Removes all previous metadata
)
```

## Troubleshooting

### Issue: "Import chromadb failed"

**Solution**: Install ChromaDB
```bash
uv pip install chromadb
```

### Issue: "Permission denied" writing to database

**Solution**: Check directory permissions
```bash
chmod 755 ./chroma_db
```

Or use different path:
```bash
CONVERSATION_MEMORY_DB_PATH=~/conversations_db
```

### Issue: "No results found" when querying

**Checklist**:
1. Verify conversations are stored:
   ```python
   result = await conversation_memory_list()
   print(result['total_in_db'])
   ```

2. Try broader query:
   ```python
   # Instead of: "PostgreSQL schema design"
   # Try: "database design"
   ```

3. Remove metadata filters:
   ```python
   # Remove filter_metadata parameter temporarily
   ```

4. Increase results:
   ```python
   result = await conversation_memory_query(
       query_text="...",
       n_results=10  # Increase from 5
   )
   ```

### Issue: Database grows too large

**Solution**: Clear old conversations
```bash
# Backup first
cp -r chroma_db/ chroma_db_backup/

# Then clear in Python
await conversation_memory_clear()
```

### Issue: Slow query performance

**Tips**:
- Keep database under 100K conversations for best performance
- Use metadata filters to narrow search
- Store summaries instead of full conversations
- Consider periodic archiving

## Advanced Configuration

### Custom Embedding Model (Future)

ChromaDB supports custom embedding functions:

```python
# Example: Using OpenAI embeddings (requires API key)
from chromadb.utils import embedding_functions

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key="your-api-key",
    model_name="text-embedding-ada-002"
)

# Then configure in conversation_memory_tool.py
# (requires code modification)
```

### Multiple Collections

For advanced use cases, modify `conversation_memory_tool.py` to support multiple collections:

```python
# Example: Separate collections per project
collection_name = f"conversations_{project_name}"
```

## Next Steps

1. **Read the full documentation**: [conversation-memory.md](conversation-memory.md)
2. **Try the examples**: Test storing, querying, and updating conversations
3. **Integrate with workflow**: Use in your daily development process
4. **Customize metadata**: Define your own metadata schema
5. **Practice updates**: Learn when to use merge vs replace strategies

## Common Workflows

### Workflow 1: Decision Tracking with Updates

```
1. Store initial decision → Get conversation_id
2. Implement based on decision
3. If requirements change → Update conversation with new decision
4. Query to see decision history
```

### Workflow 2: Progressive Documentation

```
1. Store draft notes → conversation_id saved
2. Day 2: Get conversation → Add findings → Update
3. Day 3: Get conversation → Add final decision → Update
4. Result: Complete documentation with history
```

### Workflow 3: Status Management

```
1. Store conversation with status="pending"
2. Update status="in-progress" when work starts
3. Update status="review" when ready
4. Update status="completed" when done
5. Query filter_metadata={"status": "completed"} to find finished items
```

## Support

- **Issues**: [GitHub Issues](https://github.com/HHC225/Thinking_Tools_Local/issues)
- **Documentation**: [docs/conversation-memory.md](conversation-memory.md)
- **Main README**: [README.md](../README.md)

---

**Ready to use!** Start storing important conversations and build your AI-powered knowledge base! 🚀
