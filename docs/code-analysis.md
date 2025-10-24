# Code Analysis Tool

## Overview

The Code Analysis Tool is designed to analyze enterprise-level source code and generate comprehensive documentation for new developers. It breaks down large codebases into manageable steps to avoid token rate limits, progressively building detailed analysis documentation.

## Key Features

- **Multi-Step Analysis**: Automatically divides large source files into manageable analysis steps
- **Progressive Documentation**: Updates markdown file after each step to avoid token limits
- **Language Support**: Supports Python, JavaScript, TypeScript, Java, C++, Go, Ruby, PHP, C#, Swift, Kotlin, Rust
- **Session Management**: Track multiple analysis sessions concurrently
- **Beginner-Friendly Output**: Generates clear, structured documentation for new developers
- **Real-Time Updates**: Markdown file is updated immediately after each analysis step

## What Gets Analyzed

- **Import Statements**: All external dependencies and libraries used
- **Code Structure**: Classes, functions, methods, and their relationships
- **Method Details**: Purpose, parameters, return values, and logic flow
- **Variable Usage**: How variables are used throughout the code
- **Dependencies**: Dependencies between different code components
- **Data Flow**: How data moves through the application
- **Design Patterns**: Patterns and techniques used in the code

## Architecture

### Tool Flow

```
┌─────────────────┐
│   Initialize    │ ← Read file, count lines, calculate steps
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Analyze Step 1 │ ← Analyze first code segment
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Update Markdown│ ← Immediately update documentation
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Analyze Step 2 │ ← Continue with next segment
└────────┬────────┘
         │
         ▼
        ...
         │
         ▼
┌─────────────────┐
│    Finalize     │ ← Complete analysis and finalize documentation
└─────────────────┘
```

### Step Calculation Logic

- **Lines per Step**: Default 300 lines (configurable)
- **Token Estimation**: ~4 tokens per line on average
- **Safety Margin**: Keeps analysis size under token limits
- **Step Count**: `ceil(total_lines / lines_per_step)`

### Output Structure

The generated markdown includes:

1. **File Overview**: File name, language, total lines, analysis date
2. **Import Analysis**: Categorized dependencies (standard library vs third-party)
3. **Code Structure**: Tables of classes, functions, and methods
4. **Detailed Analysis**: Step-by-step breakdown of code functionality
5. **Summary**: Statistics and completion status

## Available Actions

### 1. Initialize

Start a new code analysis session.

**Parameters:**
- `source_file_path`: Path to the source code file

**Returns:**
- Session ID
- File statistics (lines, language, structure)
- First step information
- LLM instructions for first analysis

**Example:**
```python
result = await code_analysis_initialize(
    source_file_path="/path/to/project/main.py"
)
```

### 2. Analyze Step

Submit analysis for a specific code segment.

**Parameters:**
- `session_id`: Session identifier
- `step_number`: Current step number
- `analysis_content`: Detailed analysis in markdown format

**Returns:**
- Success confirmation
- Progress information
- Next step details (if available)
- LLM instructions for next step

**Example:**
```python
result = await code_analysis_analyze_step(
    session_id="analysis_1234567890_abcd1234",
    step_number=1,
    analysis_content='''
    #### Function: `process_data()`
    
    **Purpose:** Processes incoming data and validates format.
    
    **Parameters:**
    - `data` (dict): Raw data dictionary
    - `strict` (bool): Enable strict validation
    
    **Variables Used:**
    - `validated_data`: Stores validated results
    - `errors`: Collects validation errors
    
    **Dependencies:**
    - Uses `json` module for parsing
    - Imports `Validator` from `utils.validation`
    
    **Flow:**
    1. Validates required fields
    2. Checks data types
    3. Applies business rules
    4. Returns validated data or raises error
    '''
)
```

### 3. Get Status

Check current progress of an analysis session.

**Parameters:**
- `session_id`: Session identifier

**Returns:**
- Current status
- Progress percentage
- Steps completed
- Output file path

**Example:**
```python
result = await code_analysis_get_status(
    session_id="analysis_1234567890_abcd1234"
)
```

### 4. List Sessions

View all active analysis sessions.

**Returns:**
- List of all sessions with status

**Example:**
```python
result = await code_analysis_list_sessions()
```

### 5. Finalize

Complete the analysis and finalize documentation.

**Parameters:**
- `session_id`: Session identifier

**Returns:**
- Completion confirmation
- Final output path
- Analysis statistics

