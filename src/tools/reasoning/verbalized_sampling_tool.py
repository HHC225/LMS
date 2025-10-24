"""
Verbalized Sampling Tool

Core implementation of the verbalized sampling tool that enables diverse response generation
through tail distribution sampling. This tool allows LLMs to generate multiple creative
responses and randomly select one, breaking out of repetitive response patterns.
"""

import json
import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

from configs.verbalized_sampling import VERBALIZED_SAMPLING_CONFIG
from src.utils.logger import get_logger

logger = get_logger(__name__)

# In-memory session storage
_sessions: Dict[str, Dict[str, Any]] = {}


def _generate_session_id() -> str:
    """Generate a unique session ID."""
    timestamp = int(time.time())
    random_suffix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
    return f"vs_{timestamp}_{random_suffix}"


def _validate_samples(
    samples: List[Dict[str, Any]], 
    mode: str, 
    num_samples: int,
    max_probability: float
) -> tuple[bool, Optional[str]]:
    """
    Validate sample data.
    
    Returns:
        (is_valid, error_message)
    """
    config = VERBALIZED_SAMPLING_CONFIG
    validation = config["validation"]
    
    # Check number of samples
    if len(samples) != num_samples:
        return False, f"Expected {num_samples} samples, got {len(samples)}"
    
    if len(samples) < validation["min_samples"]:
        return False, f"Minimum {validation['min_samples']} samples required"
    
    if len(samples) > validation["max_samples"]:
        return False, f"Maximum {validation['max_samples']} samples allowed"
    
    # Validate each sample
    for idx, sample in enumerate(samples):
        # Check required fields
        if "text" not in sample or "probability" not in sample:
            return False, f"Sample {idx+1} missing required fields (text, probability)"
        
        # Check text length
        text_len = len(sample["text"])
        if text_len < validation["min_text_length"]:
            return False, f"Sample {idx+1} text too short (min: {validation['min_text_length']})"
        
        if text_len > validation["max_text_length"]:
            return False, f"Sample {idx+1} text too long (max: {validation['max_text_length']})"
        
        # Check probability
        prob = sample["probability"]
        if not isinstance(prob, (int, float)):
            return False, f"Sample {idx+1} probability must be numeric"
        
        if prob < validation["min_probability"]:
            return False, f"Sample {idx+1} probability too low (min: {validation['min_probability']})"
        
        if prob >= max_probability:
            return False, f"Sample {idx+1} probability {prob} exceeds limit {max_probability}"
    
    return True, None


def _select_sample(samples: List[Dict[str, Any]], strategy: str) -> Dict[str, Any]:
    """
    Select a sample based on the specified strategy.
    
    Args:
        samples: List of sample dictionaries
        strategy: Selection strategy (uniform, weighted, lowest, highest)
        
    Returns:
        Selected sample dictionary
    """
    if strategy == "uniform":
        # Equal probability for all samples
        return random.choice(samples)
    
    elif strategy == "weighted":
        # Weight by inverse probability (lower prob = higher weight = more creative)
        weights = [1.0 / sample["probability"] for sample in samples]
        selected = random.choices(samples, weights=weights, k=1)[0]
        return selected
    
    elif strategy == "lowest":
        # Always select the sample with lowest probability (most creative)
        return min(samples, key=lambda x: x["probability"])
    
    elif strategy == "highest":
        # Select the sample with highest probability (most conservative, but still < 0.10)
        return max(samples, key=lambda x: x["probability"])
    
    else:
        # Default to uniform
        logger.warning(f"Unknown strategy '{strategy}', using uniform")
        return random.choice(samples)


