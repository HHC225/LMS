# Local MCP Server

Advanced reasoning tools for AI assistants powered by Model Context Protocol (MCP). This server provides structured thinking methodologies for complex problem-solving.

## 📁 Project Structure

```
Local_MCP_Server/
├── main.py                # Server entry point & tool registration
├── requirements.txt       # Python dependencies
│
├── configs/              # Modular configuration system
│   ├── __init__.py       # Configuration loader
│   ├── base.py           # Server & common settings
│   ├── reasoning.py      # Recursive/Sequential/ToT/Verbalized Sampling configs
│   ├── memory.py         # Conversation Memory tool config
│   ├── planning.py       # Planning & WBS tool configs
│   ├── report.py         # Report Generator tool config
│   ├── vibe.py           # Vibe Refinement tool config
│   ├── verbalized_sampling.py  # Verbalized Sampling tool config
│   ├── jira.py           # JIRA tools config (DO NOT commit)
│   ├── jira.py.template  # JIRA config template (commit this)
│   ├── confluence.py     # Confluence tools config (DO NOT commit)
│   ├── confluence.py.template  # Confluence config template (commit this)
│   ├── slack.py          # Slack tools config (DO NOT commit)
│   └── slack.py.template # Slack config template (commit this)
│
├── src/                  # Source code directory
│   ├── tools/            # Tool implementations (business logic)
│   │   ├── base.py       # Base tool classes
│   │   ├── memory/       # Memory tools
│   │   │   └── conversation_memory_tool.py
│   │   ├── planning/     # Planning tools
│   │   │   ├── planning_tool.py
│   │   │   └── wbs_execution_tool.py
│   │   ├── reasoning/    # Reasoning tools
│   │   │   ├── recursive_thinking_tool.py
│   │   │   ├── sequential_thinking_tool.py
│   │   │   ├── tree_of_thoughts_tool.py
│   │   │   └── verbalized_sampling_tool.py
│   │   ├── report/       # Report generation tools
│   │   │   ├── report_generator_tool.py
│   │   │   ├── html_builder_tool.py
│   │   │   └── templates/  # HTML/CSS/JS templates
│   │   │       ├── report_template.html
│   │   │       ├── report_styles.css
│   │   │       └── report_script.js
│   │   ├── jira/         # JIRA integration tools
│   │   │   ├── issues.py                          # Issues management (search, get, create)
│   │   │   ├── comments.py                        # Comments management (get, add, update, delete)
│   │   │   ├── attachments.py                     # Attachments management (list, download)
│   │   │   ├── projects.py                        # Projects retrieval
│   │   │   └── knowledge.py                       # Knowledge base search
│   │   ├── confluence/   # Confluence integration tools
│   │   │   ├── pages.py                           # Pages management (create, get, update, delete)
│   │   │   ├── spaces.py                          # Spaces retrieval
│   │   │   └── search.py                          # CQL-based search
│   │   ├── slack/        # Slack integration tools
│   │   │   ├── slack_message_retrieval_tool.py    # Unified message retrieval (single/thread/history)
│   │   │   ├── slack_message_posting_tool.py      # Unified message posting (public/ephemeral)
│   │   │   ├── slack_thread_search_tool.py        # Thread search with relevance scoring
│   │   │   ├── delete_message_tool.py             # Message deletion (single/bulk)
│   │   │   └── digest_tool.py
│   │   └── vibe/         # Vibe Refinement tool
│   │       └── vibe_refinement_tool.py
│   │
│   ├── wrappers/         # MCP registration wrappers
│   │   ├── memory/       # Memory tool wrappers
│   │   │   └── conversation_memory_wrappers.py
│   │   ├── planning/     # Planning tool wrappers
│   │   │   ├── planning_wrapper.py
│   │   │   └── wbs_execution_wrapper.py
│   │   ├── reasoning/    # Reasoning tool wrappers
│   │   │   ├── recursive_thinking_wrappers.py
│   │   │   ├── sequential_thinking_wrapper.py
│   │   │   ├── tree_of_thoughts_wrapper.py
│   │   │   └── verbalized_sampling_wrapper.py
│   │   ├── report/       # Report generation wrappers
│   │   │   ├── report_generator_wrapper.py
│   │   │   └── html_builder_wrapper.py
│   │   ├── jira/         # JIRA tool wrappers
│   │   │   ├── issues_wrapper.py                   # search, get_details, create
│   │   │   ├── comments_wrapper.py                 # get, add, update, delete
│   │   │   ├── attachments_wrapper.py              # list, download
│   │   │   ├── projects_wrapper.py                 # get_projects
│   │   │   └── knowledge_wrapper.py                # search_knowledge
│   │   ├── confluence/   # Confluence tool wrappers
│   │   │   ├── pages_wrapper.py                    # create_page, get_page, update_page, delete_page
│   │   │   ├── spaces_wrapper.py                   # get_spaces
│   │   │   └── search_wrapper.py                   # search_pages
│   │   ├── slack/        # Slack tool wrappers
│   │   │   ├── slack_message_retrieval_wrapper.py  # get_single_message, get_thread_content, get_channel_history
│   │   │   ├── slack_message_posting_wrapper.py    # post_message, post_ephemeral_message
│   │   │   ├── slack_thread_search_wrapper.py      # search_threads
│   │   │   ├── delete_message_wrapper.py           # delete_message, bulk_delete_messages
│   │   │   └── digest_wrapper.py
│   │   └── vibe/         # Vibe Refinement wrapper
│   │       └── vibe_refinement_wrapper.py
│   │
│   └── utils/            # Utilities
│       └── logger.py     # Logging configuration
│
├── output/               # All tool-generated outputs
│   ├── chroma_db/        # ChromaDB persistent storage
│   ├── planning/         # WBS and planning files
│   └── reports/          # Generated HTML reports
│
└── docs/                 # Documentation
```

