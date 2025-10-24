"""
Counterfactual Reasoning Tool Implementation (4-Step Phase 3)
Advanced reasoning tool for exploring alternative scenarios through counterfactual analysis
with step-by-step Phase 3 execution to prevent token limit issues
"""
from typing import Dict, Any, Optional
from fastmcp import Context
from pathlib import Path
from datetime import datetime
import json
import uuid
import time
from ..base import ReasoningTool


# Shared session store for Counterfactual Reasoning
counterfactual_sessions: Dict[str, Dict[str, Any]] = {}


class CounterfactualInitializeTool(ReasoningTool):
    """Initialize a new Counterfactual Reasoning session"""
    
    def __init__(self):
        super().__init__(
            name="counterfactual_initialize",
            description="Initialize a new counterfactual reasoning session for analyzing alternative scenarios"
        )
    
    def _ensure_output_dir(self) -> Path:
        output_dir = Path("output/counterfactual")
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    
    def _create_initial_md(self, session_id: str, problem: str) -> Path:
        """Create initial markdown file"""
        output_dir = self._ensure_output_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"counterfactual_{timestamp}.md"
        filepath = output_dir / filename
        
        content = f"""# Counterfactual Reasoning Analysis

**Session ID:** {session_id}
**Created:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Problem Statement

{problem}

---

## Analysis Progress

- [ ] Phase 1: Actual State Analysis
- [ ] Phase 2: Counterfactual Scenario Generation
- [ ] Phase 3: Deep Reasoning Analysis
- [ ] Phase 4: Comparative Analysis

---

"""
        filepath.write_text(content, encoding="utf-8")
        return filepath
    
    async def execute(
        self,
        problem: str,
        ctx: Optional[Context] = None
    ) -> str:
        """Initialize Counterfactual Reasoning session"""
        
        # Auto-generate unique session ID
        timestamp = str(int(time.time()))
        random_suffix = str(uuid.uuid4())[:8]
        session_id = f"cf_{timestamp}_{random_suffix}"
        
        # Create initial markdown file
        md_filepath = self._create_initial_md(session_id, problem)
        
        counterfactual_sessions[session_id] = {
            "session_id": session_id,
            "problem": problem,
            "md_filepath": str(md_filepath),
            "phase": "initialized",
            "phase1_result": None,
            "phase2_scenarios": None,
            "selected_type": None,
            "analyzed_types": [],  # Track analyzed types in order
            "phase3_progress": {
                "current_step": 0,
                "step1_principles": None,
                "step2_level1": None,
                "step3_level2": None,
                "step4_level3": None,
                "step5_level4": None
            },
            "phase3_result": None,
            "phase4_results": {},
            "created_at": time.time(),
            "updated_at": time.time(),
            "history": [{
                "action": "initialized",
                "timestamp": time.time(),
                "problem": problem
            }]
        }
        
        await self.log_execution(ctx, f"Initialized Counterfactual Reasoning session {session_id}")
        
        return json.dumps({
            "status": "initialized",
            "session_id": session_id,
            "problem": problem,
            "md_file": str(md_filepath),
            "current_phase": "initialized",
            "next_action": "call counterfactual_phase1",
            "message": f"✅ Session initialized. Next: counterfactual_phase1 with analysis (current_state, causal_chain)"
        }, indent=2, ensure_ascii=False)


class CounterfactualPhase1Tool(ReasoningTool):
    """Phase 1: Actual State Analysis"""
    
    def __init__(self):
        super().__init__(
            name="counterfactual_phase1",
            description="Phase 1: Analyze actual state and identify causal relationships"
        )
    
    def _update_md_phase1(self, session: Dict[str, Any], analysis: Dict[str, Any]):
        """Update markdown file with Phase 1 results"""
        filepath = Path(session["md_filepath"])
        content = filepath.read_text(encoding="utf-8")
        
        phase1_content = f"""## Phase 1: Actual State Analysis

### Current State

**What Happened:**
{analysis.get("current_state", {}).get("what_happened", "N/A")}

**Existing Conditions:**
{self._format_list(analysis.get("current_state", {}).get("existing_conditions", []))}

**Outcomes:**
{self._format_list(analysis.get("current_state", {}).get("outcomes", []))}

### Causal Chain

**Root Causes:**
{self._format_list(analysis.get("causal_chain", {}).get("root_causes", []))}

**Intermediate Processes:**
{self._format_list(analysis.get("causal_chain", {}).get("intermediate_processes", []))}

**Final Results:**
{self._format_list(analysis.get("causal_chain", {}).get("final_results", []))}

---

"""
        # Update checkbox
        content = content.replace("- [ ] Phase 1: Actual State Analysis", "- [x] Phase 1: Actual State Analysis")
        # Append Phase 1 content
        content += phase1_content
        
        filepath.write_text(content, encoding="utf-8")
    
    def _format_list(self, items: list) -> str:
        if not items:
            return "- None"
        return "\n".join([f"- {item}" for item in items])
    
    async def execute(
        self,
        session_id: str,
        analysis: Dict[str, Any],
        ctx: Optional[Context] = None
    ) -> str:
        """Execute Phase 1: Actual State Analysis"""
        
        if session_id not in counterfactual_sessions:
            return json.dumps({"error": "Session not found. Call counterfactual_initialize first."}, ensure_ascii=False)
        
        session = counterfactual_sessions[session_id]
        
        if session["phase"] != "initialized":
            return json.dumps({
                "error": "Phase 1 can only be called after initialization.",
                "current_phase": session["phase"]
            }, ensure_ascii=False)
        
        # Validate analysis structure
        required_fields = ["current_state", "causal_chain"]
        missing_fields = [f for f in required_fields if f not in analysis]
        if missing_fields:
            return json.dumps({
                "error": f"Missing required fields: {missing_fields}",
                "required_fields": required_fields
            }, ensure_ascii=False)
        
        # Store Phase 1 result
        session["phase1_result"] = analysis
        session["phase"] = "phase1_complete"
        session["updated_at"] = time.time()
        session["history"].append({
            "action": "phase1_complete",
            "timestamp": time.time(),
            "analysis": analysis
        })
        
        # Update markdown file
        self._update_md_phase1(session, analysis)
        
        await self.log_execution(ctx, f"Completed Phase 1 for session {session_id}")
        
        return json.dumps({
            "status": "phase1_complete",
            "session_id": session_id,
            "md_file": session["md_filepath"],
            "next_action": "call counterfactual_phase2",
            "message": "✅ Phase 1 complete. Next: counterfactual_phase2 with 4 scenarios (diagnostic, predictive, preventive, optimization)"
        }, indent=2, ensure_ascii=False)


