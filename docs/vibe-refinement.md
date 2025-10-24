# Vibe Refinement Tool Documentation

## Overview

The **Vibe Refinement Tool** is an advanced MCP tool designed to help transform vague, incomplete user prompts into concrete, actionable project specifications through structured, iterative refinement.

### Key Features

- ✅ **Automatic Specificity Assessment**: Analyzes prompts and calculates a specificity score (0-100)
- 🔄 **Two-Phase Refinement Process**: 
  - Phase 1: Idea Refinement (features, value proposition, user experience)
  - Phase 2: System/Architecture Refinement (tech stack, frameworks, deployment)
- 🤖 **LLM-Driven Suggestions**: Tool generates detailed instructions for LLM to create 5 contextual suggestions per step
- 👤 **User-Driven Progression**: Users select from suggestions to guide the refinement
- 📊 **Beautiful Reports**: Generates comprehensive, formatted final reports
- 💾 **Session Management**: Tracks multiple sessions with progress persistence

## How It Works

### Workflow

```
User Input (Vague)
    ↓
[1. Initialize Session]
    → Calculate specificity score
    → Determine steps needed (based on score)
    → Create session
    ↓
[2. Phase 1: Idea Refinement]
    → Get next step
    → LLM generates 5 suggestions
    → User selects one
    → Repeat for each idea step
    ↓
[3. Phase 2: System Refinement]
    → Get next step
    → LLM generates 5 technical approaches
    → User selects one
    → Repeat for each system step
    ↓
[4. Generate Final Report]
    → Compile all decisions
    → Format beautifully
    → Ready for implementation
```

### Specificity Scoring

The tool automatically analyzes prompts and scores them based on:

| Factor | Max Points | Description |
|--------|-----------|-------------|
| Length & Detail | 20 | More detailed prompts score higher |
| Technical Terms | 30 | Mentions of frameworks, languages, tools |
| Feature Descriptions | 25 | Specific features and functionality |
| Constraints | 15 | Requirements, performance needs |
| Concrete Details | 10 | UI elements, user roles, etc. |
| Vague Language | -10 | Penalty for words like "fun", "good", "nice" |

**Score Interpretation:**
- `0-10`: Extremely vague → 6 idea steps + 5 system steps (11 total)
- `10-20`: Very vague → 5 idea steps + 4 system steps (9 total)
- `20-35`: Vague → 4 idea steps + 3 system steps (7 total)
- `35-50`: Moderate-low → 3 idea steps + 3 system steps (6 total)
- `50-65`: Moderate → 2 idea steps + 2 system steps (4 total)
- `65-80`: Specific → 1 idea step + 2 system steps (3 total)
- `80-100`: Very specific → 0 idea steps + 2 system steps (2 total)

## API Reference

### Actions

#### 1. `vibe_refinement_initialize`

Start a new refinement session.

**Parameters:**
```python
initial_prompt: str  # User's initial prompt
```

**Returns:**
```json
{
  "success": true,
  "session_id": "vibe_1234567890_abcd1234",
  "analysis": {
    "specificity_score": 25,
    "score_interpretation": "Vague - needs clarification",
    "idea_steps_needed": 3,
    "system_steps_needed": 2,
    "total_steps": 5
  },
  "message": "Session initialized. Call 'get_next' to start refinement process.",
  "next_action": "get_next"
}
```

**Example:**
```python
result = await vibe_refinement_initialize(
    initial_prompt="I want to make a fun Tetris game"
)
```

---

#### 2. `vibe_refinement_get_next`

Get the next refinement step with LLM instructions.

**Parameters:**
```python
session_id: str  # Session ID from initialize
```

**Returns:**
```json
{
  "success": true,
  "action": "awaiting_suggestions",
  "session_id": "vibe_1234567890_abcd1234",
  "step_info": {
    "current_step": 1,
    "total_steps": 5,
    "phase": "idea",
    "question": "What is the core value proposition of your project?"
  },
  "llm_instructions": {
    "task": "Generate 5 creative ideas for refining: 'fun Tetris game'",
    "focus_area": "Core concept and unique value proposition",
    "context": { ... },
    "format_requirements": { ... },
    "guidelines": [ ... ],
    "example_format": { ... }
  },
  "message": "Step 1/5 (idea phase)\n\nQuestion: What is the core value proposition...",
  "next_action": "submit"
}
```