**Example:**
```python
result = await code_analysis_finalize(
    session_id="analysis_1234567890_abcd1234"
)
```

## Complete Workflow Example

### Step 1: Initialize Analysis

```python
# Start analyzing a Python file
result = await code_analysis_initialize(
    source_file_path="/home/user/project/main.py"
)

# Response includes:
# - session_id: "analysis_1702345678_abc12345"
# - totalSteps: 3
# - totalLines: 850
# - language: "python"
# - llmInstructions: {...}
```

### Step 2: Analyze Each Step

```python
# Analyze step 1 (lines 1-300)
result = await code_analysis_analyze_step(
    session_id="analysis_1702345678_abc12345",
    step_number=1,
    analysis_content='''
    ### Import Analysis
    
    The file imports the following modules:
    - `os`, `sys`: System operations
    - `json`: JSON data handling
    - `FastAPI`: Web framework
    - `typing`: Type hints
    
    ### Class: `DataProcessor`
    
    Main class for processing data files.
    
    #### Method: `__init__(config_path: str)`
    - Initializes processor with configuration
    - Loads settings from JSON file
    - Sets up logging
    
    #### Method: `process_file(file_path: str) -> dict`
    - Reads file content
    - Validates data format
    - Transforms data according to rules
    - Returns processed result
    '''
)

# Repeat for remaining steps...
```

### Step 3: Finalize

```python
# Complete the analysis
result = await code_analysis_finalize(
    session_id="analysis_1702345678_abc12345"
)

# Final markdown file is ready at:
# output/analysis/main_analysis.md
```

## Output Example

The generated markdown looks like this:

```markdown
# Code Analysis Report: main.py

**Analysis Date:** 2025-10-21T10:30:00
**Source File:** `/home/user/project/main.py`
**Language:** python
**Total Lines:** 850
**Status:** completed

## 📋 Overview

This document provides a comprehensive analysis of `main.py` 
for new developers to understand the codebase structure, dependencies, and functionality.

## 📦 Import Analysis

### External Dependencies

| Import Statement | Type |
|------------------|------|
| `import os` | Standard Library |
| `import json` | Standard Library |
| `from fastapi import FastAPI` | Third-party |
| `from typing import Dict, Optional` | Standard Library |

## 🏗️ Code Structure

### Classes

| Class Name | Line Range | Methods |
|------------|------------|---------|
| `DataProcessor` | 45-320 | 8 |
| `ConfigManager` | 325-450 | 5 |

### Functions

| Function Name | Line Range | Signature |
|---------------|------------|-----------|
| `initialize_app` | 15-42 | `def initialize_app(config: dict) -> FastAPI` |
| `validate_config` | 455-480 | `def validate_config(config: dict) -> bool` |

## 🔍 Detailed Analysis

### Step 1: Lines 1-300

[Detailed analysis content here...]

### Step 2: Lines 301-600

[Detailed analysis content here...]

### Step 3: Lines 601-850

[Detailed analysis content here...]

## 📊 Analysis Summary

- **Steps Completed:** 3 / 3
- **Classes Found:** 2
- **Functions Found:** 2
- **Methods Found:** 13
- **Import Statements:** 15
```

## Configuration

Edit `configs/analysis.py` to customize:

```python
class AnalysisConfig:
    # Enable/disable code analysis
    ENABLE_CODE_ANALYSIS = True
    
    # Output directory
    ANALYSIS_OUTPUT_DIR = Path("./output/analysis")
    
    # Lines per step (affects step calculation)
    ANALYSIS_LINES_PER_STEP = 300
    
    # Minimum/maximum lines per step
    ANALYSIS_MIN_LINES_PER_STEP = 100
    ANALYSIS_MAX_LINES_PER_STEP = 500
    
    # Supported file extensions
    ANALYSIS_SUPPORTED_EXTENSIONS = [
        '.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', 
        '.rb', '.php', '.cs', '.swift', '.kt', '.rs'
    ]
```

## Best Practices

### For Effective Analysis

1. **Start Small**: Test with smaller files first (< 500 lines)
2. **Review Steps**: Check the calculated step count before starting
3. **Detailed Content**: Provide comprehensive analysis in each step
4. **Code Examples**: Include code snippets when explaining complex logic
5. **Beginner Focus**: Write explanations for developers new to the codebase

### Analysis Content Guidelines

Each step analysis should include:

- **Function/Method Purpose**: What does it do in simple terms?
- **Parameters**: What inputs does it accept?
- **Variables**: What key variables are used and why?
- **Dependencies**: What external code/libraries does it use?
- **Logic Flow**: Step-by-step explanation of the logic
- **Important Notes**: Edge cases, gotchas, or complex patterns

### Example Good Analysis

```markdown
#### Function: `calculate_metrics(data: pd.DataFrame) -> dict`

**Purpose:** Calculates statistical metrics from pandas DataFrame for reporting.

**Parameters:**
- `data` (pd.DataFrame): Input data with columns: 'value', 'timestamp', 'category'

**Variables Used:**
- `grouped`: Groups data by category for aggregation
- `metrics`: Dictionary to store calculated results
- `threshold`: Performance threshold value (90th percentile)

**Dependencies:**
- `pandas` (pd): For data manipulation and aggregation
- `numpy` (np): For statistical calculations

**Logic Flow:**
1. Groups data by 'category' column
2. For each group:
   - Calculates mean, median, std deviation
   - Identifies outliers (> 2 std dev)
   - Computes 90th percentile threshold
3. Compiles all metrics into result dictionary
4. Returns structured metrics for dashboard display

**Important Notes:**
- Assumes data is already cleaned (no nulls)
- Performance drops significantly with > 100k rows
- Consider using `groupby().agg()` for better performance
```

## Troubleshooting

### Session Not Found

If you get "Session not found" error:
- Sessions are stored in memory (lost on server restart)
- Use `code_analysis_list_sessions()` to find valid session IDs
- Start a new session with `code_analysis_initialize()`

### Token Limit Errors

If you still encounter token limits:
- Reduce `ANALYSIS_LINES_PER_STEP` in config
- Break analysis into smaller chunks
- Use more steps for large files

### Markdown Not Updating

- Check output directory permissions
- Verify `ANALYSIS_OUTPUT_DIR` path exists
- Check logs for file writing errors

## Language Support

### Currently Supported

- ✅ Python (.py)
- ✅ JavaScript (.js)
- ✅ TypeScript (.ts)
- ✅ Java (.java)
- ✅ C++ (.cpp)
- ✅ C (.c)
- ✅ Go (.go)
- ✅ Ruby (.rb)
- ✅ PHP (.php)
- ✅ C# (.cs)
- ✅ Swift (.swift)
- ✅ Kotlin (.kt)
- ✅ Rust (.rs)

### Python-Specific Features

For Python files, additional analysis includes:
- Import statement categorization (stdlib vs third-party)
- Class and method extraction
- Decorator identification
- Function signature parsing

## Integration Examples

### Analyze Multiple Files

```python
files = [
    "/project/main.py",
    "/project/models.py",
    "/project/utils.py"
]

sessions = []

for file_path in files:
    result = await code_analysis_initialize(source_file_path=file_path)
    data = json.loads(result)
    if data['success']:
        sessions.append(data['sessionId'])

# Analyze each session...
```

### Custom Analysis Pipeline

```python
async def analyze_codebase(file_path: str) -> str:
    # Initialize
    init_result = await code_analysis_initialize(source_file_path=file_path)
    init_data = json.loads(init_result)
    
    if not init_data['success']:
        return f"Failed to initialize: {init_data.get('error')}"
    
    session_id = init_data['sessionId']
    total_steps = init_data['totalSteps']
    
    # Analyze all steps
    for step in range(1, total_steps + 1):
        # Generate analysis using LLM
        analysis = generate_analysis_for_step(init_data['currentStepInfo'])
        
        # Submit analysis
        step_result = await code_analysis_analyze_step(
            session_id=session_id,
            step_number=step,
            analysis_content=analysis
        )
        
        step_data = json.loads(step_result)
        if not step_data['success']:
            return f"Failed at step {step}: {step_data.get('error')}"
    
    # Finalize
    final_result = await code_analysis_finalize(session_id=session_id)
    final_data = json.loads(final_result)
    
    return final_data['outputPath']
```

## Related Tools

- **Planning Tool**: For project planning and WBS creation
- **WBS Execution Tool**: For step-by-step project implementation
- **Sequential Thinking**: For complex analysis with deep reasoning

## Future Enhancements

- Cross-file dependency analysis
- Call graph generation
- Complexity metrics (cyclomatic complexity)
- Test coverage analysis
- Code smell detection
- Refactoring suggestions
- Multi-language comparison
- Interactive documentation viewer
