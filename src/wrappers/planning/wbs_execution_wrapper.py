"""
WBS Execution Tool Wrapper for MCP Registration
"""
from fastmcp import Context
from src.tools.planning.wbs_execution_tool import WBSExecutionTool
from configs.planning import PlanningConfig
from typing import Optional

# Initialize tool instance with configured output directory
_wbs_execution_tool = WBSExecutionTool(default_output_dir=PlanningConfig.PLANNING_OUTPUT_DIR)


async def wbs_execution(
    action: str,
    wbs_file_path: str = None,
    session_id: str = None,
    task_id: str = None,
    thinking: str = None,
    execute_implementation: bool = True,
    continue_after_completion: bool = False,
    action_description: str = None,
    ctx: Context = None
) -> str:
    """
    WBS (Work Breakdown Structure) Execution Tool for step-by-step task implementation.

    This tool takes a WBS markdown file as input and executes tasks systematically with deep thinking analysis. 
    It updates checkboxes in real-time after each task completion to avoid token limit issues.

    🎯 **KEY FEATURES:**
    - Parse WBS markdown files and extract hierarchical tasks
    - Execute tasks step-by-step with deep thinking analysis
    - Update checkboxes in WBS file after each task completion
    - Handle task dependencies and prerequisites
    - Session management for resumable execution
    - Real-time progress tracking and file updates

    📋 **ACTIONS:**
    - **'start'**: Begin execution with a WBS file path
    - **'continue'**: Continue existing session execution
    - **'execute_task'**: Execute a specific task with thinking analysis
    - **'get_status'**: Get current session status and progress
    - **'list_sessions'**: List all active WBS execution sessions

    ⚠️ **CRITICAL EXECUTION GUIDELINES:**

    🔥 **ERROR HANDLING REQUIREMENTS:**
    - NEVER proceed to next task if current task implementation has errors
    - Always validate that code compiles, runs, and meets requirements before marking complete
    - If errors occur during implementation:
      1. Stop execution immediately
      2. Analyze and fix all errors thoroughly
      3. Re-test the implementation
      4. Only mark complete when fully verified
    - Use build/compile commands to verify code correctness
    - Test functionality before proceeding
    - Document any issues encountered and their resolutions

    🧠 **DEEP THINKING REQUIREMENTS:**
    - For complex tasks requiring architectural decisions, use Sequential Thinking tool first
    - Before implementing complex features, call Sequential Thinking (st) tool with:
      - Problem analysis and requirements breakdown
      - Design considerations and alternatives
      - Implementation strategy and step-by-step approach
    - Use Sequential Thinking for:
      - System architecture design
      - Complex algorithm implementation
      - Database schema design
      - API design and integration
      - Performance optimization strategies
      - Security implementation planning

    📋 **TASK EXECUTION FLOW:**
    1. Read task description thoroughly
    2. If task is complex → Use Sequential Thinking tool for analysis
    3. Implement the solution with proper error handling
    4. Validate implementation (compile, test, verify)
    5. Fix any errors that occur
    6. Only mark task complete when fully working
    7. Update WBS file checkbox
    8. Proceed to next task

    **WORKFLOW EXAMPLE:**
    ```python
    # 1. Start execution with WBS file
    result = await wbs_execution(
        action="start",
        wbs_file_path="/path/to/WBS.md"
    )
    
    # 2. Continue to get next task
    result = await wbs_execution(
        action="continue",
        session_id="wbs_exec_20250115_143022"
    )
    
    # 3. Execute current task with thinking
    result = await wbs_execution(
        action="execute_task",
        session_id="wbs_exec_20250115_143022",
        task_id="1.1",
        thinking="Analyzed requirements and implemented feature X...",
        action_description="Created module X, added tests, verified functionality"
    )
    
    # 4. Check status
    result = await wbs_execution(
        action="get_status",
        session_id="wbs_exec_20250115_143022"
    )
    ```

    **ARGS:**
        action (str): The action to perform (start, continue, execute_task, get_status, list_sessions)
        wbs_file_path (str, optional): Path to the WBS markdown file (required for start action)
        session_id (str, optional): Session ID for continuing or executing tasks
        task_id (str, optional): Specific task ID to execute (for execute_task action)
        thinking (str, optional): Deep thinking analysis of the current task (for execute_task action)
        execute_implementation (bool, optional): Whether to actually perform the implementation work (default: True)
        continue_after_completion (bool, optional): Whether to automatically continue to next task after completion (default: False)
        action_description (str, optional): Description of actions taken during task execution
        ctx (Context, optional): MCP context for logging

    **RETURNS:**
        str: JSON response with execution results including:
            - success: Whether the action was successful
            - sessionId: Current session ID
            - currentTask: Current task being executed
            - nextAvailableTask: Next task ready for execution
            - completedTasksCount: Number of completed tasks
            - totalTasksCount: Total number of tasks
            - message: Human-readable status message
            - progress: Progress statistics (completed, total, percentage)
            - error: Error message if action failed

    **EXAMPLE RESPONSE:**
    ```json
    {
        "success": true,
        "sessionId": "wbs_exec_20250115_143022",
        "currentTask": {
            "id": "1.1",
            "title": "Setup Project Structure",
            "description": "Create basic directory structure and configuration files",
            "priority": "High",
            "dependencies": ["0"],
            "completed": false,
            "level": 1,
            "children": []
        },
        "nextAvailableTask": {
            "id": "1.2",
            "title": "Initialize Git Repository",
            ...
        },
        "completedTasksCount": 3,
        "totalTasksCount": 15,
        "message": "▶️ Ready to execute: **Setup Project Structure**\\n\\n🔥 **EXECUTION REQUIREMENTS:**...",
        "progress": {
            "completed": 3,
            "total": 15,
            "percentage": 20
        }
    }
    ```

    **ERROR HANDLING:**
    - Validates all inputs before execution
    - Checks task dependencies before allowing execution
    - Prevents execution of parent tasks (only leaf tasks can be executed)
    - Updates WBS file safely with error logging
    - Returns detailed error messages in response

    **SESSION MANAGEMENT:**
    - Sessions persist in memory during server runtime
    - Each session tracks execution history and progress
    - Multiple sessions can be active simultaneously
    - Sessions can be resumed after interruption

    Use this tool when you need to systematically implement a project plan with real-time 
    progress tracking and file updates.
    """
    if ctx:
        await ctx.info(f"Executing WBS action: {action}")
    
    result = await _wbs_execution_tool.execute(
        action=action,
        wbs_file_path=wbs_file_path,
        session_id=session_id,
        task_id=task_id,
        thinking=thinking,
        action_description=action_description
    )
    
    return result
