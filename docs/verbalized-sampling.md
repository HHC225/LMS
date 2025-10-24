# Verbalized Sampling Tool

## Overview

The **Verbalized Sampling** tool enables diverse and creative response generation through tail distribution sampling. Instead of getting the same response repeatedly, this tool generates 5 diverse options with low probabilities and randomly selects one, breaking out of repetitive response patterns.

### Key Concept

Traditional LLM responses tend to converge on high-probability, "safe" answers. By explicitly sampling from the **tails of the probability distribution** (probability < 0.10), we force the generation of more creative, diverse, and unexpected responses.

**Example:**
- **Without Verbalized Sampling:** Asking "Tell me a coffee joke" 5 times yields similar jokes
- **With Verbalized Sampling:** Each sample provides a distinctly different creative response

## Quick Start

### Basic Workflow

1. **Initialize** a session with your query
2. **LLM generates** 5 diverse responses with probabilities
3. **Submit** samples to the tool
4. **Tool selects** one response randomly based on strategy

### Simple Example

```python
# Step 1: Initialize
result = await verbalized_sampling_initialize(
    query="Tell me a coffee joke",
    mode="generate"
)
session_id = result["session_id"]

# Step 2: LLM generates 5 diverse jokes (done by LLM based on instructions)
samples = [
    {"text": "How does coffee show affection? It gives you a latte love!", "probability": 0.08},
    {"text": "Espresso may not solve problems, but it's a good shot.", "probability": 0.07},
    {"text": "Why did latte go to therapy? Too much foam to deal with.", "probability": 0.09},
    {"text": "What do you call sad coffee? Depresso.", "probability": 0.06},
    {"text": "Cold brew is coffee that took a gap year to find itself.", "probability": 0.05}
]

# Step 3: Submit and get random selection
result = await verbalized_sampling_submit(
    session_id=session_id,
    samples=samples,
    selection_strategy="uniform"
)
print(result["selected_sample"]["text"])
```

## Operating Modes

### 1. Generate Mode (Default)
- **Purpose:** Generate new creative responses from scratch
- **Max Probability:** 0.10
- **Use Case:** Getting diverse answers to any question

```python
result = await verbalized_sampling_initialize(
    query="What are innovative ways to improve team collaboration?",
    mode="generate"
)
```

### 2. Improve Mode
- **Purpose:** Generate creative improvements to existing content
- **Max Probability:** 0.10
- **Use Case:** Enhancing reports, documents, or text

```python
result = await verbalized_sampling_initialize(
    query="Improve this report",
    mode="improve",
    input_content="Original report text here..."
)
```

### 3. Explore Mode
- **Purpose:** Maximum creativity with extreme tail sampling
- **Max Probability:** 0.05 (even more creative!)
- **Use Case:** Brainstorming unconventional ideas

```python
result = await verbalized_sampling_initialize(
    query="What are radical solutions to reduce meeting time?",
    mode="explore"
)
```

### 4. Balanced Mode
- **Purpose:** Mix creativity with reliability
- **Max Probability:** 0.15
- **Use Case:** When you want variety but not too extreme

```python
result = await verbalized_sampling_initialize(
    query="How can we optimize our deployment pipeline?",
    mode="balanced"
)
```

## Selection Strategies

Control how the tool selects one response from the 5 samples:

### 1. Uniform (Default)
- **Behavior:** Equal probability for all samples (pure random)
- **Best For:** Maximum unpredictability

```python
result = await verbalized_sampling_submit(
    session_id=session_id,
    samples=samples,
    selection_strategy="uniform"
)
```

### 2. Weighted
- **Behavior:** Inverse probability weighting (lower prob = higher selection weight)
- **Best For:** Favoring more creative samples

```python
result = await verbalized_sampling_submit(
    session_id=session_id,
    samples=samples,
    selection_strategy="weighted"
)
```

### 3. Lowest
- **Behavior:** Always select the sample with lowest probability
- **Best For:** Consistently choosing the most creative option

```python
result = await verbalized_sampling_submit(
    session_id=session_id,
    samples=samples,
    selection_strategy="lowest"
)
```

### 4. Highest
- **Behavior:** Select the sample with highest probability (still < 0.10)
- **Best For:** Most conservative creative option

```python
result = await verbalized_sampling_submit(
    session_id=session_id,
    samples=samples,
    selection_strategy="highest"
)
```

## Available Actions

### Initialize Session
```python
verbalized_sampling_initialize(
    query: str,                      # Required: Your question or task
    mode: str = "generate",          # Mode: generate, improve, explore, balanced
    input_content: str | None = None, # Required for 'improve' mode
    num_samples: int = 5,            # Number of samples (3-10)
    max_probability: float = 0.10    # Max probability threshold
)
```

### Submit Samples
```python
verbalized_sampling_submit(
    session_id: str,                  # Required: Session ID from initialize
    samples: list[dict],              # Required: List of generated samples
    selection_strategy: str = "uniform" # Strategy: uniform, weighted, lowest, highest
)
```

### Get All Samples
```python
verbalized_sampling_get_all(
    session_id: str  # Required: Session ID
)
# Returns all samples without selection, useful for analysis
```

### Resample
```python
verbalized_sampling_resample(
    session_id: str  # Required: Session ID
)
# Generate new instructions for creating fresh samples for same query
```

### List Sessions
```python
verbalized_sampling_list()
# Returns summary of all active sessions
```

### Get Status
```python
verbalized_sampling_status(
    session_id: str  # Required: Session ID
)
# Check session status and metadata
```

