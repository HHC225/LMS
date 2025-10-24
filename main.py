"""
Thinking Tools MCP Server - Main Entry Point
Advanced thinking and reasoning tools for problem-solving

This server provides:
- Recursive Thinking Model: Recursive reasoning for iterative answer improvement
- Sequential Thinking: Structured analytical thinking for software development
- Tree of Thoughts: Multi-path exploration and evaluation
- Conversation Memory: Long-term memory and context retention
- Planning & WBS: Project planning and work breakdown structure
- Code Analysis: Enterprise-level source code analysis and documentation
- Report Generator: IT report generation from raw content

All tools are registered here with modular configuration.
"""
from fastmcp import FastMCP, Context
from configs import ServerConfig, ReasoningConfig, MemoryConfig, PlanningConfig, ReportConfig
from configs.analysis import AnalysisConfig
from src.utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    name=ServerConfig.SERVER_NAME,
)

logger.info(f"Initializing {ServerConfig.SERVER_NAME} v{ServerConfig.SERVER_VERSION}")
logger.info(f"Description: {ServerConfig.SERVER_DESCRIPTION}")


# ============================================================================
# RECURSIVE THINKING TOOLS REGISTRATION
# ============================================================================

if ReasoningConfig.ENABLE_RECURSIVE_THINKING:
    from src.wrappers.reasoning.recursive_thinking_wrappers import (
        recursive_thinking_initialize,
        recursive_thinking_update_latent,
        recursive_thinking_update_answer,
        recursive_thinking_get_result,
        recursive_thinking_reset
    )
    
    logger.info("Registering Recursive Thinking tools...")
    
    # Register wrapper functions as MCP tools
    mcp.tool()(recursive_thinking_initialize)
    mcp.tool()(recursive_thinking_update_latent)
    mcp.tool()(recursive_thinking_update_answer)
    mcp.tool()(recursive_thinking_get_result)
    mcp.tool()(recursive_thinking_reset)
    
    logger.info("Recursive Thinking tools registered successfully")


# ============================================================================
# SEQUENTIAL THINKING TOOL REGISTRATION
# ============================================================================

if ReasoningConfig.ENABLE_SEQUENTIAL_THINKING:
    from src.wrappers.reasoning.sequential_thinking_wrapper import st
    
    logger.info("Registering Sequential Thinking tool...")
    
    # Register wrapper function as MCP tool
    mcp.tool()(st)
    
    logger.info("Sequential Thinking tool registered successfully")


# ============================================================================
# TREE OF THOUGHTS TOOL REGISTRATION
# ============================================================================

if ReasoningConfig.ENABLE_TREE_OF_THOUGHTS:
    from src.wrappers.reasoning.tree_of_thoughts_wrapper import tt
    
    logger.info("Registering Tree of Thoughts tool...")
    
    # Register wrapper function as MCP tool
    mcp.tool()(tt)
    
    logger.info("Tree of Thoughts tool registered successfully")


# ============================================================================
# VERBALIZED SAMPLING TOOL REGISTRATION
# ============================================================================

if ReasoningConfig.ENABLE_VERBALIZED_SAMPLING:
    from src.wrappers.reasoning.verbalized_sampling_wrapper import register_verbalized_sampling_tools
    
    logger.info("Registering Verbalized Sampling tools...")
    
    # Register all verbalized sampling tools
    register_verbalized_sampling_tools(mcp)
    
    logger.info("Verbalized Sampling tools registered successfully")


# ============================================================================
# COUNTERFACTUAL REASONING TOOLS REGISTRATION
# ============================================================================

