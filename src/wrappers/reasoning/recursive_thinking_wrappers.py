"""
Recursive Thinking Tool Wrappers for MCP Registration
These wrapper functions contain the tool descriptions and delegate to the actual tool classes.
"""
from fastmcp import Context
from src.tools.reasoning.recursive_thinking_tool import (
    Rcursive_ThinkingInitializeTool,
    Rcursive_ThinkingUpdateLatentTool,
    Rcursive_ThinkingUpdateAnswerTool,
    Rcursive_ThinkingGetResultTool,
    Rcursive_ThinkingResetTool
)

# Initialize tool instances
_init_tool = Rcursive_ThinkingInitializeTool()
_update_latent_tool = Rcursive_ThinkingUpdateLatentTool()
_update_answer_tool = Rcursive_ThinkingUpdateAnswerTool()
_get_result_tool = Rcursive_ThinkingGetResultTool()
_reset_tool = Rcursive_ThinkingResetTool()


async def recursive_thinking_initialize(
    question: str,
    initial_answer: str = "",
    n_latent_updates: int = 4,
    max_improvements: int = 16,
    ctx: Context = None
) -> str:
    """
    Initialize a new recursive reasoning session with Recursive Thinking Model.
    
    This tool sets up the recursive reasoning process where:
    - Question (x): The input problem to solve
    - Answer (y): The current predicted answer (starts empty or with initial guess)
    - Latent (z): Hidden reasoning state that helps improve the answer
    - n_latent_updates: How many times to recursively update latent z (default: 4)
    - max_improvements: Maximum improvement iterations (default: 16)
    
    Args:
        question: The problem or question to solve
        initial_answer: Optional starting answer (empty means start from scratch)
        n_latent_updates: Number of recursive latent updates per improvement step
        max_improvements: Maximum number of answer improvement iterations
    
    Returns:
        Confirmation message with session details including auto-generated unique session_id
    """
    return await _init_tool.execute(question, initial_answer, n_latent_updates, max_improvements, ctx)


async def recursive_thinking_update_latent(
    session_id: str,
    reasoning_insight: str,
    step_number: int,
    ctx: Context = None
) -> str:
    """
    Update the latent reasoning state (z) based on question (x), current answer (y), and previous latent (z).
    
    This is Step 1-n of the Recursive Thinking algorithm. The latent state represents the model's internal
    reasoning process. This function should be called n times (default: 4x) to recursively
    improve the latent reasoning before updating the answer.
    
    **VERIFICATION MODE**: When called after verify_final_answer, this performs mandatory
    final verification reasoning using the same 4-step systematic analysis.
    
    Think of this as "thinking deeply" about the problem with systematic analysis:
    
    **Step-by-Step Latent Reasoning Guidelines:**
    
    **Step 1 (Problem Decomposition):**
    - Break down the original question into core components and sub-problems
    - Identify what type of problem this is (mathematical, logical, analytical, creative, etc.)
    - List all given information, constraints, and assumptions explicitly
    - Determine what specific knowledge domains or reasoning patterns are needed
    
    **Step 2 (Current State Analysis):**
    - Thoroughly examine the current answer's logic and reasoning chain
    - Identify specific strengths: what parts are correct and why
    - Pinpoint exact weaknesses: logical gaps, incorrect assumptions, missing steps
    - Check for consistency between different parts of the reasoning
    
    **Step 3 (Alternative Perspectives & Deep Reasoning):**
    - Consider alternative approaches or interpretations of the problem
    - Apply domain-specific reasoning patterns (e.g., proof techniques for math, causal analysis for complex scenarios)
    - Question underlying assumptions and explore edge cases
    - Look for patterns, connections, or insights that weren't initially obvious
    
    **Step 4 (Synthesis & Improvement Strategy):**
    - Synthesize insights from previous steps into a coherent improvement plan
    - Prioritize which aspects of the answer need the most improvement
    - Develop specific strategies for addressing identified weaknesses
    - Prepare concrete recommendations for the next answer iteration
    
    **Cross-cutting Principles for All Steps:**
    - Be extremely specific and concrete in your reasoning
    - Reference specific parts of the question and current answer
    - Use evidence-based reasoning rather than vague intuitions
    - Build incrementally on insights from previous latent updates
    - Each recursive update should add new insights, not repeat previous ones
    
    Args:
        session_id: The reasoning session identifier
        reasoning_insight: Your new reasoning insight following the step-by-step guidelines above.
                          Include specific analysis, concrete observations, and actionable insights.
                          Reference exact parts of the question/answer being analyzed.
                          Each step should build progressively on previous insights.
        step_number: Which latent update step this is (1 to n_latent_updates)
                    Step 1: Problem decomposition and classification
                    Step 2: Current answer analysis (strengths/weaknesses)
                    Step 3: Alternative perspectives and deep domain reasoning  
                    Step 4: Synthesis and concrete improvement strategy
    
    Returns:
        Status of latent update and guidance for next step
    """
    return await _update_latent_tool.execute(session_id, reasoning_insight, step_number, ctx)


async def recursive_thinking_update_answer(
    session_id: str,
    improved_answer: str,
    improvement_rationale: str,
    ctx: Context = None
) -> str:
    """
    Update the answer (y) based on current answer and refined latent reasoning (z).
    
    This is Step n+1 of the Recursive Thinking algorithm. After recursively updating the latent reasoning
    n times, use those insights to improve the actual answer. This is where you:
    - Apply the reasoning insights from the latent state
    - Correct any errors in the previous answer
    - Refine and improve the solution
    
    **IMPORTANT**: This tool is also used to finalize the verified answer after completing
    the 4-step verification reasoning. When called after verification reasoning is complete,
    it finalizes the answer and marks verification as completed.

    Args:
        session_id: The reasoning session identifier
        improved_answer: The new improved answer based on latent reasoning (or verified answer after verification)
        improvement_rationale: Brief explanation of how you improved the answer (or verification summary)
    
    Returns:
        Updated answer and guidance on whether to continue iterating, or verification completion status
    """
    return await _update_answer_tool.execute(session_id, improved_answer, improvement_rationale, ctx)


async def recursive_thinking_get_result(
    session_id: str,
    ctx: Context = None
) -> str:
    """
    Retrieve the final answer and complete reasoning history.
    
    This tool checks verification status:
    - If not verified: Automatically starts verification mode with update_latent_reasoning (4 steps)
    - If verified: Returns the final verified answer with complete reasoning history
    
    Workflow: 
    1. Call get_final_result when confident in answer
    2. If verification needed: Complete 4 update_latent_reasoning steps → update_answer
    3. Call get_final_result again to retrieve final verified answer
    
    Args:
        session_id: The reasoning session identifier
    
    Returns:
        Either verification start instruction or complete verified results
    """
    return await _get_result_tool.execute(session_id, ctx)


async def recursive_thinking_reset(
    session_id: str,
    ctx: Context = None
) -> str:
    """
    Reset or delete a reasoning session.
    
    Args:
        session_id: The reasoning session identifier to reset
    
    Returns:
        Confirmation of reset
    """
    return await _reset_tool.execute(session_id, ctx)
