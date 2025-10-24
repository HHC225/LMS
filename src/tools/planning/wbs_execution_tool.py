"""
WBS Execution Tool Implementation
Systematic task-by-task execution tool for WBS-based project implementation
"""
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from functools import cmp_to_key
import json
import re
import os
from pathlib import Path
from ..base import ReasoningTool


# Shared session store for WBS Execution
wbs_execution_sessions: Dict[str, Dict[str, Any]] = {}


class WBSExecutionTool(ReasoningTool):
    """WBS Execution Tool for step-by-step task implementation"""
    
    def __init__(self, default_output_dir: Optional[Path] = None):
        super().__init__(
            name="wbs_execution",
            description="WBS (Work Breakdown Structure) Execution Tool for step-by-step task implementation"
        )
        self.default_output_dir = default_output_dir or Path("./output/planning")
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"wbs_exec_{timestamp}"
    
    # ===== FILE PARSING METHODS =====
    
    def _parse_wbs_file(self, file_path: str) -> Tuple[List[Dict[str, Any]], str, str]:
        """
        Parse WBS markdown file and extract tasks
        
        Returns:
            Tuple of (tasks, project_name, problem_statement)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"WBS file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self._parse_wbs_content(content)
    
    def _parse_wbs_content(self, content: str) -> Tuple[List[Dict[str, Any]], str, str]:
        """Parse WBS content from string"""
        lines = content.split('\n')
        tasks = []
        project_name = 'Unknown Project'
        problem_statement = ''
        line_number = 0
        
        # First pass: extract basic info and tasks
        for line in lines:
            line_number += 1
            
            # Extract project name
            if line.startswith('# Project:'):
                project_name = line.replace('# Project:', '').strip()
                continue
            
            # Extract problem statement
            if line.startswith('## Problem Statement'):
                # Find the next line with content
                next_line_index = line_number
                while next_line_index < len(lines):
                    next_line = lines[next_line_index].strip()
                    if next_line and not next_line.startswith('#'):
                        problem_statement = next_line
                        break
                    next_line_index += 1
                continue
            
            # Parse task lines
            if self._is_task_line(line):
                task = self._parse_task_line(line, line_number)
                if task:
                    tasks.append(task)
        
        # Second pass: build hierarchy and extract descriptions
        self._build_task_hierarchy(tasks)
        self._extract_task_descriptions(content, tasks)
        
        return tasks, project_name, problem_statement
    
    def _is_task_line(self, line: str) -> bool:
        """Check if a line contains a task"""
        return bool(re.match(r'^\s*- \[([ x])\]\s*\*\*.*\*\*', line))
    
    def _parse_task_line(self, line: str, line_number: int) -> Optional[Dict[str, Any]]:
        """Parse individual task line"""
        task_regex = r'^(\s*)- \[([ x])\]\s*\*\*(.*?)\*\*\s*\(Priority:\s*(High|Medium|Low)\)'
        match = re.match(task_regex, line)
        
        if not match:
            return None
        
        indent, completed, title, priority = match.groups()
        level = len(indent) // 2  # 2 spaces per level
        is_completed = completed == 'x'
        
        # Generate temporary task ID, will be updated during description extraction
        task_id = self._generate_task_id(title, level, line_number)
        
        task = {
            'id': task_id,
            'title': title.strip(),
            'description': '',  # Will be extracted later
            'priority': priority,
            'dependencies': [],
            'completed': is_completed,
            'level': level,
            'children': [],
            'lineNumber': line_number
        }
        
        return task
    
    def _build_task_hierarchy(self, tasks: List[Dict[str, Any]]) -> None:
        """Build parent-child relationships between tasks"""
        # Sort tasks by level and ID for proper hierarchy building
        tasks.sort(key=lambda t: (t['level'], self._parse_id_for_sorting(t['id'])))
        
        for task in tasks:
            if task['level'] == 0:
                continue  # Root level tasks have no parent
            
            # Find parent by looking for tasks with level one less and matching ID prefix
            parent_level = task['level'] - 1
            task_id_parts = task['id'].split('.')
            parent_id_parts = task_id_parts[:-1]  # Remove last part
            potential_parent_id = '.'.join(parent_id_parts)
            
            # Find parent task
            parent = None
            for t in tasks:
                if t['level'] == parent_level and (
                    t['id'] == potential_parent_id or 
                    task['id'].startswith(t['id'] + '.')
                ):
                    parent = t
                    break
            
            if parent and task['id'] not in parent['children']:
                parent['children'].append(task['id'])
    
    def _extract_task_descriptions(self, content: str, tasks: List[Dict[str, Any]]) -> None:
        """Extract detailed descriptions for tasks from the content"""
        lines = content.split('\n')
        
        for task in tasks:
            # Find the task line by matching title
            task_line_index = -1
            for i, line in enumerate(lines):
                if task['title'] in line and self._is_task_line(line):
                    task_line_index = i
                    break
            
            if task_line_index == -1:
                continue
            
            description = ''
            
            # Look for description in following lines
            for i in range(task_line_index + 1, len(lines)):
                line = lines[i].strip()
                
                # Stop if we hit another task or section
                if self._is_task_line(lines[i]) or line.startswith('#'):
                    break
                
                # Extract Task ID first (most important for ordering)
                if 'Task ID:' in line:
                    task_id_match = re.search(r'Task ID:\s*([^\s,]+)', line)
                    if task_id_match:
                        # Update task ID with the explicitly specified one
                        task['id'] = task_id_match.group(1)
                
                # Extract description content
                if line.startswith('- Description:'):
                    description = line.replace('- Description:', '').strip()
                elif line.startswith('Description:'):
                    description = line.replace('Description:', '').strip()
                
                # Extract dependencies
                if line.startswith('- Dependencies:') or line.startswith('Dependencies:'):
                    dep_str = re.sub(r'^-?\s*Dependencies:\s*', '', line).strip()
                    if dep_str not in ['None', '']:
                        # Parse dependencies - could be "0.0 (기본 디렉토리 생성)" format
                        deps = []
                        for dep in dep_str.split(','):
                            clean_dep = dep.strip()
                            # Extract just the ID part before any parentheses
                            id_match = re.match(r'^([^\s(]+)', clean_dep)
                            if id_match:
                                dep_id = id_match.group(1)
                                if dep_id not in ['None', '']:
                                    deps.append(dep_id)
                        task['dependencies'] = deps
            
            task['description'] = description
    
    def _generate_task_id(self, title: str, level: int, line_number: int) -> str:
        """Generate unique task ID"""
        clean_title = re.sub(r'[^a-zA-Z0-9]', '_', title).lower()
        return f"{level}_{line_number}_{clean_title}"
    
    def _compare_task_ids(self, id_a: str, id_b: str) -> int:
        """
        Compare task IDs for natural sorting (1 < 1.1 < 1.2 < 2 < 2.1 < 2.2)
        Handles 1-based numbering system
        """
        def parse_id(task_id: str) -> List[int]:
            numeric_part = task_id.split('_')[0] if '_' in task_id else task_id
            return [int(part) if part.isdigit() else 1 for part in numeric_part.split('.')]
        
        parts_a = parse_id(id_a)
        parts_b = parse_id(id_b)
        
        max_length = max(len(parts_a), len(parts_b))
        
        for i in range(max_length):
            part_a = parts_a[i] if i < len(parts_a) else 1
            part_b = parts_b[i] if i < len(parts_b) else 1
            
            if part_a != part_b:
                return part_a - part_b
        
        return 0
    
    def _parse_id_for_sorting(self, task_id: str) -> List[int]:
        """
        Parse task ID for sorting purposes (used as key function)
        Returns a list of integers representing the hierarchical position
        Example: "1.2.3" -> [1, 2, 3], "2" -> [2]
        """
        numeric_part = task_id.split('_')[0] if '_' in task_id else task_id
        return [int(part) if part.isdigit() else 1 for part in numeric_part.split('.')]
    
    # ===== FILE UPDATE METHODS =====
    
    def _update_task_checkbox(self, file_path: str, task: Dict[str, Any], completed: bool) -> None:
        """Update checkbox status in WBS file"""
        try:
            self._update_task_by_title(file_path, task['title'], completed)
        except Exception as e:
            raise Exception(f"Failed to update checkbox for task {task['id']}: {str(e)}")
    
    def _update_task_by_title(self, file_path: str, title: str, completed: bool) -> None:
        """Update task by title (most precise method)"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if self._is_task_line(line) and title in line:
                if completed and '- [ ]' in line:
                    lines[i] = line.replace('- [ ]', '- [x]')
                elif not completed and '- [x]' in line:
                    lines[i] = line.replace('- [x]', '- [ ]')
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                return
        
        raise ValueError(f"Task with title '{title}' not found")
    
    # ===== SESSION MANAGEMENT METHODS =====
    
    def _create_session(self, wbs_file_path: str, tasks: List[Dict[str, Any]], 
                       project_name: str) -> Dict[str, Any]:
        """Create a new execution session"""
        session_id = self._generate_session_id()
        
        # Create session with updated task IDs after description extraction
        session = {
            'sessionId': session_id,
            'wbsFilePath': wbs_file_path,
            'tasks': {task['id']: task for task in tasks},
            'executionHistory': [],
            'completedTasks': [],
            'availableTasks': self._get_executable_task_ids(tasks),
            'createdAt': datetime.now().isoformat(),
            'lastUpdated': datetime.now().isoformat(),
            'projectName': project_name,
            'currentTaskId': None
        }
        
        wbs_execution_sessions[session_id] = session
        return session
    
    def _get_session(self, session_id: str) -> Dict[str, Any]:
        """Get session by ID"""
        if session_id not in wbs_execution_sessions:
            raise ValueError(f"Session not found: {session_id}")
        return wbs_execution_sessions[session_id]
    
    def _update_session(self, session: Dict[str, Any]) -> None:
        """Update session"""
        session['lastUpdated'] = datetime.now().isoformat()
        wbs_execution_sessions[session['sessionId']] = session
    
    def _get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions"""
        return list(wbs_execution_sessions.values())
    
    # ===== TASK MANAGEMENT METHODS =====
    
    def _get_available_tasks(self, session: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get available tasks (leaf tasks, regardless of dependency status)
        Returns tasks sorted by ID for consistent execution order
        """
        tasks = list(session['tasks'].values())
        available = []
        
        for task in tasks:
            if task['completed']:
                continue
            # Exclude parent tasks: level 0 tasks OR tasks with children
            if task['level'] == 0 or len(task['children']) > 0:
                continue
            available.append(task)
        
        # Sort by task ID
        available.sort(key=lambda t: self._parse_id_for_sorting(t['id']))
        return available
    
    def _get_executable_tasks(self, session: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get executable tasks (leaf tasks with all dependencies completed)
        Used during actual execution
        """
        tasks = list(session['tasks'].values())
        executable = []
        
        for task in tasks:
            if task['completed']:
                continue
            if task['level'] == 0 or len(task['children']) > 0:
                continue
            
            # All dependencies must be completed
            dependencies_met = all(
                session['tasks'].get(dep_id, {}).get('completed', False) or 
                dep_id in session['completedTasks']
                for dep_id in task['dependencies']
            )
            
            if dependencies_met:
                executable.append(task)
        
        # Sort by task ID
        executable.sort(key=lambda t: self._parse_id_for_sorting(t['id']))
        return executable
    
    def _get_executable_task_ids(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """
        Get executable task IDs (leaf tasks only, no parent tasks)
        Only used for initial display - does not check dependencies
        """
        executable = []
        
        for task in tasks:
            if task['completed']:
                continue
            executable.append(task['id'])
        
        # Sort by task ID
        executable.sort(key=cmp_to_key(self._compare_task_ids))
        return executable
    
    def _complete_task(self, session: Dict[str, Any], task_id: str, 
                      thinking: str, action_description: str) -> Dict[str, Any]:
        """Complete a task and update session"""
        task = session['tasks'].get(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        if task['completed']:
            raise ValueError(f"Task already completed: {task_id}")
        
        # Check dependencies
        uncompleted_dependencies = [
            dep_id for dep_id in task['dependencies']
            if not session['tasks'].get(dep_id, {}).get('completed', False) and
               dep_id not in session['completedTasks']
        ]
        
        if uncompleted_dependencies:
            raise ValueError(f"Task has uncompleted dependencies: {', '.join(uncompleted_dependencies)}")
        
        # Create execution step
        execution_step = {
            'taskId': task['id'],
            'stepNumber': len(session['executionHistory']) + 1,
            'thinking': thinking or f"Executing task: {task['title']}",
            'actionTaken': action_description or "Task implementation",
            'completed': True,
            'timestamp': datetime.now().isoformat(),
            'implementationDetails': thinking
        }
        
        # Update task and session
        task['completed'] = True
        session['completedTasks'].append(task['id'])
        session['executionHistory'].append(execution_step)
        session['lastUpdated'] = datetime.now().isoformat()
        
        return execution_step
    
    def _check_and_update_parent_tasks(self, session: Dict[str, Any], 
                                       completed_task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check and update parent tasks when all children are completed
        Only marks parent as complete when ALL children are actually completed
        """
        updated_parents = []
        
        # Extract parent ID from task ID (e.g., "1.2" -> "1")
        parent_id = self._get_parent_id(completed_task['id'])
        if not parent_id:
            return updated_parents
        
        parent_task = session['tasks'].get(parent_id)
        if not parent_task or parent_task['completed']:
            return updated_parents
        
        # Check if ALL children of parent are completed
        all_children_completed = self._are_all_children_completed(session, parent_task)
        
        if all_children_completed:
            parent_task['completed'] = True
            session['completedTasks'].append(parent_task['id'])
            updated_parents.append(parent_task)
            
            # Recursively check parent's parent
            grandparent_updates = self._check_and_update_parent_tasks(session, parent_task)
            updated_parents.extend(grandparent_updates)
        
        return updated_parents
    
    def _get_parent_id(self, task_id: str) -> Optional[str]:
        """Get parent ID from task ID (e.g., "1.2" -> "1", "3.1.2" -> "3.1")"""
        parts = task_id.split('.')
        if len(parts) <= 1:
            return None
        
        parts.pop()  # Remove last part
        return '.'.join(parts)
    
    def _are_all_children_completed(self, session: Dict[str, Any], 
                                    parent_task: Dict[str, Any]) -> bool:
        """Check if all children of a parent task are completed (recursive check)"""
        if not parent_task['children']:
            # This is a leaf task, should not be processed here
            return True
        
        # Check all direct children
        for child_id in parent_task['children']:
            child_task = session['tasks'].get(child_id)
            if not child_task:
                continue
            
            if not child_task['completed']:
                return False
            
            # If child has children, recursively check them too
            if child_task['children']:
                if not self._are_all_children_completed(session, child_task):
                    return False
        
        return True
    
    def _validate_task_execution(self, session: Dict[str, Any], 
                                 task_id: str) -> Tuple[bool, List[str]]:
        """Validate task execution prerequisites"""
        errors = []
        
        task = session['tasks'].get(task_id)
        if not task:
            errors.append(f"Task not found: {task_id}")
            return False, errors
        
        if task['completed']:
            errors.append(f"Task already completed: {task_id}")
        
        if task['children']:
            errors.append(f"Cannot execute parent task with children: {task_id}")
        
        uncompleted_dependencies = [
            dep_id for dep_id in task['dependencies']
            if not session['tasks'].get(dep_id, {}).get('completed', False) and
               dep_id not in session['completedTasks']
        ]
        
        if uncompleted_dependencies:
            errors.append(f"Task has uncompleted dependencies: {', '.join(uncompleted_dependencies)}")
        
        return len(errors) == 0, errors
    
    def _is_complex_task(self, task: Dict[str, Any]) -> bool:
        """Determine if a task is complex and requires Sequential Thinking"""
        complex_keywords = [
            'architecture', 'design', 'system', 'algorithm', 'database', 'api',
            'performance', 'security', 'optimization', 'integration', 'framework',
            'structure', 'pattern', 'strategy', 'analysis', 'planning', 'schema'
        ]
        
        task_text = (task['title'] + ' ' + task['description']).lower()
        has_complex_keywords = any(keyword in task_text for keyword in complex_keywords)
        is_high_priority = task['priority'] == 'High'
        has_long_description = len(task['description']) > 200
        
        return has_complex_keywords or (is_high_priority and has_long_description)
    
    def _get_progress(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Get session progress statistics"""
        total = len(session['tasks'])
        completed = len(session['completedTasks'])
        percentage = round((completed / total * 100)) if total > 0 else 0
        
        return {
            'completed': completed,
            'total': total,
            'percentage': percentage
        }
    
    def _get_session_summary(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Get session summary for listing"""
        progress = self._get_progress(session)
        is_completed = len(session['completedTasks']) == len(session['tasks'])
        
        return {
            'sessionId': session['sessionId'],
            'projectName': session['projectName'],
            'wbsFilePath': session['wbsFilePath'],
            'progress': progress,
            'createdAt': session['createdAt'],
            'lastUpdated': session['lastUpdated'],
            'isCompleted': is_completed
        }
    
    # ===== MAIN EXECUTION METHODS =====
    
    def _start_execution(self, wbs_file_path: str) -> Dict[str, Any]:
        """Start WBS execution"""
        # Parse WBS file
        tasks, project_name, problem_statement = self._parse_wbs_file(wbs_file_path)
        
        # Create new session
        session = self._create_session(wbs_file_path, tasks, project_name)
        
        # Get initial available tasks for display
        available_tasks = self._get_available_tasks(session)
        
        response = {
            'success': True,
            'sessionId': session['sessionId'],
            'executionHistory': [],
            'completedTasksCount': 0,
            'totalTasksCount': len(tasks),
            'availableTasks': available_tasks,
            'message': f"🚀 WBS execution session started. Project: {project_name}. "
                      f"{len(tasks)} tasks loaded. Use 'continue' action to begin execution.",
            'progress': self._get_progress(session)
        }
        
        return response
    
    def _continue_execution(self, session_id: str) -> Dict[str, Any]:
        """Continue WBS execution"""
        session = self._get_session(session_id)
        available_tasks = self._get_executable_tasks(session)
        
        if not available_tasks:
            response = {
                'success': True,
                'sessionId': session['sessionId'],
                'executionHistory': [],
                'completedTasksCount': len(session['completedTasks']),
                'totalTasksCount': len(session['tasks']),
                'availableTasks': [],
                'message': "🎉 All tasks completed!",
                'progress': self._get_progress(session)
            }
            return response
        
        # Get the next task to execute
        next_task = available_tasks[0]
        session['currentTaskId'] = next_task['id']
        self._update_session(session)
        
        # Enhanced message with complexity and error handling guidance
        task_message = f"▶️ Ready to execute: **{next_task['title']}**"
        
        if self._is_complex_task(next_task):
            task_message += f"\n\n🧠 **COMPLEX TASK DETECTED** - Consider Sequential Thinking first:"
            task_message += f"\n- Task: {next_task['title']}"
            task_message += f"\n- Description: {next_task['description']}"
            task_message += f"\n- Priority: {next_task['priority']}"
        
        task_message += "\n\n🔥 **EXECUTION REQUIREMENTS:**"
        task_message += "\n- Validate implementation thoroughly"
        task_message += "\n- Test functionality before marking complete"
        task_message += "\n- Fix any errors before proceeding"
        task_message += "\n- Only mark complete when fully working"
        task_message += f"\n\nProgress: {len(session['completedTasks'])}/{len(session['tasks'])} tasks completed"
        
        next_available_task = available_tasks[1] if len(available_tasks) > 1 else None
        
        response = {
            'success': True,
            'sessionId': session['sessionId'],
            'currentTask': next_task,
            'nextAvailableTask': next_available_task,
            'executionHistory': [],  # Don't include full history to save tokens
            'completedTasksCount': len(session['completedTasks']),
            'totalTasksCount': len(session['tasks']),
            'availableTasks': [],  # Don't include full list to save tokens
            'message': task_message,
            'progress': self._get_progress(session)
        }
        
        return response
    
    def _execute_task(self, session_id: str, task_id: str, thinking: str, 
                     action_description: str) -> Dict[str, Any]:
        """Execute a specific task"""
        session = self._get_session(session_id)
        task = session['tasks'].get(task_id)
        
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        # Validate task execution
        valid, errors = self._validate_task_execution(session, task_id)
        if not valid:
            raise ValueError(f"Cannot execute task: {', '.join(errors)}")
        
        # Enhanced thinking analysis with complexity assessment
        enhanced_thinking = thinking or f"Executing task: {task['title']}"
        
        # Add guidance for complex tasks
        if self._is_complex_task(task):
            enhanced_thinking += "\n\n🧠 COMPLEX TASK GUIDANCE:"
            enhanced_thinking += "\n- Use Sequential Thinking tool for architectural decisions"
            enhanced_thinking += "\n- Break down into smaller implementation steps"
            enhanced_thinking += "\n- Consider design patterns and best practices"
            enhanced_thinking += "\n- Plan before implementing"
        
        # Add error handling guidance
        enhanced_thinking += "\n\n🛡️ ERROR HANDLING REQUIREMENTS:"
        enhanced_thinking += "\n- Validate all inputs and outputs"
        enhanced_thinking += "\n- Handle edge cases and error conditions"
        enhanced_thinking += "\n- Use try-catch blocks where appropriate"
        enhanced_thinking += "\n- Test implementation thoroughly"
        enhanced_thinking += "\n- Fix any errors before proceeding"
        enhanced_thinking += "\n- Document error resolution steps"
        
        # Complete the task in session (but don't update file yet)
        execution_step = self._complete_task(
            session,
            task['id'],
            enhanced_thinking,
            action_description or "Task implementation with enhanced error handling"
        )
        
        # Check and update parent tasks
        updated_parents = self._check_and_update_parent_tasks(session, task)
        
        # Update WBS file checkbox for completed task
        try:
            self._update_task_checkbox(session['wbsFilePath'], task, True)
            
            # Update parent tasks in file if auto-completed
            for parent in updated_parents:
                self._update_task_checkbox(session['wbsFilePath'], parent, True)
        except Exception as e:
            # Log error but don't fail the execution
            print(f"Warning: Failed to update WBS file: {str(e)}")
        
        # Update session
        self._update_session(session)
        
        # Find next available task
        available_tasks = self._get_executable_tasks(session)
        next_task = available_tasks[0] if available_tasks else None
        
        completion_message = f"✅ Task completed successfully: {task['title']}"
        
        if next_task:
            completion_message += f"\n\n📋 Next task ready: {next_task['title']}"
        else:
            completion_message += "\n\n🎉 All tasks completed!"
        
        # Optimized response with minimal output
        response = {
            'success': True,
            'sessionId': session['sessionId'],
            'currentTask': task,
            'nextAvailableTask': next_task,
            'completedTasksCount': len(session['completedTasks']),
            'totalTasksCount': len(session['tasks']),
            'message': completion_message,
            'progress': self._get_progress(session),
            'executionHistory': [],  # Don't include full history to save tokens
            'availableTasks': []  # Don't include full list to save tokens
        }
        
        return response
    
    def _get_status(self, session_id: str) -> Dict[str, Any]:
        """Get current session status"""
        session = self._get_session(session_id)
        available_tasks = self._get_executable_tasks(session)
        
        current_task = None
        if session.get('currentTaskId'):
            current_task = session['tasks'].get(session['currentTaskId'])
        
        response = {
            'success': True,
            'sessionId': session['sessionId'],
            'currentTask': current_task,
            'executionHistory': [],  # Don't include full history to save tokens
            'completedTasksCount': len(session['completedTasks']),
            'totalTasksCount': len(session['tasks']),
            'availableTasks': [],  # Don't include full list to save tokens
            'message': f"📊 Session status: {len(session['completedTasks'])}/{len(session['tasks'])} "
                      f"tasks completed | {len(available_tasks)} tasks ready for execution",
            'progress': self._get_progress(session)
        }
        
        return response
    
    def _list_sessions(self) -> Dict[str, Any]:
        """List all active sessions"""
        sessions = self._get_all_sessions()
        sessions_list = [self._get_session_summary(session) for session in sessions]
        
        return {
            'success': True,
            'sessions': sessions_list,
            'message': f"Found {len(sessions_list)} active sessions"
        }
    
    async def execute(self, 
                     action: str,
                     wbs_file_path: str = None,
                     session_id: str = None,
                     task_id: str = None,
                     thinking: str = None,
                     action_description: str = None,
                     **kwargs) -> str:
        """
        Execute WBS Execution tool action
        
        Args:
            action: Action to perform (start, continue, execute_task, get_status, list_sessions)
            wbs_file_path: Path to WBS markdown file (for start action)
            session_id: Session ID (for continue, execute_task, get_status actions)
            task_id: Task ID to execute (for execute_task action)
            thinking: Deep thinking analysis (for execute_task action)
            action_description: Description of actions taken (for execute_task action)
        
        Returns:
            JSON response with execution results
        """
        try:
            if action == 'start':
                if not wbs_file_path:
                    raise ValueError("wbsFilePath is required for start action")
                result = self._start_execution(wbs_file_path)
            
            elif action == 'continue':
                if not session_id:
                    raise ValueError("sessionId is required for continue action")
                result = self._continue_execution(session_id)
            
            elif action == 'execute_task':
                if not session_id:
                    raise ValueError("sessionId is required for execute_task action")
                if not task_id:
                    raise ValueError("taskId is required for execute_task action")
                result = self._execute_task(session_id, task_id, thinking or '', action_description or '')
            
            elif action == 'get_status':
                if not session_id:
                    raise ValueError("sessionId is required for get_status action")
                result = self._get_status(session_id)
            
            elif action == 'list_sessions':
                result = self._list_sessions()
            
            else:
                raise ValueError(f"Unknown action: {action}")
            
            return json.dumps(result, indent=2, ensure_ascii=False)
        
        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e)
            }
            return json.dumps(error_result, indent=2, ensure_ascii=False)