**What happens next:**
1. LLM reads `llm_instructions`
2. LLM generates 5 suggestions following the format
3. User reviews and selects one
4. User calls `vibe_refinement_submit` with selection

**Example:**
```python
result = await vibe_refinement_get_next(
    session_id="vibe_1234567890_abcd1234"
)
```

---

#### 3. `vibe_refinement_submit`

Submit user's selected suggestion.

**Parameters:**
```python
session_id: str
selected_suggestion: Dict[str, Any]
```

**Suggestion Format:**
```json
{
  "id": "sugg_2",
  "title": "Multiplayer Battle Royale Tetris",
  "description": "Transform classic Tetris into a competitive multiplayer experience where 100 players compete simultaneously. Last player standing wins. Features include power-ups, attack moves, and progressive difficulty.",
  "is_recommended": false
}
```

**Returns:**
```json
{
  "success": true,
  "action": "selection_recorded",
  "session_id": "vibe_1234567890_abcd1234",
  "message": "Selection recorded for step 1/5. Call 'get_next' to continue.",
  "next_action": "get_next",
  "progress": {
    "completed_steps": 1,
    "total_steps": 5,
    "percentage": 20
  }
}
```

**Example:**
```python
result = await vibe_refinement_submit(
    session_id="vibe_1234567890_abcd1234",
    selected_suggestion={
        "id": "sugg_2",
        "title": "Multiplayer Battle Royale Tetris",
        "description": "...",
        "is_recommended": False
    }
)
```

---

#### 4. `vibe_refinement_status`

Get current session status.

**Parameters:**
```python
session_id: str
```

**Returns:**
```json
{
  "success": true,
  "session_id": "vibe_1234567890_abcd1234",
  "status": "active",
  "phase": "system",
  "progress": {
    "current_step": 4,
    "total_steps": 5,
    "idea_steps": 3,
    "system_steps": 2,
    "completed_steps": 3,
    "percentage": 60
  },
  "initial_prompt": "I want to make a fun Tetris game",
  "specificity_score": 25,
  "created_at": "2025-10-19T10:30:00",
  "last_updated": "2025-10-19T10:45:00"
}
```

**Example:**
```python
result = await vibe_refinement_status(
    session_id="vibe_1234567890_abcd1234"
)
```

---

#### 5. `vibe_refinement_report`

Generate final refinement report.

**Parameters:**
```python
session_id: str
```

**Returns:**
```json
{
  "success": true,
  "session_id": "vibe_1234567890_abcd1234",
  "report": "# 🎯 Project Refinement Report\n\n**Generated:** 2025-10-19 10:50:00\n...",
  "summary": {
    "initial_prompt": "I want to make a fun Tetris game",
    "specificity_score": 25,
    "total_steps_completed": 5,
    "phases_completed": ["idea", "system"]
  }
}
```

**Report Contents:**
- 📝 Initial prompt and executive summary
- 📊 Specificity analysis with interpretation
- 💡 **Detailed** idea refinement decisions with:
  - Description and rationale
  - Key requirements (functional & non-functional)
  - Success criteria
  - Implementation guidance
- 🏗️ **Comprehensive** technical architecture decisions with:
  - Technical approach and justification
  - Implementation specifications
  - Technical and quality requirements
  - Infrastructure needs
- 🗺️ **Implementation roadmap** with 4 phases:
  - Foundation Setup
  - Core Feature Development
  - Integration & Polish
  - Deployment & Launch
- ✅ **WBS-ready specifications** with:
  - Clear work packages
  - Measurable deliverables
  - Success criteria
  - Next steps guidance

**Example:**
```python
result = await vibe_refinement_report(
    session_id="vibe_1234567890_abcd1234"
)
```

---

#### 6. `vibe_refinement_list`

List all active sessions.

**Parameters:**
```python
# No parameters required
```