### Architecture Design

**Modular Configuration System**:
- **`configs/`**: Each tool category has its own config module
  - Easy to add new tools without modifying existing configs
  - Clear separation of concerns per tool category
  - Scalable for dozens of tools

**Clear Source Directory Structure**:
- **`src/`**: All source code organized under one directory
  - **`src/tools/`**: Core tool implementations with business logic
  - **`src/wrappers/`**: MCP-specific wrappers with tool descriptions
  - **`src/utils/`**: Shared utilities and helpers
- **`main.py`**: Central registration point at root level

This structure ensures:
- ✅ Clean separation between config, source, and output
- ✅ Easy maintenance (modify tool configs independently)
- ✅ Scalability (add new tool categories without clutter)
- ✅ Clear distinction between source code and other files

## ⚡ Quick Start

### 1. Clone and Install

```bash
# Clone repository
git clone https://github.com/HHC225/Local_MCP_Server.git
cd Local_MCP_Server

# Install uv (fast Python package installer)
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# or: pip install uv

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### 2. Test Server

```bash
python main.py
```

Expected output:
```
INFO: Initializing Thinking Tools MCP Server v1.0.0
INFO: Registering Recursive Thinking tools...
INFO: Registering Sequential Thinking tools...
INFO: Registering Tree of Thoughts tools...
INFO: Registering Verbalized Sampling tools...
INFO: Registering Conversation Memory tools...
INFO: Registering Planning tools...
INFO: Registering WBS Execution tool...
INFO: Registering Slack tools...
INFO: Registering Slack Digest tools...
INFO: Registering Vibe Refinement tools...
INFO: Registering Report Generator tools...
```

Press `Ctrl+C` to stop.

### 3. Configure Your IDE

#### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "thinking-tools": {
      "command": "/ABSOLUTE/PATH/TO/Local_MCP_Server/.venv/bin/python",
      "args": ["/ABSOLUTE/PATH/TO/Local_MCP_Server/main.py"]
    }
  }
}
```

#### VSCode/Cursor (macOS/Linux)

Create `.vscode/settings.json`:

```json
{
  "mcp.servers": {
    "thinking-tools": {
      "command": "/ABSOLUTE/PATH/TO/Local_MCP_Server/.venv/bin/python",
      "args": ["/ABSOLUTE/PATH/TO/Local_MCP_Server/main.py"]
    }
  }
}
```

**Important**: Replace `/ABSOLUTE/PATH/TO/` with your actual path! Use `pwd` to get it.

#### VSCode/Cursor (Windows with WSL)

Edit `%APPDATA%\Code\User\mcp.json`:

