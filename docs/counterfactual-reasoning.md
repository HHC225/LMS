# Counterfactual Reasoning Tool

## Overview

The Counterfactual Reasoning tool provides advanced analytical capabilities for exploring alternative scenarios through systematic "what-if" analysis. By examining how different conditions would lead to different outcomes, this tool helps identify root causes, predict future scenarios, prevent risks, and discover optimization opportunities.

## Features

- **4-Phase Systematic Analysis**: Structured approach from actual state to final insights
- **4 Reasoning Types**: Diagnostic, Predictive, Preventive, and Optimization perspectives
- **Deep Reasoning Levels**: 4 levels of analysis depth (Direct, Ripple, Multidimensional, Long-term)
- **Core Principles**: Minimal Change, Causal Consistency, and Proximity
- **Comparative Analysis**: Integrated insights across all scenario types
- **Session Management**: Track multiple analysis sessions with complete history

## Architecture

### Counterfactual Reasoning Process

```
Phase 1: Actual State Analysis
    ↓
Phase 2: Counterfactual Scenarios (4 types)
    ↓
Phase 3: Deep Reasoning (for each type)
    ↓
Phase 4: Comparative Analysis & Insights
```

### 4 Reasoning Types

1. **Diagnostic (진단적)**
   - Purpose: Root cause identification
   - Question: "What if [key factor] was different?"
   - Use: Understand why something happened

2. **Predictive (예측적)**
   - Purpose: Future scenario prediction
   - Question: "What if [current trend] continues?"
   - Use: Anticipate future situations

3. **Preventive (예방적)**
   - Purpose: Risk prevention
   - Question: "What if [potential problem] occurs?"
   - Use: Identify and mitigate risks

4. **Optimization (최적화)**
   - Purpose: Improvement exploration
   - Question: "What if [alternative method] is used?"
   - Use: Find better approaches

## Tools

### 1. counterfactual_initialize

Initialize a new Counterfactual Reasoning session.

**Parameters:**
- `problem` (str): The problem or situation to analyze

**Returns:**
- `session_id`: Unique session identifier
- `workflow`: Overview of the 4-phase process
- `next_action`: Instructions for Phase 1

**Example:**
```python
result = await counterfactual_initialize(
    problem="Database outage caused 2-hour service disruption affecting 10,000 users"
)
```

### 2. counterfactual_phase1

Phase 1: Analyze actual state and causal relationships.

**Parameters:**
- `session_id` (str): Session ID from initialize
- `analysis` (dict): Phase 1 analysis containing:
  - `current_state`: Description of what happened, conditions, and outcomes
  - `causal_chain`: Root causes, intermediate processes, and final results

**Returns:**
- `phase1_result`: Stored analysis result
- `llm_instructions`: Detailed instructions for Phase 2
- `next_action`: Call Phase 2

**Example:**
```python
result = await counterfactual_phase1(
    session_id="cf_1234567890_abcd1234",
    analysis={
        "current_state": {
            "what_happened": "Database server crashed due to memory exhaustion",
            "existing_conditions": [
                "High traffic during peak hours",
                "No automatic failover configured",
                "Limited monitoring alerts"
            ],
            "outcomes": [
                "Service completely unavailable for 2 hours",
                "10,000 users affected",
                "Revenue loss estimated at $50,000"
            ]
        },
        "causal_chain": {
            "root_causes": [
                "Insufficient memory allocation",
                "Missing connection pool limits",
                "No load balancing"
            ],
            "intermediate_processes": [
                "Connection pool exhaustion",
                "Memory leaks accumulated",
                "Server became unresponsive"
            ],
            "final_results": [
                "Application errors across all services",
                "Customer complaints surge",
                "Emergency intervention required"
            ]
        }
    }
)
```

### 3. counterfactual_phase2

Phase 2: Generate 4 types of counterfactual scenarios and WAIT for user selection.