class CounterfactualPhase2Tool(ReasoningTool):
    """Phase 2: Counterfactual Scenario Generation - Generate 4 scenarios and select 1"""
    
    def __init__(self):
        super().__init__(
            name="counterfactual_phase2",
            description="Phase 2: Generate 4 scenario types and select ONE type to analyze in Phase 3"
        )
    
    def _update_md_phase2(self, session: Dict[str, Any], scenarios: Dict[str, Any], selected_type: str):
        """Update markdown file with Phase 2 results"""
        filepath = Path(session["md_filepath"])
        content = filepath.read_text(encoding="utf-8")
        
        type_names = {
            "diagnostic": "Diagnostic (Root Cause Identification)",
            "predictive": "Predictive (Future Prediction)",
            "preventive": "Preventive (Risk Prevention)",
            "optimization": "Optimization (Improvement Exploration)"
        }
        
        analyzed_types = session.get("analyzed_types", [])
        
        # For first call, create new Phase 2 section with type-specific subsections
        # For subsequent calls, update existing section
        if "## Phase 2: Counterfactual Scenario Generation" not in content:
            phase2_content = f"""## Phase 2: Counterfactual Scenario Generation

"""
            
            for type_key, type_name in type_names.items():
                scenario = scenarios.get(type_key, {})
                # Show ✓ for analyzed types, → for current selection, space for future
                if type_key in analyzed_types:
                    marker = "✓"
                elif type_key == selected_type:
                    marker = "→"
                else:
                    marker = " "
                    
                phase2_content += f"""### [{marker}] {type_name}

**Changed Condition:**
{scenario.get('changed_condition', 'N/A')}

**Counterfactual Scenario:**
{scenario.get('counterfactual_scenario', 'N/A')}

**Logical Consistency:**
{scenario.get('logical_consistency', 'N/A')}

"""
                
                # Add placeholder sections for Phase 3 & 4 (will be filled during analysis)
                phase2_content += f"""<!-- PHASE3_{type_key.upper()}_START -->
<!-- PHASE3_{type_key.upper()}_END -->

<!-- PHASE4_{type_key.upper()}_START -->
<!-- PHASE4_{type_key.upper()}_END -->

---

"""
            
            # Update checkbox
            content = content.replace("- [ ] Phase 2: Counterfactual Scenario Generation", "- [x] Phase 2: Counterfactual Scenario Generation")
            # Append Phase 2 content
            content += phase2_content
        else:
            # Update markers in existing Phase 2 section
            for type_key, type_name in type_names.items():
                # Update markers based on current state
                if type_key in analyzed_types:
                    # Change to completed marker
                    old_marker_patterns = [f"### [ ] {type_name}", f"### [\u2192] {type_name}"]
                    for pattern in old_marker_patterns:
                        if pattern in content:
                            content = content.replace(pattern, f"### [\u2713] {type_name}")
                elif type_key == selected_type:
                    # Change to current marker
                    old_marker = f"### [ ] {type_name}"
                    if old_marker in content:
                        content = content.replace(old_marker, f"### [\u2192] {type_name}")
        
        filepath.write_text(content, encoding="utf-8")
    
    async def execute(
        self,
        session_id: str,
        scenarios: Dict[str, Any],
        selected_type: Optional[str] = None,
        ctx: Optional[Context] = None
    ) -> str:
        """Execute Phase 2: Generate counterfactual scenarios and select one type"""
        
        if session_id not in counterfactual_sessions:
            return json.dumps({"error": "Session not found. Call counterfactual_initialize first."}, ensure_ascii=False)
        
        session = counterfactual_sessions[session_id]
        
        # Allow Phase 2 to be called after phase1_complete OR after phase4_complete (for next type)
        valid_phases = ["phase1_complete", "completed"]
        if session["phase"] not in valid_phases:
            return json.dumps({
                "error": f"Phase 2 can only be called after Phase 1 or Phase 4 completion.",
                "current_phase": session["phase"]
            }, ensure_ascii=False)
        
        # Validate all 4 types are present
        required_types = ["diagnostic", "predictive", "preventive", "optimization"]
        missing_types = [t for t in required_types if t not in scenarios]
        if missing_types:
            return json.dumps({
                "error": f"Missing scenario types: {missing_types}",
                "required_types": required_types
            }, ensure_ascii=False)
        
        # Auto-select next type in sequence if not provided
        if selected_type is None:
            # Sequential order: diagnostic -> predictive -> preventive -> optimization
            type_order = ["diagnostic", "predictive", "preventive", "optimization"]
            analyzed_types = session.get("analyzed_types", [])
            
            # Find first unanalyzed type
            for t in type_order:
                if t not in analyzed_types:
                    selected_type = t
                    break
            
            if selected_type is None:
                return json.dumps({
                    "error": "All types have been analyzed.",
                    "analyzed_types": analyzed_types
                }, ensure_ascii=False)
        else:
            # Validate selected_type if provided
            if selected_type not in required_types:
                return json.dumps({
                    "error": f"Invalid selected_type: {selected_type}",
                    "valid_types": required_types
                }, ensure_ascii=False)
        
        # Store Phase 2 scenarios and selected type
        session["phase2_scenarios"] = scenarios
        session["selected_type"] = selected_type
        session["phase"] = "phase2_complete"
        session["updated_at"] = time.time()
        session["history"].append({
            "action": "phase2_complete",
            "timestamp": time.time(),
            "scenarios": scenarios,
            "selected_type": selected_type
        })
        
        # Update markdown file
        self._update_md_phase2(session, scenarios, selected_type)
        
        await self.log_execution(ctx, f"Completed Phase 2 for session {session_id}, selected type: {selected_type}")
        
        return json.dumps({
            "status": "phase2_complete",
            "session_id": session_id,
            "selected_type": selected_type,
            "md_file": session["md_filepath"],
            "next_action": "call_counterfactual_phase3_step1",
            "message": f"✅ Phase 2 complete. Selected: {selected_type}. Next: counterfactual_phase3_step1 with principles_applied (dict: minimal_change, causal_consistency, proximity)"
        }, indent=2, ensure_ascii=False)


