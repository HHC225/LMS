"""
Counterfactual Reasoning Tool Implementation (4-Step Phase 3)
Advanced reasoning tool for exploring alternative scenarios through counterfactual analysis
with step-by-step Phase 3 execution to prevent token limit issues
"""
from typing import Dict, Any, Optional
from fastmcp import Context
import json
import uuid
import time
from ..base import ReasoningTool


# Shared session store for Counterfactual Reasoning
counterfactual_sessions: Dict[str, Dict[str, Any]] = {}


class CounterfactualInitializeTool(ReasoningTool):
    """Initialize a new Counterfactual Reasoning session"""
    
    def __init__(self):
        super().__init__(
            name="counterfactual_initialize",
            description="Initialize a new counterfactual reasoning session for analyzing alternative scenarios"
        )
    
    async def execute(
        self,
        problem: str,
        ctx: Optional[Context] = None
    ) -> str:
        """Initialize Counterfactual Reasoning session"""
        
        # Auto-generate unique session ID
        timestamp = str(int(time.time()))
        random_suffix = str(uuid.uuid4())[:8]
        session_id = f"cf_{timestamp}_{random_suffix}"
        
        counterfactual_sessions[session_id] = {
            "session_id": session_id,
            "problem": problem,
            "phase": "initialized",
            "phase1_result": None,
            "phase2_scenarios": None,
            "phase3_progress": {  # Track Phase 3 step-by-step progress
                "current_step": 0,  # 0=not started, 1-4=steps completed
                "step1_principles": None,
                "step2_level1": None,
                "step3_levels": None,  # level2 + level3
                "step4_complete": None  # level4 + outcomes
            },
            "phase3_result": None,  # Single result object after Phase 3 completion
            "phase4_result": None,  # Single result object after Phase 4 completion
            "created_at": time.time(),
            "updated_at": time.time(),
            "history": [{
                "action": "initialized",
                "timestamp": time.time(),
                "problem": problem
            }]
        }
        
        await self.log_execution(ctx, f"Initialized Counterfactual Reasoning session {session_id}")
        
        return json.dumps({
            "status": "initialized",
            "session_id": session_id,
            "problem": problem,
            "current_phase": "initialized",
            "next_action": "call counterfactual_phase1 to begin Phase 1: Actual State Analysis",
            "workflow": {
                "phase1": "Actual State Analysis - Understand current state and causal relationships",
                "phase2": "Counterfactual Scenarios - Create 4 types of alternative scenarios",
                "phase3": "Reasoning Process (4 Steps) - Deep analysis for each scenario type",
                "phase4": "Comparison & Insights - Compare all scenarios and extract insights"
            },
            "message": "Counterfactual Reasoning session initialized. Start with Phase 1 to analyze the actual state."
        }, indent=2, ensure_ascii=False)


class CounterfactualPhase1Tool(ReasoningTool):
    """Phase 1: Actual State Analysis"""
    
    def __init__(self):
        super().__init__(
            name="counterfactual_phase1",
            description="Phase 1: Analyze actual state and identify causal relationships"
        )
    
    async def execute(
        self,
        session_id: str,
        analysis: Dict[str, Any],
        ctx: Optional[Context] = None
    ) -> str:
        """Execute Phase 1: Actual State Analysis"""
        
        if session_id not in counterfactual_sessions:
            return json.dumps({"error": "Session not found. Call counterfactual_initialize first."}, ensure_ascii=False)
        
        session = counterfactual_sessions[session_id]
        
        if session["phase"] != "initialized":
            return json.dumps({
                "error": "Phase 1 can only be called after initialization.",
                "current_phase": session["phase"]
            }, ensure_ascii=False)
        
        # Validate analysis structure
        required_fields = ["current_state", "causal_chain"]
        missing_fields = [f for f in required_fields if f not in analysis]
        if missing_fields:
            return json.dumps({
                "error": f"Missing required fields: {missing_fields}",
                "required_fields": required_fields
            }, ensure_ascii=False)
        
        # Store Phase 1 result
        session["phase1_result"] = analysis
        session["phase"] = "phase1_complete"
        session["updated_at"] = time.time()
        session["history"].append({
            "action": "phase1_complete",
            "timestamp": time.time(),
            "analysis": analysis
        })
        
        await self.log_execution(ctx, f"Completed Phase 1 for session {session_id}")
        
        return json.dumps({
            "status": "phase1_complete",
            "session_id": session_id,
            "phase1_result": analysis,
            "next_action": "call counterfactual_phase2 to generate 4 counterfactual scenarios",
            "message": "Phase 1 Complete: Actual state analyzed. Proceed to Phase 2 to generate counterfactual scenarios."
        }, indent=2, ensure_ascii=False)


