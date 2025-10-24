# Recursive Thinking Tool

Recursive Thinking implements recursive reasoning for iterative answer improvement through latent state updates.

## 🔄 Workflow Overview

1. **Initialize** → Start session
2. **Update Latent (4 steps)** → Analyze problem deeply  
3. **Update Answer** → Write/improve answer
4. **If unsure** → Repeat steps 2-3
5. **If confident** → Get Final Result
6. **Auto-verification** → If not verified, automatic 4-step verification starts
7. **Finalize** → Update answer with verification insights
8. **Get Final Result** → Retrieve verified answer

## 🚀 Complete Workflow Example

### 1. Initialize Session
```
Tool: recursive_thinking_initialize
Parameters:
- question: "How to design an efficient cache system in Python?"
```
→ Returns: session_id

### 2. Deep Analysis (4 steps)
```
Tool: recursive_thinking_update_latent
Step 1: Problem Decomposition - Break down cache requirements
Step 2: Current State Analysis - Analyze existing approach
Step 3: Alternative Perspectives - Consider different cache strategies
Step 4: Synthesis - Develop improvement strategy
```

### 3. Write Answer
```
Tool: recursive_thinking_update_answer
Parameters:
- improved_answer: "LRU cache with TTL and eviction policy..."
- improvement_rationale: "Optimized based on latency and memory constraints"
```

### 4. If Unsure → Repeat steps 2-3

### 5. If Confident → Get Result
```
Tool: recursive_thinking_get_result
```
→ If not verified: Auto-starts verification mode

### 6. Verification (Auto-triggered)
```
Tool: recursive_thinking_update_latent (4 steps again)
- Verify problem understanding
- Check answer completeness
- Test edge cases
- Final validation
```

### 7. Finalize Answer
```
Tool: recursive_thinking_update_answer
- Final verified answer with verification insights
```

### 8. Get Final Result
```
Tool: recursive_thinking_get_result
```
→ Returns: Complete verified answer + reasoning history

## 🛠️ Tool Reference

### recursive_thinking_initialize

Initialize a new recursive reasoning session.

**Parameters:**
- `question` (string, required): The problem or question to solve
- `initial_answer` (string, optional): Starting answer (empty means start from scratch)
- `n_latent_updates` (integer, default: 4): Number of recursive latent updates per improvement step
- `max_improvements` (integer, default: 16): Maximum number of answer improvement iterations

**Returns:** Session confirmation with auto-generated unique session_id

**Example:**
```json
{
  "question": "How to design an efficient cache system in Python?",
  "n_latent_updates": 4,
  "max_improvements": 16
}
```

### recursive_thinking_update_latent

Update the latent reasoning state through recursive analysis.

**Parameters:**
- `session_id` (string, required): The reasoning session identifier
- `reasoning_insight` (string, required): Your new reasoning insight following step-by-step guidelines
- `step_number` (integer, required): Which latent update step (1 to n_latent_updates)

**Thinking Steps:**

**Step 1: Problem Decomposition**
- Break down the question into core components
- Identify problem type (mathematical, logical, analytical, creative, etc.)
- List all given information, constraints, and assumptions
- Determine required knowledge domains

**Step 2: Current State Analysis**
- Examine current answer's logic and reasoning chain
- Identify specific strengths: what parts are correct and why
- Pinpoint exact weaknesses: logical gaps, incorrect assumptions
- Check consistency between different parts

**Step 3: Alternative Perspectives**
- Consider alternative approaches or interpretations
- Apply domain-specific reasoning patterns
- Question underlying assumptions and explore edge cases
- Look for patterns, connections, or insights

**Step 4: Synthesis**
- Synthesize insights into a coherent improvement plan
- Prioritize aspects needing most improvement
- Develop specific strategies for addressing weaknesses
- Prepare concrete recommendations

**Returns:** Status of latent update and guidance for next step

**Example:**
```json
{
  "session_id": "abc123",
  "reasoning_insight": "Breaking down the cache system problem: We need to consider 1) Storage mechanism (dict-based), 2) Eviction policy (LRU/LFU), 3) Thread safety, 4) TTL support, 5) Size limits. The core components are cache storage, eviction strategy, and expiry management.",
  "step_number": 1
}
```

### recursive_thinking_update_answer

Update the answer based on refined latent reasoning.

**Parameters:**
- `session_id` (string, required): The reasoning session identifier
- `improved_answer` (string, required): The new improved answer
- `improvement_rationale` (string, required): Brief explanation of improvements

**Returns:** Updated answer and guidance on whether to continue iterating

**Example:**
```json
{
  "session_id": "abc123",
  "improved_answer": "Here's an efficient Python cache system using LRU eviction:\n\n```python\nfrom collections import OrderedDict\nimport time\n\nclass LRUCache:\n    def __init__(self, capacity: int, ttl: int = None):\n        self.cache = OrderedDict()\n        self.capacity = capacity\n        self.ttl = ttl\n```",
  "improvement_rationale": "Added OrderedDict for O(1) access and LRU ordering, included TTL support for expiry management, and structured initialization for capacity limits."
}
```

### recursive_thinking_get_result

Retrieve the final answer and complete reasoning history.

**Parameters:**
- `session_id` (string, required): The reasoning session identifier

**Behavior:**
- **First call (not verified)**: Automatically starts verification mode → requires 4 update_latent steps → update_answer
- **Second call (verified)**: Returns complete verified results and reasoning trace

**Returns:** Either verification start instruction or complete verified results

**Example:**
```json
{
  "session_id": "abc123"
}
```

### recursive_thinking_reset

Reset or delete a reasoning session.

**Parameters:**
- `session_id` (string, required): The reasoning session identifier to reset

**Returns:** Confirmation of reset

**Example:**
```json
{
  "session_id": "abc123"
}
```

## 💡 Best Practices

1. **Be Specific in Insights**: Reference exact parts of the question/answer
2. **Build Incrementally**: Each latent update should add new insights
3. **Use Evidence-Based Reasoning**: Avoid vague intuitions
4. **Follow the 4-Step Process**: Don't skip steps for best results
5. **Iterate When Needed**: Don't rush to verification if answer needs work
6. **Trust the Verification**: The auto-verification ensures quality

## 📖 Use Cases

- Complex algorithm design and optimization
- System architecture decisions
- Mathematical problem-solving
- Code refactoring strategies
- Performance optimization planning
- Security analysis and mitigation
- API design considerations
- Database schema design