**Parameters:**
- `session_id` (str): Session ID
- `scenarios` (dict): All 4 scenario types with:
  - `changed_condition`: What was changed
  - `counterfactual_scenario`: Detailed scenario description
  - `logical_consistency`: Consistency verification

**Returns:**
- `status`: "awaiting_user_selection"
- `scenarios_created`: Number of scenarios (4)
- `scenarios`: All 4 scenario summaries
- `message`: Formatted display of all 4 scenarios
- `next_action`: "wait_for_user_then_call_submit_selection"
- `available_tool`: "counterfactual_submit_selection"

**⚠️ IMPORTANT:** Phase 2 STOPS here and waits for user to select which type to analyze

**Example:**
```python
result = await counterfactual_phase2(
    session_id="cf_1234567890_abcd1234",
    scenarios={
        "diagnostic": {
            "changed_condition": "If we had automatic failover configured",
            "counterfactual_scenario": "Secondary database would have taken over immediately, reducing downtime from 2 hours to approximately 5 minutes",
            "logical_consistency": "Failover systems are proven technology, response time is realistic"
        },
        "predictive": {
            "changed_condition": "If current traffic growth trend continues (20% monthly)",
            "counterfactual_scenario": "Within 3 months, we'll face similar outages weekly without infrastructure scaling",
            "logical_consistency": "Linear extrapolation based on observed growth pattern"
        },
        "preventive": {
            "changed_condition": "If another critical service fails simultaneously",
            "counterfactual_scenario": "Cascading failure could extend outage to 6+ hours, affecting all business operations",
            "logical_consistency": "Historical data shows dependency chains between services"
        },
        "optimization": {
            "changed_condition": "If we implement microservices architecture with circuit breakers",
            "counterfactual_scenario": "Isolated failures wouldn't cascade, maintaining 90%+ service availability even during partial outages",
            "logical_consistency": "Microservices pattern is well-established for resilience"
        }
    }
)
```

### 4. counterfactual_submit_selection 🆕 NEW

Submit user's type selection after Phase 2.

**When to use:** After Phase 2 displays 4 scenarios and user responds with their choice.

**Parameters:**
- `session_id` (str): Session ID
- `selected_type_description` (str): User's natural language selection
  - Examples: "3", "preventive", "prevention", "The prevention scenario"

**Returns:**
- `status`: "selection_confirmed"
- `selected_type`: Parsed type (diagnostic/predictive/preventive/optimization)
- `type_name`: Human-readable type name
- `phase1_data`: Context from Phase 1
- `phase2_scenario`: The selected scenario details
- `next_step`: Instructions for Phase 3 analysis

**Example:**
```python
# User responds: "I want to analyze the prevention scenario"
result = await counterfactual_submit_selection(
    session_id="cf_1234567890_abcd1234",
    selected_type_description="prevention"
)

# Tool automatically:
# 1. Parses "prevention" → "preventive"
# 2. Validates the selection
# 3. Updates session phase
# 4. Returns Phase 3 instructions for deep reasoning
```

**Supported Selection Formats:**
- Numbers: "1", "2", "3", "4"
- Type names: "diagnostic", "predictive", "preventive", "optimization"
- Descriptive: "root cause", "future", "prevention", "improvement"
- Natural language: "The prevention one", "I want diagnostic", etc.

### 5. Phase 3: Deep Reasoning (4-Step Process) 🔥 NEW IN V3.0

Phase 3 is now broken into **4 separate steps** to prevent token limit issues and provide better control over the reasoning process. Each step builds on the previous one.

#### 5.1. counterfactual_phase3_step1

**Step 1/4: Apply 3 Core Principles**

Apply the 3 core principles to understand how the counterfactual scenario maintains logical consistency.

**Parameters:**
- `session_id` (str): Session ID
- `principles_applied` (dict): How each principle applies:
  - `minimal_change`: What minimal conditions were altered
  - `causal_consistency`: How logical connections are maintained
  - `proximity`: How scenario stays close to actual situation

