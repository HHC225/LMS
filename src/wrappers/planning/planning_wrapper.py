"""
Planning Tool Wrappers
FastMCP wrapper functions for Planning Tool with Multi-Action Architecture
"""
from fastmcp import Context
from typing import Optional, List, Dict, Any
from src.tools.planning.planning_tool import PlanningTool
from configs.planning import PlanningConfig


_planning_tool = PlanningTool(default_output_dir=PlanningConfig.PLANNING_OUTPUT_DIR)


async def planning_initialize(
    problem_statement: str,
    project_name: Optional[str] = None,
    ctx: Optional[Context] = None
) -> str:
    """
    Initialize new planning session
    
    Creates a new planning session and generates initial WBS.md file.
    This is the first step in the planning process.
    
    Args:
        problem_statement: The problem or project to break down into tasks
                          Example: "Build a real-time multiplayer 2048 game"
        project_name: Optional project name (auto-generated if not provided)
        ctx: FastMCP context for logging
    
    Returns:
        JSON string containing:
        - success: Whether initialization succeeded
        - sessionId: Unique session identifier for subsequent calls
        - projectName: Generated or provided project name
        - outputPath: Path to the created WBS.md file
        - message: Human-readable status message
        - nextAction: "add_step" - indicates what to do next
    
    Example:
        result = await planning_initialize(
            problem_statement="Build a task management API with authentication",
            project_name="TaskMaster API"
        )
        # Returns session_id, then call planning_add_step
    
    Note:
        The WBS.md file is created immediately with project header and problem statement.
        It will be progressively updated with each planning step.
    """
    if ctx:
        await ctx.info(f"Initializing planning session: {problem_statement[:50]}...")
    
    result = await _planning_tool.execute(
        action="initialize",
        problem_statement=problem_statement,
        project_name=project_name,
        ctx=ctx
    )
    return str(result)


async def planning_add_step(
    session_id: str,
    step_number: int,
    planning_analysis: str,
    wbs_items: Optional[List[Dict[str, Any]]] = None,
    ctx: Optional[Context] = None
) -> str:
    """
    Add planning step with WBS items
    
    Adds a planning analysis step and immediately updates the WBS.md file.
    This is the core of the planning process - called multiple times to build up the WBS.
    
    Args:
        session_id: Session ID from planning_initialize
        step_number: Current step number (1, 2, 3, ...)
        planning_analysis: Your analysis and thinking for this step
                          Describe what you're planning and why
        wbs_items: Optional list of WBS items to add in this step
                   Each item must have: id, title, description, level, priority
                   Child items (level > 0) must specify parent_id
        ctx: FastMCP context for logging
    
    WBS Item Structure:
        {
            "id": "1.0",                    // Required: Unique identifier
            "title": "Setup Project",       // Required: Task name
            "description": "Initialize...", // Required: Detailed description
            "level": 0,                     // Required: 0=root, 1,2,3=child levels
            "parent_id": None,              // Required for level > 0
            "priority": "High",             // Required: High/Medium/Low
            "dependencies": ["0.1"],        // Optional: List of dependency IDs
            "order": 0                      // Optional: Display order
        }
    
    Returns:
        JSON string containing:
        - success: Whether step was added successfully
        - sessionId: Current session ID
        - stepNumber: Completed step number
        - wbsItemsAdded: Number of WBS items added in this step
        - totalWbsItems: Total WBS items so far
        - wbsFileUpdated: True (file is updated immediately)
        - message: Human-readable status message
        - nextAction: "add_step_or_finalize" - continue or finish
    
    Example:
        result = await planning_add_step(
            session_id="planning_1234567890_abcd1234",
            step_number=1,
            planning_analysis="Breaking down the project into main phases: setup, development, testing",
            wbs_items=[
                {
                    "id": "1.0",
                    "title": "Project Setup",
                    "description": "Initialize repository and development environment",
                    "level": 0,
                    "priority": "High"
                },
                {
                    "id": "1.1",
                    "title": "Create Git Repository",
                    "description": "Initialize git, create .gitignore",
                    "level": 1,
                    "parent_id": "1.0",
                    "priority": "High",
                    "order": 1
                }
            ]
        )
    
    Note:
        - WBS.md file is updated immediately after each step
        - Previous planning steps are preserved
        - Early tasks won't be lost due to token limits
    """
    if ctx:
        await ctx.info(f"Adding planning step {step_number} to session {session_id}")
    
    result = await _planning_tool.execute(
        action="add_step",
        session_id=session_id,
        step_number=step_number,
        planning_analysis=planning_analysis,
        wbs_items=wbs_items,
        ctx=ctx
    )
    return str(result)


async def planning_finalize(
    session_id: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Finalize planning session
    
    Marks the planning session as completed and generates the final WBS.md file.
    Call this when all planning steps are complete.
    
    Args:
        session_id: Session ID from planning_initialize
        ctx: FastMCP context for logging
    
    Returns:
        JSON string containing:
        - success: Whether finalization succeeded
        - sessionId: Session ID
        - status: "completed"
        - totalSteps: Total number of planning steps completed
        - totalWbsItems: Total number of WBS items created
        - outputPath: Path to the final WBS.md file
        - message: Completion message
    
    Example:
        result = await planning_finalize(
            session_id="planning_1234567890_abcd1234"
        )
        # Planning is now complete, WBS.md is ready for execution
    
    Note:
        After finalization, the session is marked as completed and
        the final WBS.md file contains all planning steps and WBS items.
    """
    if ctx:
        await ctx.info(f"Finalizing planning session {session_id}")
    
    result = await _planning_tool.execute(
        action="finalize",
        session_id=session_id,
        ctx=ctx
    )
    return str(result)


async def planning_status(
    session_id: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Get planning session status
    
    Retrieves current status and progress information for a planning session.
    Can be called at any time to check progress.
    
    Args:
        session_id: Session ID from planning_initialize
        ctx: FastMCP context for logging
    
    Returns:
        JSON string containing:
        - success: Whether status retrieval succeeded
        - sessionId: Session ID
        - status: "active" or "completed"
        - projectName: Project name
        - currentStep: Current step number
        - totalSteps: Total steps completed so far
        - totalWbsItems: Total WBS items created
        - outputPath: Path to WBS.md file
    
    Example:
        result = await planning_status(
            session_id="planning_1234567890_abcd1234"
        )
        # Check how many steps and items have been created
    """
    if ctx:
        await ctx.info(f"Getting status for session {session_id}")
    
    result = await _planning_tool.execute(
        action="status",
        session_id=session_id,
        ctx=ctx
    )
    return str(result)


async def planning_list(
    ctx: Optional[Context] = None
) -> str:
    """
    List all planning sessions
    
    Returns a summary of all planning sessions currently in memory.
    Useful for finding session IDs or checking on multiple planning efforts.
    
    Args:
        ctx: FastMCP context for logging
    
    Returns:
        JSON string containing:
        - success: Whether listing succeeded
        - totalSessions: Total number of sessions
        - sessions: Array of session summaries, each containing:
          * sessionId: Session identifier
          * projectName: Project name
          * status: "active" or "completed"
          * totalSteps: Number of planning steps
          * totalWbsItems: Number of WBS items
          * lastUpdated: Last update timestamp
    
    Example:
        result = await planning_list()
        # Browse all planning sessions
    
    Note:
        Sessions are stored in memory and will be lost when the server restarts.
        WBS.md files are persisted to disk.
    """
    if ctx:
        await ctx.info("Listing all planning sessions")
    
    result = await _planning_tool.execute(
        action="list",
        ctx=ctx
    )
    return str(result)
