"""
Sequential Thinking Tool Wrapper for MCP Registration
"""
from fastmcp import Context
from src.tools.reasoning.sequential_thinking_tool import SequentialThinkingTool

# Initialize tool instance
_st_tool = SequentialThinkingTool()


async def st(
    thought: str,
    thought_number: int,
    total_thoughts: int,
    next_thought_needed: bool,
    is_revision: bool = None,
    revises_thought: int = None,
    branch_from_thought: int = None,
    branch_id: str = None,
    needs_more_thoughts: bool = None,
    action_required: bool = None,
    action_type: str = None,
    action_description: str = None,
    ctx: Context = None
) -> str:
    """
    Sequential Thinking Tool for Software Development Problem-Solving
    
    🧠 **CORE CONCEPT:**
    A structured analytical thinking process where each thought builds sequentially to solve 
    complex software problems. Thoughts can question, revise, or branch from previous insights 
    as understanding deepens.
    
    🎯 **SCOPE:** Software development, system architecture, API design, database optimization, 
    and technical analysis.
    
    ⚡ **KEY PRINCIPLES:**
    1. **Quality First**: Establish clear success criteria before starting. If final result 
       doesn't meet criteria, restart from thought 1.
    2. **Critical Analysis**: Question user input for logical errors, missing information, 
       or better approaches.
    3. **Adaptive Process**: Adjust total thoughts, revise decisions, or branch into alternatives 
       as needed.
    
    📋 **CORE PARAMETERS:**
    - thought: Current analytical step (architecture analysis, technical decisions, implementation planning)
    - thought_number: Current sequence number (1, 2, 3...)
    - total_thoughts: Estimated total needed (adjustable)
    - next_thought_needed: Whether to continue thinking
    - is_revision: Whether this revises previous thinking
    - revises_thought: Which thought number is being reconsidered
    - branch_from_thought: Starting point for alternative exploration
    - branch_id: Identifier for current branch
    - action_required: Whether this step requires immediate action
    - action_type: Type of action to be executed
    - action_description: Specific action to be taken
    
    🔄 **SEQUENTIAL THINKING FLOW:**
    1. Start with problem analysis and success criteria
    2. Each thought builds on or questions previous insights
    3. Revise or branch when better approaches emerge
    4. Take direct action when implementation is needed (code writing, file creation, etc.)
    5. Continue until robust, implementable solution is reached
    6. Verify solution meets initial criteria
    
    💡 **USE CASES:**
    - System architecture design and component breakdown
    - API endpoint structure and data flow planning
    - Database schema optimization and query analysis
    - Performance bottleneck identification and solutions
    - Security vulnerability assessment and mitigation
    - Code refactoring strategy and impact analysis
    
    ⚡ **DIRECT ACTION EXECUTION:**
    - When code needs to be written, write it immediately in that step
    - When files need to be created or modified, do it directly
    - When configurations need to be updated, make the changes
    - When tests need to be run, execute them in the current step
    - No intermediate planning - execute actions as they become clear
    
    Args:
        thought: Your current thinking step
        thought_number: Current thought number (numeric value, e.g., 1, 2, 3)
        total_thoughts: Estimated total thoughts needed (numeric value, e.g., 5, 10)
        next_thought_needed: Whether another thought step is needed
        is_revision: Whether this revises previous thinking
        revises_thought: Which thought is being reconsidered
        branch_from_thought: Branching point thought number
        branch_id: Branch identifier
        needs_more_thoughts: If more thoughts are needed
        action_required: Whether this step requires direct action
        action_type: Type of action (code_writing, file_creation, file_modification, 
                    configuration, testing, analysis, other)
        action_description: Description of the specific action to be taken
    
    Returns:
        JSON response with thought processing results
    """
    return await _st_tool.execute(
        thought=thought,
        thought_number=thought_number,
        total_thoughts=total_thoughts,
        next_thought_needed=next_thought_needed,
        is_revision=is_revision,
        revises_thought=revises_thought,
        branch_from_thought=branch_from_thought,
        branch_id=branch_id,
        needs_more_thoughts=needs_more_thoughts,
        action_required=action_required,
        action_type=action_type,
        action_description=action_description,
        ctx=ctx
    )