class CounterfactualPhase3Step1Tool(ReasoningTool):
    """Phase 3 Step 1: Apply 3 Core Principles to Selected Scenario"""
    
    def __init__(self):
        super().__init__(
            name="counterfactual_phase3_step1",
            description="Phase 3 Step 1: Apply the 3 core principles (Minimal Change, Causal Consistency, Proximity) to the selected counterfactual scenario"
        )
    
    def _update_md_step1(self, session: Dict[str, Any], principles: Dict[str, str]):
        """Update markdown file with Step 1 results"""
        filepath = Path(session["md_filepath"])
        content = filepath.read_text(encoding="utf-8")
        
        selected_type = session["selected_type"]
        
        step1_content = f"""#### Phase 3: Deep Reasoning Analysis

**Step 1: Core Principles Application**

**Minimal Change:**
{principles.get('minimal_change', 'N/A')}

**Causal Consistency:**
{principles.get('causal_consistency', 'N/A')}

**Proximity:**
{principles.get('proximity', 'N/A')}

"""
        
        # Insert into the type-specific Phase 3 placeholder
        placeholder_start = f"<!-- PHASE3_{selected_type.upper()}_START -->"
        placeholder_end = f"<!-- PHASE3_{selected_type.upper()}_END -->"
        
        if placeholder_start in content and placeholder_end in content:
            # Replace the placeholder with actual content
            content = content.replace(
                f"{placeholder_start}\n{placeholder_end}",
                f"{placeholder_start}\n{step1_content}{placeholder_end}"
            )
        
        # Update checkbox (only once)
        if "- [ ] Phase 3: Deep Reasoning Analysis" in content:
            content = content.replace("- [ ] Phase 3: Deep Reasoning Analysis", "- [x] Phase 3: Deep Reasoning Analysis")
        
        filepath.write_text(content, encoding="utf-8")
    
    async def execute(
        self,
        session_id: str,
        principles_applied: Dict[str, str],
        ctx: Optional[Context] = None
    ) -> str:
        """Execute Phase 3 Step 1: Apply principles"""
        
        if session_id not in counterfactual_sessions:
            return json.dumps({"error": "Session not found."}, ensure_ascii=False)
        
        session = counterfactual_sessions[session_id]
        
        if session["phase"] != "phase2_complete":
            return json.dumps({
                "error": "Phase 2 must be completed first.",
                "current_phase": session["phase"]
            }, ensure_ascii=False)
        
        # Reset phase3_progress for new type analysis
        session["phase3_progress"] = {
            "current_step": 0,
            "step1_principles": None,
            "step2_level1": None,
            "step3_level2": None,
            "step4_level3": None,
            "step5_level4": None
        }
        progress = session["phase3_progress"]
        
        # Validate principles_applied structure
        required_keys = ["minimal_change", "causal_consistency", "proximity"]
        missing_keys = [k for k in required_keys if k not in principles_applied]
        if missing_keys:
            return json.dumps({
                "error": f"Missing required principles: {missing_keys}",
                "required_keys": required_keys
            }, ensure_ascii=False)
        
        # Store Step 1 result
        progress["step1_principles"] = principles_applied
        progress["current_step"] = 1
        session["phase"] = "phase3_step1_complete"
        session["updated_at"] = time.time()
        session["history"].append({
            "action": "phase3_step1_complete",
            "timestamp": time.time(),
            "principles": principles_applied
        })
        
        # Update markdown file
        self._update_md_step1(session, principles_applied)
        
        await self.log_execution(ctx, f"Phase 3 Step 1 complete for session {session_id}")
        
        return json.dumps({
            "status": "phase3_step1_complete",
            "session_id": session_id,
            "current_step": 1,
            "total_steps": 5,
            "next_action": "call counterfactual_phase3_step2",
            "message": f"✅ Step 1/5 complete. Next: counterfactual_phase3_step2 with level1_direct (string)"
        }, indent=2, ensure_ascii=False)


