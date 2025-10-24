"""
Code Analysis Tool Wrappers
FastMCP wrapper functions for Code Analysis Tool with Multi-Action Architecture
"""
from fastmcp import Context
from typing import Optional
from src.tools.analysis.code_analysis_tool import CodeAnalysisTool
from configs.analysis import AnalysisConfig


_code_analysis_tool = CodeAnalysisTool(default_output_dir=AnalysisConfig.ANALYSIS_OUTPUT_DIR)


async def code_analysis_initialize(
    source_file_path: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Initialize new code analysis session
    
    Analyzes the source file structure, counts lines, determines number of steps needed,
    and creates an initial markdown documentation file.
    
    Args:
        source_file_path: Path to the source code file to analyze
                         Example: "/path/to/project/main.py"
        ctx: FastMCP context for logging
    
    Returns:
        JSON string containing:
        - success: Whether initialization succeeded
        - sessionId: Unique session identifier for subsequent calls
        - fileName: Name of the source file
        - totalLines: Total number of lines in the source file
        - totalSteps: Number of analysis steps required
        - language: Detected programming language
        - importsCount: Number of import statements found
        - classesCount: Number of classes found
        - functionsCount: Number of functions found
        - outputPath: Path to the created markdown file
        - message: Human-readable status message
        - nextAction: "analyze_step" - indicates what to do next
        - currentStepInfo: Information about the first step to analyze
        - llmInstructions: Detailed instructions for LLM to analyze first step
    
    Example:
        result = await code_analysis_initialize(
            source_file_path="/home/user/project/main.py"
        )
        # Returns session_id and first step info, then call code_analysis_analyze_step
    
    Note:
        - The markdown file is created immediately with file overview and structure
        - It will be progressively updated with each analysis step
        - Supports Python, JavaScript, TypeScript, Java, C++, and more
    """
    if ctx:
        await ctx.info(f"Initializing code analysis for: {source_file_path}")
    
    result = await _code_analysis_tool.execute(
        action="initialize",
        source_file_path=source_file_path,
        ctx=ctx
    )
    return str(result)


async def code_analysis_analyze_step(
    session_id: str,
    step_number: int,
    analysis_content: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Submit analysis for a specific step
    
    Submits the LLM's analysis for the current step and immediately updates the markdown file.
    This is the core of the analysis process - called multiple times to build up the documentation.
    
    Args:
        session_id: Session ID from code_analysis_initialize
        step_number: Current step number (1, 2, 3, ...)
        analysis_content: The detailed analysis content in markdown format
                         Should include function/method explanations, variable descriptions,
                         data flow, dependencies, and any important notes for new developers
        ctx: FastMCP context for logging
    
    Returns:
        JSON string containing:
        - success: Whether step was analyzed successfully
        - sessionId: Current session ID
        - stepNumber: Completed step number
        - totalSteps: Total number of steps
        - markdownUpdated: True (file is updated immediately)
        - message: Human-readable status message
        - progress: Analysis progress with percentage
        - nextAction: "analyze_step" or "finalize"
        - nextStepInfo: Information about next step (if available)
        - llmInstructions: Instructions for analyzing next step (if available)
    
    Example:
        result = await code_analysis_analyze_step(
            session_id="analysis_1234567890_abcd1234",
            step_number=1,
            analysis_content='''
            #### Function: `initialize_app()`
            
            **Purpose:** Initializes the application with configuration settings.
            
            **Parameters:**
            - `config_path` (str): Path to configuration file
            
            **Variables Used:**
            - `app_config`: Stores loaded configuration
            - `logger`: Application logger instance
            
            **Dependencies:**
            - Uses `json` module to load configuration
            - Imports `Logger` from `utils.logging`
            
            **Data Flow:**
            1. Loads configuration from JSON file
            2. Validates required settings
            3. Initializes logger with config
            4. Returns configured app instance
            '''
        )
    
    Note:
        - Markdown file is updated immediately after each step
        - Previous analysis steps are preserved
        - Analysis won't be lost due to token limits
        - Each step should be comprehensive and beginner-friendly
    """
    if ctx:
        await ctx.info(f"Analyzing step {step_number} for session {session_id}")
    
    result = await _code_analysis_tool.execute(
        action="analyze_step",
        session_id=session_id,
        step_number=step_number,
        analysis_content=analysis_content,
        ctx=ctx
    )
    return str(result)


async def code_analysis_finalize(
    session_id: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Finalize code analysis session
    
    Marks the analysis session as completed and generates the final markdown file.
    Call this when all analysis steps are complete.
    
    Args:
        session_id: Session ID from code_analysis_initialize
        ctx: FastMCP context for logging
    
    Returns:
        JSON string containing:
        - success: Whether finalization succeeded
        - sessionId: Session ID
        - status: "completed"
        - totalSteps: Total number of analysis steps
        - stepsCompleted: Number of completed steps
        - outputPath: Path to the final markdown file
        - message: Completion message
    
    Example:
        result = await code_analysis_finalize(
            session_id="analysis_1234567890_abcd1234"
        )
        # Analysis is now complete, markdown file is ready
    
    Note:
        After finalization, the session is marked as completed and
        the final markdown file contains all analysis steps and findings.
    """
    if ctx:
        await ctx.info(f"Finalizing analysis session {session_id}")
    
    result = await _code_analysis_tool.execute(
        action="finalize",
        session_id=session_id,
        ctx=ctx
    )
    return str(result)


async def code_analysis_get_status(
    session_id: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Get current status of an analysis session
    
    Retrieves current status and progress information for an analysis session.
    Can be called at any time to check progress.
    
    Args:
        session_id: Session ID from code_analysis_initialize
        ctx: FastMCP context for logging
    
    Returns:
        JSON string containing:
        - success: Whether status retrieval succeeded
        - sessionId: Session ID
        - status: "active" or "completed"
        - fileName: Source file name
        - sourceFile: Full path to source file
        - totalLines: Total lines in source file
        - totalSteps: Total steps needed
        - currentStep: Current step number
        - stepsCompleted: Steps completed so far
        - outputPath: Path to markdown file
        - progress: Progress details with percentage
    
    Example:
        result = await code_analysis_get_status(
            session_id="analysis_1234567890_abcd1234"
        )
        # Check how many steps have been completed
    """
    if ctx:
        await ctx.info(f"Getting status for session {session_id}")
    
    result = await _code_analysis_tool.execute(
        action="get_status",
        session_id=session_id,
        ctx=ctx
    )
    return str(result)


async def code_analysis_list_sessions(
    ctx: Optional[Context] = None
) -> str:
    """
    List all code analysis sessions
    
    Returns a summary of all analysis sessions currently in memory.
    Useful for finding session IDs or checking on multiple analysis efforts.
    
    Args:
        ctx: FastMCP context for logging
    
    Returns:
        JSON string containing:
        - success: Whether listing succeeded
        - totalSessions: Total number of sessions
        - sessions: Array of session summaries, each containing:
          * sessionId: Session identifier
          * fileName: Source file name
          * status: Current status
          * totalSteps: Total steps needed
          * stepsCompleted: Steps completed
          * createdAt: Creation timestamp
          * lastUpdated: Last update timestamp
    
    Example:
        result = await code_analysis_list_sessions()
        # Browse all analysis sessions and their statuses
    
    Note:
        Sessions are stored in memory and will be lost when the server restarts.
        Markdown files are persisted to disk.
    """
    if ctx:
        await ctx.info("Listing all code analysis sessions")
    
    result = await _code_analysis_tool.execute(
        action="list_sessions",
        ctx=ctx
    )
    return str(result)


def register_code_analysis_tools(mcp):
    """Register all code analysis tools with FastMCP"""
    mcp.tool()(code_analysis_initialize)
    mcp.tool()(code_analysis_analyze_step)
    mcp.tool()(code_analysis_finalize)
    mcp.tool()(code_analysis_get_status)
    mcp.tool()(code_analysis_list_sessions)
