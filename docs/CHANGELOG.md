# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.7.0] - 2025-10-23

### Added - Counterfactual Reasoning Tool 🔮

**NEW FEATURE**: Advanced "what-if" analysis through systematic counterfactual reasoning

#### Overview
Implemented Counterfactual Reasoning tool that enables exploration of alternative scenarios through 4-phase structured analysis. Helps understand root causes, predict futures, prevent risks, and discover optimization opportunities by examining how different conditions would lead to different outcomes.

#### Key Features
- 🔍 **4-Phase Systematic Analysis**:
  - **Phase 1**: Actual State Analysis - Current state and causal relationships
  - **Phase 2**: Counterfactual Scenarios - 4 types of alternative scenarios
  - **Phase 3**: Deep Reasoning - Principle-based analysis with 4 depth levels
  - **Phase 4**: Comparative Analysis - Integrated insights and action priorities

- 🎯 **4 Reasoning Types**:
  - **Diagnostic**: "What if X was different?" - Root cause identification
  - **Predictive**: "What if trend continues?" - Future scenario prediction
  - **Preventive**: "What if problem occurs?" - Risk prevention planning
  - **Optimization**: "What if alternative method?" - Improvement exploration

- 📊 **Deep Analysis Framework**:
  - **3 Core Principles**: Minimal Change, Causal Consistency, Proximity
  - **4 Reasoning Depths**: Direct, Ripple, Multidimensional, Long-term
  - **Multiple Perspectives**: Technical, Business, Organizational, Legal
  - **Time Horizons**: Short-term, Medium-term, Long-term impacts

- 🔄 **Session Management**:
  - Initialize, phase1-4 execution, get_result, reset, list_sessions
  - Complete session history tracking
  - Structured prompt chaining between phases

#### Files Added
- `src/tools/reasoning/counterfactual_reasoning_tool.py` - 8 Tool classes (Initialize, Phase1-4, GetResult, Reset, ListSessions)
- `src/wrappers/reasoning/counterfactual_reasoning_wrapper.py` - MCP wrapper functions
- `docs/counterfactual-reasoning.md` - Comprehensive documentation with examples

#### Files Modified
- `src/tools/reasoning/__init__.py` - Added Counterfactual tools export
- `src/wrappers/reasoning/__init__.py` - Added Counterfactual wrapper exports
- `configs/reasoning.py` - Added ENABLE_COUNTERFACTUAL_REASONING flag
- `main.py` - Added Counterfactual Reasoning tools registration
- `README.md` - Added Counterfactual Reasoning section

#### Use Cases
- Post-incident analysis: Understand what went wrong and prevention strategies
- Risk assessment: Identify potential problems and their impacts
- Decision making: Evaluate different courses of action
- Optimization planning: Discover improvement opportunities
- Strategic planning: Explore future scenarios and implications

#### Architecture Highlights
- Modular 4-phase structure with clear separation of concerns
- Each phase provides detailed LLM instructions for next phase
- Comprehensive session state management in memory
- Structured JSON-based communication between phases
- Extensive validation and error handling

## [1.6.0] - 2025-10-20

### Added - Verbalized Sampling Tool 🎲

**NEW FEATURE**: Creative response generation through tail distribution sampling

#### Overview
Implemented Verbalized Sampling tool that breaks repetitive LLM response patterns by sampling from the tails of the probability distribution (probability < 0.10), enabling diverse and creative outputs.

#### Key Features
- 🎲 **4 Selection Strategies**:
  - `uniform`: Equal probability for all samples (pure random)
  - `weighted`: Inverse probability weighting (favors more creative samples)
  - `lowest`: Always select lowest probability (most creative)
  - `highest`: Select highest probability (most conservative)

- 🎨 **4 Operating Modes**:
  - `generate`: New creative responses (max_prob: 0.10)
  - `improve`: Creative improvements to existing content (max_prob: 0.10)
  - `explore`: Maximum creativity (max_prob: 0.05)
  - `balanced`: Mix creativity with reliability (max_prob: 0.15)

- 📊 **Rich Statistics**:
  - Probability distribution analysis
  - Creativity index calculation
  - Text length metrics
  - Sample diversity tracking

- 🔄 **Session Management**:
  - Initialize, submit, resample, list, status, export, delete
  - Session history tracking
  - Multiple format exports (JSON, Markdown, text)

#### Files Added
- `configs/verbalized_sampling.py` - Configuration with mode templates
- `src/tools/reasoning/verbalized_sampling_tool.py` - Core tool logic
- `src/wrappers/reasoning/verbalized_sampling_wrapper.py` - MCP wrapper
- `docs/verbalized-sampling.md` - Comprehensive documentation

