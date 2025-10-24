"""
Recursive Thinking Model Tools Implementation
Recursive reasoning tools for iterative answer improvement
"""
from typing import Dict, Any, Optional
from fastmcp import Context
import json
import uuid
import time
from ..base import ReasoningTool


# Shared session store for Recursive Thinking
reasoning_sessions: Dict[str, Dict[str, Any]] = {}


class Rcursive_ThinkingInitializeTool(ReasoningTool):
    """Initialize a new Recursive Thinking reasoning session"""
    
    def __init__(self):
        super().__init__(
            name="initialize_reasoning",
            description="Initialize a new recursive reasoning session with Recursive Thinking Model"
        )
    
    async def execute(
        self,
        question: str,
        initial_answer: str = "",
        n_latent_updates: int = 4,
        max_improvements: int = 16,
        ctx: Optional[Context] = None
    ) -> str:
        """Initialize Recursive Thinking reasoning session"""
        
        # Auto-generate unique session ID
        timestamp = str(int(time.time()))
        random_suffix = str(uuid.uuid4())[:8]
        session_id = f"session_{timestamp}_{random_suffix}"
        
        reasoning_sessions[session_id] = {
            "question": question,
            "current_answer": initial_answer,
            "latent_state": "initialized",
            "n_latent_updates": n_latent_updates,
            "max_improvements": max_improvements,
            "improvement_count": 0,
            "history": []
        }
        
        await self.log_execution(ctx, f"Initialized session {session_id}")
        
        return json.dumps({
            "status": "initialized",
            "session_id": session_id,
            "question": question,
            "initial_answer": initial_answer,
            "config": {
                "n_latent_updates": n_latent_updates,
                "max_improvements": max_improvements
            },
            "next_step": "Call update_latent_reasoning to begin recursive reasoning",
            "reasoning_workflow": "Follow 4-step systematic analysis: 1) Problem decomposition, 2) Current answer analysis, 3) Alternative perspectives, 4) Improvement synthesis. Final verification loop before answer submission."
        }, indent=2, ensure_ascii=False)


class Rcursive_ThinkingUpdateLatentTool(ReasoningTool):
    """Update latent reasoning state"""
    
    def __init__(self):
        super().__init__(
            name="update_latent_reasoning",
            description="Update the latent reasoning state based on question, current answer, and previous latent"
        )
    
    async def execute(
        self,
        session_id: str,
        reasoning_insight: str,
        step_number: int,
        ctx: Optional[Context] = None
    ) -> str:
        """Update latent reasoning state"""
        
        if session_id not in reasoning_sessions:
            return json.dumps({"error": "Session not found. Call initialize_reasoning first."}, ensure_ascii=False)
        
        session = reasoning_sessions[session_id]
        
        # Check if in verification mode
        verification_status = session.get("verification_mode", False)
        is_verification_mode = verification_status in ["in_progress", True]
        
        # Update latent state with new reasoning
        previous_latent = session["latent_state"]
        session["latent_state"] = reasoning_insight
        
        if is_verification_mode:
            session["history"].append({
                "type": "verification_reasoning",
                "step": step_number,
                "verification_iteration": session["improvement_count"],
                "reasoning": reasoning_insight
            })
        else:
            session["history"].append({
                "type": "latent_update",
                "step": step_number,
                "improvement_iteration": session["improvement_count"],
                "reasoning": reasoning_insight
            })
        
        n_updates = session["n_latent_updates"]
        
        await self.log_execution(
            ctx, 
            f"Updated latent reasoning step {step_number}/{n_updates} {'(verification)' if is_verification_mode else ''}"
        )
        
        if step_number < n_updates:
            next_step_guidance = {
                1: "Step 2: Analyze current answer - identify specific strengths and weaknesses",
                2: "Step 3: Explore alternative perspectives and apply domain-specific reasoning", 
                3: "Step 4: Synthesize insights and develop concrete improvement strategy"
            }
            step_guidance = next_step_guidance.get(step_number, f"Continue systematic analysis (step {step_number + 1})")
            
            return json.dumps({
                "status": "verification_reasoning_updated" if is_verification_mode else "latent_updated",
                "session_id": session_id,
                "step": f"{step_number}/{n_updates}",
                "mode": "VERIFICATION" if is_verification_mode else "IMPROVEMENT",
                "previous_latent": previous_latent,
                "current_latent": reasoning_insight,
                "next_step": f"Continue with update_latent_reasoning (step {step_number + 1})",
                "step_guidance": step_guidance
            }, indent=2, ensure_ascii=False)
        else:
            if is_verification_mode:
                # Mark verification reasoning as completed (but not final)
                session["verification_mode"] = "reasoning_complete"
                return json.dumps({
                    "status": "verification_reasoning_complete",
                    "session_id": session_id,
                    "step": f"{step_number}/{n_updates}",
                    "mode": "VERIFICATION",
                    "final_verification_reasoning": reasoning_insight,
                    "candidate_answer": session["verification_candidate_answer"],
                    "next_step": "CRITICAL: Call update_answer to finalize the verified answer based on verification insights",
                    "verification_complete": "All 4 systematic reasoning steps completed for verification - now apply insights to finalize answer"
                }, indent=2, ensure_ascii=False)
            else:
                return json.dumps({
                    "status": "latent_reasoning_complete",
                    "session_id": session_id,
                    "step": f"{step_number}/{n_updates}",
                    "final_latent": reasoning_insight,
                    "next_step": "Call update_answer to improve the answer based on systematic analysis",
                    "improvement_guidance": "Apply concrete insights from all 4 reasoning steps to enhance the answer"
                }, indent=2, ensure_ascii=False)