class CounterfactualPhase2Tool(ReasoningTool):
    """Phase 2: Counterfactual Scenario Generation - STOPS and waits for user selection"""
    
    def __init__(self):
        super().__init__(
            name="counterfactual_phase2",
            description="Phase 2: Generate 4 scenario types, display them to user, and WAIT for user to select which type to analyze. DO NOT proceed to Phase 3 automatically."
        )
    
    async def execute(
        self,
        session_id: str,
        scenarios: Dict[str, Any],
        ctx: Optional[Context] = None
    ) -> str:
        """Execute Phase 2: Generate counterfactual scenarios"""
        
        if session_id not in counterfactual_sessions:
            return json.dumps({"error": "Session not found. Call counterfactual_initialize first."}, ensure_ascii=False)
        
        session = counterfactual_sessions[session_id]
        
        if session["phase"] != "phase1_complete":
            return json.dumps({
                "error": "Phase 1 must be completed first.",
                "current_phase": session["phase"]
            }, ensure_ascii=False)
        
        # Validate all 4 types are present
        required_types = ["diagnostic", "predictive", "preventive", "optimization"]
        missing_types = [t for t in required_types if t not in scenarios]
        if missing_types:
            return json.dumps({
                "error": f"Missing scenario types: {missing_types}",
                "required_types": required_types
            }, ensure_ascii=False)
        
        # Store Phase 2 scenarios
        session["phase2_scenarios"] = scenarios
        session["phase"] = "phase2_complete"
        session["updated_at"] = time.time()
        session["history"].append({
            "action": "phase2_complete",
            "timestamp": time.time(),
            "scenarios": scenarios
        })
        
        await self.log_execution(ctx, f"Completed Phase 2 for session {session_id} with 4 scenario types")
        
        # Format scenario summaries
        scenario_summaries = []
        type_names = {
            "diagnostic": "Diagnostic (Root Cause Identification)",
            "predictive": "Predictive (Future Prediction)",
            "preventive": "Preventive (Risk Prevention)",
            "optimization": "Optimization (Improvement Exploration)"
        }
        
        for idx, (type_key, type_name) in enumerate(type_names.items(), 1):
            scenario = scenarios.get(type_key, {})
            summary = f"\n{idx}. **{type_name}**\n"
            summary += f"   - Changed Condition: {scenario.get('changed_condition', 'N/A')}\n"
            summary += f"   - Scenario: {scenario.get('counterfactual_scenario', 'N/A')[:150]}...\n"
            scenario_summaries.append(summary)
        
        selection_message = "".join(scenario_summaries)
        
        phase1_data = session.get("phase1_result")
        
        return json.dumps({
            "status": "phase2_complete",
            "session_id": session_id,
            "phase": "phase2_complete",
            "scenarios_created": 4,
            "scenarios": {
                "diagnostic": scenarios["diagnostic"],
                "predictive": scenarios["predictive"],
                "preventive": scenarios["preventive"],
                "optimization": scenarios["optimization"]
            },
            "message": f"""✅ Phase 2 Complete - 4 Counterfactual Scenarios Generated

{selection_message}

---

🔄 **Proceeding to Phase 3: Deep Reasoning Analysis (4 Steps)**

📋 **Context:**
Phase 1 Actual State:
{json.dumps(phase1_data, indent=2, ensure_ascii=False)}

All 4 Scenarios:
{json.dumps(scenarios, indent=2, ensure_ascii=False)}

---

**Step 1/4: Apply 3 Core Principles**

Apply these principles to analyze all scenarios together:

1. **Minimal Change**: Alter only a small number of conditions
2. **Causal Consistency**: Maintain logical causal connections  
3. **Proximity**: Keep the scenarios close to the actual situation

Analyze how each principle applies across all scenarios.

Call counterfactual_phase3_step1 with:
{{
    "session_id": "{session_id}",
    "principles_applied": {{
        "minimal_change": "Explain what minimal changes were made across scenarios...",
        "causal_consistency": "Explain how causal consistency is maintained...",
        "proximity": "Explain how scenarios stay close to actual..."
    }}
}}

This is Step 1 of 4. After each step, you'll receive instructions for the next step.""",
            "next_action": "call_counterfactual_phase3_step1"
        }, indent=2, ensure_ascii=False)


