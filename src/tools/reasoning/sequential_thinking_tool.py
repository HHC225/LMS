"""
Sequential Thinking Tool Implementation
Structured analytical thinking tool for software development problem-solving
"""
from typing import Dict, Any, Optional, List
from fastmcp import Context
from datetime import datetime
import json
import time
import random
import string
from ..base import ReasoningTool


# Shared session store for Sequential Thinking
st_sessions: Dict[str, Dict[str, Any]] = {}


class SequentialThinkingTool(ReasoningTool):
    """Sequential Thinking Tool for structured analytical thinking"""
    
    def __init__(self):
        super().__init__(
            name="sequential_thinking",
            description="Sequential analytical thinking tool for software development problem-solving"
        )
    
    def _generate_session_id(self) -> str:
        """Generate session ID"""
        timestamp = str(int(time.time()))
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        return f"st_session_{timestamp}_{random_suffix}"
    
    def _get_or_create_default_session(self) -> str:
        """Get or create default session"""
        default_session_id = 'st_default_session'
        if default_session_id not in st_sessions:
            st_sessions[default_session_id] = {
                'id': default_session_id,
                'input': 'Direct sequential thinking usage',
                'thought_history': [],
                'branches': {},
                'status': 'active',
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
        return default_session_id
    
    def _validate_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data"""
        if not data.get('thought') or not isinstance(data['thought'], str):
            raise ValueError('Invalid thought: must be a string')
        
        if not isinstance(data.get('thoughtNumber'), int):
            raise ValueError('Invalid thoughtNumber: must be a number')
        
        if not isinstance(data.get('totalThoughts'), int):
            raise ValueError('Invalid totalThoughts: must be a number')
        
        if not isinstance(data.get('nextThoughtNeeded'), bool):
            raise ValueError('Invalid nextThoughtNeeded: must be a boolean')
        
        return {
            'thought': data['thought'],
            'thoughtNumber': data['thoughtNumber'],
            'totalThoughts': data['totalThoughts'],
            'nextThoughtNeeded': data['nextThoughtNeeded'],
            'isRevision': data.get('isRevision'),
            'revisesThought': data.get('revisesThought'),
            'branchFromThought': data.get('branchFromThought'),
            'branchId': data.get('branchId'),
            'needsMoreThoughts': data.get('needsMoreThoughts'),
            'actionRequired': data.get('actionRequired'),
            'actionType': data.get('actionType'),
            'actionDescription': data.get('actionDescription'),
        }
    
    def _format_thought_log(self, thought_data: Dict[str, Any]) -> str:
        """Format thought for display"""
        thought_number = thought_data['thoughtNumber']
        total_thoughts = thought_data['totalThoughts']
        thought = thought_data['thought']
        is_revision = thought_data.get('isRevision', False)
        revises_thought = thought_data.get('revisesThought')
        branch_from_thought = thought_data.get('branchFromThought')
        branch_id = thought_data.get('branchId')
        
        prefix = ''
        context = ''
        
        if is_revision:
            prefix = '🔄 Revision'
            context = f' (revising thought {revises_thought})'
        elif branch_from_thought:
            prefix = '🌿 Branch'
            context = f' (from thought {branch_from_thought}, ID: {branch_id})'
        else:
            prefix = '💭 Thought'
            context = ''
        
        header = f"{prefix} {thought_number}/{total_thoughts}{context}"
        
        return f"\n{header}\n{thought}\n"
    
    async def execute(
        self,
        thought: str,
        thought_number: int,
        total_thoughts: int,
        next_thought_needed: bool,
        is_revision: Optional[bool] = None,
        revises_thought: Optional[int] = None,
        branch_from_thought: Optional[int] = None,
        branch_id: Optional[str] = None,
        needs_more_thoughts: Optional[bool] = None,
        action_required: Optional[bool] = None,
        action_type: Optional[str] = None,
        action_description: Optional[str] = None,
        ctx: Optional[Context] = None
    ) -> str:
        """Execute sequential thinking process"""
        
        try:
            # Construct input data
            data = {
                'thought': thought,
                'thoughtNumber': thought_number,
                'totalThoughts': total_thoughts,
                'nextThoughtNeeded': next_thought_needed,
                'isRevision': is_revision,
                'revisesThought': revises_thought,
                'branchFromThought': branch_from_thought,
                'branchId': branch_id,
                'needsMoreThoughts': needs_more_thoughts,
                'actionRequired': action_required,
                'actionType': action_type,
                'actionDescription': action_description,
            }
            
            # Validate input data
            validated_input = self._validate_input(data)
            
            # Get or create session
            session_id = self._get_or_create_default_session()
            session = st_sessions[session_id]
            
            # Auto-adjust totalThoughts if needed
            if validated_input['thoughtNumber'] > validated_input['totalThoughts']:
                validated_input['totalThoughts'] = validated_input['thoughtNumber']
            
            # Add to history
            session['thought_history'].append(validated_input)
            
            # Handle branching
            if validated_input.get('branchFromThought') and validated_input.get('branchId'):
                branch_id = validated_input['branchId']
                if branch_id not in session['branches']:
                    session['branches'][branch_id] = []
                session['branches'][branch_id].append(validated_input)
            
            # Update session
            session['last_updated'] = datetime.now().isoformat()
            
            # Log thought output
            log_message = self._format_thought_log(validated_input)
            print(log_message, flush=True)
            
            # Log execution
            await self.log_execution(
                ctx,
                f"Sequential Thinking - Thought {validated_input['thoughtNumber']}/{validated_input['totalThoughts']}"
            )
            
            # Construct result
            result = {
                'thoughtNumber': validated_input['thoughtNumber'],
                'totalThoughts': validated_input['totalThoughts'],
                'nextThoughtNeeded': validated_input['nextThoughtNeeded'],
                'branches': list(session['branches'].keys()),
                'thoughtHistoryLength': len(session['thought_history']),
                'sessionId': session['id'],
                'thought': validated_input['thought']
            }
            
            # Add action-related information
            if validated_input.get('actionRequired'):
                result['actionRequired'] = validated_input['actionRequired']
                result['actionType'] = validated_input.get('actionType')
                result['actionDescription'] = validated_input.get('actionDescription')
            
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        except Exception as e:
            error_result = {
                'error': str(e),
                'status': 'failed'
            }
            return json.dumps(error_result, indent=2, ensure_ascii=False)