#### Use Cases
- Generate diverse answers instead of repetitive responses
- Improve existing content with creative variations
- Explore unconventional ideas systematically
- Break out of LLM's high-probability "safe" zone
- Brainstorming and ideation with guaranteed diversity

#### Integration
- Updated `configs/reasoning.py` with `ENABLE_VERBALIZED_SAMPLING` flag
- Updated `src/wrappers/reasoning/__init__.py` to export new tool
- Updated `main.py` to register verbalized sampling tools
- Updated `README.md` with new tool section

#### Example Usage
```python
# Initialize session
result = await verbalized_sampling_initialize(
    query="Tell me a coffee joke",
    mode="generate"
)

# LLM generates 5 diverse responses with probabilities < 0.10
samples = [
    {"text": "Coffee joke 1", "probability": 0.08},
    {"text": "Coffee joke 2", "probability": 0.07},
    # ... 3 more samples
]

# Submit and get random selection
result = await verbalized_sampling_submit(
    session_id=result["session_id"],
    samples=samples,
    selection_strategy="weighted"  # Favors more creative samples
)
```

## [1.5.0] - 2025-10-19

### Changed - Planning Tool Redesign 🎉

**BREAKING CHANGE**: Planning Tool now uses multi-action architecture

#### Overview
Completely redesigned Planning Tool following the Vibe Tool pattern for better LLM compatibility and progressive file updates.

#### Problems Fixed
- ❌ **Old**: Single monolithic tool with 18+ parameters
- ❌ **Old**: WBS generated only at end → context loss with long sessions
- ❌ **Old**: Poor performance with weaker LLMs
- ❌ **Old**: Complex multi-purpose instructions
- ❌ **Old**: Token limit issues

#### New Architecture
- ✅ **5 focused actions** instead of one tool
- ✅ **Progressive WBS.md updates** at each step
- ✅ **Clear prompt chaining** guides LLM to next action
- ✅ **No context loss** - tasks saved immediately to file
- ✅ **Better LLM compatibility** - simpler, focused interfaces
- ✅ **2-4 parameters per action** vs 18+ before

#### New Actions

1. **`planning_initialize`**
   - Creates new session
   - Generates initial WBS.md file with header
   - Returns session_id
   
2. **`planning_add_step`**
   - Adds planning analysis + WBS items
   - **Immediately updates WBS.md file**
   - Progressive file building
   - Can be called multiple times
   
3. **`planning_finalize`**
   - Marks session as completed
   - Final WBS.md generation
   - Returns summary statistics
   
4. **`planning_status`**
   - Check current progress
   - View WBS item count
   - Session state information
   
5. **`planning_list`**
   - List all planning sessions
   - Session summaries
   - Last updated timestamps

#### Migration Guide

**Old Way:**
```python
await planning(
    planning_step="Analysis...",
    step_number=1,
    total_steps=5,
    next_step_needed=True,
    problem_statement="Build game",
    wbs_items=[...],
    # + 12 more parameters
)
```

**New Way:**
```python
# Initialize
result = await planning_initialize(
    problem_statement="Build game"
)
session_id = json.loads(result)["sessionId"]

# Add steps
await planning_add_step(
    session_id=session_id,
    step_number=1,
    planning_analysis="Analysis...",
    wbs_items=[...]
)

# Finalize
await planning_finalize(session_id=session_id)
```

#### Key Benefits

1. **No Context Loss**
   - WBS.md created in step 1
   - Updated progressively at each step
   - Early tasks never lost

2. **Progressive File Updates**
   ```
   Initialize → WBS.md created
   Add Step 1 → WBS.md updated
   Add Step 2 → WBS.md updated
   ...
   Finalize → Complete WBS.md
   ```

3. **Clear Action Flow**
   - Each response includes `nextAction` field
   - Guides LLM to next step
   - No confusion about what to do next

4. **Simplified Interfaces**
   - `planning_initialize`: 2 parameters
   - `planning_add_step`: 4 parameters
   - `planning_finalize`: 1 parameter
   - vs old tool: 18+ parameters

#### Technical Details

**Files Modified:**
- `src/tools/planning/planning_tool.py` - Complete rewrite with action methods
- `src/wrappers/planning/planning_wrapper.py` - 5 separate wrapper functions
- `src/wrappers/planning/__init__.py` - Export all new functions
- `main.py` - Register 5 new tool functions