**Returns:**
- `step1_result`: Principles analysis
- `current_step`: 1
- `total_steps`: 4
- `next_action`: Instructions for Step 2

**Example:**
```python
result = await counterfactual_phase3_step1(
    session_id="cf_1234567890_abcd1234",
    principles_applied={
        "minimal_change": "Added only automatic failover, keeping all other systems unchanged",
        "causal_consistency": "Failover follows logical detection → validation → switchover sequence",
        "proximity": "99% identical to actual setup, only adds proven failover technology"
    }
)
```

#### 5.2. counterfactual_phase3_step2

**Step 2/4: Direct Impact Analysis (Level 1)**

Analyze the immediate, direct impacts of the counterfactual scenario.

**Parameters:**
- `session_id` (str): Session ID
- `level1_direct` (str): Direct impact analysis focusing on:
  - Immediate technical impacts
  - First-order consequences
  - Instant observable effects

**Returns:**
- `step2_result`: Level 1 analysis
- `current_step`: 2
- `total_steps`: 4
- `next_action`: Instructions for Step 3

**Example:**
```python
result = await counterfactual_phase3_step2(
    session_id="cf_1234567890_abcd1234",
    level1_direct="""
    Direct Impact:
    - Automatic health check detects database failure within 10 seconds
    - Failover initiates immediately, switching traffic to secondary
    - Downtime reduced from 2 hours to 5 minutes
    - 99% of users avoid service disruption
    - Revenue loss reduced from $50k to $2k
    """
)
```

#### 5.3. counterfactual_phase3_step3

**Step 3/4: Ripple Effects & Multidimensional Analysis (Levels 2 & 3)**

Analyze secondary ripple effects and impacts across 4 dimensions.

**Parameters:**
- `session_id` (str): Session ID
- `level2_ripple` (str): Secondary cascade effects
- `level3_multidimensional` (dict): Impact across 4 dimensions:
  - `technical`: Technical system impacts
  - `organizational`: Team and process impacts
  - `cultural`: Communication and decision-making impacts
  - `external`: Customer and market impacts

**Returns:**
- `step3_result`: Levels 2 & 3 analysis
- `current_step`: 3
- `total_steps`: 4
- `next_action`: Instructions for Step 4

**Example:**
```python
result = await counterfactual_phase3_step3(
    session_id="cf_1234567890_abcd1234",
    level2_ripple="""
    Ripple Effects:
    - Operations team can focus on root cause analysis instead of emergency response
    - Reduced stress leads to better decision-making
    - Customer support handles fewer escalations
    - Monitoring improvements cascade to other services
    """,
    level3_multidimensional={
        "technical": "System becomes more resilient; health monitoring improves across infrastructure",
        "organizational": "Team gains confidence; incident procedures become more proactive",
        "cultural": "Shift from reactive firefighting to preventive architecture",
        "external": "Customer trust maintained; reputation for reliability strengthened"
    }
)
```

#### 5.4. counterfactual_phase3_step4

**Step 4/4: Long-term Evolution & Outcome Scenarios (Level 4) - FINAL STEP**

Analyze long-term evolution and generate 3 outcome scenarios. This completes Phase 3 and automatically provides Phase 4 instructions.

**Parameters:**
- `session_id` (str): Session ID
- `level4_longterm` (dict): Long-term projection:
  - `timeline`: 3-6-12 month timeline
  - `sustained_benefits`: What advantages persist
  - `new_challenges`: What problems emerge
  - `evolution`: How situation transforms
- `outcome_scenarios` (dict): 3 possible futures:
  - `best_case`: Everything goes optimally
  - `worst_case`: Problems compound
  - `most_likely`: Realistic balanced projection

**Returns:**
- `status`: "phase3_all_steps_complete"
- `complete_phase3_result`: All 4 steps assembled
- `steps_completed`: 4
- `next_action`: "AUTOMATIC_PHASE4"
- `message`: Phase 4 instructions