class Rcursive_ThinkingUpdateAnswerTool(ReasoningTool):
    """Update the answer based on latent reasoning"""
    
    def __init__(self):
        super().__init__(
            name="update_answer",
            description="Update the answer based on current answer and refined latent reasoning"
        )
    
    async def execute(
        self,
        session_id: str,
        improved_answer: str,
        improvement_rationale: str,
        ctx: Optional[Context] = None
    ) -> str:
        """Update answer based on latent reasoning"""
        
        if session_id not in reasoning_sessions:
            return json.dumps({"error": "Session not found. Call initialize_reasoning first."}, ensure_ascii=False)
        
        session = reasoning_sessions[session_id]
        
        # Check if this is a verification finalization
        verification_status = session.get("verification_mode", False)
        is_verification_finalization = verification_status == "reasoning_complete"
        
        previous_answer = session["current_answer"]
        session["current_answer"] = improved_answer
        
        # Only increment improvement count if not in verification finalization
        if not is_verification_finalization:
            session["improvement_count"] += 1
        
        session["history"].append({
            "type": "verification_finalized" if is_verification_finalization else "answer_update",
            "improvement_iteration": session["improvement_count"],
            "previous_answer": previous_answer,
            "improved_answer": improved_answer,
            "rationale": improvement_rationale
        })
        
        # If this is verification finalization, mark as completed
        if is_verification_finalization:
            session["verification_mode"] = "completed"
            session["latent_state"] = "verification_finalized"
            
            await self.log_execution(ctx, f"Verification finalized - answer updated based on verification insights")
            
            return json.dumps({
                "status": "verification_finalized",
                "session_id": session_id,
                "verification_mode": "COMPLETED",
                "previous_answer": previous_answer,
                "verified_answer": improved_answer,
                "improvement_rationale": improvement_rationale,
                "next_step": "Call get_final_result to retrieve the final verified answer and complete reasoning history",
                "message": "Verification complete! Answer has been finalized based on verification insights."
            }, indent=2, ensure_ascii=False)
        
        # Reset latent for next iteration
        session["latent_state"] = "reset_for_next_iteration"
        
        max_improvements = session["max_improvements"]
        current_count = session["improvement_count"]
        
        await self.log_execution(ctx, f"Updated answer - iteration {current_count}/{max_improvements}")
        
        if current_count >= max_improvements:
            return json.dumps({
                "status": "max_iterations_reached",
                "session_id": session_id,
                "iterations_completed": current_count,
                "candidate_final_answer": improved_answer,
                "next_step": "Call get_final_result to check verification status and retrieve answer",
                "warning": "Maximum iterations reached. Check verification status via get_final_result."
            }, indent=2, ensure_ascii=False)
        else:
            return json.dumps({
                "status": "answer_updated",
                "session_id": session_id,
                "iteration": f"{current_count}/{max_improvements}",
                "previous_answer": previous_answer,
                "improved_answer": improved_answer,
                "improvement_rationale": improvement_rationale,
                "confidence_check": "Are you 100% confident in this answer?",
                "next_step": (
                    "CRITICAL: If you have ANY uncertainty or doubt (even 1%), you MUST continue with update_latent_reasoning (step 1). "
                    "If you are confident and ready to submit, call get_final_result to check verification status and proceed accordingly."
                )
            }, indent=2, ensure_ascii=False)