**Returns:**
```json
{
  "success": true,
  "total_sessions": 3,
  "sessions": [
    {
      "session_id": "vibe_1234567890_abcd1234",
      "initial_prompt": "I want to make a fun Tetris game",
      "status": "completed",
      "phase": "completed",
      "current_step": 5,
      "total_steps": 5,
      "created_at": "2025-10-19T10:30:00"
    },
    ...
  ]
}
```

**Example:**
```python
result = await vibe_refinement_list()
```

---

## Complete Usage Example

### Scenario: User wants to build a "fun Tetris game"

```python
# Step 1: Initialize
init_result = await vibe_refinement_initialize(
    initial_prompt="I want to make a fun Tetris game"
)
# → Returns session_id and analysis
# → Score: 25 (vague)
# → Needs: 3 idea steps + 2 system steps = 5 total

session_id = init_result['session_id']

# Step 2: Get first question
next_result = await vibe_refinement_get_next(session_id=session_id)
# → Question: "What is the core value proposition?"
# → LLM instructions with CRITICAL requirements to show ALL 5 suggestions + AI recommendation

# Step 3: LLM MUST generate ALL 5 suggestions + AI Recommendation
# The LLM will present:
# 1. ALL 5 suggestions with full details (sugg_1 through sugg_5)
# 2. THEN show "🤖 AI Recommendation" section explaining the recommended choice

# Example output structure:
"""
## 📋 Suggestion List

**id:** sugg_1
**title:** Classic Tetris with Modern Twist
**description:** [150-250 words detailed explanation...]
**is_recommended:** false

**id:** sugg_2
**title:** Multiplayer Battle Royale Tetris
**description:** [150-250 words detailed explanation...]
**is_recommended:** true

[... sugg_3, sugg_4, sugg_5 ...]

---

## 🤖 AI Recommendation

I recommend **Option sugg_2: Multiplayer Battle Royale Tetris**

**Why this option:**
- Unique competitive element increases engagement
- Scalable architecture supports many players
- Strong market differentiation

**Why other options are less suitable:**
- sugg_1: Too conventional, less engaging
- sugg_3: [reason]
[etc.]
"""

# Step 4: User selects suggestion 2
submit_result = await vibe_refinement_submit(
    session_id=session_id,
    selected_suggestion=suggestions[1]
)
# → Progress: 1/5 steps (20%)
# → Next action: get_next

# Step 5: Repeat for remaining steps
# ... (4 more iterations of get_next → LLM generates → submit)

# Step 6: Generate final report
report_result = await vibe_refinement_report(session_id=session_id)
# → Beautiful markdown report with all decisions
# → Ready for implementation or WBS creation
```

---

## Integration with Other Tools

### With Planning Tool

After refinement is complete:

```python
# 1. Get refined specification
report = await vibe_refinement_report(session_id=session_id)

# 2. Use as input for WBS planning
planning_result = await planning(
    problem_statement=report['report'],
    project_name="Multiplayer Battle Royale Tetris"
)
```

### With Report Generator

Export refinement report:

```python
# 1. Get refinement report
vibe_report = await vibe_refinement_report(session_id=session_id)

# 2. Create formal project proposal
final_report = await generate_report(
    input_data={
        "content": vibe_report['report'],
        "source_type": "vibe_refinement"
    }
)
```

---

## Configuration

Edit `/configs/vibe.py`:

```python
class VibeConfig:
    # Enable/Disable tool
    ENABLE_VIBE_CODING: bool = True
    
    # Max refinement stages
    MAX_REFINEMENT_STAGES: int = 10
    
    # Number of suggestions to generate (3-10)
    NUM_SUGGESTIONS: int = 5
    
    # Session timeout (seconds)
    SESSION_TIMEOUT: int = 3600
```

Environment variables:
```bash
export ENABLE_VIBE_CODING=true
export VIBE_NUM_SUGGESTIONS=5
export VIBE_MAX_STAGES=10
export VIBE_SESSION_TIMEOUT=3600
```

---

## Best Practices

### For LLM Suggestion Generation

⚠️ **CRITICAL REQUIREMENTS:**