class CounterfactualPhase3Step1Tool(ReasoningTool):
    """Phase 3 Step 1: Apply 3 Core Principles to Selected Scenario"""
    
    def __init__(self):
        super().__init__(
            name="counterfactual_phase3_step1",
            description="Phase 3 Step 1: Apply the 3 core principles (Minimal Change, Causal Consistency, Proximity) to the selected counterfactual scenario"
        )
    
    async def execute(
        self,
        session_id: str,
        principles_applied: Dict[str, str],
        ctx: Optional[Context] = None
    ) -> str:
        """Execute Phase 3 Step 1: Apply principles"""
        
        if session_id not in counterfactual_sessions:
            return json.dumps({"error": "Session not found."}, ensure_ascii=False)
        
        session = counterfactual_sessions[session_id]
        progress = session["phase3_progress"]
        
        # Validate phase
        if session["phase"] != "phase2_complete":
            return json.dumps({
                "error": "Invalid phase. Must complete Phase 2 first.",
                "current_phase": session["phase"]
            }, ensure_ascii=False)
        
        # Validate principles_applied structure
        required_keys = ["minimal_change", "causal_consistency", "proximity"]
        missing_keys = [k for k in required_keys if k not in principles_applied]
        if missing_keys:
            return json.dumps({
                "error": f"Missing required principles: {missing_keys}",
                "required_keys": required_keys,
                "message": """Phase 3 Step 1 requires all 3 principles to be applied:
                
                principles_applied = {
                    "minimal_change": "How you altered minimal conditions...",
                    "causal_consistency": "How you maintained logical connections...",
                    "proximity": "How you kept scenario close to actual situation..."
                }"""
            }, ensure_ascii=False)
        
        # Store Step 1 result
        progress["step1_principles"] = principles_applied
        progress["current_step"] = 1
        session["phase"] = "phase3_step1_complete"
        session["updated_at"] = time.time()
        session["history"].append({
            "action": "phase3_step1_complete",
            "timestamp": time.time(),
            "principles": principles_applied
        })
        
        await self.log_execution(ctx, f"Phase 3 Step 1 complete for session {session_id}")
        
        return json.dumps({
            "status": "phase3_step1_complete",
            "session_id": session_id,
            "current_step": 1,
            "total_steps": 4,
            "step1_result": principles_applied,
            "next_action": "call counterfactual_phase3_step2",
            "message": f"""✅ Phase 3 Step 1 Complete - Principles Applied

📋 **Progress:** Step 1/4 completed

🔄 **Next Step:** Phase 3 Step 2 - Direct Impact Analysis (Level 1)

**Instructions for Step 2:**
Analyze the DIRECT and IMMEDIATE impacts across all counterfactual scenarios.
Focus on first-order effects that happen immediately when conditions change.

**What to analyze:**
- Immediate technical impacts across all scenarios
- Direct operational changes
- First-order consequences
- Instant observable effects

**Context from Step 1:**
Principles Applied: {json.dumps(principles_applied, indent=2, ensure_ascii=False)}

**All Scenarios:**
{json.dumps(session["phase2_scenarios"], indent=2, ensure_ascii=False)}

Call counterfactual_phase3_step2 with:
{{
    "session_id": "{session_id}",
    "level1_direct": "Your direct impact analysis here..."
}}"""
        }, indent=2, ensure_ascii=False)


class CounterfactualPhase3Step2Tool(ReasoningTool):
    """Phase 3 Step 2: Direct Impact Analysis (Reasoning Level 1)"""
    
    def __init__(self):
        super().__init__(
            name="counterfactual_phase3_step2",
            description="Phase 3 Step 2: Analyze direct and immediate impacts (Reasoning Depth Level 1)"
        )
    
    async def execute(
        self,
        session_id: str,
        level1_direct: str,
        ctx: Optional[Context] = None
    ) -> str:
        """Execute Phase 3 Step 2: Direct impact analysis"""
        
        if session_id not in counterfactual_sessions:
            return json.dumps({"error": "Session not found."}, ensure_ascii=False)
        
        session = counterfactual_sessions[session_id]
        progress = session["phase3_progress"]
        
        # Validate step progression
        if progress["current_step"] != 1:
            return json.dumps({
                "error": "Must complete Step 1 before Step 2",
                "current_step": progress["current_step"]
            }, ensure_ascii=False)
        
        # Store Step 2 result
        progress["step2_level1"] = level1_direct
        progress["current_step"] = 2
        session["phase"] = "phase3_step2_complete"
        session["updated_at"] = time.time()
        session["history"].append({
            "action": "phase3_step2_complete",
            "timestamp": time.time(),
            "level1": level1_direct
        })
        
        await self.log_execution(ctx, f"Phase 3 Step 2 complete for session {session_id}")
        
        return json.dumps({
            "status": "phase3_step2_complete",
            "session_id": session_id,
            "current_step": 2,
            "total_steps": 4,
            "step2_result": level1_direct,
            "next_action": "call counterfactual_phase3_step3",
            "message": f"""✅ Phase 3 Step 2 Complete - Direct Impact Analyzed

📋 **Progress:** Step 2/4 completed

🔄 **Next Step:** Phase 3 Step 3 - Ripple Effects & Multidimensional Analysis (Levels 2 & 3)

**Instructions for Step 3:**
Analyze RIPPLE EFFECTS and MULTIDIMENSIONAL impacts across all scenarios.

**Level 2 - Ripple Effects:**
- Secondary consequences that cascade from direct impacts
- How changes spread to related systems
- Interconnected effects

**Level 3 - Multidimensional Analysis:**
Analyze impacts across 4 dimensions:
1. **Technical:** System architecture, code, infrastructure changes
2. **Organizational:** Team structure, processes, workflows
3. **Cultural:** Team dynamics, communication, decision-making
4. **External:** Customer impact, market, partnerships

**Previous Context:**
Step 1 Principles: {json.dumps(progress["step1_principles"], indent=2, ensure_ascii=False)}
Step 2 Direct Impact: {level1_direct[:200]}...

Call counterfactual_phase3_step3 with:
{{
    "session_id": "{session_id}",
    "level2_ripple": "Ripple effects analysis...",
    "level3_multidimensional": {{
        "technical": "Technical dimension analysis...",
        "organizational": "Organizational dimension analysis...",
        "cultural": "Cultural dimension analysis...",
        "external": "External dimension analysis..."
    }}
}}"""
        }, indent=2, ensure_ascii=False)


