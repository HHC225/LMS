"""
Verbalized Sampling Configuration

Configuration for the verbalized sampling tool that enables diverse response generation
through tail distribution sampling.
"""

VERBALIZED_SAMPLING_CONFIG = {
    # Default number of diverse samples to generate
    "default_num_samples": 5,
    
    # Default maximum probability for tail sampling
    "default_max_probability": 0.10,
    
    # Available selection strategies
    "selection_strategies": ["uniform", "weighted", "lowest", "highest"],
    
    # Operating modes with their configurations
    "modes": {
        "generate": {
            "max_prob": 0.10,
            "description": "Generate new creative responses from scratch",
            "instruction_template": """Generate {num_samples} diverse and creative responses to the following query.

**Requirements:**
- Each response must be substantially different from others
- Include a numeric probability score (must be < {max_prob})
- Sample from the tails of the distribution for maximum creativity
- Focus on unexpected, creative, and original answers

**Query:** {query}

**Format:** Return each response as a JSON object with 'text' and 'probability' fields."""
        },
        "improve": {
            "max_prob": 0.10,
            "description": "Generate creative improvements to existing content",
            "instruction_template": """Generate {num_samples} diverse improvement suggestions for the content below.

**Requirements:**
- Each suggestion must offer a unique perspective or approach
- Include a numeric probability score (must be < {max_prob})
- Sample from the tails of the distribution for creative variations
- Focus on substantial improvements, not minor tweaks

**Original Query:** {query}

**Content to Improve:**
{input_content}

**Format:** Return each improvement as a JSON object with 'text' and 'probability' fields."""
        },
        "explore": {
            "max_prob": 0.05,
            "description": "Maximum creativity mode with extreme tail sampling",
            "instruction_template": """Generate {num_samples} highly creative and unconventional responses.

**Requirements:**
- Prioritize originality and unconventional thinking
- Include a numeric probability score (must be < {max_prob})
- Sample from the extreme tails of the distribution
- Push boundaries while remaining relevant

**Query:** {query}

**Format:** Return each response as a JSON object with 'text' and 'probability' fields."""
        },
        "balanced": {
            "max_prob": 0.15,
            "description": "Balanced mode mixing creativity with reliability",
            "instruction_template": """Generate {num_samples} responses balancing creativity and reliability.

**Requirements:**
- Mix creative and practical approaches
- Include a numeric probability score (must be < {max_prob})
- Ensure variety while maintaining usefulness
- Consider both conventional and novel perspectives

**Query:** {query}

**Format:** Return each response as a JSON object with 'text' and 'probability' fields."""
        }
    },
    
    # Validation rules
    "validation": {
        "min_samples": 3,
        "max_samples": 10,
        "min_probability": 0.01,
        "max_probability": 0.20,
        "max_text_length": 5000,
        "min_text_length": 10
    },
    
    # Session configuration
    "session": {
        "max_history_items": 100,
        "session_timeout_minutes": 60,
        "auto_cleanup": True
    },
    
    # Export configuration
    "export": {
        "formats": ["json", "markdown", "text"],
        "include_metadata": True,
        "include_statistics": True
    }
}
