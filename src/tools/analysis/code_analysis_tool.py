"""
Code Analysis Tool Implementation
Progressive source code analysis for enterprise-level codebases

This tool analyzes source code in multiple steps to avoid token rate limits,
generating comprehensive documentation for new developers.
"""
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json
import time
import random
import string
import re
import os
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
from ..base import ReasoningTool


# ===== DATA STRUCTURES =====

class SessionStatus(Enum):
    """Analysis session status"""
    ACTIVE = "active"
    COMPLETED = "completed"


@dataclass
class CodeBlock:
    """Code block information"""
    type: str  # 'import', 'class', 'function', 'method'
    name: str
    start_line: int
    end_line: int
    parent: Optional[str] = None  # For methods: parent class name
    signature: Optional[str] = None  # Full signature
    decorators: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AnalysisStep:
    """Analysis step record"""
    step_number: int
    start_line: int
    end_line: int
    analysis_content: str
    timestamp: str
    blocks_analyzed: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AnalysisSession:
    """Analysis session data"""
    id: str
    source_file_path: str
    file_name: str
    total_lines: int
    total_steps: int
    status: str
    created_at: str
    last_updated: str
    current_step: int = 0
    output_path: Optional[str] = None
    imports: List[str] = field(default_factory=list)
    code_blocks: List[CodeBlock] = field(default_factory=list)
    analysis_history: List[AnalysisStep] = field(default_factory=list)
    language: str = "python"  # Detected language
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['code_blocks'] = [block.to_dict() for block in self.code_blocks]
        result['analysis_history'] = [step.to_dict() for step in self.analysis_history]
        return result


# Global session storage
analysis_sessions: Dict[str, AnalysisSession] = {}


# ===== CODE PARSER =====

class CodeParser:
    """Parse source code and extract structure"""
    
    @staticmethod
    def detect_language(file_path: str) -> str:
        """Detect programming language from file extension"""
        ext = Path(file_path).suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php',
            '.cs': 'csharp',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.rs': 'rust',
        }
        return language_map.get(ext, 'unknown')
    
    @staticmethod
    def parse_python_imports(lines: List[str]) -> List[str]:
        """Extract import statements from Python code"""
        imports = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                imports.append(stripped)
        return imports
    
    @staticmethod
    def parse_python_blocks(lines: List[str]) -> List[CodeBlock]:
        """Extract classes and functions from Python code"""
        blocks = []
        current_class = None
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Class definition
            class_match = re.match(r'^class\s+(\w+)', stripped)
            if class_match:
                class_name = class_match.group(1)
                blocks.append(CodeBlock(
                    type='class',
                    name=class_name,
                    start_line=i + 1,
                    end_line=i + 1,  # Will be updated later
                    signature=stripped
                ))
                current_class = class_name
                continue
            
            # Function/Method definition
            func_match = re.match(r'^def\s+(\w+)\s*\(', stripped)
            if func_match:
                func_name = func_match.group(1)
                block_type = 'method' if current_class else 'function'
                blocks.append(CodeBlock(
                    type=block_type,
                    name=func_name,
                    start_line=i + 1,
                    end_line=i + 1,  # Will be updated later
                    parent=current_class if block_type == 'method' else None,
                    signature=stripped
                ))
        
        return blocks
    
    @staticmethod
    def calculate_steps(total_lines: int, lines_per_step: int = 300) -> int:
        """Calculate number of steps needed"""
        import math
        return max(1, math.ceil(total_lines / lines_per_step))
    
    @staticmethod
    def get_step_range(step_number: int, total_lines: int, total_steps: int) -> Tuple[int, int]:
        """Get line range for a specific step"""
        lines_per_step = total_lines // total_steps
        start_line = (step_number - 1) * lines_per_step + 1
        
        if step_number == total_steps:
            end_line = total_lines
        else:
            end_line = step_number * lines_per_step
        
        return start_line, end_line


# ===== MARKDOWN GENERATOR =====