**Example:**
```python
result = await counterfactual_phase3_step4(
    session_id="cf_1234567890_abcd1234",
    level4_longterm={
        "timeline": "3mo: Full failover tested | 6mo: Multi-region | 12mo: Zero-downtime standard",
        "sustained_benefits": "96% downtime reduction sustained; $500k+ annual savings",
        "new_challenges": "Increased infrastructure costs; complexity in testing",
        "evolution": "From reactive to proactive; becomes industry best practice"
    },
    outcome_scenarios={
        "best_case": "Seamless failover every time; zero customer-facing incidents; industry recognition",
        "worst_case": "Occasional sync issues cause 15min delays; still 90% improvement",
        "most_likely": "5-minute failover becomes standard; rare edge cases addressed incrementally"
    }
)
```

**Phase 3 Workflow Summary:**
```
Step 1: Apply Principles (minimal_change, causal_consistency, proximity)
   ↓
Step 2: Direct Impact (level1_direct)
   ↓
Step 3: Ripple + Multidimensional (level2_ripple, level3_multidimensional)
   ↓
Step 4: Long-term + Outcomes (level4_longterm, outcome_scenarios)
   ↓
[Automatically assembles complete Phase 3 result and provides Phase 4 instructions]
```

### 6. counterfactual_phase4

Phase 4: Detailed comparative analysis for selected scenario type with professional formatted output.

**Parameters:**
- `session_id` (str): Session ID from counterfactual_initialize
- `selected_type` (str): **REQUIRED** - Type to analyze (diagnostic/predictive/preventive/optimization)
  - Can be passed as parameter OR included in comparative_analysis dict
- `comparative_analysis` (dict): Detailed analysis for selected type with:
  - `actual_vs_counterfactual`: What differs, why it differs, magnitude & importance
  - `key_insights`: Critical findings, causal factors, improvement opportunities
  - `action_recommendations`: Immediate (0-1mo), short-term (1-3mo), long-term (3-12mo) actions + monitoring metrics
  - `final_summary`: Key takeaway, expected impact, implementation timeline, next steps

**Returns:**
- `status`: "phase4_partial_complete" (more types remain) or "all_types_complete" (all done)
- `analyzed_type`: The type that was just analyzed
- `analyzed_types`: All types analyzed so far
- `remaining_types`: Types not yet analyzed (if any)
- `total_types_analyzed`: Count of completed analyses
- `detailed_report`: Professional formatted report with 4 sections
- `progress`: Current completion percentage
- `message`: Formatted output with detailed report and next steps

**Enhanced Output Features (V3.1):**
- ✅ **Section 1**: Actual vs Counterfactual Comparison with detailed breakdown
- ✅ **Section 2**: Key Insights & Findings with categorized discoveries
- ✅ **Section 3**: Action Recommendations & Roadmap with clear timelines
- ✅ **Section 4**: Executive Summary with quantified impact
- ✅ **Progress Status**: Visual progress indicator with completed/remaining types
- ✅ **Next Steps**: Clear instructions for continuing or completing analysis