if ReasoningConfig.ENABLE_COUNTERFACTUAL_REASONING:
    from src.wrappers.reasoning.counterfactual_reasoning_wrapper import (
        counterfactual_initialize,
        counterfactual_phase1,
        counterfactual_phase2,
        counterfactual_phase3_step1,
        counterfactual_phase3_step2,
        counterfactual_phase3_step3,
        counterfactual_phase3_step4,
        counterfactual_phase3_step5,
        counterfactual_phase4,
        counterfactual_get_result,
        counterfactual_reset,
        counterfactual_list_sessions
    )
    
    logger.info("Registering Counterfactual Reasoning tools...")
    
    # Register wrapper functions as MCP tools
    mcp.tool()(counterfactual_initialize)
    mcp.tool()(counterfactual_phase1)
    mcp.tool()(counterfactual_phase2)
    # Phase 3 now has 4 separate steps
    mcp.tool()(counterfactual_phase3_step1)
    mcp.tool()(counterfactual_phase3_step2)    
    mcp.tool()(counterfactual_phase3_step3)
    mcp.tool()(counterfactual_phase3_step4)
    mcp.tool()(counterfactual_phase3_step5)
    mcp.tool()(counterfactual_phase4)
    mcp.tool()(counterfactual_get_result)
    mcp.tool()(counterfactual_reset)
    mcp.tool()(counterfactual_list_sessions)
    
    logger.info("Counterfactual Reasoning tools registered successfully (Phase 3 with 5-step process)")


# ============================================================================
# CONVERSATION MEMORY TOOLS REGISTRATION
# ============================================================================

if MemoryConfig.ENABLE_CONVERSATION_MEMORY:
    from src.wrappers.memory.conversation_memory_wrappers import (
        conversation_memory_store,
        conversation_memory_query,
        conversation_memory_list,
        conversation_memory_delete,
        conversation_memory_clear,
        conversation_memory_get,
        conversation_memory_update
    )
    
    logger.info("Registering Conversation Memory tools...")
    
    # Register wrapper functions as MCP tools
    mcp.tool()(conversation_memory_store)
    mcp.tool()(conversation_memory_query)
    mcp.tool()(conversation_memory_list)
    mcp.tool()(conversation_memory_delete)
    mcp.tool()(conversation_memory_clear)
    mcp.tool()(conversation_memory_get)
    mcp.tool()(conversation_memory_update)
    
    logger.info("Conversation Memory tools registered successfully")


# ============================================================================
# PLANNING TOOLS REGISTRATION
# ============================================================================

if PlanningConfig.ENABLE_PLANNING:
    from src.wrappers.planning.planning_wrapper import (
        planning_initialize,
        planning_add_step,
        planning_finalize,
        planning_status,
        planning_list
    )
    
    logger.info("Registering Planning tools...")
    
    # Register wrapper functions as MCP tools
    mcp.tool()(planning_initialize)
    mcp.tool()(planning_add_step)
    mcp.tool()(planning_finalize)
    mcp.tool()(planning_status)
    mcp.tool()(planning_list)
    
    logger.info("Planning tools registered successfully")


# ============================================================================
# WBS EXECUTION TOOLS REGISTRATION
# ============================================================================

if PlanningConfig.ENABLE_WBS_EXECUTION:
    from src.wrappers.planning.wbs_execution_wrapper import wbs_execution
    
    logger.info("Registering WBS Execution tool...")
    
    # Register wrapper function as MCP tool
    mcp.tool()(wbs_execution)
    
    logger.info("WBS Execution tool registered successfully")


# ============================================================================
# CODE ANALYSIS TOOLS REGISTRATION
# ============================================================================

if AnalysisConfig.ENABLE_CODE_ANALYSIS:
    from src.wrappers.analysis.code_analysis_wrapper import register_code_analysis_tools
    
    logger.info("Registering Code Analysis tools...")
    
    # Register all code analysis tools
    register_code_analysis_tools(mcp)
    
    logger.info("Code Analysis tools registered successfully")


# ============================================================================
# FEATURE FLOW ANALYSIS TOOLS REGISTRATION
# ============================================================================