class AnalysisMarkdownGenerator:
    """Generate analysis markdown files"""
    
    def __init__(self, session: AnalysisSession):
        self.session = session
    
    def generate(self) -> str:
        """Generate complete markdown document"""
        sections = []
        
        # Header
        sections.append(f"# Code Analysis Report: {self.session.file_name}")
        sections.append("")
        sections.append(f"**Analysis Date:** {self.session.created_at}")
        sections.append(f"**Source File:** `{self.session.source_file_path}`")
        sections.append(f"**Language:** {self.session.language}")
        sections.append(f"**Total Lines:** {self.session.total_lines}")
        sections.append(f"**Status:** {self.session.status}")
        sections.append("")
        
        # Overview
        sections.append("## 📋 Overview")
        sections.append("")
        sections.append(f"This document provides a comprehensive analysis of `{self.session.file_name}` ")
        sections.append("for new developers to understand the codebase structure, dependencies, and functionality.")
        sections.append("")
        
        # Import Analysis
        if self.session.imports:
            sections.append("## 📦 Import Analysis")
            sections.append("")
            sections.append("### External Dependencies")
            sections.append("")
            sections.append("| Import Statement | Type |")
            sections.append("|------------------|------|")
            for imp in self.session.imports:
                import_type = "Standard Library" if self._is_stdlib(imp) else "Third-party"
                sections.append(f"| `{imp}` | {import_type} |")
            sections.append("")
        
        # Code Structure
        if self.session.code_blocks:
            sections.append("## 🏗️ Code Structure")
            sections.append("")
            
            classes = [b for b in self.session.code_blocks if b.type == 'class']
            functions = [b for b in self.session.code_blocks if b.type == 'function']
            
            if classes:
                sections.append("### Classes")
                sections.append("")
                sections.append("| Class Name | Line Range | Methods |")
                sections.append("|------------|------------|---------|")
                for cls in classes:
                    methods = [b for b in self.session.code_blocks if b.type == 'method' and b.parent == cls.name]
                    method_count = len(methods)
                    sections.append(f"| `{cls.name}` | {cls.start_line}-{cls.end_line} | {method_count} |")
                sections.append("")
            
            if functions:
                sections.append("### Functions")
                sections.append("")
                sections.append("| Function Name | Line Range | Signature |")
                sections.append("|---------------|------------|-----------|")
                for func in functions:
                    sig = func.signature[:50] + "..." if len(func.signature) > 50 else func.signature
                    sections.append(f"| `{func.name}` | {func.start_line}-{func.end_line} | `{sig}` |")
                sections.append("")
        
        # Detailed Analysis
        sections.append("## 🔍 Detailed Analysis")
        sections.append("")
        
        if self.session.analysis_history:
            for step in self.session.analysis_history:
                sections.append(f"### Step {step.step_number}: Lines {step.start_line}-{step.end_line}")
                sections.append("")
                sections.append(step.analysis_content)
                sections.append("")
        else:
            sections.append("*Analysis in progress. Detailed findings will be added step by step.*")
            sections.append("")
        
        # Summary
        sections.append("## 📊 Analysis Summary")
        sections.append("")
        sections.append(f"- **Steps Completed:** {len(self.session.analysis_history)} / {self.session.total_steps}")
        sections.append(f"- **Classes Found:** {len([b for b in self.session.code_blocks if b.type == 'class'])}")
        sections.append(f"- **Functions Found:** {len([b for b in self.session.code_blocks if b.type == 'function'])}")
        sections.append(f"- **Methods Found:** {len([b for b in self.session.code_blocks if b.type == 'method'])}")
        sections.append(f"- **Import Statements:** {len(self.session.imports)}")
        sections.append("")
        
        return '\n'.join(sections)
    
    def _is_stdlib(self, import_stmt: str) -> bool:
        """Check if import is from standard library"""
        stdlib_modules = {
            'os', 'sys', 're', 'json', 'time', 'datetime', 'math', 'random',
            'pathlib', 'typing', 'dataclasses', 'enum', 'functools', 'itertools',
            'collections', 'asyncio', 'threading', 'multiprocessing'
        }
        
        # Extract module name
        if import_stmt.startswith('import '):
            module = import_stmt.replace('import ', '').split()[0].split('.')[0]
        elif import_stmt.startswith('from '):
            module = import_stmt.replace('from ', '').split()[0].split('.')[0]
        else:
            return False
        
        return module in stdlib_modules


# ===== SESSION MANAGER =====

