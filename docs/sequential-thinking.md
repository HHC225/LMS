# Sequential Thinking Tool (st)

Sequential analytical thinking for structured problem-solving where each thought builds upon previous insights.

## 🎯 Overview

The Sequential Thinking Tool provides a structured framework for step-by-step analysis where each thought:
- Builds sequentially on previous insights
- Can question or revise earlier decisions
- Can branch into alternative approaches
- Can trigger direct actions (code writing, file creation, etc.)

## 🚀 Core Workflow

```
Thought 1: Problem Analysis
    ↓
Thought 2: Initial Approach
    ↓
Thought 3: Refinement or Revision
    ↓
Thought 4: Alternative Branch (if needed)
    ↓
Thought N: Final Solution
```

## 🛠️ Tool Reference

### st (Sequential Thinking)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `thought` | string | Yes | Current analytical step |
| `thought_number` | integer | Yes | Current sequence number (1, 2, 3...) |
| `total_thoughts` | integer | Yes | Estimated total thoughts needed |
| `next_thought_needed` | boolean | Yes | Whether another thought step is needed |
| `is_revision` | boolean | No | Whether this revises previous thinking |
| `revises_thought` | integer | No | Which thought is being reconsidered |
| `branch_from_thought` | integer | No | Branching point thought number |
| `branch_id` | string | No | Branch identifier |
| `needs_more_thoughts` | boolean | No | If more thoughts are needed |
| `action_required` | boolean | No | Whether this step requires direct action |
| `action_type` | string | No | Type of action (code_writing, file_creation, etc.) |
| `action_description` | string | No | Description of the action |

**Action Types:**
- `code_writing`: Writing or modifying code
- `file_creation`: Creating new files
- `file_modification`: Modifying existing files
- `configuration`: Updating configuration files
- `testing`: Running tests
- `analysis`: Performing analysis
- `other`: Other types of actions

**Returns:** JSON response with thought processing results

## 📋 Example Usage

### Basic Sequential Analysis

```json
{
  "thought": "First, analyze the API requirements: need user authentication, data validation, and rate limiting.",
  "thought_number": 1,
  "total_thoughts": 5,
  "next_thought_needed": true
}
```

```json
{
  "thought": "Design endpoint structure: POST /api/auth/login, GET /api/users/{id}, POST /api/data with JWT middleware.",
  "thought_number": 2,
  "total_thoughts": 5,
  "next_thought_needed": true
}
```

### Revision Example

```json
{
  "thought": "Revising thought 2: Instead of JWT middleware on all routes, implement API key + JWT hybrid for better flexibility with external clients.",
  "thought_number": 3,
  "total_thoughts": 5,
  "next_thought_needed": true,
  "is_revision": true,
  "revises_thought": 2
}
```

### Branching Example

```json
{
  "thought": "Exploring alternative: GraphQL instead of REST for more flexible data fetching.",
  "thought_number": 4,
  "total_thoughts": 6,
  "next_thought_needed": true,
  "branch_from_thought": 2,
  "branch_id": "graphql-approach"
}
```

### Action Execution Example

```json
{
  "thought": "Implementing the authentication endpoint with bcrypt password hashing and JWT token generation.",
  "thought_number": 5,
  "total_thoughts": 6,
  "next_thought_needed": true,
  "action_required": true,
  "action_type": "code_writing",
  "action_description": "Create auth.py with login endpoint, password validation, and JWT token generation"
}
```

## 💡 Key Principles

### 1. Quality First
- Establish clear success criteria before starting
- If final result doesn't meet criteria, restart from thought 1

### 2. Critical Analysis
- Question user input for logical errors
- Identify missing information
- Suggest better approaches when found

### 3. Adaptive Process
- Adjust total thoughts as understanding deepens
- Revise decisions when new insights emerge
- Branch into alternatives when needed

### 4. Direct Action
- Execute actions immediately when clear
- Don't create intermediate planning steps
- Write code, create files, run tests directly

## 📖 Use Cases

### System Architecture Design
```
Thought 1: Requirements gathering and constraints
Thought 2: Component identification and boundaries
Thought 3: Technology stack selection
Thought 4: Data flow and communication patterns
Thought 5: Scalability and performance considerations
```

### API Endpoint Design
```
Thought 1: Resource identification
Thought 2: HTTP method mapping
Thought 3: Request/response structure
Thought 4: Authentication and authorization
Thought 5: Error handling and validation
```

### Database Schema Design
```
Thought 1: Entity identification
Thought 2: Relationship mapping
Thought 3: Normalization and optimization
Thought 4: Index strategy
Thought 5: Migration planning
```

### Performance Optimization
```
Thought 1: Bottleneck identification
Thought 2: Profiling and measurement
Thought 3: Optimization strategies
Thought 4: Implementation approach
Thought 5: Testing and validation
```

### Code Refactoring Strategy
```
Thought 1: Code smell identification
Thought 2: Impact analysis
Thought 3: Refactoring pattern selection
Thought 4: Implementation steps
Thought 5: Testing strategy
```

## 🎓 Best Practices

1. **Start with Clear Criteria**: Define what success looks like
2. **Be Specific**: Include concrete details and examples
3. **Build Incrementally**: Each thought should advance understanding
4. **Question Assumptions**: Don't accept initial approach blindly
5. **Use Revisions Wisely**: Revise when genuinely better approach found
6. **Branch for Alternatives**: Explore significantly different approaches
7. **Take Direct Action**: Execute when path is clear
8. **Adjust Estimates**: Update total_thoughts as needed

## ⚠️ Common Pitfalls

1. **Too Few Thoughts**: Rushing to conclusion without thorough analysis
2. **Too Many Thoughts**: Over-analyzing simple problems
3. **Skipping Revision**: Sticking with suboptimal approach
4. **Excessive Branching**: Creating too many alternative paths
5. **Vague Thoughts**: Not being specific enough in analysis
6. **Missing Actions**: Not executing when implementation is clear

## 🔄 Comparison with Other Tools

| Feature | Sequential Thinking | Recursive Thinking | Tree of Thoughts |
|---------|-------------------|-------------------|------------------|
| Structure | Linear with revisions | Iterative improvement | Branching exploration |
| Best For | Step-by-step planning | Deep analysis | Multi-option comparison |
| Revisions | Yes | Yes | Backtracking |
| Branching | Yes | No | Yes |
| Actions | Direct execution | Post-analysis | Post-selection |