```json
{
  "servers": {
    "thinking-tools": {
      "command": "C:\\Windows\\System32\\wsl.exe",
      "args": [
        "-d", "Ubuntu",
        "--cd", "/home/YOUR_USERNAME/Local_MCP_Server",
        "/home/YOUR_USERNAME/Local_MCP_Server/.venv/bin/python3",
        "/home/YOUR_USERNAME/Local_MCP_Server/main.py"
      ],
      "env": {
        "NODE_ENV": "production",
        "CHROMA_DB_PATH": "./chroma_db"
      },
      "type": "stdio"
    }
  }
}
```

**Important**: 
- Replace `YOUR_USERNAME` with your WSL username (use `whoami` in WSL to get it)
- Replace `Ubuntu` with your WSL distribution name if different (use `wsl -l` in PowerShell)
- Full path example: `/home/john/Local_MCP_Server`

### 4. Restart IDE and Verify

1. Completely close and restart your IDE
2. Claude Desktop: Click 🔌 icon to verify "thinking-tools" server
3. VSCode/Cursor: Check MCP panel for server status

## 🧠 Available Tools

⚠️ **IMPORTANT**: Some advanced tools require **Claude Sonnet 4 or higher** for optimal performance. These are marked with a warning in their documentation.

### [Conversation Memory](docs/conversation-memory.md)

Store and retrieve complete conversation context using ChromaDB vector database.

**6 Actions**: Store • Query • List • Get • Update • Delete/Clear

**Key Features**: Full conversation text storage (no information loss), semantic search, ChromaDB embeddings, metadata support

[📖 Full Documentation →](docs/conversation-memory.md) | [🔧 Setup Guide →](docs/conversation-memory-setup.md)

### [Recursive Thinking](docs/recursive-thinking.md)

Iterative answer improvement through deep recursive analysis with automatic verification.

**4 Actions**: Initialize • Update Latent • Update Answer • Get Result • Reset

**Key Features**: Recursive reasoning refinement, automatic verification mode, improvement iteration control

[📖 Full Documentation →](docs/recursive-thinking.md)

### [Sequential Thinking](docs/sequential-thinking.md)

Step-by-step structured analysis where each thought builds on previous insights.

**1 Tool**: Sequential thinking with action execution support

**Key Features**: Thought sequencing, revision capability, branch exploration, direct action execution for code/file operations

[📖 Full Documentation →](docs/sequential-thinking.md)

### [Tree of Thoughts](docs/tree-of-thoughts.md)

Explore multiple solution paths with branching, evaluation, and backtracking.

**8 Actions**: Create Session • Add Thoughts • Add Evaluation • Search Next • Backtrack • Set Solution • Get Session • Display Results

**Key Features**: BFS/DFS search strategies, solution evaluation and scoring, backtracking from dead ends, ranked solution display

[📖 Full Documentation →](docs/tree-of-thoughts.md)

### [Verbalized Sampling](docs/verbalized-sampling.md)

Generate diverse creative responses through tail distribution sampling, breaking repetitive LLM patterns.

**6 Actions**: Initialize • Submit • Get All • Resample • Status • Export • Delete

**Key Features**: 4 selection strategies (uniform, weighted, lowest, highest), 4 operating modes (generate, improve, explore, balanced), diversity metrics

[📖 Full Documentation →](docs/verbalized-sampling.md)

### [Counterfactual Reasoning](docs/counterfactual-reasoning.md) V3.1

Explore alternative scenarios through systematic "what-if" analysis.

**6 Actions**: Initialize • Phase 1 • Phase 2 • Phase 3 (4 steps) • Phase 4 • Get Result • Reset

**Key Features**: 4 reasoning types (Diagnostic, Predictive, Preventive, Optimization), enhanced Phase 4 reports, type tracking, professional formatting

[📖 Full Documentation →](docs/counterfactual-reasoning.md)

### [Planning Tool - Multi-Action Architecture](docs/planning.md) 

Create structured Work Breakdown Structures (WBS) with progressive file updates.

**5 Actions**: Initialize • Add Step • Finalize • Status • List Sessions

**Key Features**: Multi-action architecture for better LLM compatibility, progressive WBS.md updates at each step, dependency mapping, hierarchical task structure

[📖 Full Documentation →](docs/planning.md)

### [WBS Execution Tool](docs/wbs-execution.md)

Systematic task-by-task execution with dependency-aware progress tracking.

**4 Actions**: Start • Continue • Execute Task • Get Status • List Sessions

**Key Features**: Real-time checkbox updates, error handling requirements, Sequential Thinking integration for complex tasks