class AnalysisSessionManager:
    """Manage analysis sessions"""
    
    @staticmethod
    def create_session(source_file_path: str) -> AnalysisSession:
        """Create new analysis session"""
        timestamp = str(int(time.time()))
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        session_id = f"analysis_{timestamp}_{random_suffix}"
        
        # Read source file
        if not os.path.exists(source_file_path):
            raise FileNotFoundError(f"Source file not found: {source_file_path}")
        
        with open(source_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        language = CodeParser.detect_language(source_file_path)
        total_steps = CodeParser.calculate_steps(total_lines)
        
        # Parse imports and code blocks
        imports = []
        code_blocks = []
        if language == 'python':
            imports = CodeParser.parse_python_imports(lines)
            code_blocks = CodeParser.parse_python_blocks(lines)
        
        session = AnalysisSession(
            id=session_id,
            source_file_path=source_file_path,
            file_name=os.path.basename(source_file_path),
            total_lines=total_lines,
            total_steps=total_steps,
            status=SessionStatus.ACTIVE.value,
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
            imports=imports,
            code_blocks=code_blocks,
            language=language
        )
        
        analysis_sessions[session_id] = session
        return session
    
    @staticmethod
    def get_session(session_id: str) -> Optional[AnalysisSession]:
        """Get session by ID"""
        return analysis_sessions.get(session_id)
    
    @staticmethod
    def update_session(session: AnalysisSession) -> None:
        """Update session"""
        session.last_updated = datetime.now().isoformat()
        analysis_sessions[session.id] = session
    
    @staticmethod
    def add_analysis_step(session: AnalysisSession, step: AnalysisStep) -> None:
        """Add analysis step to session"""
        session.analysis_history.append(step)
        session.current_step = step.step_number


# ===== MAIN TOOL =====

class CodeAnalysisTool(ReasoningTool):
    """Code Analysis Tool with Multi-Action Architecture"""
    
    def __init__(self, default_output_dir: Optional[Path] = None):
        super().__init__(
            name="code_analysis",
            description="Progressive Source Code Analysis Tool"
        )
        self.default_output_dir = default_output_dir or Path("./output/analysis")
    
    async def execute(self, action: str, ctx: Any = None, **kwargs) -> str:
        """Route to appropriate action method"""
        actions = {
            'initialize': self.action_initialize,
            'analyze_step': self.action_analyze_step,
            'get_status': self.action_get_status,
            'list_sessions': self.action_list_sessions,
            'finalize': self.action_finalize
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
        source_file_path: str,
        ctx: Any = None
    ) -> str:
        """Initialize new analysis session"""
        try:
            if not source_file_path:
                return json.dumps({'success': False, 'error': 'source_file_path required'}, ensure_ascii=False)
            
            session = AnalysisSessionManager.create_session(source_file_path)
            
            # Create output directory
            self.default_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate output file name
            base_name = Path(session.file_name).stem
            output_file = self.default_output_dir / f"{base_name}_analysis.md"
            
            # Generate initial markdown
            generator = AnalysisMarkdownGenerator(session)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(generator.generate())
            
            session.output_path = str(output_file)
            AnalysisSessionManager.update_session(session)
            
            # Get first step range
            start_line, end_line = CodeParser.get_step_range(1, session.total_lines, session.total_steps)
            
            # Read code for first step
            with open(source_file_path, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
            
            step_code = ''.join(all_lines[start_line-1:end_line])
            
            return json.dumps({
                'success': True,
                'sessionId': session.id,
                'fileName': session.file_name,
                'totalLines': session.total_lines,
                'totalSteps': session.total_steps,
                'language': session.language,
                'importsCount': len(session.imports),
                'classesCount': len([b for b in session.code_blocks if b.type == 'class']),
                'functionsCount': len([b for b in session.code_blocks if b.type == 'function']),
                'outputPath': str(output_file),
                'message': f'Analysis session initialized. Markdown file created at: {output_file}',
                'nextAction': 'analyze_step',
                'currentStepInfo': {
                    'stepNumber': 1,
                    'startLine': start_line,
                    'endLine': end_line,
                    'codeSnippet': step_code[:500] + '...' if len(step_code) > 500 else step_code
                },
                'llmInstructions': self._generate_analysis_instructions(session, 1, start_line, end_line, step_code)
            }, indent=2, ensure_ascii=False)
            
        except FileNotFoundError as e:
            return json.dumps({'success': False, 'error': str(e)}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({'success': False, 'error': f'Initialization failed: {str(e)}'}, ensure_ascii=False)
    
    def _generate_analysis_instructions(
        self,
        session: AnalysisSession,
        step_number: int,
        start_line: int,
        end_line: int,
        code: str
    ) -> Dict[str, Any]:
        """Generate instructions for LLM to analyze this step"""
        return {
            'task': f'Analyze lines {start_line}-{end_line} of {session.file_name}',
            'stepNumber': step_number,
            'totalSteps': session.total_steps,
            'codeToAnalyze': code,
            'analysisGuidelines': [
                'Identify all functions, methods, and classes in this section',
                'Explain what each function/method does in simple terms',
                'List all variables used and their purposes',
                'Identify any external dependencies or imports used',
                'Explain the data flow and logic',
                'Note any important patterns or techniques used',
                'Highlight potential areas of complexity for new developers'
            ],
            'outputFormat': 'Write your analysis in clear, beginner-friendly markdown format',
            'nextStep': 'Call code_analysis_submit_step with your analysis content'
        }
    
    async def action_analyze_step(
        self,
        session_id: str,
        step_number: int,
        analysis_content: str,
        ctx: Any = None
    ) -> str:
        """Analyze a specific step and update markdown"""
        try:
            session = AnalysisSessionManager.get_session(session_id)
            if not session:
                return json.dumps({'success': False, 'error': f'Session {session_id} not found'}, ensure_ascii=False)
            
            # Get step range
            start_line, end_line = CodeParser.get_step_range(step_number, session.total_lines, session.total_steps)
            
            # Create step record
            step_record = AnalysisStep(
                step_number=step_number,
                start_line=start_line,
                end_line=end_line,
                analysis_content=analysis_content,
                timestamp=datetime.now().isoformat()
            )
            
            # Add to session
            AnalysisSessionManager.add_analysis_step(session, step_record)
            
            # Update markdown file immediately
            generator = AnalysisMarkdownGenerator(session)
            with open(Path(session.output_path), 'w', encoding='utf-8') as f:
                f.write(generator.generate())
            
            AnalysisSessionManager.update_session(session)
            
            # Check if more steps needed
            has_more_steps = step_number < session.total_steps
            next_action = 'analyze_step' if has_more_steps else 'finalize'
            
            result = {
                'success': True,
                'sessionId': session.id,
                'stepNumber': step_number,
                'totalSteps': session.total_steps,
                'markdownUpdated': True,
                'message': f'Step {step_number}/{session.total_steps} completed. Markdown file updated.',
                'progress': {
                    'completed': len(session.analysis_history),
                    'total': session.total_steps,
                    'percentage': int((len(session.analysis_history) / session.total_steps) * 100)
                },
                'nextAction': next_action
            }
            
            # If more steps, provide next step info
            if has_more_steps:
                next_step_num = step_number + 1
                next_start, next_end = CodeParser.get_step_range(next_step_num, session.total_lines, session.total_steps)
                
                with open(session.source_file_path, 'r', encoding='utf-8') as f:
                    all_lines = f.readlines()
                
                next_code = ''.join(all_lines[next_start-1:next_end])
                
                result['nextStepInfo'] = {
                    'stepNumber': next_step_num,
                    'startLine': next_start,
                    'endLine': next_end,
                    'codeSnippet': next_code[:500] + '...' if len(next_code) > 500 else next_code
                }
                result['llmInstructions'] = self._generate_analysis_instructions(
                    session, next_step_num, next_start, next_end, next_code
                )
            
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({'success': False, 'error': f'Analysis step failed: {str(e)}'}, ensure_ascii=False)
    
    async def action_finalize(
        self,
        session_id: str,
        ctx: Any = None
    ) -> str:
        """Finalize analysis session"""
        try:
            session = AnalysisSessionManager.get_session(session_id)
            if not session:
                return json.dumps({'success': False, 'error': f'Session {session_id} not found'}, ensure_ascii=False)
            
            session.status = SessionStatus.COMPLETED.value
            
            # Final markdown update
            generator = AnalysisMarkdownGenerator(session)
            with open(Path(session.output_path), 'w', encoding='utf-8') as f:
                f.write(generator.generate())
            
            AnalysisSessionManager.update_session(session)
            
            return json.dumps({
                'success': True,
                'sessionId': session.id,
                'status': 'completed',
                'totalSteps': session.total_steps,
                'stepsCompleted': len(session.analysis_history),
                'outputPath': session.output_path,
                'message': f'Analysis completed! Full report available at: {session.output_path}'
            }, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({'success': False, 'error': f'Finalization failed: {str(e)}'}, ensure_ascii=False)
    
    async def action_get_status(
        self,
        session_id: str,
        ctx: Any = None
    ) -> str:
        """Get current session status"""
        session = AnalysisSessionManager.get_session(session_id)
        if not session:
            return json.dumps({'success': False, 'error': f'Session {session_id} not found'}, ensure_ascii=False)
        
        return json.dumps({
            'success': True,
            'sessionId': session.id,
            'status': session.status,
            'fileName': session.file_name,
            'sourceFile': session.source_file_path,
            'totalLines': session.total_lines,
            'totalSteps': session.total_steps,
            'currentStep': session.current_step,
            'stepsCompleted': len(session.analysis_history),
            'outputPath': session.output_path,
            'progress': {
                'completed': len(session.analysis_history),
                'total': session.total_steps,
                'percentage': int((len(session.analysis_history) / session.total_steps) * 100)
            }
        }, indent=2, ensure_ascii=False)
    
    async def action_list_sessions(self, ctx: Any = None) -> str:
        """List all analysis sessions"""
        sessions_summary = []
        for session in analysis_sessions.values():
            sessions_summary.append({
                'sessionId': session.id,
                'fileName': session.file_name,
                'status': session.status,
                'totalSteps': session.total_steps,
                'stepsCompleted': len(session.analysis_history),
                'createdAt': session.created_at,
                'lastUpdated': session.last_updated
            })
        
        return json.dumps({
            'success': True,
            'totalSessions': len(sessions_summary),
            'sessions': sessions_summary
        }, indent=2, ensure_ascii=False)