**Files Added:**
- `docs/planning-new-architecture.md` - Comprehensive new documentation

**Files Preserved:**
- `docs/planning.md` - Old documentation (marked as legacy)
- `src/tools/planning/planning_tool_old.py` - Backup of old implementation

#### Documentation

- 📖 [New Architecture Guide](docs/planning-new-architecture.md) - Complete guide with examples
- 📖 [Old Documentation](docs/planning.md) - Legacy reference
- 📖 Updated README with new Planning Tool section

#### Breaking Changes

**Removed:**
- Single `planning` tool function
- Parameters: `total_steps`, `next_step_needed`, `is_revision`, `revises_step`, `branch_from_step`, `branch_id`, `refine_wbs`, `generate_markdown`, `action_required`, `action_type`, `action_description`

**Added:**
- 5 new tool functions: `planning_initialize`, `planning_add_step`, `planning_finalize`, `planning_status`, `planning_list`
- Progressive WBS.md file updates
- Clear action-based workflow

#### Compatibility

- ⚠️ **Not backward compatible** with old `planning` tool calls
- ✅ WBS.md file format unchanged
- ✅ WBS item structure unchanged
- ✅ Validation rules unchanged
- ✅ Output directory unchanged

#### Recommendations

- **New projects**: Use new multi-action architecture
- **Existing workflows**: Migrate to new actions for better reliability
- **Weaker LLMs**: Significantly better performance with new architecture

---

## [1.4.0] - 2025-10-16

### Added
- **Vibe Coding Tool** - Interactive prompt refinement through clarifying questions
  - Prevents AI from making assumptions about vague requirements
  - Provides exactly 3 specific alternatives at each decision point
  - Interactive loop that waits for explicit user selection
  - Session management to maintain conversation context
  - Progressive refinement until prompt is fully concrete
  
### Features
- **Actions**: start, respond, get_status, list_sessions, finalize
- **3 Alternatives Rule**: Always provides exactly 3 specific suggestions
- **No Assumptions**: Forces explicit user choices instead of AI guessing
- **Session Persistence**: In-memory sessions with full conversation history
- **Status Flow**: refinement_needed → awaiting_response → completed

### Technical Details
- Implementation: `src/tools/vibe/vibe_coding_tool.py`
- Wrapper: `src/wrappers/vibe/vibe_coding_wrapper.py`
- Configuration: `configs/vibe.py`
- Feature flag: `ENABLE_VIBE_CODING` in configs/vibe.py
- Global session store: `vc_sessions` dictionary

### Configuration Options
- `ENABLE_VIBE_CODING`: Enable/disable tool (default: true)
- `MAX_REFINEMENT_STAGES`: Maximum refinement cycles (default: 10)
- `NUM_SUGGESTIONS`: Number of alternatives to provide (default: 3)
- `SESSION_TIMEOUT`: Session timeout in seconds (default: 3600)

### Documentation
- Added comprehensive [Vibe Coding Guide](docs/vibe-coding.md)
- Updated README with Vibe Coding section and examples
- Added to tool comparison table
- Includes AI usage patterns and best practices

### Use Cases
- Refining vague project requirements into concrete specifications
- Exploring architecture alternatives systematically
- Making informed technology stack decisions
- Building detailed specifications from high-level ideas
- Structured requirement gathering with stakeholders

## [1.3.0] - 2025-10-15

### Added
- **WBS Execution Tool** - Systematic task-by-task execution for WBS-based projects
  - Parse WBS markdown files and extract hierarchical tasks
  - Execute tasks step-by-step with deep thinking analysis
  - Real-time checkbox updates in WBS files after task completion
  - Automatic dependency resolution and validation
  - Session management for resumable execution
  - Progress tracking with completion statistics
  - Error prevention through strict validation
  - Complex task detection with Sequential Thinking integration
  - Parent task auto-completion when all children complete
  
### Features
- **Actions**: start, continue, execute_task, get_status, list_sessions
- **Dependency Management**: Enforces proper execution order
- **Error Handling**: Validates prerequisites before execution
- **File Updates**: Real-time WBS file checkbox synchronization
- **Session Persistence**: In-memory sessions with full state tracking

### Technical Details
- Implementation: `tools/planning/wbs_execution_tool.py`
- Wrapper: `wrappers/planning/wbs_execution_wrapper.py`
- Feature flag: `ENABLE_WBS_EXECUTION_TOOLS` in config.py
- Follows Planning Tool directory structure
- Compatible with Planning Tool WBS output format

