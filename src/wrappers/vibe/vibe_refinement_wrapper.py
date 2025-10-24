"""
Vibe Refinement Wrapper Functions
FastMCP wrapper functions for the Vibe Refinement Tool
"""
from fastmcp import Context
from typing import Dict, Any, Optional
from src.tools.vibe.vibe_refinement_tool import VibeRefinementTool


# Create single tool instance
_vibe_tool = VibeRefinementTool()


async def vibe_refinement_initialize(
    initial_prompt: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Initialize a new vibe refinement session
    
    This action starts a new progressive refinement session by:
    1. Analyzing the initial prompt's specificity (0-100 score)
    2. Calculating how many refinement steps are needed
    3. Determining the refinement phases (idea → system)
    4. Creating a new session for tracking progress
    
    Args:
        initial_prompt: User's initial vague or incomplete prompt
                       Example: "I want to make a fun Tetris game"
        ctx: FastMCP context for logging (optional)
    
    Returns:
        JSON string containing:
        - success: Whether initialization succeeded
        - session_id: Unique session identifier for subsequent calls
        - analysis: Specificity score and step calculations
        - message: Human-readable status message
        - next_action: What to do next ("get_next")
    
    Example:
        result = await vibe_refinement_initialize(
            initial_prompt="I want to build a task management app"
        )
        # Returns session_id and analysis, then call get_next
    
    Raises:
        ValueError: If initial_prompt is empty or invalid
    """
    result = await _vibe_tool.execute(
        action="initialize",
        ctx=ctx,
        initial_prompt=initial_prompt
    )
    return str(result)


async def vibe_refinement_get_next(
    session_id: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Get the next refinement step with LLM instructions
    
    This action:
    1. Advances to the next refinement step
    2. Generates appropriate question for current step
    3. Creates detailed instructions for LLM to generate 5 suggestions
    4. Returns structured format requirements
    
    The LLM should then generate 5 suggestions following the provided
    format, and the user selects one to submit via vibe_refinement_submit.
    
    Args:
        session_id: Session ID from initialize action
        ctx: FastMCP context for logging (optional)
    
    Returns:
        JSON string containing:
        - success: Whether action succeeded
        - session_id: Current session ID
        - step_info: Current step, total steps, phase, question
        - llm_instructions: Detailed instructions for LLM including:
          * task: What to generate
          * focus_area: What aspect to focus on
          * context: All relevant context from previous steps
          * format_requirements: Exact format for suggestions
          * guidelines: Best practices for generating suggestions
          * example_format: Example of properly formatted suggestion
        - message: Instructions for next steps
        - next_action: What to do next ("submit")
    
    Example:
        result = await vibe_refinement_get_next(
            session_id="vibe_1234567890_abcd1234"
        )
        # LLM reads llm_instructions and generates 5 suggestions
        # User selects one and submits via vibe_refinement_submit
    
    Raises:
        ValueError: If session_id not found
    """
    result = await _vibe_tool.execute(
        action="get_next",
        ctx=ctx,
        session_id=session_id
    )
    return str(result)


async def vibe_refinement_submit(
    session_id: str,
    selected_suggestion: Dict[str, Any],
    ctx: Optional[Context] = None
) -> str:
    """
    Submit user's selected suggestion for current step
    
    After the LLM generates 5 suggestions and the user selects one,
    this action records the selection and advances the workflow.
    
    Args:
        session_id: Session ID from initialize action
        selected_suggestion: The suggestion the user selected, must include:
            - id: Suggestion ID (e.g., "sugg_1")
            - title: Suggestion title
            - description: Detailed description
            - is_recommended: Whether it was LLM's recommendation
        ctx: FastMCP context for logging (optional)
    
    Returns:
        JSON string containing:
        - success: Whether submission succeeded
        - session_id: Current session ID
        - action: "selection_recorded" or "selection_recorded_final"
        - message: Human-readable status
        - next_action: "get_next" or "generate_report"
        - progress: Completion percentage and step counts (if not final)
    
    Example:
        result = await vibe_refinement_submit(
            session_id="vibe_1234567890_abcd1234",
            selected_suggestion={
                "id": "sugg_2",
                "title": "Multiplayer Battle Mode",
                "description": "Add real-time competitive multiplayer...",
                "is_recommended": False
            }
        )
        # If more steps needed, call get_next again
        # If completed, call generate_report
    
    Raises:
        ValueError: If session_id not found or selected_suggestion is invalid
    """
    result = await _vibe_tool.execute(
        action="submit",
        ctx=ctx,
        session_id=session_id,
        selected_suggestion=selected_suggestion
    )
    return str(result)


async def vibe_refinement_status(
    session_id: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Get current status of a refinement session
    
    This action provides comprehensive status information about
    the refinement session without modifying any state.
    
    Args:
        session_id: Session ID to query
        ctx: FastMCP context for logging (optional)
    
    Returns:
        JSON string containing:
        - success: Whether query succeeded
        - session_id: Queried session ID
        - status: Current session status (active, completed, etc.)
        - phase: Current phase (idea, system, completed)
        - progress: Detailed progress information:
          * current_step: Current step number
          * total_steps: Total steps needed
          * idea_steps: Number of idea refinement steps
          * system_steps: Number of system refinement steps
          * completed_steps: Number of completed steps
          * percentage: Completion percentage
        - initial_prompt: The original user prompt
        - specificity_score: Calculated specificity score
        - created_at: Session creation timestamp
        - last_updated: Last update timestamp
    
    Example:
        result = await vibe_refinement_status(
            session_id="vibe_1234567890_abcd1234"
        )
        # Check progress and current phase
    
    Raises:
        ValueError: If session_id not found
    """
    result = await _vibe_tool.execute(
        action="get_status",
        ctx=ctx,
        session_id=session_id
    )
    return str(result)


async def vibe_refinement_report(
    session_id: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Generate final refinement report
    
    This action creates a beautiful, comprehensive report of all
    decisions made during the refinement process. Should be called
    after all refinement steps are completed.
    
    The report includes:
    - Initial prompt and analysis
    - All idea refinement decisions
    - All system/architecture decisions
    - Final project specification summary
    - Ready-for-implementation checklist
    
    Args:
        session_id: Session ID to generate report for
        ctx: FastMCP context for logging (optional)
    
    Returns:
        JSON string containing:
        - success: Whether report generation succeeded
        - session_id: Session ID
        - report: Full markdown-formatted report
        - summary: Quick summary including:
          * initial_prompt: Original prompt
          * specificity_score: Calculated score
          * total_steps_completed: Number of steps completed
          * phases_completed: List of completed phases
    
    Example:
        result = await vibe_refinement_report(
            session_id="vibe_1234567890_abcd1234"
        )
        # Display the beautiful report to user
        # Use report content for documentation or planning
    
    Raises:
        ValueError: If session_id not found
    
    Note:
        The report is cached after first generation, so calling
        this multiple times returns the same report without
        regenerating it.
    """
    result = await _vibe_tool.execute(
        action="generate_report",
        ctx=ctx,
        session_id=session_id
    )
    return str(result)


async def vibe_refinement_list(
    ctx: Optional[Context] = None
) -> str:
    """
    List all vibe refinement sessions
    
    This action returns a summary of all refinement sessions
    currently stored in memory. Useful for:
    - Finding session IDs
    - Checking session statuses
    - Reviewing past refinements
    
    Args:
        ctx: FastMCP context for logging (optional)
    
    Returns:
        JSON string containing:
        - success: Whether listing succeeded
        - total_sessions: Total number of sessions
        - sessions: Array of session summaries, each containing:
          * session_id: Unique session identifier
          * initial_prompt: First 50 chars of prompt
          * status: Current status
          * phase: Current phase
          * current_step: Current step number
          * total_steps: Total steps needed
          * created_at: Creation timestamp
    
    Example:
        result = await vibe_refinement_list()
        # Browse all sessions and their statuses
    
    Note:
        Sessions are stored in memory and will be lost when
        the server restarts. Consider saving important reports
        before restarting.
    """
    result = await _vibe_tool.execute(
        action="list_sessions",
        ctx=ctx
    )
    return str(result)