[📖 Full Documentation →](docs/wbs-execution.md)

### [Code Analysis Tool](docs/code-analysis.md)

Progressive source code analysis with step-by-step documentation generation.

**4 Actions**: Initialize • Analyze Step • Get Status • Finalize • List Sessions

**Key Features**: Multi-step analysis for large files, progressive markdown updates, multi-language support (12+ languages), beginner-friendly explanations

[📖 Full Documentation →](docs/code-analysis.md)

### [Feature Flow Analysis Tool](docs/feature-flow-analysis.md) ⭐ UPDATED - Flow Visualization

ASCII-based flow visualization for understanding feature execution paths.

**3 Actions**: Analyze • Get Session • List Sessions

**Key Features**: Human-readable ASCII diagrams (no external tools), two-level visualization (file + method), one-shot analysis, file type classification

[📖 Full Documentation →](docs/feature-flow-analysis.md)

### [Vibe Refinement](docs/vibe-refinement.md)

Transform vague ideas into concrete specifications through structured two-phase refinement (Idea → System).

**6 Actions**: Initialize • Get Next • Submit • Status • Report • List Sessions

**Key Features**: Automatic specificity analysis (0-100 score), LLM-generated suggestions at each step, two-phase workflow, progress tracking, beautiful markdown reports

[📖 Full Documentation →](docs/vibe-refinement.md)

### [Report Generator](docs/report-generator.md)

Generate professional IT reports from raw content (Slack, JIRA, logs, etc.).

**2-Step Process**: generate_report (LLM analysis) → build_report_from_json (HTML output)

**Key Features**: Automatic severity assessment, executive summary, action items, glassmorphism UI

[📖 Full Documentation →](docs/report-generator.md)

### [Slack Tools](docs/slack-tools.md)

Integrate with Slack to retrieve messages, post communications, search threads, and manage channel content.

**Best for**: Team collaboration, automated notifications, thread analysis, knowledge discovery, channel history analysis, bulk message management

**8 Tools Available**:
```
Message Retrieval:
1. get_thread_content - Get threads with all replies
2. get_single_message - Get single message without replies
3. get_channel_history - Get channel message history with pagination

Message Search:
4. search_threads - Search with intelligent relevance scoring

Message Posting:
5. post_message - Send public messages to channels
6. post_ephemeral_message - Send private messages to specific users

Message Deletion:
7. delete_message - Delete single message
8. bulk_delete_messages - Delete multiple messages by date/timestamp range
```

**Key Features**:
- 📨 **Message Retrieval**: 
  - Get full threads with all replies
  - Get single messages for quick lookup
  - Get channel history with automatic pagination
  - Support for precise Slack timestamp queries
-  **Thread Search**: 
  - Multi-factor relevance scoring (native score, keyword freq, recency, engagement, title match)
  - Advanced filters (channels, dates, users)
  - Multiple output formats (summary, detailed, json, markdown)
  - LLM-ready analysis prompts
  - Full thread content retrieval for top results
- 📤 **Message Posting**: 
  - Send public messages visible to all
  - Send private ephemeral messages to specific users
  - Custom username and emoji support
  - Thread reply support
- 🗑️ **Message Deletion**: 
  - Single deletion by URL or channel+timestamp
  - Bulk deletion by date/timestamp range
  - **Thread-aware**: Automatically includes thread replies
  - Bot-only filtering option
  - Preview mode for safety (default enabled)
  - Maximum deletion limit protection
  - Precise timestamp support (e.g., 1760948716.586639)

**Bulk Deletion Example**:
```python
# Preview what would be deleted (safe)
await bulk_delete_messages(
    channel="G01G9JY2U3C",
    from_date="1760948716.586639",  # Precise Slack timestamp
    bot_only=True,
    preview=True,  # Shows what would be deleted without actually deleting
    max_messages=100
)

# Actually delete (DANGEROUS!)
await bulk_delete_messages(
    channel="G01G9JY2U3C",
    from_date="2025-10-07",
    to_date="2025-10-10",
    bot_only=True,
    preview=False,  # ⚠️ Actually deletes messages (including thread replies)
    max_messages=100
)
```

[📖 Full Documentation →](docs/slack-tools.md)

### [JIRA Tools](docs/jira-tools.md)

Complete JIRA integration for issue tracking, project management, and knowledge base operations.

