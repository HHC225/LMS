"""
Feature Flow Analysis Tool - Flow Visualization
Analyzes execution flow with ASCII diagrams for easy understanding

This tool provides file-level flow visualization:
1. Analyze: Parse files, determine execution order, generate ASCII flow diagrams
2. Get Session: Retrieve analysis results

Purpose: Visualize "HOW this feature flows" with clear ASCII diagrams
"""
from typing import Dict, Any, Optional, List, Tuple, Set
from datetime import datetime
import json
import time
import random
import os
import re
import traceback
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
from ..base import ReasoningTool


class FileType(Enum):
    """Source file classification"""
    PIPELINE = "pipeline"
    TRANSFORM = "transform"
    DTO = "dto"
    REPOSITORY = "repository"
    ENTITY = "entity"
    OPTIONS = "options"
    SERVICE = "service"
    UNKNOWN = "unknown"


@dataclass
class FileInfo:
    """Information about a source file"""
    path: str
    name: str
    class_name: str
    file_type: str
    description: str = ""
    size_lines: int = 0
    dependencies: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FlowAnalysisSession:
    """Feature flow analysis session data"""
    id: str
    feature_name: str
    status: str
    created_at: str
    last_updated: str
    file_infos: List[FileInfo] = field(default_factory=list)
    entry_points: List[str] = field(default_factory=list)
    execution_order: List[str] = field(default_factory=list)
    output_path: Optional[str] = None
    file_flow_ascii: Optional[str] = None


flow_sessions: Dict[str, FlowAnalysisSession] = {}


