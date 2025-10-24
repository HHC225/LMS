"""
Counterfactual Reasoning Wrapper
Wrapper functions for Counterfactual Reasoning tools
"""
from typing import Dict, Any, Optional
from fastmcp import Context
import json
from src.tools.reasoning.counterfactual_reasoning_tool import (
    CounterfactualInitializeTool,
    CounterfactualPhase1Tool,
    CounterfactualPhase2Tool,
    CounterfactualPhase3Step1Tool,
    CounterfactualPhase3Step2Tool,
    CounterfactualPhase3Step3Tool,
    CounterfactualPhase3Step4Tool,
    CounterfactualPhase3Step5Tool,
    CounterfactualPhase4Tool,
    CounterfactualGetResultTool,
    CounterfactualResetTool,
    CounterfactualListSessionsTool
)


# Initialize tool instances
_initialize_tool = CounterfactualInitializeTool()
_phase1_tool = CounterfactualPhase1Tool()
_phase2_tool = CounterfactualPhase2Tool()
_phase3_step1_tool = CounterfactualPhase3Step1Tool()
_phase3_step2_tool = CounterfactualPhase3Step2Tool()
_phase3_step3_tool = CounterfactualPhase3Step3Tool()
_phase3_step4_tool = CounterfactualPhase3Step4Tool()
_phase3_step5_tool = CounterfactualPhase3Step5Tool()
_phase4_tool = CounterfactualPhase4Tool()
_get_result_tool = CounterfactualGetResultTool()
_reset_tool = CounterfactualResetTool()
_list_sessions_tool = CounterfactualListSessionsTool()