def _calculate_statistics(samples: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate statistics for the samples."""
    probabilities = [s["probability"] for s in samples]
    text_lengths = [len(s["text"]) for s in samples]
    
    return {
        "num_samples": len(samples),
        "probability": {
            "min": min(probabilities),
            "max": max(probabilities),
            "mean": sum(probabilities) / len(probabilities),
            "sum": sum(probabilities)
        },
        "text_length": {
            "min": min(text_lengths),
            "max": max(text_lengths),
            "mean": sum(text_lengths) / len(text_lengths)
        },
        "creativity_index": sum(1.0 / p for p in probabilities) / len(probabilities)
    }


def initialize_session(
    query: str,
    mode: str = "generate",
    input_content: Optional[str] = None,
    num_samples: int = 5,
    max_probability: float = 0.10
) -> Dict[str, Any]:
    """
    Initialize a new verbalized sampling session.
    
    Args:
        query: The query or question to generate samples for
        mode: Operating mode (generate, improve, explore, balanced)
        input_content: Content to improve (required for 'improve' mode)
        num_samples: Number of samples to generate (default: 5)
        max_probability: Maximum probability threshold (default: 0.10)
        
    Returns:
        Session initialization data including session_id and LLM instructions
    """
    config = VERBALIZED_SAMPLING_CONFIG
    
    # Validate mode
    if mode not in config["modes"]:
        raise ValueError(f"Invalid mode '{mode}'. Valid modes: {list(config['modes'].keys())}")
    
    # Validate num_samples
    if num_samples < config["validation"]["min_samples"] or num_samples > config["validation"]["max_samples"]:
        raise ValueError(f"num_samples must be between {config['validation']['min_samples']} and {config['validation']['max_samples']}")
    
    # For improve mode, input_content is required
    if mode == "improve" and not input_content:
        raise ValueError("input_content is required for 'improve' mode")
    
    # Generate session ID
    session_id = _generate_session_id()
    
    # Get mode configuration
    mode_config = config["modes"][mode]
    mode_max_prob = mode_config["max_prob"]
    
    # Use provided max_probability or mode default
    final_max_prob = min(max_probability, mode_max_prob)
    
    # Generate LLM instructions
    instruction_template = mode_config["instruction_template"]
    llm_instructions = instruction_template.format(
        num_samples=num_samples,
        max_prob=final_max_prob,
        query=query,
        input_content=input_content or ""
    )
    
    # Create session
    session = {
        "session_id": session_id,
        "query": query,
        "mode": mode,
        "input_content": input_content,
        "num_samples": num_samples,
        "max_probability": final_max_prob,
        "samples": [],
        "selected_sample": None,
        "selection_strategy": None,
        "history": [],
        "statistics": None,
        "status": "initialized",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    _sessions[session_id] = session
    
    logger.info(f"Initialized verbalized sampling session: {session_id}")
    
    return {
        "success": True,
        "session_id": session_id,
        "mode": mode,
        "num_samples": num_samples,
        "max_probability": final_max_prob,
        "llm_instructions": llm_instructions,
        "message": f"Session initialized. Please generate {num_samples} diverse responses.",
        "next_action": "submit_samples"
    }


def submit_samples(
    session_id: str,
    samples: List[Dict[str, Any]],
    selection_strategy: str = "uniform"
) -> Dict[str, Any]:
    """
    Submit generated samples and get a randomly selected response.
    
    Args:
        session_id: The session identifier
        samples: List of sample dictionaries with 'text' and 'probability' fields
        selection_strategy: Strategy for selecting sample (uniform, weighted, lowest, highest)
        
    Returns:
        Selected sample and session data
    """
    if session_id not in _sessions:
        raise ValueError(f"Session '{session_id}' not found")
    
    session = _sessions[session_id]
    config = VERBALIZED_SAMPLING_CONFIG
    
    # Validate selection strategy
    if selection_strategy not in config["selection_strategies"]:
        raise ValueError(f"Invalid strategy '{selection_strategy}'. Valid: {config['selection_strategies']}")
    
    # Validate samples
    is_valid, error_msg = _validate_samples(
        samples, 
        session["mode"], 
        session["num_samples"],
        session["max_probability"]
    )
    
    if not is_valid:
        raise ValueError(f"Sample validation failed: {error_msg}")
    
    # Calculate statistics
    statistics = _calculate_statistics(samples)
    
    # Select a sample
    selected = _select_sample(samples, selection_strategy)
    
    # Add selection metadata
    selected_with_meta = {
        **selected,
        "selected_at": datetime.now().isoformat(),
        "selection_strategy": selection_strategy
    }
    
    # Update session
    session["samples"] = samples
    session["selected_sample"] = selected_with_meta
    session["selection_strategy"] = selection_strategy
    session["statistics"] = statistics
    session["status"] = "completed"
    session["updated_at"] = datetime.now().isoformat()
    
    # Add to history
    session["history"].append({
        "timestamp": datetime.now().isoformat(),
        "action": "submit_samples",
        "num_samples": len(samples),
        "selected_index": samples.index(selected),
        "selection_strategy": selection_strategy
    })
    
    logger.info(f"Samples submitted for session {session_id}, selected: {selection_strategy}")
    
    return {
        "success": True,
        "session_id": session_id,
        "selected_sample": selected_with_meta,
        "statistics": statistics,
        "message": f"Sample selected using '{selection_strategy}' strategy",
        "status": "completed"
    }


def get_all_samples(session_id: str) -> Dict[str, Any]:
    """
    Retrieve all samples without selection.
    
    Args:
        session_id: The session identifier
        
    Returns:
        All samples and session data
    """
    if session_id not in _sessions:
        raise ValueError(f"Session '{session_id}' not found")
    
    session = _sessions[session_id]
    
    if not session["samples"]:
        return {
            "success": False,
            "session_id": session_id,
            "message": "No samples submitted yet",
            "status": session["status"]
        }
    
    return {
        "success": True,
        "session_id": session_id,
        "query": session["query"],
        "mode": session["mode"],
        "samples": session["samples"],
        "statistics": session["statistics"],
        "selected_sample": session["selected_sample"],
        "status": session["status"]
    }


def resample(session_id: str) -> Dict[str, Any]:
    """
    Generate new instructions for resampling the same query.
    
    Args:
        session_id: The session identifier
        
    Returns:
        New LLM instructions for generating samples
    """
    if session_id not in _sessions:
        raise ValueError(f"Session '{session_id}' not found")
    
    session = _sessions[session_id]
    
    # Save current samples to history if they exist
    if session["samples"]:
        session["history"].append({
            "timestamp": datetime.now().isoformat(),
            "action": "resample",
            "previous_samples": session["samples"],
            "previous_selected": session["selected_sample"]
        })
    
    # Reset samples
    session["samples"] = []
    session["selected_sample"] = None
    session["status"] = "initialized"
    session["updated_at"] = datetime.now().isoformat()
    
    # Generate new instructions
    config = VERBALIZED_SAMPLING_CONFIG
    mode_config = config["modes"][session["mode"]]
    instruction_template = mode_config["instruction_template"]
    
    llm_instructions = instruction_template.format(
        num_samples=session["num_samples"],
        max_prob=session["max_probability"],
        query=session["query"],
        input_content=session["input_content"] or ""
    )
    
    logger.info(f"Resampling session: {session_id}")
    
    return {
        "success": True,
        "session_id": session_id,
        "llm_instructions": llm_instructions,
        "message": f"Ready for resampling. Generate {session['num_samples']} new diverse responses.",
        "next_action": "submit_samples"
    }


def list_sessions() -> Dict[str, Any]:
    """
    List all active sessions.
    
    Returns:
        Summary of all sessions
    """
    session_summaries = []
    
    for session_id, session in _sessions.items():
        session_summaries.append({
            "session_id": session_id,
            "query": session["query"][:50] + "..." if len(session["query"]) > 50 else session["query"],
            "mode": session["mode"],
            "status": session["status"],
            "num_samples": session["num_samples"],
            "created_at": session["created_at"],
            "has_selection": session["selected_sample"] is not None
        })
    
    return {
        "success": True,
        "total_sessions": len(session_summaries),
        "sessions": session_summaries
    }


def get_session_status(session_id: str) -> Dict[str, Any]:
    """
    Get current status of a session.
    
    Args:
        session_id: The session identifier
        
    Returns:
        Session status and metadata
    """
    if session_id not in _sessions:
        raise ValueError(f"Session '{session_id}' not found")
    
    session = _sessions[session_id]
    
    return {
        "success": True,
        "session_id": session_id,
        "status": session["status"],
        "mode": session["mode"],
        "query": session["query"],
        "num_samples": session["num_samples"],
        "max_probability": session["max_probability"],
        "samples_submitted": len(session["samples"]) > 0,
        "has_selection": session["selected_sample"] is not None,
        "selection_strategy": session["selection_strategy"],
        "created_at": session["created_at"],
        "updated_at": session["updated_at"],
        "history_length": len(session["history"])
    }


def export_session(session_id: str, format: str = "json") -> Dict[str, Any]:
    """
    Export session data in specified format.
    
    Args:
        session_id: The session identifier
        format: Export format (json, markdown, text)
        
    Returns:
        Exported session data
    """
    if session_id not in _sessions:
        raise ValueError(f"Session '{session_id}' not found")
    
    session = _sessions[session_id]
    config = VERBALIZED_SAMPLING_CONFIG
    
    if format not in config["export"]["formats"]:
        raise ValueError(f"Invalid format '{format}'. Valid: {config['export']['formats']}")
    
    if format == "json":
        return {
            "success": True,
            "format": "json",
            "data": json.dumps(session, ensure_ascii=False, indent=2)
        }
    
    elif format == "markdown":
        md_content = f"""# Verbalized Sampling Session Report

## Session Information
- **Session ID:** {session['session_id']}
- **Mode:** {session['mode']}
- **Status:** {session['status']}
- **Created:** {session['created_at']}

## Query
{session['query']}

## Generated Samples
"""
        if session["samples"]:
            for idx, sample in enumerate(session["samples"], 1):
                selected_marker = " ⭐ **SELECTED**" if session["selected_sample"] and sample["text"] == session["selected_sample"]["text"] else ""
                md_content += f"\n### Sample {idx}{selected_marker}\n"
                md_content += f"**Probability:** {sample['probability']}\n\n"
                md_content += f"{sample['text']}\n"
        
        if session["statistics"]:
            stats = session["statistics"]
            md_content += f"\n## Statistics\n"
            md_content += f"- **Number of Samples:** {stats['num_samples']}\n"
            md_content += f"- **Probability Range:** {stats['probability']['min']:.3f} - {stats['probability']['max']:.3f}\n"
            md_content += f"- **Mean Probability:** {stats['probability']['mean']:.3f}\n"
            md_content += f"- **Creativity Index:** {stats['creativity_index']:.2f}\n"
        
        return {
            "success": True,
            "format": "markdown",
            "data": md_content
        }
    
    elif format == "text":
        text_content = f"Verbalized Sampling Session: {session_id}\n"
        text_content += f"Query: {session['query']}\n\n"
        
        if session["selected_sample"]:
            text_content += f"Selected Sample ({session['selection_strategy']}):\n"
            text_content += f"{session['selected_sample']['text']}\n"
            text_content += f"(Probability: {session['selected_sample']['probability']})\n"
        
        return {
            "success": True,
            "format": "text",
            "data": text_content
        }


def delete_session(session_id: str) -> Dict[str, Any]:
    """
    Delete a session.
    
    Args:
        session_id: The session identifier
        
    Returns:
        Deletion confirmation
    """
    if session_id not in _sessions:
        raise ValueError(f"Session '{session_id}' not found")
    
    del _sessions[session_id]
    
    logger.info(f"Deleted session: {session_id}")
    
    return {
        "success": True,
        "session_id": session_id,
        "message": "Session deleted successfully"
    }