class CounterfactualPhase3Step3Tool(ReasoningTool):
    """Phase 3 Step 3: Ripple Effects & Multidimensional Analysis (Levels 2 & 3)"""
    
    def __init__(self):
        super().__init__(
            name="counterfactual_phase3_step3",
            description="Phase 3 Step 3: Analyze ripple effects and multidimensional impacts (Reasoning Depth Levels 2 & 3)"
        )
    
    async def execute(
        self,
        session_id: str,
        level2_ripple: str,
        level3_multidimensional: Dict[str, str],
        ctx: Optional[Context] = None
    ) -> str:
        """Execute Phase 3 Step 3: Ripple and multidimensional analysis"""
        
        if session_id not in counterfactual_sessions:
            return json.dumps({"error": "Session not found."}, ensure_ascii=False)
        
        session = counterfactual_sessions[session_id]
        progress = session["phase3_progress"]
        
        # Validate step progression
        if progress["current_step"] != 2:
            return json.dumps({
                "error": "Must complete Step 2 before Step 3",
                "current_step": progress["current_step"]
            }, ensure_ascii=False)
        
        # Validate multidimensional structure
        required_dimensions = ["technical", "organizational", "cultural", "external"]
        missing_dimensions = [d for d in required_dimensions if d not in level3_multidimensional]
        if missing_dimensions:
            return json.dumps({
                "error": f"Missing dimensions: {missing_dimensions}",
                "required_dimensions": required_dimensions
            }, ensure_ascii=False)
        
        # Store Step 3 result
        progress["step3_levels"] = {
            "level2_ripple": level2_ripple,
            "level3_multidimensional": level3_multidimensional
        }
        progress["current_step"] = 3
        session["updated_at"] = time.time()
        session["history"].append({
            "action": "phase3_step3_complete",
            "timestamp": time.time(),
            "level2": level2_ripple,
            "level3": level3_multidimensional
        })
        
        session["phase"] = "phase3_step3_complete"
        await self.log_execution(ctx, f"Phase 3 Step 3 complete for session {session_id}")
        
        return json.dumps({
            "status": "phase3_step3_complete",
            "session_id": session_id,
            "current_step": 3,
            "total_steps": 4,
            "step3_result": {
                "level2_ripple": level2_ripple,
                "level3_multidimensional": level3_multidimensional
            },
            "next_action": "call counterfactual_phase3_step4",
            "message": f"""✅ Phase 3 Step 3 Complete - Ripple & Multidimensional Analysis Done

📋 **Progress:** Step 3/4 completed

🔄 **Next Step:** Phase 3 Step 4 (Final) - Long-term Evolution & Outcome Scenarios

**Instructions for Step 4:**

**Level 4 - Long-term Evolution:**
Analyze how all scenarios evolve over time:
- **Timeline:** 3-6-12 month projection
- **Sustained Benefits:** What advantages persist long-term?
- **New Challenges:** What problems emerge over time?
- **Evolution:** How does the situation transform?

**Outcome Scenarios:**
Project 3 possible futures:
1. **Best Case:** Everything goes optimally
2. **Worst Case:** Problems compound negatively
3. **Most Likely:** Realistic balanced projection

**Complete Reasoning Context:**
Step 1: {json.dumps(progress["step1_principles"], indent=2, ensure_ascii=False)}
Step 2: {progress["step2_level1"][:150]}...
Step 3: Ripple & Multidimensional (just completed)

Call counterfactual_phase3_step4 with:
{{
    "session_id": "{session_id}",
    "level4_longterm": {{
        "timeline": "Timeline projection...",
        "sustained_benefits": "Long-term benefits...",
        "new_challenges": "Emerging challenges...",
        "evolution": "How situation evolves..."
    }},
    "outcome_scenarios": {{
        "best_case": "Optimal outcome...",
        "worst_case": "Negative outcome...",
        "most_likely": "Realistic outcome..."
    }}
}}

This is the FINAL step of Phase 3. After completion, Phase 4 instructions will be provided automatically."""
        }, indent=2, ensure_ascii=False)