**Example:**
```python
# Analyze only "diagnostic" type
result = await counterfactual_phase4(
    session_id="cf_1234567890_abcd1234",
    selected_type="diagnostic",  # ✨ NEW parameter
    comparative_analysis={  # ✨ CHANGED - only for diagnostic type
        "actual_vs_counterfactual": {
            "what_differs": "Downtime reduced from 2 hours to 5 minutes",
            "why_differs": "Automatic failover prevents extended manual recovery",
            "magnitude_importance": "96% reduction in downtime, $48k cost savings"
        },
        "key_insights": {
            "critical_findings": [
                "Lack of redundancy is single point of failure",
                "Manual intervention introduces significant delay"
            ],
            "causal_factors": [
                "Automatic failover: highest impact, moderate effort",
                "Enhanced monitoring: moderate impact, low effort"
            ],
            "improvement_opportunities": [
                "Implement database failover within 1-2 weeks",
                "Add memory alerts within 1 day"
            ]
        },
        "action_recommendations": {
            "immediate_actions": [
                "Set up secondary database instance",
                "Configure health check monitoring"
            ],
            "short_term_plans": [
                "Test failover procedure (1-2 weeks)",
                "Document runbook for operations team"
            ],
            "long_term_initiatives": [
                "Implement automatic capacity scaling",
                "Develop comprehensive disaster recovery plan"
            ],
            "monitoring_metrics": [
                "Database response time",
                "Connection pool utilization",
                "Failover trigger frequency"
            ]
        },
        "final_summary": {
            "key_takeaway": "Automatic failover would have prevented 96% of downtime",
            "expected_impact": "$48k cost savings, 10x improved user experience",
            "implementation_timeline": "1-2 weeks for basic failover, 3 months for full resilience",
            "next_steps": [
                "Get budget approval for secondary database",
                "Schedule implementation sprint",
                "Plan testing and rollout strategy"
            ]
        }
    }
)

# Response shows remaining types
# {
#   "status": "phase4_complete_partial",
#   "remaining_types": ["predictive", "preventive", "optimization"],
#   "message": "3 types remaining. Select another to continue..."
# }
```

### 6. counterfactual_get_result

Retrieve complete analysis results.

**Parameters:**
- `session_id` (str): Session ID

**Returns:**
Complete analysis including all phases, history, and metadata.

**Example:**
```python
result = await counterfactual_get_result(
    session_id="cf_1234567890_abcd1234"
)
```

### 7. counterfactual_reset

Reset or delete a session.

**Parameters:**
- `session_id` (str): Session ID to reset

**Returns:**
Reset confirmation message.

### 8. counterfactual_list_sessions

List all active sessions.

**Returns:**
List of all Counterfactual Reasoning sessions with metadata.

## Workflow Example

### Complete Analysis Flow

```python
# 1. Initialize session
init_result = await counterfactual_initialize(
    problem="Production database outage"
)
session_id = json.loads(init_result)["session_id"]

# 2. Phase 1: Analyze actual state
phase1_result = await counterfactual_phase1(
    session_id=session_id,
    analysis={
        "current_state": { /* analysis */ },
        "causal_chain": { /* causal relationships */ }
    }
)

# 3. Phase 2: Create counterfactual scenarios
phase2_result = await counterfactual_phase2(
    session_id=session_id,
    scenarios={
        "diagnostic": { /* what if different */ },
        "predictive": { /* what if continues */ },
        "preventive": { /* what if problem */ },
        "optimization": { /* what if alternative */ }
    }
)

# 4. Phase 3: Deep reasoning
phase3_result = await counterfactual_phase3(
    session_id=session_id,
    reasoning_results={
        "diagnostic": { /* deep analysis */ },
        "predictive": { /* deep analysis */ },
        "preventive": { /* deep analysis */ },
        "optimization": { /* deep analysis */ }
    }
)

# 5. Phase 4: Comparative analysis
phase4_result = await counterfactual_phase4(
    session_id=session_id,
    comparative_analysis={
        "type_comparisons": { /* comparisons */ },
        "actual_vs_counterfactual": { /* differences */ },
        "integrated_insights": { /* insights */ },
        "final_results_by_type": { /* results */ }
    }
)

# 6. Get complete results
final_result = await counterfactual_get_result(
    session_id=session_id
)
```

## Use Cases

### 1. Post-Incident Analysis
Understand what went wrong and how it could have been prevented.

### 2. Risk Assessment
Identify potential future problems and their impacts.

### 3. Decision Making
Evaluate different courses of action before committing.

### 4. Optimization Planning
Discover opportunities for improvement in existing systems.

### 5. Strategic Planning
Explore future scenarios and their implications.

## Best Practices

### 1. Phase 1 Analysis
- Be thorough in identifying current state
- Map complete causal chains
- Include all relevant conditions

### 2. Phase 2 Scenarios
- Ensure logical consistency
- Apply minimal change principle
- Keep scenarios realistic

