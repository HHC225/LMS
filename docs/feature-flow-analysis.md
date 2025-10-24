# Feature Flow Analysis Tool

**Enhanced ASCII-Based Flow Visualization** for understanding feature execution paths.

## Overview

The Feature Flow Analysis Tool provides **beautiful visual flow analysis** of source files implementing a feature. The tool generates:

- **File-level enhanced ASCII flow diagram** - Shows execution order with box drawings and emojis
- **Method-level enhanced ASCII flow diagram** - Shows method call chains with tree structure
- **File classification** - Automatic categorization with visual icons (⚙️ pipeline, 🔄 transform, 📦 dto, etc.)
- **Statistics** - Total files, methods, call relationships

### Key Benefits

- 🎨 **Professional-Looking**: Unicode box-drawing characters (╔═╗ ║ ├─┤ └─┘ ▶ ▼)
- 📦 **Visual Icons**: Emojis for file types (🚀 start, ⚙️ pipeline, 🔄 transform, 💾 repository, 🏁 end)
- ⚡ **One-Shot**: Complete analysis in single call
- 📊 **Two-Level View**: Both file and method perspectives
- 👁️ **Readable**: Clear visual hierarchy with proper indentation

## Architecture

### Simple Single-Step Workflow

```
analyze → Parse files → Classify → Analyze flow → Generate ASCII diagrams → Done
```

No multi-step process, no PlantUML dependencies, no external tools needed.

## Key Features

### 📈 File-Level Flow Diagram
Shows execution flow between source files with professional visual representation:
- Entry points marked with 🚀 START box
- Files shown in bordered boxes with icons
- File types labeled with emojis (⚙️ ⚙️ 🔄 📦 💾 🗃️ 🔧 📄)
- Dependencies shown with tree-style arrows (├──→ └──→)
- End marked with 🏁 END box

**Example Output:**
```
╔══════════════════════════════════════════════════════════════════════════════╗
║                         FILE EXECUTION FLOW                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

    ╭─────────────────────────────────────────────╮
    │  🚀 START: ForceCancelPipeline.java    │
    ╰─────────────────────────────────────────────╯
                      │
                      ▼
    ┌─────────────────────────────────────────────┐
    │ ⚙️  ForceCancelPipeline.java           │
    │ 📋 Type: pipeline                           │
    └─────────────────────────────────────────────┘
                      │
                      ├──→ 🔄 [ForceCancelFn.java] (transform)
                      ├──→ 📦 [ForceCancelDto.java] (dto)
                      └──→ 💾 [Repository.java] (repository)
                      │
                      ▼
    ┌─────────────────────────────────────────────┐
    │ 🔄  ForceCancelFn.java                 │
    │ 📋 Type: transform                          │
    └─────────────────────────────────────────────┘
                      │
                      ▼
    ╭─────────────────────────────────────────────╮
    │  🏁 END                                      │
    ╰─────────────────────────────────────────────╯
```

### 🔄 Method-Level Flow Diagram
Shows actual method call chains in professional tree format:

**Example Output:**
```
╔══════════════════════════════════════════════════════════════════════════════╗
║                          METHOD CALL FLOW                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

    ╭─ 🎯 Entry Point
    │
    ▼  ForceCancelPipeline.apply()
        │
        └──▶ 🔸 ForceCancelFn.processElement()
                │
                ├──▶ 🔸 ForceCancelDto.builder()
                │
                ├──▶ 🔸 Repository.findById()
                │
                └──▶ 🔸 Repository.save()

    ╰─────────────────────────────────────────────╯
      🏁 Flow End
```

### 📊 File Classification

The tool automatically classifies files based on naming patterns:

- **PIPELINE**: Entry point files (`*Pipeline.java`)
- **TRANSFORM**: Processing logic (`*Fn.java`, `*Transform*`)  
- **DTO**: Data transfer objects (`*Dto.java`)
- **REPOSITORY**: Database access (`*Repository.java`)
- **ENTITY**: Database models (`*Entity.java`)
- **OPTIONS**: Configuration (`*Options.java`, `*Config*`)
- **SERVICE**: Business logic (`*Service.java`)
- **UNKNOWN**: Other supporting files

## Usage

### Single-Step Analysis

```python
from src.wrappers.analysis.feature_flow_wrapper import feature_flow_analyze

# Complete analysis in one call
result = await feature_flow_analyze(
    feature_name="ForceCancel",
    file_paths=[
        "/path/to/ForceCancelPipeline.java",
        "/path/to/ForceCancelFn.java",
        "/path/to/ForceCancelDto.java",
        "/path/to/Repository.java"
    ]
)

# Returns:
# {
#   "success": true,
#   "sessionId": "flow_1234567890_5678",
#   "featureName": "ForceCancel",
#   "status": "completed",
#   "totalFiles": 4,
#   "totalMethods": 23,
#   "entryPoints": ["ForceCancelPipeline.java"],
#   "outputPath": "/path/to/output/ForceCancel_flow.md",
#   "message": "Flow analysis completed!"
# }
```

### Retrieve Session Info