class CounterfactualPhase3Step2Tool(ReasoningTool):
    """Phase 3 Step 2: Direct Impact Analysis (Reasoning Level 1)"""
    
    def __init__(self):
        super().__init__(
            name="counterfactual_phase3_step2",
            description="Phase 3 Step 2: Analyze direct and immediate impacts (Reasoning Depth Level 1)"
        )
    
    def _update_md_step2(self, session: Dict[str, Any], level1: str):
        """Update markdown file with Step 2 results"""
        filepath = Path(session["md_filepath"])
        content = filepath.read_text(encoding="utf-8")
        
        selected_type = session["selected_type"]
        
        step2_content = f"""**Step 2: Direct Impact Analysis (Level 1)**

{level1}

"""
        
        # Append to the type-specific Phase 3 section
        placeholder_end = f"<!-- PHASE3_{selected_type.upper()}_END -->"
        
        if placeholder_end in content:
            # Insert before the end placeholder
            content = content.replace(
                placeholder_end,
                f"{step2_content}{placeholder_end}"
            )
        
        filepath.write_text(content, encoding="utf-8")
    
    async def execute(
        self,
        session_id: str,
        level1_direct: str,
        ctx: Optional[Context] = None
    ) -> str:
        """Execute Phase 3 Step 2: Direct impact analysis"""
        
        if session_id not in counterfactual_sessions:
            return json.dumps({"error": "Session not found."}, ensure_ascii=False)
        
        session = counterfactual_sessions[session_id]
        progress = session["phase3_progress"]
        
        # Validate step progression
        if progress["current_step"] != 1:
            return json.dumps({
                "error": "Must complete Step 1 before Step 2",
                "current_step": progress["current_step"]
            }, ensure_ascii=False)
        
        # Store Step 2 result
        progress["step2_level1"] = level1_direct
        progress["current_step"] = 2
        session["phase"] = "phase3_step2_complete"
        session["updated_at"] = time.time()
        session["history"].append({
            "action": "phase3_step2_complete",
            "timestamp": time.time(),
            "level1": level1_direct
        })
        
        # Update markdown file
        self._update_md_step2(session, level1_direct)
        
        await self.log_execution(ctx, f"Phase 3 Step 2 complete for session {session_id}")
        
        return json.dumps({
            "status": "phase3_step2_complete",
            "session_id": session_id,
            "current_step": 2,
            "total_steps": 5,
            "next_action": "call counterfactual_phase3_step3",
            "message": f"✅ Step 2/5 complete. Next: counterfactual_phase3_step3 with level2_ripple (string)"
        }, indent=2, ensure_ascii=False)


class CounterfactualPhase3Step3Tool(ReasoningTool):
    """Phase 3 Step 3: Ripple Effects Analysis (Level 2)"""
    
    def __init__(self):
        super().__init__(
            name="counterfactual_phase3_step3",
            description="Phase 3 Step 3: Analyze ripple effects (Reasoning Depth Level 2)"
        )
    
    def _update_md_step3(self, session: Dict[str, Any], level2: str):
        """Update markdown file with Step 3 results"""
        filepath = Path(session["md_filepath"])
        content = filepath.read_text(encoding="utf-8")
        
        selected_type = session["selected_type"]
        
        step3_content = f"""**Step 3: Ripple Effects Analysis (Level 2)**

{level2}

"""
        
        # Append to the type-specific Phase 3 section
        placeholder_end = f"<!-- PHASE3_{selected_type.upper()}_END -->"
        
        if placeholder_end in content:
            # Insert before the end placeholder
            content = content.replace(
                placeholder_end,
                f"{step3_content}{placeholder_end}"
            )
        
        filepath.write_text(content, encoding="utf-8")
    
    async def execute(
        self,
        session_id: str,
        level2_ripple: str,
        ctx: Optional[Context] = None
    ) -> str:
        """Execute Phase 3 Step 3: Ripple effects analysis"""
        
        print(f"\n[DEBUG] CounterfactualPhase3Step3Tool.execute called")
        print(f"  - session_id: {session_id}")
        print(f"  - level2_ripple type: {type(level2_ripple)}")
        print(f"  - level2_ripple value: {level2_ripple[:100] if isinstance(level2_ripple, str) else level2_ripple}...")
        
        if session_id not in counterfactual_sessions:
            return json.dumps({"error": "Session not found."}, ensure_ascii=False)
        
        session = counterfactual_sessions[session_id]
        progress = session["phase3_progress"]
        
        print(f"[DEBUG] Session found, current_step: {progress['current_step']}")
        
        # Validate step progression
        if progress["current_step"] != 2:
            return json.dumps({
                "error": "Must complete Step 2 before Step 3",
                "current_step": progress["current_step"]
            }, ensure_ascii=False)
        
        # Store Step 3 result
        progress["step3_level2"] = level2_ripple
        progress["current_step"] = 3
        session["updated_at"] = time.time()
        session["history"].append({
            "action": "phase3_step3_complete",
            "timestamp": time.time(),
            "level2": level2_ripple
        })
        
        session["phase"] = "phase3_step3_complete"
        
        # Update markdown file
        self._update_md_step3(session, level2_ripple)
        
        await self.log_execution(ctx, f"Phase 3 Step 3 complete for session {session_id}")
        
        return json.dumps({
            "status": "phase3_step3_complete",
            "session_id": session_id,
            "current_step": 3,
            "total_steps": 5,
            "next_action": "call counterfactual_phase3_step4",
            "message": f"✅ Step 3/5 complete. Next: counterfactual_phase3_step4 with level3_multidimensional (dict: technical, organizational, cultural, external)"
        }, indent=2, ensure_ascii=False)