### Export Session
```python
verbalized_sampling_export(
    session_id: str,           # Required: Session ID
    format: str = "json"       # Format: json, markdown, text
)
# Export complete session data for documentation
```

### Delete Session
```python
verbalized_sampling_delete(
    session_id: str  # Required: Session ID
)
# Remove session from memory
```

## Advanced Use Cases

### 1. Content Improvement Pipeline

```python
# Start with original content
original = "Our API is fast and reliable."

# Initialize improvement session
result = await verbalized_sampling_initialize(
    query="Make this more compelling and specific",
    mode="improve",
    input_content=original
)

# LLM generates 5 diverse improvements
# Submit and get one creative improvement
improved = await verbalized_sampling_submit(
    session_id=result["session_id"],
    samples=generated_samples,
    selection_strategy="weighted"  # Favor more creative options
)
```

### 2. Brainstorming Session

```python
# Explore multiple creative angles
for round in range(3):
    result = await verbalized_sampling_initialize(
        query="How can we reduce server costs?",
        mode="explore"  # Maximum creativity
    )
    
    # Generate samples and select
    # Each round gives different creative perspectives
```

### 3. Report Variation Generation

```python
# Generate different versions of the same report
result = await verbalized_sampling_initialize(
    query="Create executive summary",
    mode="generate",
    num_samples=5
)

# Get all samples to review options
all_samples = await verbalized_sampling_get_all(
    session_id=result["session_id"]
)

# Export for documentation
export = await verbalized_sampling_export(
    session_id=result["session_id"],
    format="markdown"
)
```

## Sample Format

Each sample must be a dictionary with these fields:

```python
{
    "text": "Your response text here",  # Required: string
    "probability": 0.08                 # Required: float < max_probability
}
```

### Validation Rules

- **Number of Samples:** 3-10 (default: 5)
- **Probability Range:** 0.01 - max_probability
- **Max Probability:** Depends on mode (0.05-0.15)
- **Text Length:** 10-5000 characters
- **Required Fields:** text, probability

## Statistics and Metadata

After submitting samples, you'll receive statistics:

```json
{
    "statistics": {
        "num_samples": 5,
        "probability": {
            "min": 0.05,
            "max": 0.09,
            "mean": 0.07,
            "sum": 0.35
        },
        "text_length": {
            "min": 45,
            "max": 120,
            "mean": 82
        },
        "creativity_index": 14.5  // Higher = more creative
    }
}
```

## Best Practices

### 1. Choose the Right Mode
- **Generate:** New content from scratch
- **Improve:** Enhance existing content
- **Explore:** Maximum creativity needed
- **Balanced:** Mix of creativity and reliability

### 2. Select Appropriate Strategy
- **Uniform:** When you want pure randomness
- **Weighted:** When you prefer creative options
- **Lowest:** For consistently maximum creativity
- **Highest:** For slightly more conservative creativity

### 3. Probability Guidelines
- **< 0.05:** Very creative, potentially risky
- **0.05-0.08:** Sweet spot for creativity
- **0.08-0.10:** Creative but safer
- **> 0.10:** Outside tail sampling range

### 4. Use Resampling
If initial samples aren't diverse enough, use `resample()` to generate fresh options.

### 5. Export Important Sessions
Save interesting results using `export()` for documentation and analysis.

## Integration Examples

### With Report Generator

```python
# Generate creative report intro
result = await verbalized_sampling_initialize(
    query="Create an engaging introduction for incident report",
    mode="generate"
)

# Submit samples and get selection
intro = await verbalized_sampling_submit(
    session_id=result["session_id"],
    samples=samples,
    selection_strategy="weighted"
)

# Use in report
report = create_report(intro=intro["selected_sample"]["text"])
```

### With Planning Tools

```python
# Generate creative project names
result = await verbalized_sampling_initialize(
    query="Suggest creative names for authentication service",
    mode="explore",
    num_samples=5
)

# Get diverse options
all_names = await verbalized_sampling_get_all(
    session_id=result["session_id"]
)
```

## Troubleshooting

### Problem: Samples rejected due to probability

**Solution:** Ensure all probabilities are less than the mode's max_probability:
- Generate mode: < 0.10
- Explore mode: < 0.05
- Balanced mode: < 0.15

### Problem: Not enough diversity in samples

**Solutions:**
1. Switch to `explore` mode for more creativity
2. Use `resample()` to generate fresh samples
3. Adjust temperature in LLM generation

### Problem: Sample validation fails

**Check:**
- All samples have 'text' and 'probability' fields
- Text length is 10-5000 characters
- Probability is numeric and in valid range
- Correct number of samples (matches num_samples)

## Performance Considerations

### Session Management
- Sessions are stored in memory
- Use `delete_session()` to free resources
- Sessions timeout after inactivity (configurable)

### Scalability
- Each session uses minimal memory (~5-10KB)
- Can handle hundreds of concurrent sessions
- Consider cleanup for long-running servers

## Configuration

Default settings in `configs/verbalized_sampling.py`:

```python
VERBALIZED_SAMPLING_CONFIG = {
    "default_num_samples": 5,
    "default_max_probability": 0.10,
    "selection_strategies": ["uniform", "weighted", "lowest", "highest"],
    "validation": {
        "min_samples": 3,
        "max_samples": 10,
        "min_probability": 0.01,
        "max_text_length": 5000
    }
}
```

## Summary

Verbalized Sampling is a powerful tool for:
- **Breaking repetitive patterns** in LLM responses
- **Generating diverse creative options** through tail sampling
- **Enhancing content** with varied perspectives
- **Exploring unconventional ideas** systematically

Start with `generate` mode and `uniform` strategy, then experiment with other combinations to find what works best for your use case!
