# Tree of Thoughts Tool (tt)

Advanced Tree of Thoughts framework for exploring multiple solution paths with branching, evaluation, and backtracking.

## 🌳 Overview

The Tree of Thoughts tool implements a complete ToT framework optimized for software development and system design challenges. It allows you to:

- Explore multiple solution paths simultaneously
- Evaluate each approach systematically
- Backtrack when paths prove infeasible
- Find optimal solutions through structured exploration

## 🎯 Core Concepts

### Tree Structure
```
                    Problem
                       |
        +--------------+--------------+
        |              |              |
   Solution A     Solution B     Solution C
        |              |              |
    +---+---+      +---+---+      Evaluation
    |       |      |       |
  A.1     A.2    B.1     B.2
```

### Search Strategies

**BFS (Breadth-First Search)**
- Explores all options at current level before going deeper
- Best for finding optimal solution across all possibilities
- Use when: Comparing multiple fundamentally different approaches

**DFS (Depth-First Search)**
- Explores one path deeply before backtracking
- Best for quickly finding any working solution
- Use when: Need to validate feasibility fast

### Generation Strategies

**Sampling**
- Generate multiple diverse solutions at once
- Best for: Creative brainstorming phase
- Example: "Give me 5 different cache implementation approaches"

**Proposing**
- Generate single best solution based on current state
- Best for: Refinement and optimization
- Example: "What's the next best step given current architecture?"

### Evaluation Methods

**Value-Based**
- Assign numerical score (1-10)
- Include confidence level (0-1)
- Specify viability (promising/uncertain/dead_end)
- Best for: Quantitative comparison

**Vote-Based**
- Multiple evaluations vote on best option
- Democratic selection process
- Best for: Subjective decisions

## 🛠️ Tool Reference

### create_session

Start a new problem-solving session.

**Parameters:**
- `action`: "create_session"
- `problem_statement` (string, required): Problem to solve
- `config` (object, optional):
  - `search_strategy`: "bfs" or "dfs" (default: "bfs")
  - `generation_strategy`: "sampling" or "proposing" (default: "sampling")
  - `evaluation_method`: "value" or "vote" (default: "value")
  - `max_depth`: Maximum tree depth (default: 10)
  - `max_branches`: Maximum branches per node (default: 5)

**Example:**
```json
{
  "action": "create_session",
  "problem_statement": "Design a scalable microservices architecture for e-commerce platform",
  "config": {
    "search_strategy": "bfs",
    "generation_strategy": "sampling",
    "evaluation_method": "value",
    "max_depth": 8,
    "max_branches": 4
  }
}
```

### add_thoughts

Add multiple implementation approaches to the tree.

**Parameters:**
- `action`: "add_thoughts"
- `session_id` (string, required)
- `thoughts` (array, required): List of thought strings
- `parent_node_id` (string, optional): Parent node to attach thoughts to (defaults to root)

**Example:**
```json
{
  "action": "add_thoughts",
  "session_id": "session_123",
  "thoughts": [
    "Use API Gateway pattern with Kong/Nginx for routing",
    "Implement service mesh with Istio for inter-service communication",
    "Direct service-to-service REST calls with circuit breaker pattern"
  ],
  "parent_node_id": "root"
}
```

### add_evaluation

Add evaluation results for solutions.

**Parameters:**
- `action`: "add_evaluation"
- `session_id` (string, required)
- `node_id` (string, required): Node ID to evaluate
- `evaluation` (object, required):
  - `value` (integer, 1-10): Quality score
  - `confidence` (float, 0-1): Confidence in evaluation
  - `viability` (string): "promising", "uncertain", or "dead_end"
  - `reasoning` (string): Explanation of evaluation

**Example:**
```json
{
  "action": "add_evaluation",
  "session_id": "session_123",
  "node_id": "node_456",
  "evaluation": {
    "value": 8,
    "confidence": 0.85,
    "viability": "promising",
    "reasoning": "API Gateway provides good abstraction and centralized routing, but adds single point of failure. Need to consider high availability setup."
  }
}
```

### search_next

Find the next best approach to explore.

**Parameters:**
- `action`: "search_next"
- `session_id` (string, required)
- `search_strategy` (string, optional): "bfs" or "dfs" (overrides session config)

**Example:**
```json
{
  "action": "search_next",
  "session_id": "session_123",
  "search_strategy": "bfs"
}
```

**Returns:** Next node to explore based on strategy

### backtrack

Return to previous design decisions when current path proves problematic.

**Parameters:**
- `action`: "backtrack"
- `session_id` (string, required)
- `dead_end_node_id` (string, required): Node that reached dead end
- `backtrack_strategy` (string, optional):
  - `"parent"`: Go back to immediate parent (default)
  - `"best_alternative"`: Jump to best alternative at same level
  - `"root"`: Start over from root

**Example:**
```json
{
  "action": "backtrack",
  "session_id": "session_123",
  "dead_end_node_id": "node_789",
  "backtrack_strategy": "best_alternative"
}
```

### set_solution

Document the final solution.

**Parameters:**
- `action`: "set_solution"
- `session_id` (string, required)
- `solution` (string, required): Final solution text with implementation details

**Example:**
```json
{
  "action": "set_solution",
  "session_id": "session_123",
  "solution": "Final architecture: API Gateway (Kong) for external routing, service mesh (Istio) for internal communication, with circuit breaker pattern for resilience. Includes monitoring with Prometheus/Grafana and distributed tracing with Jaeger."
}
```

### get_session

Retrieve complete analysis history.

