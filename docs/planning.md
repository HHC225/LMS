# Planning Tool - Multi-Action Architecture

## Overview

The Planning Tool has been redesigned with a **multi-action architecture** following the Vibe tool pattern. This new design provides:

- **Separate focused actions** instead of one monolithic tool
- **Progressive WBS.md file updates** at each planning step
- **Better LLM compatibility** with simpler, clearer interfaces
- **Prompt chaining** that guides the LLM through the planning process
- **Token efficiency** by updating files incrementally

## Why the New Architecture?

### Problems with the Old Design

The previous monolithic planning tool had several issues:

1. **Too many parameters** - One tool tried to handle all planning scenarios
2. **Context loss** - WBS generated only at the end, losing early tasks with long planning sessions
3. **Token limit issues** - Full WBS generation after all thinking steps
4. **Poor LLM performance** - Weaker LLMs struggled with complex multi-purpose instructions
5. **Confusing flow** - Unclear progression through planning steps

### Benefits of the New Design

1. **Clear separation of concerns** - Each action has a single, focused purpose
2. **Progressive file updates** - WBS.md created immediately and updated at each step
3. **No context loss** - Early planning tasks preserved in file, not just memory
4. **Prompt chaining** - Each action response guides to the next action
5. **Better LLM compatibility** - Simple, clear instructions for each action
6. **Easier to maintain** - Modular code structure

## Architecture Components

### Five Core Actions

| Action | Purpose | When to Use |
|--------|---------|-------------|
| **`planning_initialize`** | Create new session, initial WBS.md | Start of planning |
| **`planning_add_step`** | Add planning analysis + WBS items | During planning (multiple times) |
| **`planning_finalize`** | Mark complete, final WBS.md | End of planning |
| **`planning_status`** | Check progress | Anytime |
| **`planning_list`** | List all sessions | Browse sessions |

### Action Flow

```
planning_initialize
    ↓
    Creates session
    Creates WBS.md with header
    Returns session_id
    ↓
planning_add_step (Step 1)
    ↓
    Adds WBS items
    Updates WBS.md file ← IMMEDIATE UPDATE
    Returns progress
    ↓
planning_add_step (Step 2)
    ↓
    Adds more WBS items
    Updates WBS.md file ← IMMEDIATE UPDATE
    Returns progress
    ↓
    ... (repeat as needed)
    ↓
planning_finalize
    ↓
    Marks session complete
    Final WBS.md update
    Returns summary
```

## Detailed Action Reference

### 1. planning_initialize

**Purpose:** Initialize a new planning session and create the initial WBS.md file.

**Parameters:**
- `problem_statement` (required): The problem or project to break down
- `project_name` (optional): Project name (auto-generated if not provided)

**Returns:**
```json
{
  "success": true,
  "sessionId": "planning_1234567890_abcd1234",
  "projectName": "Build a task management",
  "outputPath": "/path/to/WBS.md",
  "message": "Session initialized. WBS file created at: /path/to/WBS.md",
  "nextAction": "add_step"
}
```

**Example:**
```python
result = await planning_initialize(
    problem_statement="Build a real-time multiplayer 2048 game with leaderboards",
    project_name="Multiplayer 2048"
)
```

**What Happens:**
1. Creates new session with unique ID
2. Creates WBS.md file with project header and problem statement
3. Returns session_id for subsequent calls
4. File is ready for progressive updates

---

### 2. planning_add_step

**Purpose:** Add a planning step with analysis and WBS items, immediately updating the WBS.md file.

**Parameters:**
- `session_id` (required): Session ID from `planning_initialize`
- `step_number` (required): Current step number (1, 2, 3, ...)
- `planning_analysis` (required): Your planning thoughts for this step
- `wbs_items` (optional): List of WBS items to add

**WBS Item Structure:**
```json
{
  "id": "1.0",
  "title": "Project Setup",
  "description": "Initialize repository and development environment",
  "level": 0,
  "priority": "High",
  "dependencies": [],
  "order": 0,
  "parent_id": null
}
```

**Critical Requirements:**
- `parent_id` is **REQUIRED** for all child items (level > 0)
- `parent_id` must reference an existing parent item
- Child items must be added after their parents

**Returns:**
```json
{
  "success": true,
  "sessionId": "planning_1234567890_abcd1234",
  "stepNumber": 1,
  "wbsItemsAdded": 5,
  "totalWbsItems": 5,
  "wbsFileUpdated": true,
  "outputPath": "/path/to/WBS.md",
  "message": "Step 1 completed. Added 5 WBS items. WBS file updated.",
  "nextAction": "add_step_or_finalize"
}
```

