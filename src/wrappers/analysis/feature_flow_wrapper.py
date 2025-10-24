"""
Feature Flow Analysis Tool Wrappers
FastMCP wrapper functions for Feature Flow Analysis Tool - Flow Visualization Only
"""
from fastmcp import Context
from typing import Optional, List
from src.tools.analysis.feature_flow_analysis_tool import FeatureFlowAnalysisTool
from configs.analysis import AnalysisConfig


_feature_flow_tool = FeatureFlowAnalysisTool(
    default_output_dir=AnalysisConfig.ANALYSIS_OUTPUT_DIR / "flows"
)


async def feature_flow_analyze(
    feature_name: str,
    file_paths: List[str],
    ctx: Optional[Context] = None
) -> str:
    """
    Analyze feature flow and generate ASCII flow diagram
    
    This tool analyzes source files and generates clear ASCII flow visualization:
    - File-level execution flow showing which files interact
    - File descriptions and purposes
    - Dependency relationships with action labels
    
    Args:
        feature_name: Name of the feature to analyze
                     Example: "ForceCancel"
        file_paths: List of source file paths related to this feature
                   Example: ["/path/to/Pipeline.java", "/path/to/Transform1.java", ...]
        ctx: FastMCP context for logging
    
    Returns:
        JSON string containing:
        - success: Whether analysis succeeded
        - sessionId: Unique session identifier
        - featureName: Name of the feature
        - status: "completed"
        - totalFiles: Total number of files analyzed
        - entryPoints: List of entry point file names
        - outputPath: Path to the generated MD file with ASCII diagram
        - message: Human-readable status message
    
    Example:
        result = await feature_flow_analyze(
            feature_name="ForceCancel",
            file_paths=[
                "/path/to/ForceCancelPipeline.java",
                "/path/to/ForceCancelFn.java",
                "/path/to/ForceCancelDto.java"
            ]
        )
        # Analysis complete! Check output MD file for ASCII flow diagram
    
    Note:
        - This is a one-shot analysis - no multi-step process
        - Generates ASCII diagram that is human-readable without tools
        - Focus is on file-level flow visualization only
        - Each file box includes description and type
        - Arrows show what action is performed between files
    """
    if ctx:
        await ctx.info(f"Starting feature flow analysis for: {feature_name}")
    
    result = await _feature_flow_tool.execute(
        action="analyze",
        feature_name=feature_name,
        file_paths=file_paths,
        ctx=ctx
    )
    return str(result)


async def feature_flow_get_session(
    session_id: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Get feature flow analysis session details
    
    Retrieves information about a completed analysis session.
    
    Args:
        session_id: Session ID from feature_flow_analyze
        ctx: FastMCP context for logging
    
    Returns:
        JSON string containing:
        - success: Whether retrieval succeeded
        - sessionId: Session ID
        - featureName: Feature name
        - status: Current status
        - totalFiles: Total files analyzed
        - outputPath: Path to MD file
    
    Example:
        result = await feature_flow_get_session(
            session_id="flow_1234567890_1234"
        )
    """
    if ctx:
        await ctx.info(f"Retrieving session: {session_id}")
    
    result = await _feature_flow_tool.execute(
        action="get_session",
        session_id=session_id,
        ctx=ctx
    )
    return str(result)


async def feature_flow_list_sessions(
    ctx: Optional[Context] = None
) -> str:
    """
    List all feature flow analysis sessions
    
    Returns a summary of all analysis sessions currently in memory.
    
    Args:
        ctx: FastMCP context for logging
    
    Returns:
        JSON string containing:
        - success: Whether listing succeeded
        - totalSessions: Total number of sessions
        - sessions: Array of session summaries
    
    Example:
        result = await feature_flow_list_sessions()
    
    Note:
        Sessions are stored in memory and will be lost when the server restarts.
        MD files are persisted to disk.
    """
    if ctx:
        await ctx.info("Listing all flow analysis sessions")
    
    result = await _feature_flow_tool.execute(
        action="list_sessions",
        ctx=ctx
    )
    return str(result)


def register_feature_flow_tools(mcp):
    """Register feature flow analysis tools with FastMCP server"""
    mcp.tool()(feature_flow_analyze)
    mcp.tool()(feature_flow_get_session)
    mcp.tool()(feature_flow_list_sessions)
