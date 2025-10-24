"""
Vibe Refinement Tool Implementation
Progressive prompt refinement through structured iterations with LLM-generated suggestions

This tool helps refine vague user prompts into concrete, actionable specifications through:
1. Automatic specificity assessment
2. Two-phase refinement (Idea → System/Architecture)
3. LLM-driven suggestion generation
4. User-driven selection and progression
5. Beautiful final report generation
"""
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json
import time
import random
import string
from dataclasses import dataclass, field, asdict
from enum import Enum
from ..base import ReasoningTool


# ===== ENUMS =====

class Phase(Enum):
    """Refinement phase types"""
    IDEA = "idea"
    SYSTEM = "system"
    COMPLETED = "completed"


class SessionStatus(Enum):
    """Session status types"""
    ACTIVE = "active"
    AWAITING_SUGGESTIONS = "awaiting_suggestions"
    AWAITING_SELECTION = "awaiting_selection"
    COMPLETED = "completed"
    PAUSED = "paused"


# ===== DATA STRUCTURES =====

@dataclass
class Suggestion:
    """Individual suggestion structure"""
    id: str
    title: str
    description: str
    is_recommended: bool
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class RefinementStep:
    """Single refinement step record"""
    step_number: int
    phase: str
    question: str
    context: Dict[str, Any]
    suggestions_generated: Optional[List[Suggestion]] = None
    user_selection: Optional[Dict[str, Any]] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        if self.suggestions_generated:
            result['suggestions_generated'] = [s.to_dict() for s in self.suggestions_generated]
        return result


@dataclass
class RefinementSession:
    """Complete refinement session data"""
    id: str
    initial_prompt: str
    specificity_score: int
    idea_steps_needed: int
    system_steps_needed: int
    current_step: int
    phase: str
    status: str
    refinement_history: List[RefinementStep]
    final_decisions: Dict[str, Any]
    final_report: Optional[str]
    created_at: str
    last_updated: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['refinement_history'] = [step.to_dict() for step in self.refinement_history]
        return result


# Shared session store
vibe_sessions: Dict[str, RefinementSession] = {}


# ===== MAIN TOOL CLASS =====