async def counterfactual_initialize(
    problem: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Initialize a new Counterfactual Reasoning session.
    
    This tool starts counterfactual analysis for exploring alternative scenarios
    through systematic reasoning across 4 phases.
    
    Args:
        problem: The problem or situation to analyze
        ctx: FastMCP context for logging
    
    Returns:
        JSON string with session_id and next action instructions
    
    Example:
        result = await counterfactual_initialize(
            problem="Database outage caused 2-hour service disruption"
        )
    """
    return await _initialize_tool.execute(problem=problem, ctx=ctx)


async def counterfactual_phase1(
    session_id: str,
    analysis: Dict[str, Any],
    ctx: Optional[Context] = None
) -> str:
    """
    Phase 1: Actual State Analysis.
    
    Analyze the current/actual state and identify causal relationships.
    
    Args:
        session_id: Session ID from counterfactual_initialize
        analysis: Phase 1 analysis result containing:
            - current_state: Current state description
            - causal_chain: Causal relationships
        ctx: FastMCP context for logging
    
    Returns:
        JSON string with Phase 1 result and Phase 2 instructions
    
    Example:
        result = await counterfactual_phase1(
            session_id="cf_1234567890_abcd1234",
            analysis={
                "current_state": {
                    "what_happened": "Database server crashed",
                    "existing_conditions": ["High load", "No backup"],
                    "outcomes": ["Service down", "Data loss risk"]
                },
                "causal_chain": {
                    "root_causes": ["Insufficient capacity"],
                    "intermediate_processes": ["Connection pool exhausted"],
                    "final_results": ["Application errors"]
                }
            }
        )
    """
    return await _phase1_tool.execute(
        session_id=session_id,
        analysis=analysis,
        ctx=ctx
    )


async def counterfactual_phase2(
    session_id: str,
    scenarios: Dict[str, Any],
    selected_type: Optional[str] = None,
    ctx: Optional[Context] = None
) -> str:
    """
    Phase 2: Counterfactual Scenario Generation.
    
    Generate 4 types of counterfactual scenarios and automatically select in sequence:
    1st call: Diagnostic (Root cause identification)
    2nd call: Predictive (Future prediction)
    3rd call: Preventive (Risk prevention)
    4th call: Optimization (Improvement exploration)
    
    Args:
        session_id: Session ID from counterfactual_initialize
        scenarios: Dict containing all 4 scenario types:
            {
                "diagnostic": {...},
                "predictive": {...},
                "preventive": {...},
                "optimization": {...}
            }
        selected_type: Optional. If not provided, automatically selects next type in sequence.
                      Manual override available (one of: diagnostic, predictive, preventive, optimization)
        ctx: FastMCP context for logging
    
    Returns:
        JSON string with Phase 2 result and Phase 3 instructions
    
    Example (first call - auto-selects diagnostic):
        result = await counterfactual_phase2(
            session_id="cf_1234567890_abcd1234",
            scenarios={
                "diagnostic": {
                    "changed_condition": "If we had backup database",
                    "counterfactual_scenario": "Quick failover possible",
                    "logical_consistency": "Backup enables fast recovery"
                },
                "predictive": {...},
                "preventive": {...},
                "optimization": {...}
            }
        )
    
    Example (manual override):
        result = await counterfactual_phase2(
            session_id="cf_1234567890_abcd1234",
            scenarios={...},
            selected_type="preventive"  # Skip diagnostic and predictive
        )
    """
    return await _phase2_tool.execute(
        session_id=session_id,
        scenarios=scenarios,
        selected_type=selected_type,
        ctx=ctx
    )


async def counterfactual_phase3_step1(
    session_id: str,
    principles_applied: Dict[str, str],
    ctx: Optional[Context] = None
) -> str:
    """
    Phase 3 Step 1: Apply 3 Core Principles to Selected Scenario.
    
    This is the first of 4 steps in Phase 3 deep reasoning analysis.
    Apply the 3 core principles to the selected counterfactual scenario.
    
    Args:
        session_id: Session ID from counterfactual_initialize
        principles_applied: Dict with 3 principles:
            - minimal_change: How you altered minimal conditions
            - causal_consistency: How you maintained logical connections
            - proximity: How you kept scenario close to actual situation
        ctx: FastMCP context for logging
    
    Returns:
        JSON string with Step 1 result and Step 2 instructions
    
    Example:
        result = await counterfactual_phase3_step1(
            session_id="cf_1234567890_abcd1234",
            principles_applied={
                "minimal_change": "Changed only the backup system configuration",
                "causal_consistency": "Maintained all existing causal relationships",
                "proximity": "Kept 95% of actual conditions unchanged"
            }
        )
    """
    return await _phase3_step1_tool.execute(
        session_id=session_id,
        principles_applied=principles_applied,
        ctx=ctx
    )


async def counterfactual_phase3_step2(
    session_id: str,
    level1_direct: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Phase 3 Step 2: Direct Impact Analysis (Reasoning Level 1).
    
    Analyze the direct and immediate impacts of the counterfactual scenario.
    Focus on first-order effects.
    
    Args:
        session_id: Session ID from counterfactual_initialize
        level1_direct: Direct impact analysis text
        ctx: FastMCP context for logging
    
    Returns:
        JSON string with Step 2 result and Step 3 instructions
    
    Example:
        result = await counterfactual_phase3_step2(
            session_id="cf_1234567890_abcd1234",
            level1_direct="Immediate impact: Database failover occurs within 30 seconds..."
        )
    """
    return await _phase3_step2_tool.execute(
        session_id=session_id,
        level1_direct=level1_direct,
        ctx=ctx
    )


async def counterfactual_phase3_step3(
    session_id: str,
    level2_ripple: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Phase 3 Step 3: Ripple Effects Analysis (Level 2).
    
    Analyze secondary ripple effects.
    
    Args:
        session_id: Session ID from counterfactual_initialize
        level2_ripple: Ripple effects analysis
        ctx: FastMCP context for logging
    
    Returns:
        JSON string with Step 3 result and Step 4 instructions
    
    Example:
        result = await counterfactual_phase3_step3(
            session_id="cf_1234567890_abcd1234",
            level2_ripple="Cascading effects include improved monitoring..."
        )
    """
    print(f"\n[DEBUG] counterfactual_phase3_step3 called with parameters:")
    print(f"  - session_id: {session_id}")
    print(f"  - level2_ripple type: {type(level2_ripple)}")
    print(f"  - level2_ripple length: {len(level2_ripple) if isinstance(level2_ripple, str) else 'N/A'}")
    print(f"  - ctx: {ctx}")
    
    return await _phase3_step3_tool.execute(
        session_id=session_id,
        level2_ripple=level2_ripple,
        ctx=ctx
    )


async def counterfactual_phase3_step4(
    session_id: str,
    level3_multidimensional: Dict[str, str],
    ctx: Optional[Context] = None
) -> str:
    """
    Phase 3 Step 4: Multidimensional Analysis (Level 3).
    
    Analyze impacts across 4 dimensions.
    
    Args:
        session_id: Session ID from counterfactual_initialize
        level3_multidimensional: Dict with 4 dimensions:
            - technical: Technical dimension analysis
            - organizational: Organizational dimension analysis
            - cultural: Cultural dimension analysis
            - external: External dimension analysis
        ctx: FastMCP context for logging
    
    Returns:
        JSON string with Step 4 result and Step 5 instructions
    
    Example:
        result = await counterfactual_phase3_step4(
            session_id="cf_1234567890_abcd1234",
            level3_multidimensional={
                "technical": "System architecture becomes more resilient",
                "organizational": "Teams adopt new incident procedures",
                "cultural": "Culture shifts toward proactive prevention",
                "external": "Customer trust improves"
            }
        )
    """
    return await _phase3_step4_tool.execute(
        session_id=session_id,
        level3_multidimensional=level3_multidimensional,
        ctx=ctx
    )


async def counterfactual_phase3_step5(
    session_id: str,
    level4_longterm: Dict[str, str],
    outcome_scenarios: Dict[str, str],
    ctx: Optional[Context] = None
) -> str:
    """
    Phase 3 Step 5: Long-term Evolution & Outcome Scenarios (Level 4).
    
    Final step of Phase 3. Analyze long-term evolution and generate outcome scenarios.
    Automatically provides Phase 4 instructions upon completion.
    
    Args:
        session_id: Session ID from counterfactual_initialize
        level4_longterm: Dict with:
            - timeline: Timeline projection
            - sustained_benefits: Long-term benefits
            - new_challenges: Emerging challenges
            - evolution: How situation evolves
        outcome_scenarios: Dict with:
            - best_case: Optimal outcome
            - worst_case: Negative outcome
            - most_likely: Realistic outcome
        ctx: FastMCP context for logging
    
    Returns:
        JSON string with complete Phase 3 result and Phase 4 instructions
    
    Example:
        result = await counterfactual_phase3_step5(
            session_id="cf_1234567890_abcd1234",
            level4_longterm={
                "timeline": "3-6-12 month phases",
                "sustained_benefits": "Reduced downtime by 80%",
                "new_challenges": "Higher infrastructure costs",
                "evolution": "System becomes industry standard"
            },
            outcome_scenarios={
                "best_case": "Zero unplanned outages in 12 months",
                "worst_case": "Some edge cases still cause issues",
                "most_likely": "95% improvement in reliability"
            }
        )
    """
    return await _phase3_step5_tool.execute(
        session_id=session_id,
        level4_longterm=level4_longterm,
        outcome_scenarios=outcome_scenarios,
        ctx=ctx
    )


async def counterfactual_phase4(
    session_id: str,
    comparative_analysis: Dict[str, Any],
    ctx: Optional[Context] = None
) -> str:
    """
    Phase 4: Comparative Analysis.
    
    Perform comparative analysis for the selected type.
    The type is determined from the Phase 2 selection.
    
    Args:
        session_id: Session ID from counterfactual_initialize
        comparative_analysis: Comparative analysis:
            {
                "actual_vs_counterfactual": {
                    "what_differs": "...",
                    "why_differs": "...",
                    "magnitude_importance": "..."
                },
                "key_insights": {
                    "critical_findings": [...],
                    "causal_factors": [...],
                    "improvement_opportunities": [...]
                },
                "action_recommendations": {
                    "immediate_actions": [...],
                    "short_term_plans": [...],
                    "long_term_initiatives": [...],
                    "monitoring_metrics": [...]
                },
                "final_summary": {
                    "key_takeaway": "...",
                    "expected_impact": "...",
                    "implementation_timeline": "...",
                    "next_steps": [...]
                }
            }
        ctx: FastMCP context for logging
    
    Returns:
        JSON string with Phase 4 result
        
    Example:
        result = await counterfactual_phase4(
            session_id="cf_1234567890_abcd1234",
            comparative_analysis={...}
        )
    """
    return await _phase4_tool.execute(
        session_id=session_id,
        comparative_analysis=comparative_analysis,
        ctx=ctx
    )


async def counterfactual_get_result(
    session_id: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Get complete counterfactual reasoning analysis results.
    
    Retrieve all phases of analysis including:
    - Phase 1: Actual state
    - Phase 2: Counterfactual scenarios
    - Phase 3: Deep reasoning
    - Phase 4: Comparative analysis
    
    Args:
        session_id: Session ID to retrieve
        ctx: FastMCP context for logging
    
    Returns:
        JSON string with complete analysis results
    """
    return await _get_result_tool.execute(session_id=session_id, ctx=ctx)


async def counterfactual_reset(
    session_id: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Reset or delete a counterfactual reasoning session.
    
    Args:
        session_id: Session ID to reset
        ctx: FastMCP context for logging
    
    Returns:
        JSON string with reset confirmation
    """
    return await _reset_tool.execute(session_id=session_id, ctx=ctx)


async def counterfactual_list_sessions(
    ctx: Optional[Context] = None
) -> str:
    """
    List all active counterfactual reasoning sessions.
    
    Args:
        ctx: FastMCP context for logging
    
    Returns:
        JSON string with list of all sessions
    """
    return await _list_sessions_tool.execute(ctx=ctx)