```python
from src.wrappers.analysis.feature_flow_wrapper import feature_flow_get_session

# Get details of completed analysis
result = await feature_flow_get_session(
    session_id="flow_1234567890_5678"
)
```

### List All Sessions

```python
from src.wrappers.analysis.feature_flow_wrapper import feature_flow_list_sessions

# List all analysis sessions
result = await feature_flow_list_sessions()
```

## Output Format

The tool generates a Markdown file with the following sections:

1. **Overview**: Feature name, file count, method count, entry points
2. **File-Level Flow**: ASCII diagram showing file execution order
3. **File List by Type**: Categorized file listing
4. **Method-Level Flow**: ASCII diagram showing method calls
5. **Method Statistics**: Total methods, call relationships, max depth
6. **Summary**: Analysis completion details

## Practical Examples

### Example 1: Apache Beam Pipeline Analysis

```python
result = await feature_flow_analyze(
    feature_name="User Registration Flow",
    file_paths=[
        "/src/RegistrationPipeline.java",
        "/src/ValidateUserFn.java",
        "/src/CreateAccountFn.java",
        "/src/SendWelcomeEmailFn.java",
        "/src/UserDto.java",
        "/src/UserRepository.java"
    ]
)
```

**Generated Flow**:
```
[START: RegistrationPipeline.java]
    |
    v
[RegistrationPipeline.java] (pipeline)
    |
    +--> Uses: [ValidateUserFn.java] (transform)
    |
    +--> Uses: [UserDto.java] (dto)
    |
    v
[ValidateUserFn.java] (transform)
    |
    +--> Uses: [UserRepository.java] (repository)
    |
    v
[CreateAccountFn.java] (transform)
    |
    v
[SendWelcomeEmailFn.java] (transform)
    |
    v
[END]
```

### Example 2: Microservice Flow Analysis

```python
result = await feature_flow_analyze(
    feature_name="Order Processing",
    file_paths=[
        "/src/OrderController.java",
        "/src/OrderService.java",
        "/src/OrderRepository.java",
        "/src/OrderDto.java",
        "/src/OrderEntity.java"
    ]
)
```

## Best Practices

### 1. **Include All Related Files**
Provide all source files that participate in the feature for complete flow visualization.

### 2. **Use Descriptive Feature Names**
Choose clear feature names that describe the business functionality.

### 3. **Review Both Flow Levels**
- File-level flow: Understand overall architecture
- Method-level flow: Understand detailed implementation

### 4. **Check File Classification**
Verify automatic classification matches your intended architecture.

### 5. **Use for Onboarding**
Share generated flow diagrams with new team members for quick understanding.

## Comparison: Old vs New

### Old Approach (Multi-Step with PlantUML)
```python
# Step 1: Initialize
await feature_flow_initialize(...)

# Step 2: File-level PlantUML
await feature_flow_analyze_file_level(session_id)

# Step 3: Method-level PlantUML
await feature_flow_analyze_method_level(session_id)

# Step 4-N: LLM analysis per file (interactive)
await feature_flow_generate_guide(session_id)
await feature_flow_submit_file_guide(...)
# Repeat for each file...

# Step N+1: Finalize
await feature_flow_finalize(session_id)
```

**Issues**: 
- Complex multi-step workflow
- Requires PlantUML rendering
- Interactive LLM analysis per file
- Time-consuming for large features

### New Approach (Single-Step ASCII)
```python
# One call - done!
await feature_flow_analyze(
    feature_name="ForceCancel",
    file_paths=[...]
)
```

**Benefits**:
- Simple single call
- ASCII viewable immediately
- No external tools needed
- Fast for any size feature

## Troubleshooting

### Issue: No Methods Extracted
**Cause**: File doesn't match Java/Python method patterns  
**Solution**: Check file language support (currently Java, Python)

### Issue: Wrong File Classification
**Cause**: Filename doesn't match expected patterns  
**Solution**: Files with unclear names classified as "unknown" - this is normal

### Issue: Empty Method Call Flow
**Cause**: Methods don't call each other (simple data classes)  
**Solution**: Expected for DTOs, entities - focus on file-level flow

### Issue: Circular Dependencies
**Cause**: Files depend on each other  
**Solution**: Tool handles this gracefully, shows all dependencies

## Technical Details

### File Analysis
- Counts lines of code
- Extracts imports
- Identifies class names
- Classifies file types

### Method Extraction
- Regex-based method signature detection
- Supports Java and Python
- Skips getters/setters
- Limits to first 50 methods per file

### Dependency Analysis
- Import-based dependency detection
- Topological sorting for execution order
- Handles missing dependencies gracefully

### Call Graph Building
- Method call detection via regex
- Limited to 5 levels depth to avoid noise
- Tracks caller/callee relationships

## Future Enhancements

Potential improvements:
- Support for more languages (C++, Go, TypeScript)
- Configurable diagram symbols
- Interactive HTML output
- Export to other formats (DOT, Mermaid)
- Performance profiling integration

## Related Tools

- **Code Analysis Tool**: For detailed line-by-line code explanation
- **Planning Tool**: For breaking down features into tasks
- **WBS Execution**: For executing planned tasks systematically

## Support

For issues or feature requests, check the main LMS documentation or create an issue in the repository.