class FeatureFlowAnalysisTool(ReasoningTool):
    """Feature Flow Analysis Tool - Flow Visualization Only"""
    
    def __init__(self, default_output_dir: Optional[Path] = None):
        super().__init__(name="feature_flow_analysis", description="Flow Visualization Analysis")
        self.default_output_dir = default_output_dir or Path("./output/analysis/flows")
    
    async def execute(self, action: str, ctx: Any = None, **kwargs) -> str:
        actions = {
            'analyze': self.action_analyze,
            'get_session': self.action_get_session,
            'list_sessions': self.action_list_sessions
        }
        
        action_method = actions.get(action)
        if not action_method:
            return json.dumps({'success': False, 'error': f'Unknown action: {action}'}, ensure_ascii=False)
        
        return await action_method(ctx=ctx, **kwargs)
    
    # ===== Action Methods =====
    
    async def action_analyze(self, feature_name: str, file_paths: List[str], ctx: Any = None) -> str:
        """Complete flow analysis in one shot"""
        try:
            session_id = f"flow_{int(time.time())}_{random.randint(1000,9999):04d}"
            
            session = FlowAnalysisSession(
                id=session_id,
                feature_name=feature_name,
                status="analyzing",
                created_at=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat()
            )
            
            # Step 1: Parse and classify files
            file_infos = []
            entry_points = []
            
            for fpath in file_paths:
                if os.path.exists(fpath):
                    fname = os.path.basename(fpath)
                    ftype = self._classify_file(fpath)
                    
                    file_info = FileInfo(
                        path=fpath,
                        name=fname,
                        class_name=self._extract_class_name(fpath),
                        file_type=ftype,
                        description=self._generate_file_description(fpath),
                        size_lines=self._count_lines(fpath),
                        imports=self._extract_imports(fpath)
                    )
                    file_infos.append(file_info)
                    
                    if ftype == "pipeline":
                        entry_points.append(fpath)
            
            session.file_infos = file_infos
            session.entry_points = entry_points if entry_points else [file_infos[0].path if file_infos else None]
            
            # Step 2: Analyze dependencies and execution order
            self._analyze_file_dependencies(session)
            session.execution_order = self._determine_execution_order(session)
            
            # Step 3: Generate ASCII flow diagram
            session.file_flow_ascii = self._generate_file_flow_ascii(session)
            
            # Step 4: Write complete MD file
            self.default_output_dir.mkdir(parents=True, exist_ok=True)
            safe_name = feature_name.replace(' ', '_').replace('/', '_')
            output_file = self.default_output_dir / f"{safe_name}_flow.md"
            
            self._write_complete_md(output_file, session)
            
            session.output_path = str(output_file)
            session.status = "completed"
            session.last_updated = datetime.now().isoformat()
            
            flow_sessions[session_id] = session
            
            return json.dumps({
                'success': True,
                'sessionId': session_id,
                'featureName': feature_name,
                'status': session.status,
                'totalFiles': len(file_infos),
                'entryPoints': [os.path.basename(ep) for ep in session.entry_points],
                'outputPath': str(output_file),
                'message': f'Flow analysis completed! Report saved to {output_file}'
            }, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc()
            }, ensure_ascii=False)
    
    async def action_get_session(self, session_id: str, ctx: Any = None) -> str:
        """Get session information"""
        session = flow_sessions.get(session_id)
        if not session:
            return json.dumps({'success': False, 'error': 'Session not found'}, ensure_ascii=False)
        
        return json.dumps({
            'success': True,
            'sessionId': session_id,
            'featureName': session.feature_name,
            'status': session.status,
            'totalFiles': len(session.file_infos),
            'outputPath': session.output_path
        }, indent=2, ensure_ascii=False)
    
    async def action_list_sessions(self, ctx: Any = None) -> str:
        """List all sessions"""
        sessions = [{
            'sessionId': s.id,
            'featureName': s.feature_name,
            'status': s.status,
            'totalFiles': len(s.file_infos),
            'createdAt': s.created_at
        } for s in flow_sessions.values()]
        
        return json.dumps({
            'success': True,
            'totalSessions': len(sessions),
            'sessions': sessions
        }, indent=2, ensure_ascii=False)

    # ===== Helper Methods =====
    
    def _classify_file(self, fpath: str) -> str:
        """Classify file type based on filename"""
        fname = os.path.basename(fpath).lower()
        if 'pipeline' in fname:
            return "pipeline"
        elif 'dto' in fname:
            return "dto"
        elif 'fn.java' in fname or 'transform' in fname:
            return "transform"
        elif 'repository' in fname:
            return "repository"
        elif 'entity' in fname:
            return "entity"
        elif 'options' in fname:
            return "options"
        elif 'service' in fname:
            return "service"
        return "unknown"
    
    def _extract_class_name(self, fpath: str) -> str:
        """Extract class name from file"""
        fname = os.path.basename(fpath)
        return fname.replace('.java', '').replace('.py', '')
    
    def _count_lines(self, fpath: str) -> int:
        """Count lines in file"""
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                return len(f.readlines())
        except:
            return 0
    
    def _extract_imports(self, fpath: str) -> List[str]:
        """Extract import statements"""
        imports = []
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
                java_imports = re.findall(r'import\s+([a-zA-Z0-9_.]+);', content)
                python_imports = re.findall(r'(?:from|import)\s+([a-zA-Z0-9_.]+)', content)
                imports = java_imports + python_imports
        except:
            pass
        return imports[:20]
    
    def _generate_file_description(self, fpath: str) -> str:
        """Generate a brief description of the file from comments and code"""
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:50]  # Read first 50 lines
            
            description = ""
            
            # Look for javadoc-style class comments
            in_comment = False
            comment_lines = []
            for line in lines:
                stripped = line.strip()
                
                # Javadoc style /** ... */
                if '/**' in stripped:
                    in_comment = True
                    continue
                elif '*/' in stripped:
                    in_comment = False
                    if comment_lines:
                        # Get first meaningful line from comment
                        for cline in comment_lines:
                            cleaned = cline.strip('* ').strip()
                            if cleaned and not cleaned.startswith('@'):
                                description = cleaned
                                break
                        if description:
                            break
                    comment_lines = []
                elif in_comment:
                    comment_lines.append(stripped)
                
                # Single line // comment before class
                if stripped.startswith('//') and not description:
                    cleaned = stripped.lstrip('/ ').strip()
                    if cleaned and len(cleaned) > 10:
                        description = cleaned
                        break
                
                # Python docstring
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    doc_end = stripped[3:]
                    if doc_end and '"""' not in doc_end and "'''" not in doc_end:
                        description = doc_end.strip()
                        break
            
            # If no description found, try to infer from class name
            if not description:
                class_name = self._extract_class_name(fpath)
                # Extract meaningful words from camelCase/PascalCase
                words = re.findall(r'[A-Z][a-z]+', class_name)
                if words:
                    description = ' '.join(words)
            
            # Truncate to reasonable length
            if len(description) > 55:
                description = description[:52] + "..."
            
            return description if description else "Source file"
            
        except Exception as e:
            return "Source file"
    
    def _infer_dependency_action(self, from_file: FileInfo, to_file: FileInfo) -> str:
        """Infer what action happens in dependency relationship"""
        from_type = from_file.file_type
        to_type = to_file.file_type
        
        # Action mapping based on file type relationships
        action_map = {
            ('pipeline', 'transform'): 'process',
            ('pipeline', 'repository'): 'fetch',
            ('pipeline', 'dto'): 'use',
            ('transform', 'repository'): 'persist',
            ('transform', 'dto'): 'convert',
            ('transform', 'entity'): 'map',
            ('transform', 'service'): 'call',
            ('transform', 'transform'): 'delegate',
            ('repository', 'entity'): 'store',
            ('repository', 'dto'): 'map',
            ('dto', 'entity'): 'wrap',
            ('service', 'repository'): 'query',
        }
        
        key = (from_type, to_type)
        action = action_map.get(key)
        
        if action:
            return action
        
        # Fallback inference
        if to_type == 'repository':
            return 'access'
        elif to_type == 'dto':
            return 'use'
        elif to_type == 'entity':
            return 'handle'
        elif to_type == 'transform':
            return 'invoke'
        else:
            return 'uses'
    
    def _analyze_file_dependencies(self, session: FlowAnalysisSession):
        """Analyze dependencies between files"""
        class_to_file = {f.class_name: f for f in session.file_infos}
        
        for file_info in session.file_infos:
            deps = []
            for imp in file_info.imports:
                class_name = imp.split('.')[-1]
                if class_name in class_to_file and class_to_file[class_name].path != file_info.path:
                    deps.append(class_to_file[class_name].path)
            file_info.dependencies = list(set(deps))
    
    def _determine_execution_order(self, session: FlowAnalysisSession) -> List[str]:
        """Determine execution order using topological sort"""
        if not session.entry_points:
            return [f.path for f in session.file_infos]
        
        visited = set()
        order = []
        
        def dfs(file_path: str):
            if file_path in visited:
                return
            visited.add(file_path)
            
            file_info = next((f for f in session.file_infos if f.path == file_path), None)
            if not file_info:
                return
            
            for dep in file_info.dependencies:
                if dep not in visited:
                    dfs(dep)
            
            order.append(file_path)
        
        for entry_point in session.entry_points:
            dfs(entry_point)
        
        for file_info in session.file_infos:
            if file_info.path not in visited:
                order.append(file_info.path)
        
        return list(reversed(order))



    def _generate_file_flow_ascii(self, session: FlowAnalysisSession) -> str:
        """Generate ASCII file-level flow diagram with descriptions and actions"""
        lines = []
        
        # File type emoji mapping
        type_emoji = {
            "pipeline": "⚙️",
            "transform": "🔄",
            "dto": "📦",
            "repository": "💾",
            "entity": "🗃️",
            "options": "⚙️",
            "service": "🔧",
            "unknown": "📄"
        }
        
        # Calculate max widths for dynamic box sizing (no truncation)
        max_name_len = max(len(f.name) for f in session.file_infos) if session.file_infos else 40
        max_type_len = max(len(f.file_type) for f in session.file_infos) if session.file_infos else 10
        max_desc_len = max(len(f.description) for f in session.file_infos) if session.file_infos else 30
        
        # Set comfortable box width (content + padding)
        box_content_width = max(max_name_len + 5, max_desc_len + 8, max_type_len + 8, 65)
        box_total_width = box_content_width + 4  # 4 for "│ " and " │"
        
        # Header
        header_text = "FILE EXECUTION FLOW"
        header_padding = (box_total_width - len(header_text)) // 2
        lines.append("╔" + "═" * box_total_width + "╗")
        lines.append("║" + " " * header_padding + header_text + " " * (box_total_width - header_padding - len(header_text)) + "║")
        lines.append("╚" + "═" * box_total_width + "╝")
        lines.append("")
        
        # Start with entry point
        if session.entry_points:
            entry_file = next((f for f in session.file_infos if f.path == session.entry_points[0]), None)
            if entry_file:
                entry_name = entry_file.name
                start_text = f"🚀 START: {entry_name}"
                start_padding = (box_content_width - len(start_text)) // 2
                lines.append("    ╭" + "─" * box_content_width + "╮")
                lines.append("    │" + " " * start_padding + start_text + " " * (box_content_width - start_padding - len(start_text)) + "│")
                lines.append("    ╰" + "─" * box_content_width + "╯")
                lines.append(" " * (box_content_width // 2 + 2) + "│")
                lines.append(" " * (box_content_width // 2 + 2) + "▼")
        
        # Show execution flow
        for i, file_path in enumerate(session.execution_order):
            file_info = next((f for f in session.file_infos if f.path == file_path), None)
            if not file_info:
                continue
            
            emoji = type_emoji.get(file_info.file_type, "📄")
            
            # Build box lines with proper padding (no truncation)
            name_line = f"{emoji}  {file_info.name}"
            type_line = f"Type: {file_info.file_type}"
            desc_line = f"Desc: {file_info.description}"
            
            # Show current file in a box with description
            lines.append("    ┌" + "─" * box_content_width + "┐")
            lines.append(f"    │ {name_line:<{box_content_width - 1}}│")
            lines.append(f"    │ {type_line:<{box_content_width - 1}}│")
            lines.append(f"    │ {desc_line:<{box_content_width - 1}}│")
            lines.append("    └" + "─" * box_content_width + "┘")
            
            # Show dependencies with actions
            if file_info.dependencies:
                dep_files = [next((f for f in session.file_infos if f.path == dep), None) 
                           for dep in file_info.dependencies]
                dep_files = [f for f in dep_files if f is not None]
                
                if dep_files:
                    lines.append(" " * (box_content_width // 2 + 2) + "│")
                    for j, dep_file in enumerate(dep_files):
                        dep_emoji = type_emoji.get(dep_file.file_type, "📄")
                        dep_name = dep_file.name  # No truncation
                        
                        # Get action for this dependency
                        action = self._infer_dependency_action(file_info, dep_file)
                        
                        connector = "└─" if j == len(dep_files) - 1 else "├─"
                        indent = " " * (box_content_width // 2 + 1)
                        lines.append(f"{indent}{connector}[{action}]→ {dep_emoji} {dep_name}")
                    lines.append(" " * (box_content_width // 2 + 2) + "│")
            
            # Continue to next if not last
            if i < len(session.execution_order) - 1:
                lines.append(" " * (box_content_width // 2 + 2) + "│")
                lines.append(" " * (box_content_width // 2 + 2) + "▼")
        
        lines.append("")
        end_text = "🏁 END"
        end_padding = (box_content_width - len(end_text)) // 2
        lines.append("    ╭" + "─" * box_content_width + "╮")
        lines.append("    │" + " " * end_padding + end_text + " " * (box_content_width - end_padding - len(end_text)) + "│")
        lines.append("    ╰" + "─" * box_content_width + "╯")
        lines.append("")
        return '\n'.join(lines)

    

    
    def _write_complete_md(self, output_file: Path, session: FlowAnalysisSession):
        """Write complete MD file with flow diagram"""
        lines = []
        
        # Header
        lines.append(f"# Feature Flow Analysis: {session.feature_name}")
        lines.append("")
        lines.append(f"**Analysis ID:** `{session.id}`")
        lines.append(f"**Created:** {session.created_at}")
        lines.append(f"**Status:** {session.status}")
        lines.append("")
        
        # Overview
        lines.append("## Overview")
        lines.append("")
        lines.append(f"- **Feature:** {session.feature_name}")
        lines.append(f"- **Total Files:** {len(session.file_infos)}")
        lines.append(f"- **Entry Points:** {', '.join([os.path.basename(ep) for ep in session.entry_points])}")
        lines.append(f"- **Analysis Date:** {session.created_at}")
        lines.append("")
        
        # File-Level Flow
        lines.append("## File Execution Flow")
        lines.append("")
        lines.append("```")
        lines.append(session.file_flow_ascii)
        lines.append("```")
        lines.append("")
        
        # File Details
        lines.append("## File Details")
        lines.append("")
        
        # Group files by type
        files_by_type = defaultdict(list)
        for f in session.file_infos:
            files_by_type[f.file_type].append(f)
        
        for ftype, files in sorted(files_by_type.items()):
            lines.append(f"### {ftype.upper()}")
            lines.append("")
            for f in files:
                lines.append(f"**`{f.name}`** ({f.size_lines} lines)")
                lines.append(f"- {f.description}")
                if f.dependencies:
                    dep_names = [os.path.basename(d) for d in f.dependencies]
                    lines.append(f"- Dependencies: {', '.join(dep_names)}")
                lines.append("")
        
        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append("File-level flow analysis completed successfully.")
        lines.append("")
        lines.append("This analysis provides:")
        lines.append("- Visual representation of file execution flow")
        lines.append("- File descriptions and classifications")
        lines.append("- Dependency relationships with actions")
        lines.append("- Execution order determination")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*Generated by Feature Flow Analysis Tool*")
        lines.append("")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