class CounterfactualPhase3Step4Tool(ReasoningTool):
    """Phase 3 Step 4: Multidimensional Analysis (Level 3)"""
    
    def __init__(self):
        super().__init__(
            name="counterfactual_phase3_step4",
            description="Phase 3 Step 4: Analyze multidimensional impacts (Reasoning Depth Level 3)"
        )
    
    def _update_md_step4(self, session: Dict[str, Any], level3: Dict[str, str]):
        """Update markdown file with Step 4 results"""
        filepath = Path(session["md_filepath"])
        content = filepath.read_text(encoding="utf-8")
        
        selected_type = session["selected_type"]
        
        step4_content = f"""**Step 4: Multidimensional Analysis (Level 3)**

**Technical Dimension:**
{level3.get('technical', 'N/A')}

**Organizational Dimension:**
{level3.get('organizational', 'N/A')}

**Cultural Dimension:**
{level3.get('cultural', 'N/A')}

**External Dimension:**
{level3.get('external', 'N/A')}

"""
        
        # Append to the type-specific Phase 3 section
        placeholder_end = f"<!-- PHASE3_{selected_type.upper()}_END -->"
        
        if placeholder_end in content:
            # Insert before the end placeholder
            content = content.replace(
                placeholder_end,
                f"{step4_content}{placeholder_end}"
            )
        
        filepath.write_text(content, encoding="utf-8")
    
    async def execute(
        self,
        session_id: str,
        level3_multidimensional: Dict[str, str],
        ctx: Optional[Context] = None
    ) -> str:
        """Execute Phase 3 Step 4: Multidimensional analysis"""
        
        if session_id not in counterfactual_sessions:
            return json.dumps({"error": "Session not found."}, ensure_ascii=False)
        
        session = counterfactual_sessions[session_id]
        progress = session["phase3_progress"]
        
        # Validate step progression
        if progress["current_step"] != 3:
            return json.dumps({
                "error": "Must complete Step 3 before Step 4",
                "current_step": progress["current_step"]
            }, ensure_ascii=False)
        
        # Validate multidimensional structure
        required_dimensions = ["technical", "organizational", "cultural", "external"]
        missing_dimensions = [d for d in required_dimensions if d not in level3_multidimensional]
        if missing_dimensions:
            return json.dumps({
                "error": f"Missing dimensions: {missing_dimensions}",
                "required_dimensions": required_dimensions
            }, ensure_ascii=False)
        
        # Store Step 4 result
        progress["step4_level3"] = level3_multidimensional
        progress["current_step"] = 4
        session["updated_at"] = time.time()
        session["history"].append({
            "action": "phase3_step4_complete",
            "timestamp": time.time(),
            "level3": level3_multidimensional
        })
        
        session["phase"] = "phase3_step4_complete"
        
        # Update markdown file
        self._update_md_step4(session, level3_multidimensional)
        
        await self.log_execution(ctx, f"Phase 3 Step 4 complete for session {session_id}")
        
        return json.dumps({
            "status": "phase3_step4_complete",
            "session_id": session_id,
            "current_step": 4,
            "total_steps": 5,
            "next_action": "call counterfactual_phase3_step5",
            "message": f"✅ Step 4/5 complete. Next: counterfactual_phase3_step5 with level4_longterm (timeline, sustained_benefits, new_challenges, evolution) and outcome_scenarios (best_case, worst_case, most_likely)"
        }, indent=2, ensure_ascii=False)


class CounterfactualPhase3Step5Tool(ReasoningTool):
    """Phase 3 Step 5: Long-term Evolution & Outcome Scenarios (Level 4) - FINAL Step"""
    
    def __init__(self):
        super().__init__(
            name="counterfactual_phase3_step5",
            description="Phase 3 Step 5: Analyze long-term evolution and outcome scenarios (Level 4). Final step of Phase 3."
        )
    
    def _update_md_step5(self, session: Dict[str, Any], level4: Dict[str, str], outcomes: Dict[str, str]):
        """Update markdown file with Step 5 results"""
        filepath = Path(session["md_filepath"])
        content = filepath.read_text(encoding="utf-8")
        
        selected_type = session["selected_type"]
        
        step5_content = f"""**Step 5: Long-term Evolution & Outcome Scenarios (Level 4)**

**Timeline:**
{level4.get('timeline', 'N/A')}

**Sustained Benefits:**
{level4.get('sustained_benefits', 'N/A')}

**New Challenges:**
{level4.get('new_challenges', 'N/A')}

**Evolution:**
{level4.get('evolution', 'N/A')}

**Outcome Scenarios:**

- **Best Case:** {outcomes.get('best_case', 'N/A')}
- **Worst Case:** {outcomes.get('worst_case', 'N/A')}
- **Most Likely:** {outcomes.get('most_likely', 'N/A')}

"""
        
        # Append to the type-specific Phase 3 section
        placeholder_end = f"<!-- PHASE3_{selected_type.upper()}_END -->"
        
        if placeholder_end in content:
            # Insert before the end placeholder
            content = content.replace(
                placeholder_end,
                f"{step5_content}{placeholder_end}"
            )
        
        filepath.write_text(content, encoding="utf-8")
    
    async def execute(
        self,
        session_id: str,
        level4_longterm: Dict[str, str],
        outcome_scenarios: Dict[str, str],
        ctx: Optional[Context] = None
    ) -> str:
        """Execute Phase 3 Step 5: Long-term evolution and outcomes"""
        
        if session_id not in counterfactual_sessions:
            return json.dumps({"error": "Session not found."}, ensure_ascii=False)
        
        session = counterfactual_sessions[session_id]
        progress = session["phase3_progress"]
        
        # Validate step progression
        if progress["current_step"] != 4:
            return json.dumps({
                "error": "Must complete Step 4 before Step 5",
                "current_step": progress["current_step"]
            }, ensure_ascii=False)
        
        # Validate level4 structure
        required_level4_keys = ["timeline", "sustained_benefits", "new_challenges", "evolution"]
        missing_level4 = [k for k in required_level4_keys if k not in level4_longterm]
        if missing_level4:
            return json.dumps({
                "error": f"Missing level4 keys: {missing_level4}",
                "required_keys": required_level4_keys
            }, ensure_ascii=False)
        
        # Validate outcome scenarios
        required_outcomes = ["best_case", "worst_case", "most_likely"]
        missing_outcomes = [o for o in required_outcomes if o not in outcome_scenarios]
        if missing_outcomes:
            return json.dumps({
                "error": f"Missing outcome scenarios: {missing_outcomes}",
                "required_outcomes": required_outcomes
            }, ensure_ascii=False)
        
        # Store Step 5 result
        progress["step5_level4"] = {
            "level4_longterm": level4_longterm,
            "outcome_scenarios": outcome_scenarios
        }
        progress["current_step"] = 5
        
        # Assemble complete Phase 3 result from all 5 steps
        complete_phase3_result = {
            "principles_applied": progress["step1_principles"],
            "reasoning_depth": {
                "level1_direct": progress["step2_level1"],
                "level2_ripple": progress["step3_level2"],
                "level3_multidimensional": progress["step4_level3"],
                "level4_longterm": level4_longterm
            },
            "outcome_scenarios": outcome_scenarios
        }
        
        # Store complete Phase 3 result
        session["phase3_result"] = complete_phase3_result
        session["phase"] = "phase3_complete"
        session["updated_at"] = time.time()
        session["history"].append({
            "action": "phase3_complete",
            "timestamp": time.time(),
            "complete_result": complete_phase3_result
        })
        
        # Update markdown file
        self._update_md_step5(session, level4_longterm, outcome_scenarios)
        
        await self.log_execution(ctx, f"Phase 3 complete for session {session_id}")
        
        selected_type = session["selected_type"]
        
        return json.dumps({
            "status": "phase3_complete",
            "session_id": session_id,
            "current_step": 5,
            "total_steps": 5,
            "next_action": "call counterfactual_phase4",
            "message": f"✅ Phase 3 complete (5/5). Next: counterfactual_phase4 with comparative_analysis (actual_vs_counterfactual, key_insights, action_recommendations, final_summary)"
        }, indent=2, ensure_ascii=False)