class CounterfactualPhase3Step4Tool(ReasoningTool):
    """Phase 3 Step 4: Long-term Evolution & Outcome Scenarios (Level 4) - Auto-triggers Phase 4"""
    
    def __init__(self):
        super().__init__(
            name="counterfactual_phase3_step4",
            description="Phase 3 Step 4: Analyze long-term evolution and generate outcome scenarios (Reasoning Depth Level 4). Completes Phase 3 and automatically provides Phase 4 instructions."
        )
    
    async def execute(
        self,
        session_id: str,
        level4_longterm: Dict[str, str],
        outcome_scenarios: Dict[str, str],
        ctx: Optional[Context] = None
    ) -> str:
        """Execute Phase 3 Step 4: Long-term and outcomes (FINAL STEP)"""
        
        if session_id not in counterfactual_sessions:
            return json.dumps({"error": "Session not found."}, ensure_ascii=False)
        
        session = counterfactual_sessions[session_id]
        progress = session["phase3_progress"]
        
        # Validate step progression
        if progress["current_step"] != 3:
            return json.dumps({
                "error": "Must complete Step 3 before Step 4",
                "current_step": progress["current_step"]
            }, ensure_ascii=False)
        
        # Validate level4 structure
        required_level4_keys = ["timeline", "sustained_benefits", "new_challenges", "evolution"]
        missing_level4 = [k for k in required_level4_keys if k not in level4_longterm]
        if missing_level4:
            return json.dumps({
                "error": f"Missing level4 keys: {missing_level4}",
                "required_keys": required_level4_keys
            }, ensure_ascii=False)
        
        # Validate outcome scenarios
        required_outcomes = ["best_case", "worst_case", "most_likely"]
        missing_outcomes = [o for o in required_outcomes if o not in outcome_scenarios]
        if missing_outcomes:
            return json.dumps({
                "error": f"Missing outcome scenarios: {missing_outcomes}",
                "required_outcomes": required_outcomes
            }, ensure_ascii=False)
        
        # Store Step 4 result
        progress["step4_complete"] = {
            "level4_longterm": level4_longterm,
            "outcome_scenarios": outcome_scenarios
        }
        progress["current_step"] = 4
        
        # Assemble complete Phase 3 result from all 4 steps
        complete_phase3_result = {
            "principles_applied": progress["step1_principles"],
            "reasoning_depth": {
                "level1_direct": progress["step2_level1"],
                "level2_ripple": progress["step3_levels"]["level2_ripple"],
                "level3_multidimensional": progress["step3_levels"]["level3_multidimensional"],
                "level4_longterm": level4_longterm
            },
            "outcome_scenarios": outcome_scenarios
        }
        
        # Store complete Phase 3 result
        session["phase3_result"] = complete_phase3_result
        session["phase"] = "phase3_complete"
        session["updated_at"] = time.time()
        session["history"].append({
            "action": "phase3_complete",
            "timestamp": time.time(),
            "complete_result": complete_phase3_result
        })
        
        await self.log_execution(ctx, f"Phase 3 complete for session {session_id}")
        
        phase4_instructions = f"""
✅ **Phase 3 Complete (All 4 Steps Done)**

📊 **Complete Phase 3 Analysis Summary:**

**Step 1 - Principles Applied:**
{json.dumps(progress["step1_principles"], indent=2, ensure_ascii=False)}

**Step 2 - Direct Impact:**
{progress["step2_level1"]}

**Step 3 - Ripple Effects:**
{progress["step3_levels"]["level2_ripple"]}

**Step 3 - Multidimensional:**
{json.dumps(progress["step3_levels"]["level3_multidimensional"], indent=2, ensure_ascii=False)}

**Step 4 - Long-term Evolution:**
{json.dumps(level4_longterm, indent=2, ensure_ascii=False)}

**Step 4 - Outcome Scenarios:**
{json.dumps(outcome_scenarios, indent=2, ensure_ascii=False)}

---

🔄 **Now Proceeding to Phase 4: Comparative Analysis**

**Phase 1 Actual State:**
{json.dumps(session["phase1_result"], indent=2, ensure_ascii=False)}

**All Phase 2 Scenarios:**
{json.dumps(session["phase2_scenarios"], indent=2, ensure_ascii=False)}

---

**Phase 4 Instructions:**

Compare the actual state (Phase 1) with all counterfactual scenarios and deep analysis (Phase 3) and provide:

## 1. Actual vs Counterfactual Comparison
- **What Differs:** Key differences between actual and counterfactual scenarios
- **Why It Differs:** Causal mechanisms behind differences
- **Magnitude & Importance:** Significance of changes

## 2. Key Insights
- **Critical Findings:** Most important discoveries across all scenarios
- **Causal Factors:** Key causal factors and leverage points
- **Improvement Opportunities:** Actionable improvements

## 3. Action Recommendations
- **Immediate Actions (0-1 month):** Quick wins
- **Short-term Plans (1-3 months):** Important improvements
- **Long-term Initiatives (3-12 months):** Strategic changes
- **Monitoring & Metrics:** What to track

## 4. Final Summary
- **Key Takeaway:** Single most important insight
- **Expected Impact:** Quantified impact
- **Implementation Timeline:** Realistic timeline
- **Next Steps:** Concrete actions

**IMPORTANT:** You must select which scenario type to analyze in Phase 4.
Available types: diagnostic, predictive, preventive, optimization

Call counterfactual_phase4 with:
{{
    "session_id": "{session_id}",
    "selected_type": "diagnostic",  // or predictive/preventive/optimization
    "comparative_analysis": {{
        "actual_vs_counterfactual": {{"what_differs": "...", "why_differs": "...", "magnitude_importance": "..."}},
        "key_insights": {{"critical_findings": [...], "causal_factors": [...], "improvement_opportunities": [...]}},
        "action_recommendations": {{"immediate_actions": [...], "short_term_plans": [...], "long_term_initiatives": [...], "monitoring_metrics": [...]}},
        "final_summary": {{"key_takeaway": "...", "expected_impact": "...", "implementation_timeline": "...", "next_steps": [...]}}
    }}
}}

After Phase 4 completion, you can analyze additional types by running Phase 3 & 4 again for different types.
"""
        
        return json.dumps({
            "status": "phase3_all_steps_complete",
            "session_id": session_id,
            "steps_completed": 4,
            "complete_phase3_result": complete_phase3_result,
            "next_action": "call_counterfactual_phase4",
            "message": phase4_instructions
        }, indent=2, ensure_ascii=False)


