"""
Planning Tool Implementation
Progressive Work Breakdown Structure (WBS) Creation with Multi-Action Architecture

Following Vibe tool pattern for better LLM compatibility
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import time
import random
import string
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
from ..base import ReasoningTool


# ===== DATA STRUCTURES =====

class Priority(Enum):
    """Task priority levels"""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class SessionStatus(Enum):
    """Planning session status"""
    ACTIVE = "active"
    COMPLETED = "completed"


@dataclass
class WBSItem:
    """WBS item data structure"""
    id: str
    title: str
    description: str
    level: int
    priority: str
    dependencies: List[str] = field(default_factory=list)
    order: int = 0
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PlanningStep:
    """Planning step record"""
    step_number: int
    planning_analysis: str
    timestamp: str
    wbs_items_added: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PlanningSession:
    """Planning session data"""
    id: str
    problem_statement: str
    project_name: str
    status: str
    created_at: str
    last_updated: str
    wbs_items: List[WBSItem] = field(default_factory=list)
    planning_history: List[PlanningStep] = field(default_factory=list)
    current_step: int = 0
    output_path: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['wbs_items'] = [item.to_dict() for item in self.wbs_items]
        result['planning_history'] = [step.to_dict() for step in self.planning_history]
        return result


planning_sessions: Dict[str, PlanningSession] = {}


# ===== VALIDATION =====

class PlanningValidator:
    """Validation utilities"""
    
    @staticmethod
    def validate_wbs_items(items: List[Dict[str, Any]], existing_items: List[WBSItem]) -> Dict[str, Any]:
        errors = []
        warnings = []
        
        if not items:
            return {'valid': True, 'warnings': ['No WBS items provided']}
        
        existing_ids = {item.id for item in existing_items}
        new_ids = set()
        
        for idx, item in enumerate(items):
            if not item.get('id'):
                errors.append(f"Item {idx}: 'id' is required")
                continue
            
            if not item.get('title'):
                errors.append(f"Item {item['id']}: 'title' is required")
            
            if not isinstance(item.get('level'), int) or item['level'] < 0:
                errors.append(f"Item {item['id']}: 'level' must be non-negative integer")
            
            if item.get('level', 0) > 0 and not item.get('parent_id'):
                errors.append(f"Item {item['id']}: 'parent_id' required for level > 0")
            
            if item.get('priority') not in ['High', 'Medium', 'Low']:
                errors.append(f"Item {item['id']}: priority must be High/Medium/Low")
            
            if item['id'] in existing_ids or item['id'] in new_ids:
                warnings.append(f"Item {item['id']}: Duplicate ID")
            else:
                new_ids.add(item['id'])
        
        return {'valid': len(errors) == 0, 'errors': errors, 'warnings': warnings}


# ===== MARKDOWN GENERATOR =====

class WBSMarkdownGenerator:
    """Generate WBS markdown files"""
    
    def __init__(self, session: PlanningSession):
        self.session = session
        self._id_to_item = {item.id: item for item in session.wbs_items}
    
    def generate(self) -> str:
        sections = []
        sections.append(f"# Project: {self.session.project_name}")
        sections.append("")
        sections.append("## Problem Statement")
        sections.append(self.session.problem_statement)
        sections.append("")
        sections.append("## Work Breakdown Structure")
        sections.append("")
        sections.append(self._generate_wbs_tree())
        sections.append("")
        sections.append(self._generate_summary())
        return '\n'.join(sections)
    
    def _generate_wbs_tree(self) -> str:
        if not self.session.wbs_items:
            return "*No WBS items yet*"
        
        lines = []
        root_items = [item for item in self.session.wbs_items if item.level == 0]
        root_items.sort(key=lambda x: x.order)
        
        for root in root_items:
            lines.extend(self._generate_item_lines(root, 0))
        
        return '\n'.join(lines)
    
    def _generate_item_lines(self, item: WBSItem, indent_level: int) -> List[str]:
        lines = []
        indent = '  ' * indent_level
        
        lines.append(f"{indent}- [ ] **{item.title}** (Priority: {item.priority})")
        lines.append(f"{indent}  - ID: {item.id}")
        lines.append(f"{indent}  - Description: {item.description}")
        if item.dependencies:
            lines.append(f"{indent}  - Dependencies: {', '.join(item.dependencies)}")
        lines.append("")
        
        children = [self._id_to_item[cid] for cid in item.children if cid in self._id_to_item]
        children.sort(key=lambda x: x.order)
        
        for child in children:
            lines.extend(self._generate_item_lines(child, indent_level + 1))
        
        return lines
    
    def _generate_summary(self) -> str:
        lines = []
        lines.append("## Planning Summary")
        lines.append("")
        lines.append(f"- **Steps**: {len(self.session.planning_history)}")
        lines.append(f"- **WBS Items**: {len(self.session.wbs_items)}")
        lines.append(f"- **Status**: {self.session.status}")
        return '\n'.join(lines)


# ===== SESSION MANAGER =====

class PlanningSessionManager:
    """Manage planning sessions"""
    
    @staticmethod
    def create_session(problem_statement: str, project_name: Optional[str] = None) -> PlanningSession:
        timestamp = str(int(time.time()))
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        session_id = f"planning_{timestamp}_{random_suffix}"
        
        if not project_name:
            words = problem_statement.split()[:5]
            project_name = ' '.join(words)
        
        session = PlanningSession(
            id=session_id,
            problem_statement=problem_statement,
            project_name=project_name,
            status=SessionStatus.ACTIVE.value,
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat()
        )
        
        planning_sessions[session_id] = session
        return session
    
    @staticmethod
    def get_session(session_id: str) -> Optional[PlanningSession]:
        return planning_sessions.get(session_id)
    
    @staticmethod
    def update_session(session: PlanningSession) -> None:
        session.last_updated = datetime.now().isoformat()
        planning_sessions[session.id] = session
    
    @staticmethod
    def add_wbs_items(session: PlanningSession, new_items: List[Dict[str, Any]]) -> int:
        added_count = 0
        existing_ids = {item.id for item in session.wbs_items}
        
        for item_data in new_items:
            if item_data['id'] not in existing_ids:
                wbs_item = WBSItem(
                    id=item_data['id'],
                    title=item_data['title'],
                    description=item_data.get('description', ''),
                    level=item_data['level'],
                    priority=item_data.get('priority', 'Medium'),
                    dependencies=item_data.get('dependencies', []),
                    order=item_data.get('order', 0),
                    parent_id=item_data.get('parent_id'),
                    children=item_data.get('children', [])
                )
                session.wbs_items.append(wbs_item)
                added_count += 1
        
        PlanningSessionManager._rebuild_hierarchy(session)
        return added_count
    
    @staticmethod
    def _rebuild_hierarchy(session: PlanningSession) -> None:
        id_to_item = {item.id: item for item in session.wbs_items}
        
        for item in session.wbs_items:
            item.children = []
        
        for item in session.wbs_items:
            if item.parent_id and item.parent_id in id_to_item:
                parent = id_to_item[item.parent_id]
                if item.id not in parent.children:
                    parent.children.append(item.id)
    
    @staticmethod
    def add_planning_step(session: PlanningSession, step: PlanningStep) -> None:
        session.planning_history.append(step)
        session.current_step = step.step_number


# ===== MAIN TOOL =====

class PlanningTool(ReasoningTool):
    """Planning Tool with Multi-Action Architecture"""
    
    def __init__(self, default_output_dir: Optional[Path] = None):
        super().__init__(
            name="planning",
            description="Progressive WBS Creation Tool"
        )
        self.default_output_dir = default_output_dir or Path("./output/planning")
    
    async def execute(self, action: str, ctx: Any = None, **kwargs) -> str:
        """Route to appropriate action method"""
        actions = {
            'initialize': self.action_initialize,
            'add_step': self.action_add_step,
            'finalize': self.action_finalize,
            'status': self.action_status,
            'list': self.action_list
        }
        
        action_method = actions.get(action)
        if not action_method:
            return json.dumps({
                'success': False,
                'error': f'Unknown action: {action}'
            }, ensure_ascii=False)
        
        return await action_method(ctx=ctx, **kwargs)
    
    async def action_initialize(
        self,
        problem_statement: str,
        project_name: Optional[str] = None,
        ctx: Any = None
    ) -> str:
        """Initialize new planning session"""
        if not problem_statement:
            return json.dumps({'success': False, 'error': 'problem_statement required'}, ensure_ascii=False)
        
        session = PlanningSessionManager.create_session(problem_statement, project_name)
        
        self.default_output_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.default_output_dir / f"{session.project_name.replace(' ', '_')}_WBS.md"
        
        generator = WBSMarkdownGenerator(session)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(generator.generate())
        
        session.output_path = str(file_path)
        PlanningSessionManager.update_session(session)
        
        return json.dumps({
            'success': True,
            'sessionId': session.id,
            'projectName': session.project_name,
            'outputPath': str(file_path),
            'message': f'Session initialized. WBS file created at: {file_path}',
            'nextAction': 'add_step'
        }, indent=2, ensure_ascii=False)
    
    async def action_add_step(
        self,
        session_id: str,
        step_number: int,
        planning_analysis: str,
        wbs_items: Optional[List[Dict[str, Any]]] = None,
        ctx: Any = None
    ) -> str:
        """Add planning step and update WBS"""
        session = PlanningSessionManager.get_session(session_id)
        if not session:
            return json.dumps({'success': False, 'error': f'Session {session_id} not found'}, ensure_ascii=False)
        
        step_record = PlanningStep(
            step_number=step_number,
            planning_analysis=planning_analysis,
            timestamp=datetime.now().isoformat(),
            wbs_items_added=0
        )
        
        if wbs_items:
            validation = PlanningValidator.validate_wbs_items(wbs_items, session.wbs_items)
            if not validation['valid']:
                return json.dumps({
                    'success': False,
                    'error': 'Validation failed',
                    'details': validation['errors']
                }, ensure_ascii=False)
            
            added_count = PlanningSessionManager.add_wbs_items(session, wbs_items)
            step_record.wbs_items_added = added_count
        
        PlanningSessionManager.add_planning_step(session, step_record)
        
        generator = WBSMarkdownGenerator(session)
        with open(Path(session.output_path), 'w', encoding='utf-8') as f:
            f.write(generator.generate())
        
        PlanningSessionManager.update_session(session)
        
        return json.dumps({
            'success': True,
            'sessionId': session.id,
            'stepNumber': step_number,
            'wbsItemsAdded': step_record.wbs_items_added,
            'totalWbsItems': len(session.wbs_items),
            'wbsFileUpdated': True,
            'message': f'Step {step_number} completed. WBS file updated.',
            'nextAction': 'add_step_or_finalize'
        }, indent=2, ensure_ascii=False)
    
    async def action_finalize(
        self,
        session_id: str,
        ctx: Any = None
    ) -> str:
        """Finalize planning session"""
        session = PlanningSessionManager.get_session(session_id)
        if not session:
            return json.dumps({'success': False, 'error': f'Session {session_id} not found'}, ensure_ascii=False)
        
        session.status = SessionStatus.COMPLETED.value
        
        generator = WBSMarkdownGenerator(session)
        with open(Path(session.output_path), 'w', encoding='utf-8') as f:
            f.write(generator.generate())
        
        PlanningSessionManager.update_session(session)
        
        return json.dumps({
            'success': True,
            'sessionId': session.id,
            'status': session.status,
            'totalSteps': len(session.planning_history),
            'totalWbsItems': len(session.wbs_items),
            'outputPath': session.output_path,
            'message': f'Planning completed! {len(session.wbs_items)} WBS items generated.'
        }, indent=2, ensure_ascii=False)
    
    async def action_status(
        self,
        session_id: str,
        ctx: Any = None
    ) -> str:
        """Get session status"""
        session = PlanningSessionManager.get_session(session_id)
        if not session:
            return json.dumps({'success': False, 'error': f'Session {session_id} not found'}, ensure_ascii=False)
        
        return json.dumps({
            'success': True,
            'sessionId': session.id,
            'status': session.status,
            'projectName': session.project_name,
            'currentStep': session.current_step,
            'totalSteps': len(session.planning_history),
            'totalWbsItems': len(session.wbs_items),
            'outputPath': session.output_path
        }, indent=2, ensure_ascii=False)
    
    async def action_list(
        self,
        ctx: Any = None
    ) -> str:
        """List all sessions"""
        sessions_summary = [
            {
                'sessionId': s.id,
                'projectName': s.project_name,
                'status': s.status,
                'totalSteps': len(s.planning_history),
                'totalWbsItems': len(s.wbs_items),
                'lastUpdated': s.last_updated
            }
            for s in planning_sessions.values()
        ]
        
        sessions_summary.sort(key=lambda x: x['lastUpdated'], reverse=True)
        
        return json.dumps({
            'success': True,
            'totalSessions': len(sessions_summary),
            'sessions': sessions_summary
        }, indent=2, ensure_ascii=False)