### 3. Phase 3 Reasoning
- Analyze all 4 depth levels
- Consider multiple dimensions
- Develop multiple outcome scenarios

### 4. Phase 4 Insights
- Compare across all types
- Prioritize actions realistically
- Focus on actionable insights

## Configuration

Enable/disable in `configs/reasoning.py`:

```python
ENABLE_COUNTERFACTUAL_REASONING = True  # Set to False to disable
```

## Technical Details

### Session Storage
- Sessions stored in memory: `counterfactual_sessions` dictionary
- Persists during server runtime
- Lost on server restart

### Session Structure
```python
{
    "session_id": "cf_timestamp_uuid",
    "problem": "Problem statement",
    "phase": "initialized|phase1_complete|phase2_complete|phase3_complete|completed",
    "phase1_result": {...},
    "phase2_branches": {...},
    "phase3_results": {...},
    "phase4_analysis": {...},
    "created_at": timestamp,
    "updated_at": timestamp,
    "completed_at": timestamp,
    "history": [...]
}
```

### LLM Integration
- Tool provides structured prompts for LLM analysis
- LLM performs actual reasoning and analysis
- Tool manages session state and workflow
- Prompt chaining guides through 4 phases

## Error Handling

- Session validation before each phase
- Phase prerequisite checking
- Required field validation
- Detailed error messages

## Limitations

- Sessions stored in memory only
- No persistence across server restarts
- LLM-dependent analysis quality
- Requires systematic completion of all phases

## Related Tools

- **Sequential Thinking**: For step-by-step problem solving
- **Tree of Thoughts**: For exploring multiple solution paths
- **Recursive Thinking**: For iterative answer refinement

## Version History

- v2.0.0 (2025-10-23): **Major Refactoring** - Interactive per-type analysis to prevent token limits
- v1.0.0 (2025-01-23): Initial implementation with 4-phase analysis and 4 reasoning types

---

## V2.0 Refactoring (2025-10-23)

### What Changed

**Version 2.0 introduces a user-interactive, incremental analysis approach** that prevents token limit issues and improves user experience.

#### Key Improvements

1. **One Type at a Time**: Analyze scenario types individually instead of all 4 at once
2. **User Control**: Users select which types to analyze and in what order
3. **No Token Limits**: Smaller context per analysis prevents LLM token limit errors
4. **Incremental Progress**: Results saved after each type, no loss of work
5. **Flexible Workflow**: Analyze only needed types, stop anytime

### Breaking Changes

#### Phase 3 Signature Change
```python
# OLD (v1.0)
counterfactual_phase3(
    session_id: str,
    reasoning_results: Dict[str, Any],  # All 4 types
)

# NEW (v2.0)
counterfactual_phase3(
    session_id: str,
    selected_type: str,  # Single type: "diagnostic", "predictive", etc.
    reasoning_result: Dict[str, Any],  # Single type result
)
```

#### Phase 4 Signature Change
```python
# OLD (v1.0)
counterfactual_phase4(
    session_id: str,
    comparative_analysis: Dict[str, Any],  # All types
)

# NEW (v2.0)
counterfactual_phase4(
    session_id: str,
    selected_type: str,  # Single type
    comparative_analysis: Dict[str, Any],  # Single type analysis
)
```

#### Phase 2 Behavior Change
- **OLD**: Automatically generated Phase 3 instructions for all 4 types
- **NEW**: Displays all 4 types and waits for user selection

### New Workflow