class VibeRefinementTool(ReasoningTool):
    """Vibe Refinement Tool for progressive prompt clarification"""
    
    def __init__(self):
        super().__init__(
            name="vibe_refinement",
            description="Progressive prompt refinement through LLM-guided iterations"
        )
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = str(int(time.time()))
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"vibe_{timestamp}_{random_suffix}"
    
    def calculate_specificity_score(self, prompt: str) -> int:
        """
        Calculate prompt specificity score (0-100)
        
        Factors:
        - Length and detail level
        - Technical keywords
        - Feature descriptions
        - Constraints and requirements
        - Vague language penalty
        
        Args:
            prompt: User's initial prompt
            
        Returns:
            Specificity score (0-100)
        """
        score = 0
        prompt_lower = prompt.lower()
        words = prompt.split()
        
        # 1. Length factor (max 20 points)
        word_count = len(words)
        if word_count < 10:
            score += word_count * 1
        elif word_count < 30:
            score += 10 + (word_count - 10) * 0.5
        else:
            score += 20
        
        # 2. Technical terms (max 30 points)
        tech_keywords = [
            'react', 'vue', 'angular', 'python', 'typescript', 'javascript',
            'api', 'database', 'mongodb', 'postgresql', 'mysql', 'redis',
            'rest', 'graphql', 'grpc', 'microservice', 'monolith',
            'architecture', 'framework', 'library', 'algorithm',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'frontend', 'backend', 'fullstack', 'mobile', 'web'
        ]
        tech_count = sum(1 for kw in tech_keywords if kw in prompt_lower)
        score += min(tech_count * 5, 30)
        
        # 3. Feature specificity (max 25 points)
        feature_indicators = [
            'feature', 'function', 'component', 'module', 'class',
            'should', 'must', 'will', 'can', 'include', 'support',
            'allow', 'enable', 'provide', 'implement'
        ]
        feature_count = sum(1 for fi in feature_indicators if fi in prompt_lower)
        score += min(feature_count * 5, 25)
        
        # 4. Constraints/Requirements (max 15 points)
        constraint_words = [
            'requirement', 'constraint', 'must have', 'need to',
            'should support', 'compatible', 'performance', 'scalable',
            'secure', 'accessible', 'responsive'
        ]
        constraint_count = sum(1 for cw in constraint_words if cw in prompt_lower)
        score += min(constraint_count * 5, 15)
        
        # 5. Concrete details (max 10 points)
        detail_indicators = ['user', 'admin', 'dashboard', 'page', 'screen',
                           'button', 'form', 'list', 'table', 'chart']
        detail_count = sum(1 for di in detail_indicators if di in prompt_lower)
        score += min(detail_count * 2, 10)
        
        # 6. Penalty for vague words (max -10 points)
        vague_words = [
            'fun', 'good', 'nice', 'cool', 'interesting', 'awesome',
            'something', 'thing', 'stuff', 'maybe', 'kind of', 'sort of'
        ]
        vague_count = sum(1 for vw in vague_words if vw in prompt_lower)
        score -= min(vague_count * 3, 10)
        
        return max(0, min(100, score))
    
    def calculate_steps_needed(self, score: int) -> Tuple[int, int]:
        """
        Calculate refinement steps needed based on specificity score
        
        More granular scoring to ensure thorough refinement for vague prompts.
        Very vague prompts need extensive refinement to reach WBS-ready state.
        
        Args:
            score: Specificity score (0-100)
            
        Returns:
            Tuple of (idea_steps, system_steps)
        """
        if score < 10:      # Extremely vague (e.g., "make a game")
            return (6, 5)   # 11 total steps
        elif score < 20:    # Very vague (e.g., "make a fun 2048 game")
            return (5, 4)   # 9 total steps
        elif score < 35:    # Vague (e.g., "make a multiplayer 2048 with leaderboard")
            return (4, 3)   # 7 total steps
        elif score < 50:    # Moderate-low (some details but incomplete)
            return (3, 3)   # 6 total steps
        elif score < 65:    # Moderate (decent detail)
            return (2, 2)   # 4 total steps
        elif score < 80:    # Specific (good detail)
            return (1, 2)   # 3 total steps
        else:               # Very specific (implementation-ready)
            return (0, 2)   # 2 total steps (only tech decisions needed)
    
    def _build_context_summary(self, session: RefinementSession) -> str:
        """
        Build summary of decisions made so far
        
        Args:
            session: Current session
            
        Returns:
            Formatted context summary
        """
        if not session.refinement_history:
            return "No decisions made yet."
        
        summary_parts = []
        for step in session.refinement_history:
            if step.user_selection:
                summary_parts.append(
                    f"Step {step.step_number} ({step.phase}): "
                    f"{step.user_selection.get('title', 'N/A')}"
                )
        
        return "\n".join(summary_parts) if summary_parts else "No decisions made yet."
    
    def _generate_llm_prompt_instructions(
        self,
        session: RefinementSession,
        step_number: int
    ) -> Dict[str, Any]:
        """
        Generate structured instructions for LLM to create suggestions
        
        This does NOT generate suggestions - it creates instructions
        that tell the LLM what to generate.
        
        Args:
            session: Current session
            step_number: Current step number
            
        Returns:
            Structured instructions for LLM
        """
        context_summary = self._build_context_summary(session)
        
        if session.phase == Phase.IDEA.value:
            return self._generate_idea_phase_instructions(
                session, step_number, context_summary
            )
        else:  # System phase
            return self._generate_system_phase_instructions(
                session, step_number, context_summary
            )
    
    def _generate_idea_phase_instructions(
        self,
        session: RefinementSession,
        step_number: int,
        context_summary: str
    ) -> Dict[str, Any]:
        """Generate instructions for idea refinement phase"""
        
        # Determine what aspect to focus on based on step number
        focus_areas = [
            "Core concept and unique value proposition",
            "Key features and functionality",
            "User experience and interaction design",
            "Innovation and differentiation factors"
        ]
        
        focus = focus_areas[min(step_number - 1, len(focus_areas) - 1)]
        
        return {
            "task": f"Generate 5 creative ideas for refining: '{session.initial_prompt}'",
            "focus_area": focus,
            "context": {
                "initial_prompt": session.initial_prompt,
                "specificity_score": session.specificity_score,
                "decisions_so_far": context_summary,
                "current_step": step_number,
                "total_idea_steps": session.idea_steps_needed
            },
            "format_requirements": {
                "number_of_suggestions": 5,
                "each_suggestion_must_include": {
                    "id": "string (sugg_1, sugg_2, sugg_3, sugg_4, sugg_5)",
                    "title": "string (concise, 5-10 words)",
                    "description": "string (detailed, 150-250 words, explain benefits and approach)",
                    "is_recommended": "boolean (mark exactly ONE as true - your top recommendation)"
                }
            },
            "CRITICAL_OUTPUT_FORMAT": {
                "MANDATORY_INSTRUCTIONS": [
                    "⚠️ CRITICAL: You MUST present ALL 5 suggestions in full detail FIRST",
                    "⚠️ CRITICAL: Each of the 5 suggestions MUST include id, title, description (150-250 words), and is_recommended",
                    "⚠️ CRITICAL: AFTER showing all 5 complete suggestions, add a SEPARATE '🤖 AI Recommendation' section",
                    "⚠️ CRITICAL: DO NOT skip or summarize any suggestions - show ALL 5 in complete detail",
                    "⚠️ CRITICAL: Users need to see ALL options to make informed decisions",
                    "⚠️ CRITICAL: DO NOT use variable names like 'sugg_1', 'is_recommended' in your output - use human-readable format",
                    "⚠️ CRITICAL: Format should be natural language, not code/variable names"
                ],
                "HUMAN_READABLE_FORMAT_REQUIREMENTS": [
                    "DO NOT write 'id: sugg_1' - Instead write '**Option 1**' or '**Suggestion 1**'",
                    "DO NOT write 'is_recommended: true/false' - Only mark the recommended one with ✅ or ⭐",
                    "DO NOT write 'title:' or 'description:' - Just present the content naturally",
                    "Use clear formatting: Bold for titles, paragraphs for descriptions",
                    "Make it look like a professional presentation, not a data structure"
                ],
                "required_structure": """
STEP 1: Present ALL 5 Suggestions in this HUMAN-READABLE format:
═══════════════════════════════════════════════════════

## 📋 Five Suggestions

### **Option 1: [Concise Title]**

[Detailed 150-250 word explanation with benefits, approach, and technical considerations. Write in natural paragraphs, not as data fields.]

---

### **Option 2: [Concise Title]** ⭐ *Recommended*

[Detailed 150-250 word explanation with benefits, approach, and technical considerations. Write in natural paragraphs, not as data fields.]

---

### **Option 3: [Concise Title]**

[Detailed 150-250 word explanation with benefits, approach, and technical considerations.]

---

### **Option 4: [Concise Title]**

[Detailed 150-250 word explanation with benefits, approach, and technical considerations.]

---

### **Option 5: [Concise Title]**

[Detailed 150-250 word explanation with benefits, approach, and technical considerations.]

═══════════════════════════════════════════════════════

STEP 2: AFTER showing all 5 suggestions above, add this section:

## 🤖 AI Recommendation

I recommend **Option 2: [Title]**

**Why I recommend this option:**
- [Specific reason 1 related to user's context]
- [Specific reason 2 about feasibility/best practices]
- [Specific reason 3 about long-term benefits]

**Why other options are less suitable:**
- **Option 1**: [Brief reason why it's less ideal]
- **Option 3**: [Brief reason why it's less ideal]
- **Option 4**: [Brief reason why it's less ideal]
- **Option 5**: [Brief reason why it's less ideal]

This approach best balances [relevant factors] for this specific project.

═══════════════════════════════════════════════════════

IMPORTANT REMINDERS:
- Use "Option 1", "Option 2", etc. - NOT "sugg_1", "sugg_2"
- Use "⭐ *Recommended*" next to the title - NOT "is_recommended: true"
- Write descriptions as natural paragraphs - NOT as "description: [text]"
- Make it look professional and readable - NOT like JSON or variable output
"""
            },
            "guidelines": [
                "Be creative and innovative",
                "Consider user needs and pain points",
                "Think about feasibility and practicality",
                "Build upon previous decisions if any exist",
                "Make suggestions diverse to give good options",
                "Ensure exactly ONE suggestion is marked as recommended",
                "⚠️ NEVER skip showing all 5 suggestions in full detail",
                "⚠️ ALWAYS separate the suggestion list from the recommendation section",
                "⚠️ NEVER use variable names in output - use human-readable format"
            ],
            "example_complete_output": """
### **Option 1: Classic Web-First 2048**

A lightweight web app faithfully recreating the traditional 2048 experience. Uses minimal dependencies (vanilla JavaScript or TypeScript with simple bundler), CSS grid-based UI, arrow/touch swipe input handling, and local storage for score persistence. Focus is on creating a quickly deployable codebase for learning/demo purposes with clean, well-documented code. Testing emphasizes unit tests for game logic, with a light, responsive design. Extensions limited to themes and grid size options (4x4 default, optional 5x5).

---

### **Option 2: Component-Based React Architecture** ⭐ *Recommended*

[Detailed description in natural language paragraphs...]

[... then show AI Recommendation section ...]
"""
        }
    
    def _generate_system_phase_instructions(
        self,
        session: RefinementSession,
        step_number: int,
        context_summary: str
    ) -> Dict[str, Any]:
        """Generate instructions for system/architecture refinement phase"""
        
        # Determine technical aspect based on step number
        tech_areas = [
            "Technology stack and architecture pattern",
            "Development tools, frameworks, and libraries",
            "Deployment strategy and infrastructure"
        ]
        
        focus = tech_areas[min(step_number - session.idea_steps_needed - 1, len(tech_areas) - 1)]
        
        return {
            "task": f"Generate 5 technical approaches for implementing the project",
            "focus_area": focus,
            "context": {
                "initial_prompt": session.initial_prompt,
                "finalized_idea": context_summary,
                "current_step": step_number,
                "total_system_steps": session.system_steps_needed
            },
            "format_requirements": {
                "number_of_suggestions": 5,
                "each_suggestion_must_include": {
                    "id": "string (sugg_1, sugg_2, sugg_3, sugg_4, sugg_5)",
                    "title": "string (concise tech stack/approach name)",
                    "description": "string (detailed technical explanation 150-250 words including: languages, frameworks, architecture, deployment, why this approach)",
                    "is_recommended": "boolean (mark exactly ONE as true)"
                }
            },
            "CRITICAL_OUTPUT_FORMAT": {
                "MANDATORY_INSTRUCTIONS": [
                    "⚠️ CRITICAL: You MUST present ALL 5 technical suggestions in full detail FIRST",
                    "⚠️ CRITICAL: Each of the 5 suggestions MUST include complete technical details (150-250 words)",
                    "⚠️ CRITICAL: AFTER showing all 5 complete suggestions, add a SEPARATE '🤖 AI Recommendation' section",
                    "⚠️ CRITICAL: DO NOT skip or summarize any suggestions - show ALL 5 in complete technical detail",
                    "⚠️ CRITICAL: Users need to see ALL technical options to make informed architecture decisions",
                    "⚠️ CRITICAL: DO NOT use variable names like 'sugg_1', 'is_recommended' in your output - use human-readable format",
                    "⚠️ CRITICAL: Format should be natural language, not code/variable names"
                ],
                "HUMAN_READABLE_FORMAT_REQUIREMENTS": [
                    "DO NOT write 'id: sugg_1' - Instead write '**Option 1**' or '**Technical Approach 1**'",
                    "DO NOT write 'is_recommended: true/false' - Only mark the recommended one with ✅ or ⭐",
                    "DO NOT write 'title:' or 'description:' - Just present the content naturally",
                    "Use clear formatting: Bold for tech stack names, paragraphs for technical descriptions",
                    "Make it look like a professional technical presentation, not a data structure"
                ],
                "required_structure": """
STEP 1: Present ALL 5 Technical Suggestions in HUMAN-READABLE format:
═══════════════════════════════════════════════════════

## 🔧 Five Technical Approaches

### **Option 1: [Tech Stack Name]**

[Detailed 150-250 word technical explanation in natural paragraphs covering: Frontend technologies, Backend architecture, Database choices, Deployment strategy, CI/CD setup, Why this approach fits, Performance considerations, Scalability aspects. Write as a professional technical proposal, not as data fields.]

---

### **Option 2: [Tech Stack Name]** ⭐ *Recommended*

[Detailed 150-250 word technical explanation in natural paragraphs. Write professionally, not as JSON.]

---

### **Option 3: [Tech Stack Name]**

[Detailed technical explanation in natural paragraphs.]

---

### **Option 4: [Tech Stack Name]**

[Detailed technical explanation in natural paragraphs.]

---

### **Option 5: [Tech Stack Name]**

[Detailed technical explanation in natural paragraphs.]

═══════════════════════════════════════════════════════

STEP 2: AFTER showing all 5 technical suggestions above, add:

## 🤖 AI Recommendation

I recommend **Option 2: [Tech Stack Name]**

**Why I recommend this technical approach:**
- [Specific technical benefit related to project requirements]
- [Scalability and performance considerations]
- [Development efficiency and team expertise alignment]
- [Long-term maintenance and ecosystem support]

**Why other technical options are less suitable:**
- **Option 1**: [Technical reason why it's less ideal]
- **Option 3**: [Technical reason why it's less ideal]
- **Option 4**: [Technical reason why it's less ideal]
- **Option 5**: [Technical reason why it's less ideal]

This technology stack optimally addresses [key technical requirements] for this implementation.

═══════════════════════════════════════════════════════

IMPORTANT REMINDERS:
- Use "Option 1", "Option 2", etc. - NOT "sugg_1", "sugg_2"
- Use "⭐ *Recommended*" next to the title - NOT "is_recommended: true"
- Write descriptions as natural technical paragraphs - NOT as "description: [text]"
- Make it look professional and readable - NOT like JSON or variable output
"""
            },
            "guidelines": [
                "Consider scalability and maintainability",
                "Suggest proven, production-ready technologies",
                "Balance between modern and stable tech",
                "Consider team size and expertise requirements",
                "Think about development speed vs long-term maintenance",
                "Include deployment and DevOps considerations",
                "Ensure exactly ONE suggestion is marked as recommended",
                "⚠️ NEVER skip showing all 5 technical suggestions in full detail",
                "⚠️ ALWAYS separate the technical suggestion list from the recommendation section",
                "⚠️ NEVER use variable names in output - use human-readable format"
            ],
            "example_complete_output": """
### **Option 1: React + Node.js + MongoDB Stack**

Frontend: React with TypeScript for type safety, component reusability, and robust development experience. Backend: Node.js with Express framework for RESTful API development, leveraging JavaScript full-stack benefits. Database: MongoDB for flexible schema design and easy scalability. Deployment: AWS ECS with Docker containers for consistent environments. CI/CD: GitHub Actions for automated testing and deployment. This stack offers excellent community support, abundant learning resources, and proven production reliability. Performance is strong for most use cases, and the unified language (JavaScript/TypeScript) reduces context switching.

---

### **Option 2: Vue.js + Python FastAPI + PostgreSQL** ⭐ *Recommended*

[Detailed technical description in natural language paragraphs...]

[... then show AI Recommendation section ...]
"""
        }
    
    def _generate_question_for_step(
        self,
        session: RefinementSession,
        step_number: int
    ) -> str:
        """
        Generate appropriate question for current step
        
        Args:
            session: Current session
            step_number: Current step number
            
        Returns:
            Question string
        """
        if session.phase == Phase.IDEA.value:
            questions = [
                "What is the core value proposition of your project?",
                "What key features should be included?",
                "How should users interact with the system?",
                "What makes your project unique and innovative?"
            ]
            idx = min(step_number - 1, len(questions) - 1)
            return questions[idx]
        else:  # System phase
            questions = [
                "What technology stack would best fit your project?",
                "What development tools and frameworks should be used?",
                "How should the system be deployed and scaled?"
            ]
            idx = min(step_number - session.idea_steps_needed - 1, len(questions) - 1)
            return questions[idx]
    
    def _generate_final_report(self, session: RefinementSession) -> str:
        """
        Generate comprehensive final report ready for WBS creation
        
        This report includes detailed specifications for each decision
        with implementation guidance, requirements, and technical depth.
        
        Args:
            session: Completed session
            
        Returns:
            Detailed WBS-ready markdown report
        """
        report_parts = []
        
        # Header
        report_parts.append("# 🎯 Project Specification Report")
        report_parts.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_parts.append(f"**Session ID:** {session.id}")
        report_parts.append(f"**Status:** WBS-Ready Specification\n")
        
        # Executive Summary
        report_parts.append("## � Executive Summary")
        report_parts.append(f"\n**Original Request:** {session.initial_prompt}")
        report_parts.append(f"\n**Specificity Assessment:** {session.specificity_score}/100 ({self._interpret_score(session.specificity_score)})")
        report_parts.append(f"**Refinement Process:** {session.idea_steps_needed + session.system_steps_needed} steps completed")
        report_parts.append(f"- Idea Refinement: {session.idea_steps_needed} steps")
        report_parts.append(f"- Technical Refinement: {session.system_steps_needed} steps\n")
        
        # Idea Phase - Detailed
        report_parts.append("---")
        report_parts.append("## 💡 PART 1: Product & Feature Specifications")
        report_parts.append("\nThis section defines WHAT will be built from a user and product perspective.\n")
        
        idea_steps = [s for s in session.refinement_history if s.phase == Phase.IDEA.value]
        for idx, step in enumerate(idea_steps, 1):
            if step.user_selection:
                report_parts.append(f"### {idx}. {step.question}")
                report_parts.append(f"\n**Decision: {step.user_selection.get('title', 'N/A')}**\n")
                
                # Description
                report_parts.append("#### 📝 Description")
                report_parts.append(f"{step.user_selection.get('description', 'N/A')}\n")
                
                # Why This Decision
                report_parts.append("#### ✅ Rationale")
                report_parts.append("This decision was selected because:")
                report_parts.append("- Aligns with project goals and user needs")
                report_parts.append("- Provides clear value proposition")
                report_parts.append("- Feasible within project constraints")
                report_parts.append("- Builds upon previous decisions coherently\n")
                
                # Implementation Requirements
                report_parts.append("#### 📌 Key Requirements")
                report_parts.append("**Functional Requirements:**")
                report_parts.append("- [ ] Implement core functionality as described")
                report_parts.append("- [ ] Ensure user-facing features meet specifications")
                report_parts.append("- [ ] Include necessary UI/UX components")
                report_parts.append("- [ ] Support required user interactions\n")
                
                report_parts.append("**Non-Functional Requirements:**")
                report_parts.append("- [ ] Performance: Must be responsive and efficient")
                report_parts.append("- [ ] Usability: Intuitive and user-friendly")
                report_parts.append("- [ ] Accessibility: Follow accessibility standards")
                report_parts.append("- [ ] Compatibility: Work across target platforms\n")
                
                # Success Criteria
                report_parts.append("#### � Success Criteria")
                report_parts.append("This feature/aspect will be considered complete when:")
                report_parts.append("- All functional requirements are implemented and tested")
                report_parts.append("- User acceptance criteria are met")
                report_parts.append("- Performance benchmarks are achieved")
                report_parts.append("- Documentation is complete\n")
                
                report_parts.append("---\n")
        
        # System Phase - Detailed
        report_parts.append("## 🏗️ PART 2: Technical Architecture & Implementation")
        report_parts.append("\nThis section defines HOW it will be built from a technical perspective.\n")
        
        system_steps = [s for s in session.refinement_history if s.phase == Phase.SYSTEM.value]
        for idx, step in enumerate(system_steps, 1):
            if step.user_selection:
                report_parts.append(f"### {idx}. {step.question}")
                report_parts.append(f"\n**Technical Decision: {step.user_selection.get('title', 'N/A')}**\n")
                
                # Technical Description
                report_parts.append("#### 🔧 Technical Approach")
                report_parts.append(f"{step.user_selection.get('description', 'N/A')}\n")
                
                # Technical Rationale
                report_parts.append("#### ✅ Technical Justification")
                report_parts.append("This technical approach was selected because:")
                report_parts.append("- Meets scalability and performance requirements")
                report_parts.append("- Uses proven, production-ready technologies")
                report_parts.append("- Balances development speed with maintainability")
                report_parts.append("- Fits team expertise and project timeline\n")
                
                # Implementation Details
                report_parts.append("#### 📋 Implementation Specifications")
                report_parts.append("**Technical Stack Components:**")
                report_parts.append("- [ ] Set up chosen framework/library")
                report_parts.append("- [ ] Configure development environment")
                report_parts.append("- [ ] Establish coding standards and patterns")
                report_parts.append("- [ ] Implement core architecture\n")
                
                report_parts.append("**Infrastructure & DevOps:**")
                report_parts.append("- [ ] Set up version control and branching strategy")
                report_parts.append("- [ ] Configure CI/CD pipeline")
                report_parts.append("- [ ] Establish deployment process")
                report_parts.append("- [ ] Set up monitoring and logging\n")
                
                # Technical Requirements
                report_parts.append("#### 🔐 Technical Requirements")
                report_parts.append("**Architecture Requirements:**")
                report_parts.append("- Clear separation of concerns")
                report_parts.append("- Modular and maintainable code structure")
                report_parts.append("- Proper error handling and validation")
                report_parts.append("- Security best practices implemented\n")
                
                report_parts.append("**Quality Requirements:**")
                report_parts.append("- Unit test coverage > 80%")
                report_parts.append("- Integration tests for critical paths")
                report_parts.append("- Code review process established")
                report_parts.append("- Documentation for all major components\n")
                
                report_parts.append("---\n")
        
        # Consolidated Implementation Roadmap
        report_parts.append("## 🗺️ Implementation Roadmap")
        report_parts.append("\n### Phase 1: Foundation Setup (Weeks 1-2)")
        report_parts.append("**Objective:** Establish development infrastructure and basic architecture")
        report_parts.append("\n**Key Activities:**")
        report_parts.append("1. Set up development environment and tools")
        report_parts.append("2. Initialize project structure and repository")
        report_parts.append("3. Configure CI/CD pipeline")
        report_parts.append("4. Implement basic architecture skeleton")
        report_parts.append("5. Set up testing framework")
        report_parts.append("\n**Deliverables:**")
        report_parts.append("- Working development environment for all team members")
        report_parts.append("- Initialized project with basic structure")
        report_parts.append("- CI/CD pipeline running basic checks")
        report_parts.append("- Architecture documentation\n")
        
        report_parts.append("### Phase 2: Core Feature Development (Weeks 3-6)")
        report_parts.append("**Objective:** Implement primary features and functionality")
        report_parts.append("\n**Key Activities:**")
        report_parts.append("1. Implement core features from Part 1 specifications")
        report_parts.append("2. Develop main user workflows")
        report_parts.append("3. Create UI/UX components")
        report_parts.append("4. Implement business logic and data models")
        report_parts.append("5. Write unit and integration tests")
        report_parts.append("\n**Deliverables:**")
        report_parts.append("- Working implementation of all core features")
        report_parts.append("- Comprehensive test suite")
        report_parts.append("- User-facing interfaces")
        report_parts.append("- API documentation (if applicable)\n")
        
        report_parts.append("### Phase 3: Integration & Polish (Weeks 7-8)")
        report_parts.append("**Objective:** Integrate all components and refine user experience")
        report_parts.append("\n**Key Activities:**")
        report_parts.append("1. Integrate all features and components")
        report_parts.append("2. Perform end-to-end testing")
        report_parts.append("3. Optimize performance")
        report_parts.append("4. Refine UI/UX based on testing")
        report_parts.append("5. Complete documentation")
        report_parts.append("\n**Deliverables:**")
        report_parts.append("- Fully integrated application")
        report_parts.append("- Performance optimizations completed")
        report_parts.append("- Complete user and technical documentation")
        report_parts.append("- Ready for deployment\n")
        
        report_parts.append("### Phase 4: Deployment & Launch (Week 9)")
        report_parts.append("**Objective:** Deploy to production and ensure stable operation")
        report_parts.append("\n**Key Activities:**")
        report_parts.append("1. Deploy to production environment")
        report_parts.append("2. Set up monitoring and alerting")
        report_parts.append("3. Perform smoke tests in production")
        report_parts.append("4. Train users/stakeholders if needed")
        report_parts.append("5. Establish support processes")
        report_parts.append("\n**Deliverables:**")
        report_parts.append("- Application running in production")
        report_parts.append("- Monitoring dashboard operational")
        report_parts.append("- User documentation published")
        report_parts.append("- Support processes in place\n")
        
        # WBS Ready Summary
        report_parts.append("---")
        report_parts.append("## ✅ WBS Creation Readiness")
        report_parts.append("\n### This Specification is Ready For:")
        report_parts.append("\n**1. Work Breakdown Structure (WBS) Creation**")
        report_parts.append("   - All major features and components identified")
        report_parts.append("   - Technical approach clearly defined")
        report_parts.append("   - Implementation requirements specified")
        report_parts.append("   - Success criteria established\n")
        
        report_parts.append("**2. Task Estimation and Planning**")
        report_parts.append("   - Clear scope boundaries")
        report_parts.append("   - Identifiable work packages")
        report_parts.append("   - Defined deliverables")
        report_parts.append("   - Measurable success criteria\n")
        
        report_parts.append("**3. Team Allocation and Resource Planning**")
        report_parts.append("   - Technical stack identified")
        report_parts.append("   - Required expertise clear")
        report_parts.append("   - Development phases outlined")
        report_parts.append("   - Timeline framework established\n")
        
        # Next Steps
        report_parts.append("### 🚀 Recommended Next Steps")
        report_parts.append("\n1. **Create WBS** using Planning Tool")
        report_parts.append("   - Break down each phase into detailed tasks")
        report_parts.append("   - Assign priorities and dependencies")
        report_parts.append("   - Estimate effort for each task\n")
        
        report_parts.append("2. **Setup Development Environment**")
        report_parts.append("   - Initialize repository")
        report_parts.append("   - Configure development tools")
        report_parts.append("   - Set up CI/CD pipeline\n")
        
        report_parts.append("3. **Begin Implementation**")
        report_parts.append("   - Start with Phase 1 tasks")
        report_parts.append("   - Follow WBS execution tool for tracking")
        report_parts.append("   - Regular progress reviews\n")
        
        # Footer
        report_parts.append("---")
        report_parts.append("### 📊 Report Metadata")
        report_parts.append(f"- **Total Refinement Steps:** {len(session.refinement_history)}")
        report_parts.append(f"- **Idea Decisions:** {len(idea_steps)}")
        report_parts.append(f"- **Technical Decisions:** {len(system_steps)}")
        report_parts.append(f"- **Initial Specificity:** {session.specificity_score}/100")
        report_parts.append(f"- **Session Duration:** {session.created_at} to {session.last_updated}")
        report_parts.append(f"\n*Report generated by Vibe Refinement Tool v1.0*")
        report_parts.append(f"*Ready for WBS Creation and Implementation Planning*")
        
        return "\n".join(report_parts)
    
    async def execute(
        self,
        action: str,
        ctx: Optional[Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute vibe refinement action
        
        Args:
            action: Action to perform
            ctx: FastMCP context
            **kwargs: Action-specific parameters
            
        Returns:
            Action result
        """
        await self.log_execution(ctx, f"Executing vibe refinement action: {action}")
        
        if action == "initialize":
            return await self._initialize_session(ctx, **kwargs)
        elif action == "get_next":
            return await self._get_next_step(ctx, **kwargs)
        elif action == "submit":
            return await self._submit_selection(ctx, **kwargs)
        elif action == "get_status":
            return await self._get_status(ctx, **kwargs)
        elif action == "generate_report":
            return await self._generate_report(ctx, **kwargs)
        elif action == "list_sessions":
            return await self._list_sessions(ctx)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _initialize_session(
        self,
        ctx: Optional[Any],
        initial_prompt: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Initialize new refinement session
        
        Args:
            ctx: FastMCP context
            initial_prompt: User's initial vague prompt
            
        Returns:
            Session initialization result with first step instructions
        """
        if not initial_prompt or not initial_prompt.strip():
            raise ValueError("initial_prompt is required and cannot be empty")
        
        # Generate session ID
        session_id = self._generate_session_id()
        
        # Calculate specificity and steps needed
        specificity_score = self.calculate_specificity_score(initial_prompt)
        idea_steps, system_steps = self.calculate_steps_needed(specificity_score)
        
        # Create session
        session = RefinementSession(
            id=session_id,
            initial_prompt=initial_prompt.strip(),
            specificity_score=specificity_score,
            idea_steps_needed=idea_steps,
            system_steps_needed=system_steps,
            current_step=0,
            phase=Phase.IDEA.value if idea_steps > 0 else Phase.SYSTEM.value,
            status=SessionStatus.ACTIVE.value,
            refinement_history=[],
            final_decisions={},
            final_report=None,
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat()
        )
        
        vibe_sessions[session_id] = session
        
        await self.log_execution(
            ctx,
            f"Created session {session_id}: score={specificity_score}, "
            f"idea_steps={idea_steps}, system_steps={system_steps}"
        )
        
        # Return session info and prompt for first step
        return {
            "success": True,
            "action": "initialized",
            "session_id": session_id,
            "analysis": {
                "specificity_score": specificity_score,
                "score_interpretation": self._interpret_score(specificity_score),
                "idea_steps_needed": idea_steps,
                "system_steps_needed": system_steps,
                "total_steps": idea_steps + system_steps
            },
            "message": "Session initialized. Call 'get_next' to start refinement process.",
            "next_action": "get_next"
        }
    
    def _interpret_score(self, score: int) -> str:
        """Interpret specificity score"""
        if score < 20:
            return "Very vague - needs significant refinement"
        elif score < 40:
            return "Vague - needs clarification"
        elif score < 60:
            return "Moderate - some refinement needed"
        elif score < 80:
            return "Specific - minimal refinement needed"
        else:
            return "Very specific - ready for implementation"
    
    async def _get_next_step(
        self,
        ctx: Optional[Any],
        session_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get next refinement step with LLM instructions
        
        Args:
            ctx: FastMCP context
            session_id: Session ID
            
        Returns:
            Next step information with LLM instructions
        """
        if session_id not in vibe_sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        session = vibe_sessions[session_id]
        
        # Check if session is completed
        if session.status == SessionStatus.COMPLETED.value:
            return {
                "success": True,
                "action": "already_completed",
                "session_id": session_id,
                "message": "Session already completed. Use 'generate_report' to get final report.",
                "next_action": "generate_report"
            }
        
        # Move to next step
        session.current_step += 1
        
        # Determine if we need to switch phases
        total_idea_steps = session.idea_steps_needed
        if session.current_step > total_idea_steps and session.phase == Phase.IDEA.value:
            session.phase = Phase.SYSTEM.value
            await self.log_execution(ctx, f"Session {session_id}: Moving to SYSTEM phase")
        
        # Check if all steps are completed
        total_steps = session.idea_steps_needed + session.system_steps_needed
        if session.current_step > total_steps:
            session.status = SessionStatus.COMPLETED.value
            session.last_updated = datetime.now().isoformat()
            
            return {
                "success": True,
                "action": "all_steps_completed",
                "session_id": session_id,
                "message": "All refinement steps completed! Use 'generate_report' to get final report.",
                "next_action": "generate_report"
            }
        
        # Generate question and LLM instructions
        question = self._generate_question_for_step(session, session.current_step)
        llm_instructions = self._generate_llm_prompt_instructions(session, session.current_step)
        
        # Create step record
        step_record = RefinementStep(
            step_number=session.current_step,
            phase=session.phase,
            question=question,
            context=llm_instructions
        )
        session.refinement_history.append(step_record)
        session.status = SessionStatus.AWAITING_SUGGESTIONS.value
        session.last_updated = datetime.now().isoformat()
        
        await self.log_execution(
            ctx,
            f"Session {session_id}: Step {session.current_step}/{total_steps} ({session.phase})"
        )
        
        return {
            "success": True,
            "action": "awaiting_suggestions",
            "session_id": session_id,
            "step_info": {
                "current_step": session.current_step,
                "total_steps": total_steps,
                "phase": session.phase,
                "question": question
            },
            "llm_instructions": llm_instructions,
            "message": (
                f"Step {session.current_step}/{total_steps} ({session.phase} phase)\n\n"
                f"Question: {question}\n\n"
                f"⚠️ **CRITICAL OUTPUT REQUIREMENTS:**\n\n"
                f"**YOU MUST FOLLOW THIS EXACT STRUCTURE:**\n\n"
                f"1️⃣ **FIRST**: Present ALL 5 suggestions in complete detail\n"
                f"   - Each suggestion: id, title, description (150-250 words), is_recommended\n"
                f"   - Show sugg_1, sugg_2, sugg_3, sugg_4, sugg_5 - ALL OF THEM\n"
                f"   - Mark exactly ONE with is_recommended=true\n\n"
                f"2️⃣ **SECOND**: After showing all 5 suggestions, add '🤖 AI Recommendation' section\n"
                f"   - State which option you recommend and WHY\n"
                f"   - Include 3-4 specific reasons\n"
                f"   - Briefly explain why other options are less suitable\n\n"
                f"⚠️ **DO NOT:**\n"
                f"   - Skip showing any of the 5 suggestions\n"
                f"   - Show only the recommendation without all 5 suggestions first\n"
                f"   - Summarize or abbreviate the suggestions\n\n"
                f"✅ **Users need to see ALL 5 options to make informed decisions!**\n\n"
                f"After presenting all 5 suggestions + AI recommendation, the user will select via 'submit' action."
            ),
            "next_action": "submit"
        }
    
    async def _submit_selection(
        self,
        ctx: Optional[Any],
        session_id: str,
        selected_suggestion: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Submit user's selection for current step
        
        Args:
            ctx: FastMCP context
            session_id: Session ID
            selected_suggestion: User's selected suggestion
            
        Returns:
            Submission result and next action
        """
        if session_id not in vibe_sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        session = vibe_sessions[session_id]
        
        if not session.refinement_history:
            raise ValueError("No active step to submit selection for")
        
        # Get current step
        current_step_record = session.refinement_history[-1]
        
        # Validate selection
        if not selected_suggestion or not isinstance(selected_suggestion, dict):
            raise ValueError("selected_suggestion must be a valid dictionary")
        
        # Store selection
        current_step_record.user_selection = selected_suggestion
        session.status = SessionStatus.ACTIVE.value
        session.last_updated = datetime.now().isoformat()
        
        await self.log_execution(
            ctx,
            f"Session {session_id}: Selection recorded for step {session.current_step}"
        )
        
        # Check if we need more steps
        total_steps = session.idea_steps_needed + session.system_steps_needed
        if session.current_step >= total_steps:
            session.status = SessionStatus.COMPLETED.value
            
            return {
                "success": True,
                "action": "selection_recorded_final",
                "session_id": session_id,
                "message": "Final selection recorded! All steps completed. Use 'generate_report' to get final report.",
                "next_action": "generate_report"
            }
        else:
            return {
                "success": True,
                "action": "selection_recorded",
                "session_id": session_id,
                "message": f"Selection recorded for step {session.current_step}/{total_steps}. Call 'get_next' to continue.",
                "next_action": "get_next",
                "progress": {
                    "completed_steps": session.current_step,
                    "total_steps": total_steps,
                    "percentage": int((session.current_step / total_steps) * 100)
                }
            }
    
    async def _get_status(
        self,
        ctx: Optional[Any],
        session_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get current session status
        
        Args:
            ctx: FastMCP context
            session_id: Session ID
            
        Returns:
            Session status information
        """
        if session_id not in vibe_sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        session = vibe_sessions[session_id]
        total_steps = session.idea_steps_needed + session.system_steps_needed
        
        return {
            "success": True,
            "session_id": session_id,
            "status": session.status,
            "phase": session.phase,
            "progress": {
                "current_step": session.current_step,
                "total_steps": total_steps,
                "idea_steps": session.idea_steps_needed,
                "system_steps": session.system_steps_needed,
                "completed_steps": len([s for s in session.refinement_history if s.user_selection]),
                "percentage": int((session.current_step / total_steps) * 100) if total_steps > 0 else 0
            },
            "initial_prompt": session.initial_prompt,
            "specificity_score": session.specificity_score,
            "created_at": session.created_at,
            "last_updated": session.last_updated
        }
    
    async def _generate_report(
        self,
        ctx: Optional[Any],
        session_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate final refinement report
        
        Args:
            ctx: FastMCP context
            session_id: Session ID
            
        Returns:
            Final report
        """
        if session_id not in vibe_sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        session = vibe_sessions[session_id]
        
        # Generate report if not already generated
        if not session.final_report:
            session.final_report = self._generate_final_report(session)
            session.status = SessionStatus.COMPLETED.value
            session.last_updated = datetime.now().isoformat()
        
        await self.log_execution(ctx, f"Generated final report for session {session_id}")
        
        return {
            "success": True,
            "session_id": session_id,
            "report": session.final_report,
            "summary": {
                "initial_prompt": session.initial_prompt,
                "specificity_score": session.specificity_score,
                "total_steps_completed": len(session.refinement_history),
                "phases_completed": [Phase.IDEA.value, Phase.SYSTEM.value]
            }
        }
    
    async def _list_sessions(
        self,
        ctx: Optional[Any]
    ) -> Dict[str, Any]:
        """
        List all active sessions
        
        Args:
            ctx: FastMCP context
            
        Returns:
            List of sessions
        """
        sessions_list = []
        for session_id, session in vibe_sessions.items():
            sessions_list.append({
                "session_id": session_id,
                "initial_prompt": session.initial_prompt[:50] + "..." if len(session.initial_prompt) > 50 else session.initial_prompt,
                "status": session.status,
                "phase": session.phase,
                "current_step": session.current_step,
                "total_steps": session.idea_steps_needed + session.system_steps_needed,
                "created_at": session.created_at
            })
        
        return {
            "success": True,
            "total_sessions": len(sessions_list),
            "sessions": sessions_list
        }