**Example:**
```python
result = await planning_add_step(
    session_id="planning_1234567890_abcd1234",
    step_number=1,
    planning_analysis="Breaking down project into three main phases: setup, development, deployment",
    wbs_items=[
        {
            "id": "1.0",
            "title": "Project Setup Phase",
            "description": "Initialize all project infrastructure",
            "level": 0,
            "priority": "High"
        },
        {
            "id": "1.1",
            "title": "Create Git Repository",
            "description": "Initialize git repository with proper .gitignore",
            "level": 1,
            "parent_id": "1.0",
            "priority": "High",
            "order": 1
        }
    ]
)
```

**What Happens:**
1. Validates WBS items structure and hierarchy
2. Adds items to session
3. **Immediately updates WBS.md file** with new items
4. Returns progress information
5. Previous items are preserved in the file

---

### 3. planning_finalize

**Purpose:** Mark the planning session as completed and generate the final WBS.md.

**Parameters:**
- `session_id` (required): Session ID from `planning_initialize`

**Returns:**
```json
{
  "success": true,
  "sessionId": "planning_1234567890_abcd1234",
  "status": "completed",
  "totalSteps": 5,
  "totalWbsItems": 23,
  "outputPath": "/path/to/WBS.md",
  "message": "Planning completed! 23 WBS items generated."
}
```

**Example:**
```python
result = await planning_finalize(
    session_id="planning_1234567890_abcd1234"
)
```

**What Happens:**
1. Marks session as "completed"
2. Generates final WBS.md with all items
3. Returns summary statistics
4. WBS.md is ready for execution

---

### 4. planning_status

**Purpose:** Check current status and progress of a planning session.

**Parameters:**
- `session_id` (required): Session ID to query

**Returns:**
```json
{
  "success": true,
  "sessionId": "planning_1234567890_abcd1234",
  "status": "active",
  "projectName": "Multiplayer 2048",
  "currentStep": 3,
  "totalSteps": 3,
  "totalWbsItems": 15,
  "outputPath": "/path/to/WBS.md"
}
```

**Example:**
```python
result = await planning_status(
    session_id="planning_1234567890_abcd1234"
)
```

---

### 5. planning_list

**Purpose:** List all planning sessions currently in memory.

**Parameters:** None

**Returns:**
```json
{
  "success": true,
  "totalSessions": 3,
  "sessions": [
    {
      "sessionId": "planning_1234567890_abcd1234",
      "projectName": "Multiplayer 2048",
      "status": "active",
      "totalSteps": 3,
      "totalWbsItems": 15,
      "lastUpdated": "2025-01-19T14:30:22"
    }
  ]
}
```

**Example:**
```python
result = await planning_list()
```

## Complete Usage Example

### Step-by-Step Planning Flow

```python
# Step 1: Initialize planning session
result = await planning_initialize(
    problem_statement="Build a real-time multiplayer 2048 game with Firebase",
    project_name="Multiplayer 2048"
)
session_id = json.loads(result)["sessionId"]

# Step 2: Add first planning step
await planning_add_step(
    session_id=session_id,
    step_number=1,
    planning_analysis="Identifying main project phases: setup, game logic, multiplayer, UI",
    wbs_items=[
        {
            "id": "1.0",
            "title": "Project Setup",
            "description": "Initialize project structure and dependencies",
            "level": 0,
            "priority": "High"
        },
        {
            "id": "2.0",
            "title": "Game Logic Development",
            "description": "Implement core 2048 game mechanics",
            "level": 0,
            "priority": "High",
            "order": 1
        }
    ]
)

# Step 3: Add second planning step (breaking down tasks)
await planning_add_step(
    session_id=session_id,
    step_number=2,
    planning_analysis="Breaking down project setup into specific tasks",
    wbs_items=[
        {
            "id": "1.1",
            "title": "Create React Project",
            "description": "Initialize React app with TypeScript",
            "level": 1,
            "parent_id": "1.0",
            "priority": "High",
            "order": 1
        },
        {
            "id": "1.2",
            "title": "Setup Firebase",
            "description": "Configure Firebase project and authentication",
            "level": 1,
            "parent_id": "1.0",
            "priority": "High",
            "dependencies": ["1.1"],
            "order": 2
        }
    ]
)

# Step 4: Add third planning step (more detailed breakdown)
await planning_add_step(
    session_id=session_id,
    step_number=3,
    planning_analysis="Detailing game logic implementation tasks",
    wbs_items=[
        {
            "id": "2.1",
            "title": "Grid State Management",
            "description": "Implement 4x4 grid state with Redux",
            "level": 1,
            "parent_id": "2.0",
            "priority": "High",
            "dependencies": ["1.1"],
            "order": 1
        },
        {
            "id": "2.2",
            "title": "Tile Movement Logic",
            "description": "Implement swipe detection and tile merging",
            "level": 1,
            "parent_id": "2.0",
            "priority": "High",
            "dependencies": ["2.1"],
            "order": 2
        }
    ]
)

# Step 5: Check status
status = await planning_status(session_id=session_id)
print(status)  # Shows 3 steps, 6 WBS items

# Step 6: Finalize planning
await planning_finalize(session_id=session_id)
# WBS.md is now complete and ready for execution
```