**11 Tools**: Issues (search, get, create) • Comments (get, add, update, delete) • Attachments (list, download) • Projects • Knowledge Search

**Key Features**: JQL search, issue CRUD, comment management, attachment handling, custom fields support

[📖 Full Documentation →](docs/jira-tools.md)

### [Confluence Tools](docs/confluence-tools.md)

Confluence REST API v2 integration for page management and collaboration.

**6 Tools**: Pages (create, get, update, delete) • Spaces • Search

**Key Features**: CQL search, storage format content, version control, expand options, page hierarchy management

[📖 Full Documentation →](docs/confluence-tools.md)


## 🔧 Configuration Management

[📖 Full Documentation →](docs/slack-tools.md)

### [Slack Digest Tool](docs/slack-tools.md#slack-digest-tool) 

Automated team digest generation with LLM-powered analysis for wrap-up meetings.

**2 Tools**: Generate Digest • Post Digest

**Key Features**: Smart message collection (JST timezone), intelligent filtering, LLM analysis with anti-duplication, language auto-detection, wrap-up meeting optimized

[📖 Full Documentation →](docs/slack-tools.md#slack-digest-tool)

## 🛠️ Tool Comparison

| Tool | Structure | Best For | Complexity |
|------|-----------|----------|------------|
| **Conversation Memory** | Vector DB storage | Context retention, knowledge base | Low |
| **Planning Tool** | WBS hierarchy | Project breakdown, task planning | Medium |
| **WBS Execution Tool** | Task execution | Implementing WBS tasks systematically | Medium |
| **Vibe Refinement** | Interactive refinement | Clarifying vague requirements | Low |
| **Report Generator** | JSON to HTML | IT reports, incident analysis | Low |
| **Slack Tools** | API integration | Team communication, thread analysis | Low |
| **Slack Digest** | Automated analysis | Daily team digests, progress tracking | Low |
| **Recursive Thinking** | Iterative refinement | Deep analysis, verification needed | High |
| **Sequential Thinking** | Linear progression | Step-by-step planning | Medium |
| **Tree of Thoughts** | Branching exploration | Comparing multiple options | High |
| **Verbalized Sampling** | Tail sampling | Creative diversity, breaking patterns | Low |

## 📖 Documentation

- **Tools**:
  - [Conversation Memory Guide](docs/conversation-memory.md)
  - [Planning Tool Guide](docs/planning.md)
  - [WBS Execution Tool Guide](docs/wbs-execution.md)
  - [Vibe Refinement Guide](docs/vibe-refinement.md)
  - [Recursive Thinking Guide](docs/recursive-thinking.md)
  - [Sequential Thinking Guide](docs/sequential-thinking.md)
  - [Tree of Thoughts Guide](docs/tree-of-thoughts.md)
  - [Verbalized Sampling Guide](docs/verbalized-sampling.md)
  - [Counterfactual Reasoning Guide](docs/counterfactual-reasoning.md)
  - [Code Analysis Guide](docs/code-analysis.md)
  - [Feature Flow Analysis Guide](docs/feature-flow-analysis.md)
  - [Report Generator Guide](docs/report-generator.md)
  - [Slack Tools Guide](docs/slack-tools.md)
  - [JIRA Tools Guide](docs/jira-tools.md)
  - [Confluence Tools Guide](docs/confluence-tools.md)
- **Help**:
  - [Troubleshooting Guide](docs/troubleshooting.md)
  - [GitHub Issues](https://github.com/HHC225/Local_MCP_Server/issues)

## ⚙️ Configuration

This server uses **modular configuration system** under `configs/` directory - **no `.env` file needed**!

### Modular Configuration Structure

Each tool category has its own configuration file for better organization:

```python
# configs/base.py - Server & common settings
class ServerConfig:
    SERVER_NAME: str = "Thinking Tools MCP Server"
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    OUTPUT_DIR: Path = BASE_DIR / "output"

# configs/reasoning.py - Recursive/Sequential/ToT/Verbalized Sampling settings
class ReasoningConfig:
    ENABLE_RECURSIVE_THINKING: bool = True
    ENABLE_SEQUENTIAL_THINKING: bool = True
    ENABLE_TREE_OF_THOUGHTS: bool = True
    ENABLE_VERBALIZED_SAMPLING: bool = True
    # ... tool-specific settings

# configs/verbalized_sampling.py - Verbalized Sampling specific settings
VERBALIZED_SAMPLING_CONFIG = {
    "default_num_samples": 5,
    "default_max_probability": 0.10,
    "selection_strategies": ["uniform", "weighted", "lowest", "highest"],
    # ... mode-specific settings
}

# configs/memory.py - Conversation Memory settings
class MemoryConfig:
    ENABLE_CONVERSATION_MEMORY: bool = True
    CHROMA_DB_PATH: str = str(OUTPUT_DIR / "chroma_db")
    # ... tool-specific settings

# configs/planning.py - Planning & WBS settings
class PlanningConfig:
    ENABLE_PLANNING_TOOL: bool = True
    ENABLE_WBS_EXECUTION: bool = True
    WBS_FILENAME: str = "WBS.md"
    # ... tool-specific settings

# configs/vibe.py - Vibe Refinement settings
class VibeConfig:
    ENABLE_VIBE_REFINEMENT: bool = True
    MAX_REFINEMENT_STEPS: int = 10
    NUM_SUGGESTIONS: int = 5
    # ... tool-specific settings

# configs/report.py - Report Generator settings
class ReportConfig:
    ENABLE_REPORT_GENERATOR: bool = True
    REPORT_OUTPUT_DIR: Path = OUTPUT_DIR / "reports"
    REPORT_MAX_CONTENT_LENGTH: int = 50000
    # ... tool-specific settings

# configs/slack.py - Slack integration settings (see slack.py.template)
class SlackConfig:
    bot_token: str  # From environment variable
    workspace_domain: str = "your-workspace.slack.com"
    default_user_id: str = "U00000000"
    ENABLE_SLACK_TOOLS: bool = True
```

**⚠️ Security Note for Slack**: 
- Use `configs/slack.py.template` as template (commit to Git)
- Copy to `configs/slack.py` with actual credentials (DO NOT commit)
- `configs/slack.py` is in `.gitignore` to protect your credentials

### Adding New Tool Configurations

1. Create new config file: `configs/your_tool.py`
2. Define config class with settings
3. Import in `configs/__init__.py`
4. Use in your tool implementation

**Benefits**:
- 🎯 Easy to locate tool-specific settings
- 📦 No config file bloat as tools grow
- 🔧 Independent configuration per tool category

### Environment Variable Overrides

You can still override settings via environment variables:

```bash
# Temporary override for one session
MCP_LOG_LEVEL=DEBUG python main.py

# Or set in your shell profile
export MCP_LOG_LEVEL=DEBUG
export ENABLE_TREE_OF_THOUGHTS=false
```

### Output Directory Structure

All tool-generated files are organized under `output/`:

```
output/
├── chroma_db/           # Conversation Memory ChromaDB storage
├── planning/            # Planning tool WBS files
│   └── execution/       # WBS execution session data
└── reports/             # Generated HTML reports
    ├── incident_20251016_143022.html
    ├── investigation_20251016_150134.html
    └── ...
```

**Note**: The `output/` directory is in `.gitignore` and created automatically on startup.

## 💡 Quick Tips

- **Adjust Log Level**: Edit `LOG_LEVEL` in `config.py` or use `MCP_LOG_LEVEL` env var
- **Enable/Disable Tools**: Edit `ENABLE_*_TOOLS` in `config.py`
- **Output Location**: All files go to `output/` directory (auto-organized)
- **Save Session IDs**: Keep them in notepad for resuming later
- **Use uv for Speed**: 10-100x faster than pip for installations

## 🚀 Why uv?

[uv](https://github.com/astral-sh/uv) is a fast Python package installer:
- ⚡ 10-100x faster than pip
- 🔒 Built-in dependency resolution
- 🎯 Drop-in replacement for pip

```bash
# Common uv commands
uv pip install package_name
uv pip install -r requirements.txt
uv venv
```

## 🤝 Contributing

**⚠️ Important: All contributions must go through Pull Requests**

1. Fork the repository on GitHub
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/Local_MCP_Server.git`
3. Create feature branch: `git checkout -b feature/your-feature`
4. Make changes, test, and submit PR

Direct commits to `main` branch are NOT allowed.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Need help?** Check the [Troubleshooting Guide](docs/troubleshooting.md) or [open an issue](https://github.com/HHC225/Local_MCP_Server/issues)!