**Parameters:**
- `action`: "get_session"
- `session_id` (string, required)

**Example:**
```json
{
  "action": "get_session",
  "session_id": "session_123"
}
```

### list_sessions

List all active sessions.

**Parameters:**
- `action`: "list_sessions"

**Example:**
```json
{
  "action": "list_sessions"
}
```

### display_results

Display ranked solutions with scores and paths.

**Parameters:**
- `action`: "display_results"
- `session_id` (string, required)

**Example:**
```json
{
  "action": "display_results",
  "session_id": "session_123"
}
```

## 📋 Complete Workflow Example

### 1. Create Session
```json
{
  "action": "create_session",
  "problem_statement": "Choose between REST API vs GraphQL for mobile app backend"
}
```

### 2. Add Initial Thoughts
```json
{
  "action": "add_thoughts",
  "session_id": "session_abc",
  "thoughts": [
    "REST API with versioning and pagination",
    "GraphQL with schema stitching",
    "Hybrid: GraphQL for mobile, REST for web"
  ]
}
```

### 3. Evaluate Each Option
```json
{
  "action": "add_evaluation",
  "session_id": "session_abc",
  "node_id": "node_rest",
  "evaluation": {
    "value": 7,
    "confidence": 0.9,
    "viability": "promising",
    "reasoning": "REST is well-understood, has good tooling, but may cause over-fetching for mobile clients"
  }
}
```

### 4. Search Next Best Path
```json
{
  "action": "search_next",
  "session_id": "session_abc"
}
```

### 5. Add Deeper Analysis
```json
{
  "action": "add_thoughts",
  "session_id": "session_abc",
  "parent_node_id": "node_graphql",
  "thoughts": [
    "Use Apollo Server with DataLoader for N+1 query optimization",
    "Implement with Hasura for auto-generated GraphQL"
  ]
}
```

### 6. Backtrack if Needed
```json
{
  "action": "backtrack",
  "session_id": "session_abc",
  "dead_end_node_id": "node_hasura",
  "backtrack_strategy": "best_alternative"
}
```

### 7. Set Final Solution
```json
{
  "action": "set_solution",
  "session_id": "session_abc",
  "solution": "Hybrid approach: GraphQL (Apollo Server) for mobile app to minimize data transfer and enable flexible queries, REST for web dashboard for simpler caching and CDN integration."
}
```

### 8. Display Results
```json
{
  "action": "display_results",
  "session_id": "session_abc"
}
```

## 📖 Use Cases

### Multi-Architecture Exploration
**Problem**: Microservices vs Monolithic vs Serverless

**Approach**:
1. Create session with problem
2. Add thoughts for each architecture style
3. Evaluate based on scalability, cost, complexity
4. Explore implementation details for promising options
5. Compare final scores and select winner

### Technology Stack Selection
**Problem**: Choose frontend framework (React vs Vue vs Angular)

**Approach**:
1. Create session with project requirements
2. Add thoughts for each framework
3. Evaluate on criteria: learning curve, ecosystem, performance
4. Branch into state management options for top choices
5. Select based on team expertise and project needs

### Database Design Alternatives
**Problem**: SQL vs NoSQL for user data storage

**Approach**:
1. Create session with data model and access patterns
2. Add thoughts for different database types
3. Evaluate based on ACID requirements, scalability, query patterns
4. Explore specific implementations (PostgreSQL vs MongoDB vs Cassandra)
5. Select optimal solution with migration strategy

### API Design Patterns
**Problem**: Choose authentication approach

**Approach**:
1. Create session with security requirements
2. Add thoughts: JWT, OAuth2, Session-based, API Keys
3. Evaluate on security, scalability, complexity
4. Branch into implementation details for top choices
5. Document final pattern with libraries and best practices

## 💡 Best Practices

1. **Start Broad**: Generate diverse initial thoughts
2. **Evaluate Objectively**: Use consistent criteria across options
3. **Go Deep Selectively**: Only explore promising paths in detail
4. **Document Reasoning**: Always explain why evaluations matter
5. **Backtrack Gracefully**: Don't be afraid to abandon dead ends
6. **Compare Systematically**: Use display_results to review all paths
7. **Set Clear Viability**: Mark dead_end nodes to avoid revisiting

## 🎓 Strategy Selection Guide

| Scenario | Search Strategy | Generation Strategy | Evaluation Method |
|----------|----------------|-------------------|-------------------|
| Unknown problem space | BFS | Sampling | Value |
| Time-constrained | DFS | Proposing | Value |
| Creative brainstorming | BFS | Sampling | Vote |
| Incremental refinement | DFS | Proposing | Value |
| Team decision | BFS | Sampling | Vote |

## ⚠️ Common Pitfalls

1. **Too Many Branches**: Limit to 3-5 initial thoughts
2. **Shallow Evaluation**: Include detailed reasoning
3. **Ignoring Dead Ends**: Mark non-viable paths clearly
4. **Forgetting to Backtrack**: Use when stuck
5. **Inconsistent Criteria**: Keep evaluation standards uniform
6. **Premature Selection**: Explore thoroughly before deciding

## 🔄 Comparison with Other Tools

| Feature | Tree of Thoughts | Sequential Thinking | Recursive Thinking |
|---------|-----------------|--------------------|--------------------|
| Multiple paths | Yes | Limited | No |
| Backtracking | Yes | Via revision | No |
| Evaluation | Explicit scores | Implicit | Implicit |
| Best for | Comparing options | Linear planning | Deep analysis |
| Complexity | High | Medium | High |