## Progressive WBS.md File Updates

### Initial State (After planning_initialize)

```markdown
# Project: Multiplayer 2048

## Problem Statement
Build a real-time multiplayer 2048 game with Firebase

## Work Breakdown Structure

*No WBS items yet*

## Planning Summary

- **Steps**: 0
- **WBS Items**: 0
- **Status**: active
```

### After Step 1 (planning_add_step)

```markdown
# Project: Multiplayer 2048

## Problem Statement
Build a real-time multiplayer 2048 game with Firebase

## Work Breakdown Structure

- [ ] **Project Setup** (Priority: High)
  - ID: 1.0
  - Description: Initialize project structure and dependencies

- [ ] **Game Logic Development** (Priority: High)
  - ID: 2.0
  - Description: Implement core 2048 game mechanics

## Planning Summary

- **Steps**: 1
- **WBS Items**: 2
- **Status**: active
```

### After Step 2 (planning_add_step)

```markdown
# Project: Multiplayer 2048

## Problem Statement
Build a real-time multiplayer 2048 game with Firebase

## Work Breakdown Structure

- [ ] **Project Setup** (Priority: High)
  - ID: 1.0
  - Description: Initialize project structure and dependencies
  
  - [ ] **Create React Project** (Priority: High)
    - ID: 1.1
    - Description: Initialize React app with TypeScript
    - Dependencies: None

  - [ ] **Setup Firebase** (Priority: High)
    - ID: 1.2
    - Description: Configure Firebase project and authentication
    - Dependencies: 1.1 (Create React Project)

- [ ] **Game Logic Development** (Priority: High)
  - ID: 2.0
  - Description: Implement core 2048 game mechanics

## Planning Summary

- **Steps**: 2
- **WBS Items**: 4
- **Status**: active
```

## Key Advantages

### 1. No Context Loss

❌ **Old Way:**
```
Step 1: Think about task A → (stored in memory)
Step 2: Think about task B → (stored in memory)
Step 3: Think about task C → (stored in memory)
...
Step 10: Think about task J → (stored in memory)
Final: Generate WBS → (task A might be lost if context too long)
```

✅ **New Way:**
```
Step 1: Think about task A → Write to file immediately
Step 2: Think about task B → Add to file immediately
Step 3: Think about task C → Add to file immediately
...
Step 10: Think about task J → Add to file immediately
Final: File already complete with all tasks
```

### 2. Better LLM Guidance

Each action response includes clear next steps:

```json
{
  "nextAction": "add_step",
  "instructions": {
    "next_step": "Call planning_add_step to add your first planning analysis",
    "wbs_file": "WBS.md file has been created and will be updated progressively"
  }
}
```

### 3. Simplified Tool Interface

❌ **Old Way:** One tool with 18+ parameters
✅ **New Way:** Five focused tools with 2-4 parameters each

### 4. Progressive Validation

Each step validates and saves immediately, catching errors early rather than at the end.

## Migration from Old Planning Tool

### Old Tool Call

```python
await planning(
    planning_step="Analyzing project structure...",
    step_number=1,
    total_steps=5,
    next_step_needed=True,
    problem_statement="Build a game",
    project_name="Game Project",
    wbs_items=[...],
    export_to_file=True,
    # ... many more parameters
)
```

### New Tool Calls

