"""
Verbalized Sampling Wrapper

MCP wrapper for verbalized sampling tool that registers all tool functions
with FastMCP server.
"""

import json

from mcp.server import FastMCP

from src.tools.reasoning.verbalized_sampling_tool import (
    initialize_session,
    submit_samples,
    get_all_samples,
    resample,
    list_sessions,
    get_session_status,
    export_session,
    delete_session
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


def register_verbalized_sampling_tools(mcp: FastMCP):
    """Register all verbalized sampling tools with the MCP server."""
    
    @mcp.tool()
    async def verbalized_sampling_initialize(
        query: str,
        mode: str = "generate",
        input_content: str | None = None,
        num_samples: int = 5,
        max_probability: float = 0.10
    ) -> str:
        """
        Initialize a new verbalized sampling session for diverse response generation.
        
        This tool enables generating multiple creative responses by sampling from the tails
        of the probability distribution. Instead of getting the same response repeatedly,
        you get 5 diverse options with low probabilities, then randomly select one.
        
        **Use Cases:**
        - Getting creative variations of answers
        - Improving existing content with diverse suggestions
        - Breaking out of repetitive response patterns
        - Exploring alternative solutions to problems
        
        **Workflow:**
        1. Initialize session with a query
        2. LLM generates 5 diverse responses with probabilities < 0.10
        3. Submit samples via verbalized_sampling_submit
        4. Tool randomly selects and returns one response
        
        **Modes:**
        - 'generate': Generate new creative responses (max_prob: 0.10)
        - 'improve': Improve existing content (max_prob: 0.10)
        - 'explore': Maximum creativity mode (max_prob: 0.05)
        - 'balanced': Mix creativity with reliability (max_prob: 0.15)
        
        **Example:**
        ```python
        # Initialize for a creative joke
        result = await verbalized_sampling_initialize(
            query="Tell me a coffee joke",
            mode="generate",
            num_samples=5
        )
        # LLM then generates 5 diverse jokes with probabilities
        ```
        
        Args:
            query: The query or question to generate samples for
            mode: Operating mode (generate, improve, explore, balanced)
            input_content: Content to improve (required for 'improve' mode)
            num_samples: Number of samples to generate (default: 5, range: 3-10)
            max_probability: Maximum probability threshold (default: 0.10)
            
        Returns:
            JSON string with session_id and LLM instructions for generating samples
        """
        try:
            result = initialize_session(
                query=query,
                mode=mode,
                input_content=input_content,
                num_samples=num_samples,
                max_probability=max_probability
            )
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error initializing verbalized sampling: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)
    
    @mcp.tool()
    async def verbalized_sampling_submit(
        session_id: str,
        samples: list[dict],
        selection_strategy: str = "uniform"
    ) -> str:
        """
        Submit generated samples and get a randomly selected response.
        
        After LLM generates 5 diverse responses, submit them here to get one
        randomly selected based on the chosen strategy.
        
        **Selection Strategies:**
        - 'uniform': Equal probability for all samples (default, pure random)
        - 'weighted': Weight by inverse probability (favors more creative/lower prob samples)
        - 'lowest': Always select the lowest probability (most creative)
        - 'highest': Select the highest probability (most conservative, still < 0.10)
        
        **Sample Format:**
        Each sample must be a dictionary with:
        - 'text': The response text (string)
        - 'probability': Numeric probability score (must be < max_probability)
        
        **Example:**
        ```python
        samples = [
            {"text": "Why did coffee file a police report? It got mugged!", "probability": 0.08},
            {"text": "How does coffee show affection? A latte love!", "probability": 0.07},
            {"text": "Espresso yourself! Life's too short for bad coffee.", "probability": 0.09},
            {"text": "Why did the latte go to therapy? Too much foam.", "probability": 0.06},
            {"text": "Cold brew is coffee that took a gap year.", "probability": 0.05}
        ]
        
        result = await verbalized_sampling_submit(
            session_id="vs_1234567890_abcd1234",
            samples=samples,
            selection_strategy="weighted"  # Favors more creative samples
        )
        ```
        
        Args:
            session_id: The session identifier from initialize
            samples: List of sample dictionaries with 'text' and 'probability' fields
            selection_strategy: Strategy for selecting sample (uniform, weighted, lowest, highest)
            
        Returns:
            JSON string with selected sample and statistics
        """
        try:
            result = submit_samples(
                session_id=session_id,
                samples=samples,
                selection_strategy=selection_strategy
            )
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error submitting samples: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)
    
    @mcp.tool()
    async def verbalized_sampling_get_all(
        session_id: str
    ) -> str:
        """
        Retrieve all samples without selection.
        
        Get all generated samples along with statistics and metadata.
        Useful for analyzing the diversity of responses before selection.
        
        Args:
            session_id: The session identifier
            
        Returns:
            JSON string with all samples, statistics, and session data
        """
        try:
            result = get_all_samples(session_id=session_id)
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error getting all samples: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)
    
    @mcp.tool()
    async def verbalized_sampling_resample(
        session_id: str
    ) -> str:
        """
        Generate new instructions for resampling the same query.
        
        If you want to explore more diverse options for the same query,
        use this to generate a fresh set of 5 samples. Previous samples
        are saved to session history.
        
        **Example:**
        ```python
        # After first round of samples
        result = await verbalized_sampling_resample(
            session_id="vs_1234567890_abcd1234"
        )
        # LLM generates 5 new diverse responses
        # Submit via verbalized_sampling_submit again
        ```
        
        Args:
            session_id: The session identifier
            
        Returns:
            JSON string with new LLM instructions for generating samples
        """
        try:
            result = resample(session_id=session_id)
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error resampling: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)
    
    @mcp.tool()
    async def verbalized_sampling_list() -> str:
        """
        List all active verbalized sampling sessions.
        
        Get a summary of all sessions currently in memory.
        Useful for finding session IDs or checking on multiple sampling efforts.
        
        Returns:
            JSON string with list of session summaries
        """
        try:
            result = list_sessions()
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)
    
    @mcp.tool()
    async def verbalized_sampling_status(
        session_id: str
    ) -> str:
        """
        Get current status of a verbalized sampling session.
        
        Check session status, metadata, and progress without retrieving all samples.
        
        Args:
            session_id: The session identifier
            
        Returns:
            JSON string with session status and metadata
        """
        try:
            result = get_session_status(session_id=session_id)
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error getting session status: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)
    
    @mcp.tool()
    async def verbalized_sampling_export(
        session_id: str,
        format: str = "json"
    ) -> str:
        """
        Export session data in specified format.
        
        Export complete session data including all samples, selection,
        and statistics for documentation or analysis.
        
        **Formats:**
        - 'json': Complete session data as JSON
        - 'markdown': Formatted markdown report
        - 'text': Simple text summary
        
        Args:
            session_id: The session identifier
            format: Export format (json, markdown, text)
            
        Returns:
            JSON string with exported data
        """
        try:
            result = export_session(session_id=session_id, format=format)
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error exporting session: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)
    
    @mcp.tool()
    async def verbalized_sampling_delete(
        session_id: str
    ) -> str:
        """
        Delete a verbalized sampling session.
        
        Remove session from memory to free up resources.
        
        Args:
            session_id: The session identifier
            
        Returns:
            JSON string with deletion confirmation
        """
        try:
            result = delete_session(session_id=session_id)
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)
    
    logger.info("Verbalized Sampling tools registered successfully")