class CounterfactualPhase4Tool(ReasoningTool):
    """Phase 4: Comparative Analysis"""
    
    def __init__(self):
        super().__init__(
            name="counterfactual_phase4",
            description="Phase 4: Perform comparative analysis for the selected type"
        )
    
    def _format_list(self, items: list) -> str:
        """Format list items with bullet points"""
        if not items:
            return "- None"
        return "\n".join([f"- {item}" for item in items])
    
    def _temp_placeholder_function(self, session: Dict[str, Any]) -> str:
        """Generate MD file header with Phase 1 and Phase 2 results"""
        created_time = datetime.fromtimestamp(session["created_at"]).strftime("%Y-%m-%d %H:%M:%S")
        
        phase1 = session.get("phase1_result", {})
        phase2 = session.get("phase2_scenarios", {})
        
        # Format Phase 1 current state
        current_state = phase1.get("current_state", {})
        current_state_md = f"""### Current State

**What Happened:**
{current_state.get('what_happened', 'Not specified')}

**Existing Conditions:**
{self._format_list(current_state.get('existing_conditions', []))}

**Outcomes:**
{self._format_list(current_state.get('outcomes', []))}
"""
        
        # Format Phase 1 causal chain
        causal_chain = phase1.get("causal_chain", {})
        causal_chain_md = f"""### Causal Chain

**Root Causes:**
{self._format_list(causal_chain.get('root_causes', []))}

**Intermediate Processes:**
{self._format_list(causal_chain.get('intermediate_processes', []))}

**Final Results:**
{self._format_list(causal_chain.get('final_results', []))}
"""
        
        # Format Phase 2 scenarios
        type_names = {
            "diagnostic": "Diagnostic Scenario (Root Cause Identification)",
            "predictive": "Predictive Scenario (Future Prediction)",
            "preventive": "Preventive Scenario (Risk Prevention)",
            "optimization": "Optimization Scenario (Improvement Exploration)"
        }
        
        scenarios_md = ""
        for type_key, type_name in type_names.items():
            scenario = phase2.get(type_key, {})
            scenarios_md += f"""### {type_name}

**Changed Condition:**
{scenario.get('changed_condition', 'Not specified')}

**Counterfactual Scenario:**
{scenario.get('counterfactual_scenario', 'Not specified')}

**Logical Consistency:**
{scenario.get('logical_consistency', 'Not specified')}

"""
        
        return f"""# Counterfactual Reasoning Analysis Report

**Session ID:** {session['session_id']}  
**Created:** {created_time}  
**Problem:** {session['problem']}

---

## Phase 1: Actual State Analysis

{current_state_md}

{causal_chain_md}

---

## Phase 2: Counterfactual Scenarios

{scenarios_md}

---

"""
    
    def _format_phase3_for_md(self, phase3_result: Dict[str, Any], type_name: str) -> str:
        """Format Phase 3 analysis for markdown"""
        principles = phase3_result.get("principles_applied", {})
        reasoning = phase3_result.get("reasoning_depth", {})
        outcomes = phase3_result.get("outcome_scenarios", {})
        
        level3_multi = reasoning.get("level3_multidimensional", {})
        level4_long = reasoning.get("level4_longterm", {})
        
        return f"""### Phase 3: Deep Reasoning Process

#### Step 1: Core Principles Applied

**Minimal Change:**
{principles.get('minimal_change', 'Not specified')}

**Causal Consistency:**
{principles.get('causal_consistency', 'Not specified')}

**Proximity:**
{principles.get('proximity', 'Not specified')}

#### Step 2: Direct Impact Analysis (Level 1)

{reasoning.get('level1_direct', 'Not specified')}

#### Step 3: Ripple Effects & Multidimensional Analysis (Levels 2 & 3)

**Level 2 - Ripple Effects:**

{reasoning.get('level2_ripple', 'Not specified')}

**Level 3 - Multidimensional Impact:**

**Technical Dimension:**
{level3_multi.get('technical', 'Not specified')}

**Organizational Dimension:**
{level3_multi.get('organizational', 'Not specified')}

**Cultural Dimension:**
{level3_multi.get('cultural', 'Not specified')}

**External Dimension:**
{level3_multi.get('external', 'Not specified')}

#### Step 4: Long-term Evolution & Outcome Scenarios (Level 4)

**Timeline:**
{level4_long.get('timeline', 'Not specified')}

**Sustained Benefits:**
{level4_long.get('sustained_benefits', 'Not specified')}

**New Challenges:**
{level4_long.get('new_challenges', 'Not specified')}

**Evolution:**
{level4_long.get('evolution', 'Not specified')}

**Outcome Scenarios:**

- **Best Case:** {outcomes.get('best_case', 'Not specified')}
- **Worst Case:** {outcomes.get('worst_case', 'Not specified')}
- **Most Likely:** {outcomes.get('most_likely', 'Not specified')}

"""
    
    def _format_phase4_for_md(self, comparative_analysis: Dict[str, Any], type_name: str) -> str:
        """Format Phase 4 comparative analysis for markdown"""
        actual_vs = comparative_analysis.get("actual_vs_counterfactual", {})
        insights = comparative_analysis.get("key_insights", {})
        actions = comparative_analysis.get("action_recommendations", {})
        summary = comparative_analysis.get("final_summary", {})
        
        return f"""### Phase 4: Comparative Analysis

#### Actual vs Counterfactual Comparison

**What Differs:**
{actual_vs.get('what_differs', 'Not specified')}

**Why It Differs:**
{actual_vs.get('why_differs', 'Not specified')}

**Magnitude & Importance:**
{actual_vs.get('magnitude_importance', 'Not specified')}

#### Key Insights & Findings

**Critical Findings:**
{self._format_list(insights.get('critical_findings', []))}

**Causal Factors & Leverage Points:**
{self._format_list(insights.get('causal_factors', []))}

**Improvement Opportunities:**
{self._format_list(insights.get('improvement_opportunities', []))}

#### Action Recommendations & Roadmap

**Immediate Actions (0-1 month):**
{self._format_list(actions.get('immediate_actions', []))}

**Short-term Plans (1-3 months):**
{self._format_list(actions.get('short_term_plans', []))}

**Long-term Initiatives (3-12 months):**
{self._format_list(actions.get('long_term_initiatives', []))}

**Monitoring & Metrics:**
{self._format_list(actions.get('monitoring_metrics', []))}

#### Executive Summary

**Key Takeaway:**
{summary.get('key_takeaway', 'Not specified')}

**Expected Impact:**
{summary.get('expected_impact', 'Not specified')}

**Implementation Timeline:**
{summary.get('implementation_timeline', 'Not specified')}

**Next Steps:**
{self._format_list(summary.get('next_steps', []))}

"""
    
    def _update_md_phase4(self, session: Dict[str, Any], analysis: Dict[str, Any]):
        """Update markdown file with Phase 4 results"""
        filepath = Path(session["md_filepath"])
        content = filepath.read_text(encoding="utf-8")
        
        selected_type = session["selected_type"]
        
        phase4_content = f"""#### Phase 4: Comparative Analysis

**Actual vs Counterfactual Comparison**

**What Differs:**
{analysis.get('actual_vs_counterfactual', {}).get('what_differs', 'N/A')}

**Why It Differs:**
{analysis.get('actual_vs_counterfactual', {}).get('why_differs', 'N/A')}

**Magnitude & Importance:**
{analysis.get('actual_vs_counterfactual', {}).get('magnitude_importance', 'N/A')}

**Key Insights**

- **Critical Findings:**
{self._format_list(analysis.get('key_insights', {}).get('critical_findings', []))}

- **Causal Factors:**
{self._format_list(analysis.get('key_insights', {}).get('causal_factors', []))}

- **Improvement Opportunities:**
{self._format_list(analysis.get('key_insights', {}).get('improvement_opportunities', []))}

**Action Recommendations**

- **Immediate Actions (0-1 month):**
{self._format_list(analysis.get('action_recommendations', {}).get('immediate_actions', []))}

- **Short-term Plans (1-3 months):**
{self._format_list(analysis.get('action_recommendations', {}).get('short_term_plans', []))}

- **Long-term Initiatives (3-12 months):**
{self._format_list(analysis.get('action_recommendations', {}).get('long_term_initiatives', []))}

- **Monitoring Metrics:**
{self._format_list(analysis.get('action_recommendations', {}).get('monitoring_metrics', []))}

**Final Summary**

**Key Takeaway:**
{analysis.get('final_summary', {}).get('key_takeaway', 'N/A')}

**Expected Impact:**
{analysis.get('final_summary', {}).get('expected_impact', 'N/A')}

**Implementation Timeline:**
{analysis.get('final_summary', {}).get('implementation_timeline', 'N/A')}

**Next Steps:**
{self._format_list(analysis.get('final_summary', {}).get('next_steps', []))}

"""
        
        # Insert into the type-specific Phase 4 placeholder
        placeholder_start = f"<!-- PHASE4_{selected_type.upper()}_START -->"
        placeholder_end = f"<!-- PHASE4_{selected_type.upper()}_END -->"
        
        if placeholder_start in content and placeholder_end in content:
            # Replace the placeholder with actual content
            content = content.replace(
                f"{placeholder_start}\n{placeholder_end}",
                f"{placeholder_start}\n{phase4_content}{placeholder_end}"
            )
        
        # Update checkbox (only once)
        if "- [ ] Phase 4: Comparative Analysis" in content:
            content = content.replace("- [ ] Phase 4: Comparative Analysis", "- [x] Phase 4: Comparative Analysis")
        
        filepath.write_text(content, encoding="utf-8")
    
    async def execute(
        self,
        session_id: str,
        comparative_analysis: Dict[str, Any],
        ctx: Optional[Context] = None
    ) -> str:
        """Execute Phase 4: Comparative analysis for selected scenario type"""
        
        if session_id not in counterfactual_sessions:
            return json.dumps({"error": "Session not found."}, ensure_ascii=False)
        
        session = counterfactual_sessions[session_id]
        
        # Validate Phase 3 completion
        if session["phase"] != "phase3_complete":
            return json.dumps({
                "error": "Phase 3 must be completed first.",
                "current_phase": session["phase"]
            }, ensure_ascii=False)
        
        # Use the selected_type from session
        selected_type = session.get("selected_type")
        if not selected_type:
            return json.dumps({
                "error": "No selected_type found in session. This is a system error.",
                "message": "selected_type should have been set in Phase 2"
            }, ensure_ascii=False)
        
        # Validate comparative_analysis structure
        required_sections = ["actual_vs_counterfactual", "key_insights", "action_recommendations", "final_summary"]
        missing_sections = [s for s in required_sections if s not in comparative_analysis]
        if missing_sections:
            return json.dumps({
                "error": f"Missing required sections in comparative_analysis: {missing_sections}",
                "required_sections": required_sections
            }, ensure_ascii=False)
        
        # Store Phase 4 result and track analyzed type
        session["phase4_results"][selected_type] = {
            "type": selected_type,
            "analysis": comparative_analysis,
            "analyzed_at": time.time()
        }
        
        # Add to analyzed_types list
        if "analyzed_types" not in session:
            session["analyzed_types"] = []
        if selected_type not in session["analyzed_types"]:
            session["analyzed_types"].append(selected_type)
        
        session["phase"] = "completed"
        session["completed_at"] = time.time()
        session["updated_at"] = time.time()
        session["history"].append({
            "action": f"phase4_complete",
            "timestamp": time.time(),
            "type": selected_type,
            "comparative_analysis": comparative_analysis
        })
        
        # Update markdown file
        self._update_md_phase4(session, comparative_analysis)
        
        await self.log_execution(ctx, f"Phase 4 complete for type '{selected_type}' in session {session_id}")
        
        type_names = {
            "diagnostic": "Diagnostic",
            "predictive": "Predictive",
            "preventive": "Preventive",
            "optimization": "Optimization"
        }
        
        # Get next type to analyze (in order)
        type_order = ["diagnostic", "predictive", "preventive", "optimization"]
        analyzed_types = session["analyzed_types"]
        next_type = None
        
        for t in type_order:
            if t not in analyzed_types:
                next_type = t
                break
        
        # Build response message
        if next_type:
            # There are more types to analyze
            return json.dumps({
                "status": "type_complete",
                "session_id": session_id,
                "analyzed_type": type_names.get(selected_type, selected_type),
                "analyzed_count": len(analyzed_types),
                "total_types": 4,
                "next_type": next_type,
                "next_type_name": type_names[next_type],
                "md_file": session["md_filepath"],
                "next_action": "call counterfactual_phase2",
                "message": f"✅ Phase 4 complete ({len(analyzed_types)}/4). Next: {next_type}. Call counterfactual_phase2 with same scenarios"
            }, indent=2, ensure_ascii=False)
        else:
            # All types analyzed - complete
            return json.dumps({
                "status": "all_complete",
                "session_id": session_id,
                "analyzed_types": [type_names.get(t, t) for t in analyzed_types],
                "analyzed_count": len(analyzed_types),
                "md_file": session["md_filepath"],
                "message": f"✅ All 4 types complete! Report: {session['md_filepath']}"
            }, indent=2, ensure_ascii=False)
    
    def _format_list(self, items: list) -> str:
        """Format list items with bullet points"""
        if not items:
            return "  (None specified)"
        return "\n".join([f"  • {item}" for item in items])