```python
# Initialize
result = await planning_initialize(
    problem_statement="Build a game",
    project_name="Game Project"
)
session_id = json.loads(result)["sessionId"]

# Add steps
await planning_add_step(
    session_id=session_id,
    step_number=1,
    planning_analysis="Analyzing project structure...",
    wbs_items=[...]
)

# Finalize
await planning_finalize(session_id=session_id)
```

## Best Practices

### 1. Start with High-Level Structure

In step 1, define major phases (level 0):
```python
wbs_items=[
    {"id": "1.0", "title": "Setup", "level": 0, ...},
    {"id": "2.0", "title": "Development", "level": 0, ...},
    {"id": "3.0", "title": "Testing", "level": 0, ...}
]
```

### 2. Progressive Decomposition

In subsequent steps, break down each phase:
```python
# Step 2: Break down Setup
wbs_items=[
    {"id": "1.1", "title": "Init Repo", "level": 1, "parent_id": "1.0", ...},
    {"id": "1.2", "title": "Install Deps", "level": 1, "parent_id": "1.0", ...}
]

# Step 3: Break down Development
wbs_items=[
    {"id": "2.1", "title": "Build API", "level": 1, "parent_id": "2.0", ...},
    {"id": "2.2", "title": "Build UI", "level": 1, "parent_id": "2.0", ...}
]
```

### 3. Specify Dependencies Clearly

Use task IDs to specify dependencies:
```python
{
    "id": "2.2",
    "title": "Build UI",
    "dependencies": ["2.1"],  # UI depends on API being ready
    ...
}
```

### 4. Use Descriptive Analysis

Provide clear reasoning in `planning_analysis`:
```python
planning_analysis="""
Breaking down the API development phase:
- Need authentication endpoint first (dependency for others)
- Then user management APIs
- Finally game-specific endpoints
This order ensures proper foundation before complex features.
"""
```

### 5. Check Status Periodically

```python
status = await planning_status(session_id=session_id)
# Verify items are being added correctly
```

## Troubleshooting

### Error: Session Not Found

**Problem:** Called `planning_add_step` without valid session_id

**Solution:** 
1. Call `planning_initialize` first
2. Save the returned `sessionId`
3. Use that ID in subsequent calls

### Error: parent_id Required

**Problem:** Added child item (level > 0) without `parent_id`

**Solution:**
```python
# ❌ Wrong
{"id": "1.1", "level": 1, "title": "Task"}

# ✅ Correct
{"id": "1.1", "level": 1, "parent_id": "1.0", "title": "Task"}
```

### Error: Parent Not Found

**Problem:** Referenced non-existent parent_id

**Solution:** Add parent before children
```python
# ❌ Wrong order
wbs_items=[
    {"id": "1.1", "parent_id": "1.0", ...},  # Parent doesn't exist yet!
    {"id": "1.0", ...}
]

# ✅ Correct order
wbs_items=[
    {"id": "1.0", ...},  # Parent first
    {"id": "1.1", "parent_id": "1.0", ...}  # Then children
]
```

### WBS.md File Not Updating

**Check:**
1. Session status is "active" (not "completed")
2. Output path is accessible and writable
3. No file permission issues

### Sessions Lost After Server Restart

**Note:** Sessions are stored in memory. WBS.md files persist to disk, but session metadata is lost on restart.

**Solution:** Use `planning_list` to find existing sessions, or re-initialize if needed.

## Technical Details

### File Storage

- **Location:** `output/planning/` (configurable via `PlanningConfig.PLANNING_OUTPUT_DIR`)
- **Format:** Markdown with checkboxes
- **Naming:** `{project_name}_WBS.md`
- **Encoding:** UTF-8

### Session Management

- **Storage:** In-memory dictionary
- **ID Format:** `planning_{timestamp}_{random}`
- **Lifetime:** Until server restart
- **Concurrency:** Thread-safe within single server instance

### Validation

- **Required fields:** id, title, level, priority
- **Optional fields:** description, dependencies, order, parent_id
- **Constraints:** 
  - level >= 0
  - priority in ["High", "Medium", "Low"]
  - parent_id required when level > 0
  - No circular dependencies

## Summary

The new multi-action planning architecture provides:

✅ **Progressive file updates** - No context loss  
✅ **Clear action flow** - Better LLM guidance  
✅ **Simpler interfaces** - Easier to use  
✅ **Better performance** - Works with weaker LLMs  
✅ **Modular design** - Easier to maintain  

Use this architecture for all new planning workflows!