### Documentation
- Added comprehensive [WBS Execution Guide](docs/wbs-execution.md)
- Updated README with tool comparison and examples
- Added API reference and troubleshooting section

## [1.2.0] - 2025-10-15

### Changed
- **Configuration System Refactoring**
  - Removed `.env` file dependency - `config.py` is now the main configuration file
  - Direct configuration in `config.py` with environment variable override support
  - Cleaner, more maintainable configuration approach

### Added
- **Centralized Output Directory Management**
  - New `output/` directory for all tool-generated files
  - `output/chroma_db/` - ChromaDB conversation memory storage
  - `output/planning/` - Planning tool WBS files
  - Auto-creation of output directories on startup
- **Planning Tool Configuration**
  - `PLANNING_OUTPUT_DIR` - configurable planning output directory
  - `PLANNING_WBS_FILENAME` - customizable WBS filename
  - Default WBS files now saved to `output/planning/`

### Fixed
- ChromaDB path now uses centralized config
- Planning tool WBS export now uses centralized output directory
- Removed hardcoded paths from tool implementations

### Technical Details
- `ServerConfig.ensure_output_directories()` - auto-creates all output paths
- `Path` objects used for cross-platform path handling
- Backward compatible: environment variables still work for overrides
- Migrated existing `chroma_db/` data to `output/chroma_db/`

### Documentation
- Updated README with new configuration section
- Marked `.env.example` as deprecated
- Added output directory structure documentation

## [1.1.0] - 2025-10-14

### Added
- **Conversation Memory Tool** with ChromaDB integration
  - Store important conversation summaries with speaker tracking
  - Semantic search for retrieving relevant conversations
  - Automatic embedding generation (no manual embedding needed)
  - Metadata filtering and organization
  - List, delete, and clear operations
  - Persistent storage across server restarts
- New `tools/memory/` directory for memory-related tools
- ChromaDB dependency (v1.1.1) with automatic embedding support
- Comprehensive documentation:
  - Full feature guide: `docs/conversation-memory.md`
  - Setup and configuration: `docs/conversation-memory-setup.md`
- Test suite: `test_conversation_memory.py`
- Configuration options:
  - `ENABLE_CONVERSATION_MEMORY_TOOLS` flag
  - `CONVERSATION_MEMORY_DB_PATH` for custom database location
  - `CONVERSATION_MEMORY_DEFAULT_RESULTS` for query limits

### Changed
- Reorganized tool structure: memory tools now in separate directory
- Updated `requirements.txt` with all installed dependencies (generated from pip freeze)
- Enhanced README with Conversation Memory section
- Updated `.gitignore` to exclude ChromaDB database files

### Technical Details
- ChromaDB uses `all-MiniLM-L6-v2` embedding model (384 dimensions)
- Automatic persistence to disk (SQLite + embeddings)
- Semantic similarity search with distance scoring
- Support for custom metadata schemas

## [1.0.0] - 2025-10-13

### Added
- Initial release of Thinking Tools MCP Server
- Recursive Thinking Model reasoning tools
  - Initialize reasoning sessions
  - Update latent reasoning with 4-step systematic analysis
  - Update answer based on reasoning insights
  - Verify final answer with mandatory verification loop
  - Get result and status of sessions
  - Reset sessions
- Sequential Thinking tool for structured analytical thinking
  - Sequential thought progression
  - Revision capabilities
  - Branch exploration
  - Action execution integration
- Tree of Thoughts tool for complex problem-solving
  - Session creation and management
  - Thought node addition
  - Node evaluation
  - Search strategies (BFS/DFS)
  - Backtracking capabilities
  - Solution ranking and display
- FastMCP server implementation with modular architecture
- Comprehensive logging system
- Environment-based configuration management
- Feature flags for tool activation/deactivation

### Documentation
- Complete README.md with installation and usage instructions
- CONTRIBUTING.md for contribution guidelines
- LICENSE file (MIT License)
- .env.example for environment configuration
- Detailed tool documentation with parameters and examples

### Configuration
- .gitignore for Python projects
- .gitattributes for consistent line endings
- Environment variable support via python-dotenv
- Configurable logging levels

## [Unreleased]

### Planned
- Persistent session storage (SQLite/Redis)
- Web UI interface
- Additional thinking tools (Analogical Reasoning, Critical Thinking)
- Tool integration workflows
- Performance metrics and analytics
- Multi-language support
- Unit tests and integration tests
- CI/CD pipeline
- Docker containerization
- API documentation with examples

---

For more details, see the [full commit history](https://github.com/HHC225/Thinking_Tools_Local/commits/main).