class CounterfactualGetResultTool(ReasoningTool):
    """Get complete counterfactual reasoning analysis results"""
    
    def __init__(self):
        super().__init__(
            name="counterfactual_get_result",
            description="Retrieve complete counterfactual reasoning analysis results"
        )
    
    async def execute(
        self,
        session_id: str,
        ctx: Optional[Context] = None
    ) -> str:
        """Get complete results including all analyzed scenario types"""
        
        if session_id not in counterfactual_sessions:
            return json.dumps({"error": "Session not found."}, ensure_ascii=False)
        
        session = counterfactual_sessions[session_id]
        
        # Prepare Phase 4 results (support both old and new format)
        phase4_data = session.get("phase4_results", {})
        if not phase4_data and session.get("phase4_result"):
            # Old format - single result
            phase4_data = {"legacy": session.get("phase4_result")}
        
        result = {
            "session_id": session_id,
            "status": session["phase"],
            "problem": session["problem"],
            "phase1_actual_state": session.get("phase1_result"),
            "phase2_scenarios": session.get("phase2_scenarios"),
            "phase3_reasoning": session.get("phase3_result"),
            "phase4_comparative_analyses": phase4_data,
            "analyzed_types": session.get("analyzed_types", []),
            "total_types_analyzed": len(session.get("analyzed_types", [])),
            "duration_seconds": round(session.get("completed_at", time.time()) - session["created_at"], 2) if session.get("completed_at") else None,
            "history": session["history"]
        }
        
        await self.log_execution(ctx, f"Retrieved results for session {session_id}")
        
        return json.dumps(result, indent=2, ensure_ascii=False)