class Rcursive_ThinkingGetResultTool(ReasoningTool):
    """Retrieve final result"""
    
    def __init__(self):
        super().__init__(
            name="get_final_result",
            description="Retrieve the final answer and complete reasoning history"
        )
    
    async def execute(
        self,
        session_id: str,
        ctx: Optional[Context] = None
    ) -> str:
        """Retrieve final result"""
        
        if session_id not in reasoning_sessions:
            return json.dumps({"error": "Session not found."}, ensure_ascii=False)
        
        session = reasoning_sessions[session_id]
        
        # Check if verification was completed
        verification_status = session.get("verification_mode", False)
        verification_completed = verification_status == "completed"
        
        # If verification not completed, start verification process
        if not verification_completed:
            # Set verification mode
            session["verification_mode"] = "in_progress"
            session["verification_candidate_answer"] = session["current_answer"]
            
            # Add verification initiation to history
            session["history"].append({
                "type": "auto_verification_initiated",
                "improvement_iteration": session["improvement_count"],
                "candidate_answer": session["current_answer"]
            })
            
            # Reset latent state for verification reasoning
            session["latent_state"] = "verification_mode_initialized"
            
            await self.log_execution(ctx, f"Auto-started verification for session {session_id}")
            
            return json.dumps({
                "status": "verification_started",
                "session_id": session_id,
                "verification_mode": "ACTIVE",
                "candidate_answer": session["current_answer"],
                "next_step": "MANDATORY: Start verification with update_latent_reasoning (step 1)",
                "verification_instructions": {
                    "step_1": "Problem decomposition and classification",
                    "step_2": "Current answer analysis (strengths/weaknesses)", 
                    "step_3": "Alternative perspectives and deep domain reasoning",
                    "step_4": "Synthesis and concrete improvement strategy"
                },
                "workflow": "After 4 verification steps, call update_answer to finalize, then call get_final_result again to retrieve final answer"
            }, indent=2, ensure_ascii=False)
        
        # Clean up verification mode flag
        if "verification_mode" in session:
            del session["verification_mode"]
        if "verification_candidate_answer" in session:
            del session["verification_candidate_answer"]
        
        await self.log_execution(ctx, f"Retrieved final result for session {session_id}")
        
        return json.dumps({
            "session_id": session_id,
            "question": session["question"],
            "final_answer": session["current_answer"],
            "total_improvements": session["improvement_count"],
            "max_improvements": session["max_improvements"],
            "n_latent_updates_per_iteration": session["n_latent_updates"],
            "verification_completed": True,
            "reasoning_history": session["history"],
            "status": "complete"
        }, indent=2, ensure_ascii=False)


class Rcursive_ThinkingResetTool(ReasoningTool):
    """Reset or delete a reasoning session"""
    
    def __init__(self):
        super().__init__(
            name="reset_session",
            description="Reset or delete a reasoning session"
        )
    
    async def execute(
        self,
        session_id: str,
        ctx: Optional[Context] = None
    ) -> str:
        """Reset session"""
        
        if session_id in reasoning_sessions:
            del reasoning_sessions[session_id]
            await self.log_execution(ctx, f"Reset session {session_id}")
            return json.dumps({"status": "reset", "session_id": session_id}, ensure_ascii=False)
        else:
            return json.dumps({"error": "Session not found."}, ensure_ascii=False)