class CounterfactualPhase4Tool(ReasoningTool):
    """Phase 4: Comparative Analysis for Selected Type - checks for remaining types"""
    
    def __init__(self):
        super().__init__(
            name="counterfactual_phase4",
            description="Phase 4: Perform comparative analysis for the selected type. After completion, checks if more types remain and WAITS for user."
        )
    
    async def execute(
        self,
        session_id: str,
        comparative_analysis: Dict[str, Any],
        selected_type: Optional[str] = None,
        ctx: Optional[Context] = None
    ) -> str:
        """Execute Phase 4: Comparative analysis for selected scenario type
        
        Args:
            session_id: Session ID
            comparative_analysis: Detailed comparative analysis with all required sections
            selected_type: The scenario type being analyzed (diagnostic/predictive/preventive/optimization)
            ctx: FastMCP context
        """
        
        if session_id not in counterfactual_sessions:
            return json.dumps({"error": "Session not found."}, ensure_ascii=False)
        
        session = counterfactual_sessions[session_id]
        
        # Validate Phase 3 completion
        if session["phase"] != "phase3_complete":
            return json.dumps({
                "error": "Phase 3 must be completed first.",
                "current_phase": session["phase"]
            }, ensure_ascii=False)
        
        # Validate selected_type
        valid_types = ["diagnostic", "predictive", "preventive", "optimization"]
        if selected_type and selected_type not in valid_types:
            return json.dumps({
                "error": f"Invalid selected_type: {selected_type}",
                "valid_types": valid_types,
                "message": "selected_type must be one of: diagnostic, predictive, preventive, optimization"
            }, ensure_ascii=False)
        
        # Extract type from comparative_analysis if not provided as parameter
        if not selected_type:
            selected_type = comparative_analysis.get("type") or comparative_analysis.get("scenario_type")
            if not selected_type:
                return json.dumps({
                    "error": "selected_type must be provided either as parameter or in comparative_analysis dict",
                    "valid_types": valid_types,
                    "message": "Please include 'type' field in comparative_analysis or pass selected_type parameter"
                }, ensure_ascii=False)
        
        # Initialize analyzed_types if not exists
        if "analyzed_types" not in session:
            session["analyzed_types"] = []
        
        # Check if type already analyzed
        if selected_type in session["analyzed_types"]:
            return json.dumps({
                "warning": f"Type '{selected_type}' has already been analyzed.",
                "analyzed_types": session["analyzed_types"],
                "message": "This scenario type was already analyzed. You can still re-analyze it, but previous results will be overwritten."
            }, ensure_ascii=False)
        
        # Validate comparative_analysis structure
        required_sections = ["actual_vs_counterfactual", "key_insights", "action_recommendations", "final_summary"]
        missing_sections = [s for s in required_sections if s not in comparative_analysis]
        if missing_sections:
            return json.dumps({
                "error": f"Missing required sections in comparative_analysis: {missing_sections}",
                "required_sections": required_sections,
                "message": """comparative_analysis must include:
                - actual_vs_counterfactual: Detailed comparison
                - key_insights: Critical findings and opportunities
                - action_recommendations: Immediate to long-term actions
                - final_summary: Key takeaway and expected impact"""
            }, ensure_ascii=False)
        
        # Store Phase 4 result for this type
        if "phase4_results" not in session:
            session["phase4_results"] = {}
        
        session["phase4_results"][selected_type] = {
            "type": selected_type,
            "analysis": comparative_analysis,
            "analyzed_at": time.time()
        }
        
        # Add to analyzed types
        session["analyzed_types"].append(selected_type)
        session["updated_at"] = time.time()
        session["history"].append({
            "action": f"phase4_complete_{selected_type}",
            "timestamp": time.time(),
            "type": selected_type,
            "comparative_analysis": comparative_analysis
        })
        
        await self.log_execution(ctx, f"Phase 4 complete for type '{selected_type}' in session {session_id}")
        
        # Check for remaining types
        remaining_types = [t for t in valid_types if t not in session["analyzed_types"]]
        
        # Generate detailed analysis report for this type
        type_names = {
            "diagnostic": "Diagnostic Analysis (Root Cause Identification)",
            "predictive": "Predictive Analysis (Future Prediction)",
            "preventive": "Preventive Analysis (Risk Prevention)",
            "optimization": "Optimization Analysis (Improvement Exploration)"
        }
        
        detailed_report = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 PHASE 4 DETAILED COMPARATIVE ANALYSIS REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **Scenario Type:** {type_names.get(selected_type, selected_type)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 SECTION 1: ACTUAL VS COUNTERFACTUAL COMPARISON
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**What Differs:**
{comparative_analysis["actual_vs_counterfactual"].get("what_differs", "Not specified")}

**Why It Differs:**
{comparative_analysis["actual_vs_counterfactual"].get("why_differs", "Not specified")}

**Magnitude & Importance:**
{comparative_analysis["actual_vs_counterfactual"].get("magnitude_importance", "Not specified")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 SECTION 2: KEY INSIGHTS & FINDINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Critical Findings:**
{self._format_list(comparative_analysis["key_insights"].get("critical_findings", []))}

**Causal Factors & Leverage Points:**
{self._format_list(comparative_analysis["key_insights"].get("causal_factors", []))}

**Improvement Opportunities:**
{self._format_list(comparative_analysis["key_insights"].get("improvement_opportunities", []))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 SECTION 3: ACTION RECOMMENDATIONS & ROADMAP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**🚀 Immediate Actions (0-1 month):**
{self._format_list(comparative_analysis["action_recommendations"].get("immediate_actions", []))}

**📅 Short-term Plans (1-3 months):**
{self._format_list(comparative_analysis["action_recommendations"].get("short_term_plans", []))}

**🎯 Long-term Initiatives (3-12 months):**
{self._format_list(comparative_analysis["action_recommendations"].get("long_term_initiatives", []))}

**📊 Monitoring & Metrics:**
{self._format_list(comparative_analysis["action_recommendations"].get("monitoring_metrics", []))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 SECTION 4: EXECUTIVE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**💎 Key Takeaway:**
{comparative_analysis["final_summary"].get("key_takeaway", "Not specified")}

**📈 Expected Impact:**
{comparative_analysis["final_summary"].get("expected_impact", "Not specified")}

**⏱️ Implementation Timeline:**
{comparative_analysis["final_summary"].get("implementation_timeline", "Not specified")}

**✅ Next Steps:**
{self._format_list(comparative_analysis["final_summary"].get("next_steps", []))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        if remaining_types:
            # More types to analyze
            session["phase"] = "phase4_partial"
            
            remaining_names = [type_names.get(t, t) for t in remaining_types]
            
            result = {
                "status": "phase4_partial_complete",
                "session_id": session_id,
                "analyzed_type": selected_type,
                "analyzed_types": session["analyzed_types"],
                "remaining_types": remaining_types,
                "total_types": len(valid_types),
                "progress": f"{len(session['analyzed_types'])}/{len(valid_types)} types analyzed",
                "detailed_report": detailed_report,
                "message": f"""✅ Phase 4 Analysis Complete for '{type_names.get(selected_type, selected_type)}'

{detailed_report}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 PROGRESS STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Completed Analysis:** {len(session['analyzed_types'])}/{len(valid_types)} scenario types

✅ **Analyzed Types:**
{self._format_list([type_names.get(t, t) for t in session['analyzed_types']])}

⏳ **Remaining Types:**
{self._format_list(remaining_names)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Option 1: Continue Analysis**
To analyze another scenario type, repeat Phase 3 & 4 for one of the remaining types:
{self._format_list(remaining_types)}

1. Select a type from remaining types
2. Run Phase 3 (4 steps) for that type
3. Run Phase 4 for that type

**Option 2: Complete Session**
If you want to end the analysis now, call:
counterfactual_get_result(session_id="{session_id}")

This will retrieve all completed analyses so far.
"""
            }
        else:
            # All types analyzed - session complete
            session["phase"] = "completed"
            session["completed_at"] = time.time()
            duration = session["completed_at"] - session["created_at"]
            
            result = {
                "status": "all_types_complete",
                "session_id": session_id,
                "analyzed_type": selected_type,
                "analyzed_types": session["analyzed_types"],
                "total_types_analyzed": len(session["analyzed_types"]),
                "duration_seconds": round(duration, 2),
                "detailed_report": detailed_report,
                "message": f"""🎉 COMPLETE COUNTERFACTUAL REASONING ANALYSIS FINISHED!

{detailed_report}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ FINAL STATUS - ALL SCENARIO TYPES ANALYZED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Total Types Analyzed:** {len(session['analyzed_types'])}/{len(valid_types)}

**Completed Analyses:**
{self._format_list([type_names.get(t, t) for t in session['analyzed_types']])}

**Total Duration:** {round(duration, 2)} seconds

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 RETRIEVE COMPLETE RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Call counterfactual_get_result(session_id="{session_id}") to retrieve:
- All Phase 1-3 analysis results
- Complete Phase 4 comparative analyses for all {len(session['analyzed_types'])} types
- Full reasoning history and timeline
- Comprehensive insights and recommendations across all scenarios
"""
            }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    def _format_list(self, items: list) -> str:
        """Format list items with bullet points"""
        if not items:
            return "  (None specified)"
        return "\n".join([f"  • {item}" for item in items])


class CounterfactualGetResultTool(ReasoningTool):
    """Get complete counterfactual reasoning analysis results"""
    
    def __init__(self):
        super().__init__(
            name="counterfactual_get_result",
            description="Retrieve complete counterfactual reasoning analysis results"
        )
    
    async def execute(
        self,
        session_id: str,
        ctx: Optional[Context] = None
    ) -> str:
        """Get complete results including all analyzed scenario types"""
        
        if session_id not in counterfactual_sessions:
            return json.dumps({"error": "Session not found."}, ensure_ascii=False)
        
        session = counterfactual_sessions[session_id]
        
        # Prepare Phase 4 results (support both old and new format)
        phase4_data = session.get("phase4_results", {})
        if not phase4_data and session.get("phase4_result"):
            # Old format - single result
            phase4_data = {"legacy": session.get("phase4_result")}
        
        result = {
            "session_id": session_id,
            "status": session["phase"],
            "problem": session["problem"],
            "phase1_actual_state": session.get("phase1_result"),
            "phase2_scenarios": session.get("phase2_scenarios"),
            "phase3_reasoning": session.get("phase3_result"),
            "phase4_comparative_analyses": phase4_data,
            "analyzed_types": session.get("analyzed_types", []),
            "total_types_analyzed": len(session.get("analyzed_types", [])),
            "duration_seconds": round(session.get("completed_at", time.time()) - session["created_at"], 2) if session.get("completed_at") else None,
            "history": session["history"]
        }
        
        await self.log_execution(ctx, f"Retrieved results for session {session_id}")
        
        return json.dumps(result, indent=2, ensure_ascii=False)


class CounterfactualResetTool(ReasoningTool):
    """Reset or delete a counterfactual reasoning session"""
    
    def __init__(self):
        super().__init__(
            name="counterfactual_reset",
            description="Reset or delete a counterfactual reasoning session"
        )
    
    async def execute(
        self,
        session_id: str,
        ctx: Optional[Context] = None
    ) -> str:
        """Reset session"""
        
        if session_id not in counterfactual_sessions:
            return json.dumps({"error": "Session not found."}, ensure_ascii=False)
        
        del counterfactual_sessions[session_id]
        
        await self.log_execution(ctx, f"Reset session {session_id}")
        
        return json.dumps({
            "status": "session_deleted",
            "session_id": session_id,
            "message": "Session deleted successfully."
        }, ensure_ascii=False)


class CounterfactualListSessionsTool(ReasoningTool):
    """List all active counterfactual reasoning sessions"""
    
    def __init__(self):
        super().__init__(
            name="counterfactual_list_sessions",
            description="List all active counterfactual reasoning sessions"
        )
    
    async def execute(
        self,
        ctx: Optional[Context] = None
    ) -> str:
        """List sessions"""
        
        if not counterfactual_sessions:
            return json.dumps({
                "total_sessions": 0,
                "sessions": [],
                "message": "No active sessions."
            }, ensure_ascii=False)
        
        sessions_list = []
        for session_id, session in counterfactual_sessions.items():
            sessions_list.append({
                "session_id": session_id,
                "problem": session["problem"][:50] + "..." if len(session["problem"]) > 50 else session["problem"],
                "phase": session["phase"],
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(session["created_at"]))
            })
        
        return json.dumps({
            "total_sessions": len(sessions_list),
            "sessions": sessions_list
        }, indent=2, ensure_ascii=False)