```
┌─────────────────────────────────────────┐
│ Initialize → Phase 1 → Phase 2          │
│ (No changes - same as v1.0)             │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ Phase 2 Output:                         │
│ - Shows all 4 scenario types            │
│ - Returns status: awaiting_user_selection │
│ ⚠️  STOPS HERE - WAITS FOR USER         │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 🆕 User Responds with Selection          │
│ (e.g., "3", "preventive", "prevention") │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ 🆕 counterfactual_submit_selection       │
│ - Parses natural language input         │
│ - Validates selection                   │
│ - Updates session phase                 │
│ - Returns Phase 3 instructions          │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ Phase 3: Analyze selected type only     │
│ - Deep reasoning for one type           │
│ - Generates Phase 4 instructions        │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│ Phase 4: Compare selected type          │
│ - Analysis for one type                 │
│ - Checks remaining types                │
│ - Prompts user if more types remain     │
└────────────────┬────────────────────────┘
                 │
          ┌──────┴──────┐
          │             │
          ▼             ▼
  ┌─────────────┐  ┌──────────┐
  │ More types? │  │ Complete │
  │ Loop back   │  │          │
  │ to submit   │  │ get_result│
  └─────────────┘  └──────────┘
```

### Updated Examples

#### Example 1: Analyze Single Type

```python
# Initialize and complete Phase 1 & 2 (same as v1.0)
session_id = "cf_xxx"

# Phase 2 output shows 4 types, waits for selection
phase2_result = await counterfactual_phase2(session_id, scenarios)
# Output: Shows 4 scenarios, status="awaiting_user_selection"
# Message: "Which scenario type would you like to analyze?"

# 🆕 User responds: "I want to analyze the prevention scenario"
selection_result = await counterfactual_submit_selection(
    session_id=session_id,
    selected_type_description="prevention"  # Natural language
)
# Tool parses "prevention" → "preventive"
# Returns Phase 3 instructions

# Now proceed to Phase 3 with selected type
phase3_result = await counterfactual_phase3(
    session_id=session_id,
    reasoning_result={
        "type": "preventive",  # Must match selected type
        "principles_applied": {...},
        "reasoning_depth": {...},
        "outcome_scenarios": {...}
    }
)

# Phase 4 for selected type
phase4_result = await counterfactual_phase4(
    session_id=session_id,
    comparative_analysis={
        "actual_vs_counterfactual": {...},
        "key_insights": {...},
        "action_recommendations": {...},
        "final_summary": {...}
    }
)
# Output: "Type 'preventive' complete. 3 types remaining. Continue?"

# Get results (shows partial analysis)
result = await counterfactual_get_result(session_id)
```

#### Example 2: Analyze Multiple Types

```python
# After Phase 2
types_to_analyze = ["preventive", "diagnostic"]

for type_name in types_to_analyze:
    # 🆕 Submit selection for each type
    selection = await counterfactual_submit_selection(
        session_id=session_id,
        selected_type_description=type_name
    )
    
    # Phase 3 for this type
    await counterfactual_phase3(
        session_id=session_id,
        reasoning_result={
            "type": type_name,  # Must include type field
            ...  # LLM generates rest
        }
    )
    
    # Phase 4 for this type
    result = await counterfactual_phase4(
        session_id=session_id,
        comparative_analysis={...}  # LLM generates
    )
    
    print(f"✓ Completed {type_name}")
    print(f"Progress: {result['progress']['analyzed']}/4")

# Get complete results
final = await counterfactual_get_result(session_id)
```

### Updated Phase 4 Output Structure

#### When More Types Remain:
```json
{
  "status": "phase4_complete_partial",
  "phase": "phase2_complete_awaiting_selection",
  "completed_type": "preventive",
  "analyzed_types": ["preventive"],
  "remaining_types": ["diagnostic", "predictive", "optimization"],
  "progress": {
    "analyzed": 1,
    "total": 4,
    "percentage": 25
  },
  "next_action": "USER_SELECTION_REQUIRED",
  "message": "Phase 4 Complete for Preventive!\n\nRemaining types: diagnostic, predictive, optimization\n\nSelect another type to continue..."
}
```

#### When All Types Complete:
```json
{
  "status": "analysis_complete",
  "phase": "completed",
  "analyzed_types": ["preventive", "diagnostic", "predictive", "optimization"],
  "message": "🎉 All 4 types analyzed!\n\nCall counterfactual_get_result to retrieve complete analysis."
}
```