if AnalysisConfig.ENABLE_FEATURE_FLOW_ANALYSIS:
    from src.wrappers.analysis.feature_flow_wrapper import register_feature_flow_tools
    
    logger.info("Registering Feature Flow Analysis tools...")
    
    # Register all feature flow analysis tools
    register_feature_flow_tools(mcp)
    
    logger.info("Feature Flow Analysis tools registered successfully")


# ============================================================================
# SLACK TOOLS REGISTRATION
# ============================================================================

try:
    from configs.slack import SlackConfig, get_slack_config
    
    # Check if Slack is enabled
    slack_config = get_slack_config()
    if slack_config.ENABLE_SLACK_TOOLS:
        from src.wrappers.slack import (
            get_thread_content,
            get_single_message,
            get_channel_history,
            post_message,
            post_ephemeral_message,
            delete_message,
            bulk_delete_messages
        )
        from src.wrappers.slack.slack_thread_search_wrapper import search_threads
        
        logger.info("Registering Slack tools...")
        
        # Register wrapper functions as MCP tools
        mcp.tool()(get_thread_content)
        mcp.tool()(get_single_message)
        mcp.tool()(get_channel_history)
        mcp.tool()(post_message)
        mcp.tool()(post_ephemeral_message)
        mcp.tool()(delete_message)
        mcp.tool()(bulk_delete_messages)
        mcp.tool()(search_threads)
        
        logger.info("Slack tools registered successfully")
        
        # Register Slack Digest tool
        try:
            from src.wrappers.slack.digest_wrapper import generate_digest, post_digest
            
            logger.info("Registering Slack Digest tools...")
            mcp.tool()(generate_digest)
            mcp.tool()(post_digest)
            logger.info("Slack Digest tools registered successfully")
        except Exception as digest_error:
            logger.warning(f"Slack Digest tools not available: {digest_error}")
            logger.info("Continuing without Slack Digest tools...")
    else:
        logger.info("Slack tools disabled in configuration")
        
except Exception as e:
    logger.warning(f"Slack tools not available: {e}")
    logger.info("Continuing without Slack tools...")


# ============================================================================
# VIBE CODING TOOL REGISTRATION
# ============================================================================

try:
    from configs.vibe import VibeConfig, get_vibe_config
    
    # Check if Vibe Coding is enabled
    vibe_config = get_vibe_config()
    if vibe_config.ENABLE_VIBE_CODING:
        # Import new vibe refinement wrappers
        from src.wrappers.vibe import (
            vibe_refinement_initialize,
            vibe_refinement_get_next,
            vibe_refinement_submit,
            vibe_refinement_status,
            vibe_refinement_report,
            vibe_refinement_list
        )
        
        logger.info("Registering Vibe Refinement tools...")
        
        # Register all vibe refinement wrapper functions as MCP tools
        mcp.tool()(vibe_refinement_initialize)
        mcp.tool()(vibe_refinement_get_next)
        mcp.tool()(vibe_refinement_submit)
        mcp.tool()(vibe_refinement_status)
        mcp.tool()(vibe_refinement_report)
        mcp.tool()(vibe_refinement_list)
        
        logger.info("Vibe Refinement tools registered successfully")
    else:
        logger.info("Vibe Refinement tools disabled in configuration")
        
except Exception as e:
    logger.warning(f"Vibe Refinement tools not available: {e}")
    logger.info("Continuing without Vibe Refinement tools...")


# ============================================================================
# REPORT GENERATOR TOOLS REGISTRATION
# ============================================================================

if ReportConfig.ENABLE_REPORT_GENERATOR:
    from src.wrappers.report import (
        generate_report,
        build_report_from_json
    )
    
    logger.info("Registering Report Generator tools...")
    
    # Register wrapper functions as MCP tools
    mcp.tool()(generate_report)
    mcp.tool()(build_report_from_json)
    
    logger.info("Report Generator tools registered successfully")


# ============================================================================
# JIRA TOOLS REGISTRATION
# ============================================================================