class CounterfactualResetTool(ReasoningTool):
    """Reset or delete a counterfactual reasoning session"""
    
    def __init__(self):
        super().__init__(
            name="counterfactual_reset",
            description="Reset or delete a counterfactual reasoning session"
        )
    
    async def execute(
        self,
        session_id: str,
        ctx: Optional[Context] = None
    ) -> str:
        """Reset session"""
        
        if session_id not in counterfactual_sessions:
            return json.dumps({"error": "Session not found."}, ensure_ascii=False)
        
        del counterfactual_sessions[session_id]
        
        await self.log_execution(ctx, f"Reset session {session_id}")
        
        return json.dumps({
            "status": "session_deleted",
            "session_id": session_id,
            "message": "Session deleted successfully."
        }, ensure_ascii=False)


class CounterfactualListSessionsTool(ReasoningTool):
    """List all active counterfactual reasoning sessions"""
    
    def __init__(self):
        super().__init__(
            name="counterfactual_list_sessions",
            description="List all active counterfactual reasoning sessions"
        )
    
    async def execute(
        self,
        ctx: Optional[Context] = None
    ) -> str:
        """List sessions"""
        
        if not counterfactual_sessions:
            return json.dumps({
                "total_sessions": 0,
                "sessions": [],
                "message": "No active sessions."
            }, ensure_ascii=False)
        
        sessions_list = []
        for session_id, session in counterfactual_sessions.items():
            sessions_list.append({
                "session_id": session_id,
                "problem": session["problem"][:50] + "..." if len(session["problem"]) > 50 else session["problem"],
                "phase": session["phase"],
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(session["created_at"]))
            })
        
        return json.dumps({
            "total_sessions": len(sessions_list),
            "sessions": sessions_list
        }, indent=2, ensure_ascii=False)