### Migration Guide for v1.0 Users

If you have existing code using v1.0:

1. **Update Phase 3 calls**:
   ```python
   # Add selected_type parameter
   # Change reasoning_results (plural) to reasoning_result (singular)
   await counterfactual_phase3(
       session_id=session_id,
       selected_type="diagnostic",  # ADD THIS
       reasoning_result={...}  # SINGULAR, not plural
   )
   ```

2. **Update Phase 4 calls**:
   ```python
   # Add selected_type parameter
   await counterfactual_phase4(
       session_id=session_id,
       selected_type="diagnostic",  # ADD THIS
       comparative_analysis={...}
   )
   ```

3. **Add user selection logic after Phase 2**:
   ```python
   # After Phase 2, don't automatically proceed to Phase 3
   # Show types to user and get selection
   phase2_result = await counterfactual_phase2(...)
   selected_type = user_selects_type()  # Your selection logic
   ```

4. **Handle remaining types after Phase 4**:
   ```python
   phase4_result = await counterfactual_phase4(...)
   
   if phase4_result["remaining_types"]:
       # Prompt user to select another type
       continue_analysis = ask_user_continue()
   ```

### Session Structure Changes

```python
# v2.0 Session Structure
{
    "session_id": "cf_xxx",
    "problem": "...",
    "phase": "phase2_complete_awaiting_selection",  # NEW phase state
    "phase1_result": {...},
    "phase2_scenarios": {...},  # Renamed from phase2_branches
    "analyzed_types": [],  # NEW: track analyzed types
    "phase3_results": {  # CHANGED: per-type storage
        "diagnostic": None,
        "predictive": None,
        "preventive": None,
        "optimization": None
    },
    "phase4_results": {  # CHANGED: per-type storage
        "diagnostic": None,
        "predictive": None,
        "preventive": None,
        "optimization": None
    },
    "created_at": timestamp,
    "updated_at": timestamp,
    "history": [...]
}
```

### Benefits of v2.0

| Aspect | v1.0 | v2.0 |
|--------|------|------|
| **Token Usage** | High (all 4 types) | Low (1 type at a time) |
| **Token Limit Errors** | Frequent | Rare |
| **User Control** | None (automatic) | Full (selective) |
| **Progress Loss Risk** | High | None (saved per type) |
| **Analysis Time** | Long (all at once) | Short (per type) |
| **Flexibility** | Low (must do all) | High (do what you need) |
| **LLM Quality** | Lower (too much context) | Higher (focused context) |

### Quick Reference

#### Valid Type Names
```python
"diagnostic"    # Type 1: Root cause identification
"predictive"    # Type 2: Future prediction  
"preventive"    # Type 3: Risk prevention
"optimization"  # Type 4: Improvement exploration
```

#### Type Selection Tips

| Your Goal | Recommended Type |
|-----------|-----------------|
| Understand what went wrong | **diagnostic** |
| Plan for future scenarios | **predictive** |
| Identify and prevent risks | **preventive** |
| Find improvement opportunities | **optimization** |

#### Progress Tracking
```python
# Check progress anytime
result = await counterfactual_get_result(session_id)
print(f"Analyzed: {result['analyzed_types']}")
print(f"Remaining: {result['remaining_types']}")
print(f"Progress: {result['total_types_analyzed']}/4")
```

### Error Messages (v2.0)

**"Invalid selected_type"**
- Use exact spelling: "diagnostic", "predictive", "preventive", "optimization"

**"Type 'X' has already been analyzed"**
- Select a different unanalyzed type

**"Phase 3 must be completed for type 'X' first"**
- Complete Phase 3 before Phase 4 for the same type

### Support

For v2.0 specific issues:
1. Verify you're using correct type names (exact spelling)
2. Check you completed phases in order for each type
3. Use `counterfactual_get_result` to check current progress
4. Review error messages carefully - they include helpful hints