1. **ALWAYS show ALL 5 suggestions FIRST** - Users need complete information to decide
   - Never skip suggestions or show only the recommendation
   - Each suggestion: 150-250 word description in natural language
   - Present as "Option 1", "Option 2", etc. (NOT "sugg_1", "sugg_2")
   - Mark recommended option with ⭐ *Recommended* (NOT "is_recommended: true")

2. **Use HUMAN-READABLE format** - NOT variable names:
   - ✅ Correct: "### **Option 1: Classic Web-First Approach**"
   - ❌ Wrong: "id: sugg_1" or "title: Classic Web-First"
   - ✅ Correct: "⭐ *Recommended*" next to title
   - ❌ Wrong: "is_recommended: true"
   - Write descriptions as natural paragraphs, not as "description: [text]"

3. **THEN show AI Recommendation section SEPARATELY** - After all 5 suggestions:
   ```
   ## 🤖 AI Recommendation
   
   I recommend **Option 2: [Title]**
   
   **Why I recommend this option:**
   - [Specific reason 1 based on context]
   - [Specific reason 2 about feasibility]
   - [Specific reason 3 about best practices]
   
   **Why other options are less suitable:**
   - **Option 1**: [Brief reason]
   - **Option 3**: [Brief reason]
   - [etc.]
   ```

4. **Follow the two-step structure strictly:**
   - Step 1: Present ALL 5 complete suggestions in human-readable format
   - Step 2: Add AI Recommendation section

5. **Read llm_instructions.CRITICAL_OUTPUT_FORMAT** - Contains exact structure requirements

6. **Be detailed** - Each description should be 150-250 words with clear benefits, approach, and considerations

7. **Be contextual** - Build upon previous decisions from context

8. **Be diverse** - Provide varied options across different approaches

9. **Make it professional** - Format like a business presentation, not like code or JSON output

### For Session Management

1. **Save session_id** - You'll need it for all subsequent calls
2. **Check progress** - Use status action to track completion
3. **Generate report early** - Can be called multiple times without penalty
4. **Document decisions** - Save important insights from suggestions

### For Best Results

1. **Start with clearer prompts** - Higher specificity = fewer steps
2. **Select thoughtfully** - Each selection guides future suggestions
3. **Complete all phases** - Don't skip system/architecture refinement
4. **Use reports** - Excellent starting point for planning and WBS

---

## Troubleshooting

### Session not found
```python
# Check if session exists
sessions = await vibe_refinement_list()
# Verify session_id is correct
```

### Invalid selection format
```python
# Ensure all required fields present
selection = {
    "id": "sugg_1",           # Required
    "title": "...",           # Required
    "description": "...",     # Required
    "is_recommended": False   # Required
}
```

### Steps not progressing
```python
# Check current status
status = await vibe_refinement_status(session_id=session_id)
# Verify you're calling actions in correct order:
# initialize → get_next → submit → get_next → submit → ... → report
```

---

## Architecture Notes

### Why LLM Generates Suggestions

The tool does NOT generate suggestions itself. Instead:

1. **Tool Role**: State management, workflow orchestration, score calculation
2. **LLM Role**: Creative suggestion generation based on tool's instructions
3. **User Role**: Selection and decision-making

This architecture ensures:
- ✅ Suggestions are contextual and creative (LLM strength)
- ✅ Workflow is structured and reliable (Tool strength)
- ✅ Decisions reflect user needs (User control)

### Session Storage

- Sessions stored in-memory (not persisted to disk)
- Lost on server restart
- Generate and save reports before restarting
- Future: Can add database persistence if needed

---

## Future Enhancements

Potential improvements:

- [ ] Database persistence for sessions
- [ ] Export to various formats (PDF, HTML, JSON)
- [ ] Collaborative refinement (multiple users)
- [ ] Integration with project management tools
- [ ] Custom refinement templates
- [ ] AI-powered suggestion evaluation
- [ ] Version control for refinement history

---

## Support

For issues or questions:
1. Check this documentation
2. Review example usage above
3. Examine `llm_instructions` in get_next response
4. Check server logs for detailed errors

---

**Last Updated:** October 19, 2025  
**Version:** 1.0.0  
**Status:** Production Ready
