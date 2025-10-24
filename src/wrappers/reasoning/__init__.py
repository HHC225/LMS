"""
Reasoning Tool Wrappers
Wrapper functions for recursive thinking, sequential thinking, tree of thoughts, verbalized sampling, and counterfactual reasoning tools
"""
from .recursive_thinking_wrappers import (
    recursive_thinking_initialize,
    recursive_thinking_update_latent,
    recursive_thinking_update_answer,
    recursive_thinking_get_result,
    recursive_thinking_reset
)
from .sequential_thinking_wrapper import st
from .tree_of_thoughts_wrapper import tt
from .verbalized_sampling_wrapper import register_verbalized_sampling_tools
from .counterfactual_reasoning_wrapper import (
    counterfactual_initialize,
    counterfactual_phase1,
    counterfactual_phase2,
    counterfactual_phase3_step1,
    counterfactual_phase3_step2,
    counterfactual_phase3_step3,
    counterfactual_phase3_step4,
    counterfactual_phase4,
    counterfactual_get_result,
    counterfactual_reset,
    counterfactual_list_sessions
)

__all__ = [
    # Recursive Thinking
    'recursive_thinking_initialize',
    'recursive_thinking_update_latent',
    'recursive_thinking_update_answer',
    'recursive_thinking_get_result',
    'recursive_thinking_reset',
    # Sequential Thinking
    'st',
    # Tree of Thoughts
    'tt',
    # Verbalized Sampling
    'register_verbalized_sampling_tools',
    # Counterfactual Reasoning
    'counterfactual_initialize',
    'counterfactual_phase1',
    'counterfactual_phase2',
    'counterfactual_phase3_step1',
    'counterfactual_phase3_step2',
    'counterfactual_phase3_step3',
    'counterfactual_phase3_step4',
    'counterfactual_phase4',
    'counterfactual_get_result',
    'counterfactual_reset',
    'counterfactual_list_sessions'
]