try:
    from configs.jira import get_jira_config, validate_config
    
    # Try to get and validate JIRA config
    jira_config = get_jira_config()
    validate_config(jira_config)
    
    # Import JIRA wrapper functions
    from src.wrappers.jira import (
        jira_search_issues,
        jira_get_issue_details,
        jira_create_issue,
        jira_get_comments,
        jira_add_comment,
        jira_update_comment,
        jira_delete_comment,
        jira_list_attachments,
        jira_download_attachment,
        jira_get_projects,
        jira_search_knowledge
    )
    
    logger.info("Registering JIRA tools...")
    
    # Register JIRA wrapper functions as MCP tools
    mcp.tool()(jira_search_issues)
    mcp.tool()(jira_get_issue_details)
    mcp.tool()(jira_create_issue)
    mcp.tool()(jira_get_comments)
    mcp.tool()(jira_add_comment)
    mcp.tool()(jira_update_comment)
    mcp.tool()(jira_delete_comment)
    mcp.tool()(jira_list_attachments)
    mcp.tool()(jira_download_attachment)
    mcp.tool()(jira_get_projects)
    mcp.tool()(jira_search_knowledge)
    
    logger.info("JIRA tools registered successfully (11 tools)")
    logger.info("  Issues: search, get_details, create")
    logger.info("  Comments: get, add, update, delete")
    logger.info("  Attachments: list, download")
    logger.info("  Projects: get_projects")
    logger.info("  Knowledge: search_knowledge")
    
except Exception as e:
    logger.warning(f"JIRA tools not available: {e}")
    logger.info("Continuing without JIRA tools...")
    logger.info("To enable JIRA tools:")
    logger.info("  1. Copy configs/jira.py.template to configs/jira.py")
    logger.info("  2. Update JIRA credentials and custom fields in configs/jira.py")


# ============================================================================
# CONFLUENCE TOOLS REGISTRATION
# ============================================================================

try:
    from configs.confluence import get_confluence_config, validate_config
    
    # Try to get and validate Confluence config
    confluence_config = get_confluence_config()
    validate_config(confluence_config)
    
    # Import Confluence wrapper functions
    from src.wrappers.confluence import (
        confluence_create_page,
        confluence_get_page,
        confluence_update_page,
        confluence_delete_page,
        confluence_get_spaces,
        confluence_search_pages
    )
    
    logger.info("Registering Confluence tools...")
    
    # Register Confluence wrapper functions as MCP tools
    mcp.tool()(confluence_create_page)
    mcp.tool()(confluence_get_page)
    mcp.tool()(confluence_update_page)
    mcp.tool()(confluence_delete_page)
    mcp.tool()(confluence_get_spaces)
    mcp.tool()(confluence_search_pages)
    
    logger.info("Confluence tools registered successfully (6 tools)")
    logger.info("  Pages: create, get, update, delete")
    logger.info("  Spaces: get_spaces")
    logger.info("  Search: search_pages")
    
except Exception as e:
    logger.warning(f"Confluence tools not available: {e}")
    logger.info("Continuing without Confluence tools...")
    logger.info("To enable Confluence tools:")
    logger.info("  1. Copy configs/confluence.py.template to configs/confluence.py")
    logger.info("  2. Update Confluence credentials in configs/confluence.py")


# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    logger.info(f"Starting {ServerConfig.SERVER_NAME} with transport: {ServerConfig.TRANSPORT_TYPE}")
    
    # Run the MCP server
    if ServerConfig.TRANSPORT_TYPE == "stdio":
        mcp.run(transport='stdio')
    elif ServerConfig.TRANSPORT_TYPE == "http":
        logger.info(f"HTTP server starting on {ServerConfig.HTTP_HOST}:{ServerConfig.HTTP_PORT}{ServerConfig.HTTP_PATH}")
        # Note: HTTP transport configuration would go here
        mcp.run(transport='stdio')  # Fallback to stdio for now
    else:
        logger.warning(f"Unknown transport type: {ServerConfig.TRANSPORT_TYPE}, falling back to stdio")
        mcp.run(transport='stdio')
