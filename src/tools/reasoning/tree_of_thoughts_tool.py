"""
Tree of Thoughts Tool Implementation
Tree of Thoughts framework for complex problem-solving
"""
from typing import Dict, Any, Optional, List
from fastmcp import Context
from datetime import datetime
import json
import time
import random
import string
from ..base import ReasoningTool


# Shared session store for Tree of Thoughts
tot_sessions: Dict[str, Dict[str, Any]] = {}


class TreeOfThoughtsNode:
    """Tree of Thoughts Node"""
    def __init__(self, id: str, thought: str, parent_id: Optional[str] = None, depth: int = 0):
        self.id = id
        self.thought = thought
        self.parent_id = parent_id
        self.depth = depth
        self.children: List[str] = []
        self.created_at = datetime.now().isoformat()


class TreeOfThoughtsEvaluation:
    """Node Evaluation"""
    def __init__(self, node_id: str, value: float, confidence: float, viability: str, reasoning: str):
        self.node_id = node_id
        self.value = value
        self.confidence = confidence
        self.viability = viability  # 'promising', 'uncertain', 'dead_end'
        self.reasoning = reasoning
        self.evaluated_at = datetime.now().isoformat()


class TreeOfThoughtsTool(ReasoningTool):
    """Tree of Thoughts Tool for branching exploration"""
    
    def __init__(self):
        super().__init__(
            name="tree_of_thoughts",
            description="Advanced Tree of Thoughts framework for complex problem-solving"
        )
    
    def _generate_session_id(self) -> str:
        """Generate session ID"""
        timestamp = str(int(time.time()))
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
        return f"tot_session_{timestamp}_{random_suffix}"
    
    def _generate_node_id(self) -> str:
        """Generate node ID"""
        timestamp = str(int(time.time() * 1000))
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return f"node_{timestamp}_{random_suffix}"
    
    def _create_session(self, problem_statement: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create new session"""
        session_id = self._generate_session_id()
        root_node_id = self._generate_node_id()
        
        # Default configuration
        default_config = {
            'search_strategy': 'bfs',  # 'bfs' or 'dfs'
            'generation_strategy': 'sampling',  # 'sampling' or 'proposing'
            'evaluation_method': 'value',  # 'value' or 'vote'
            'max_depth': 10,
            'max_branches': 5
        }
        
        if config:
            default_config.update(config)
        
        # Create root node
        root_node = TreeOfThoughtsNode(root_node_id, problem_statement, None, 0)
        
        session = {
            'id': session_id,
            'problem_statement': problem_statement,
            'config': default_config,
            'root_node_id': root_node_id,
            'nodes': {root_node_id: root_node.__dict__},
            'evaluations': {},
            'current_path': [root_node_id],
            'visited_paths': [],
            'execution_log': [],
            'status': 'active',
            'solution_found': False,
            'final_solution': None,
            'total_nodes': 1,
            'total_evaluations': 0,
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        
        tot_sessions[session_id] = session
        return session
    
    def _add_thoughts(self, session_id: str, parent_node_id: Optional[str], thoughts: List[str]) -> List[Dict[str, Any]]:
        """Add new thoughts to session"""
        if session_id not in tot_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = tot_sessions[session_id]
        
        # Use root if parent_node_id is not provided
        if not parent_node_id:
            parent_node_id = session['root_node_id']
        
        if parent_node_id not in session['nodes']:
            raise ValueError(f"Parent node {parent_node_id} not found")
        
        parent_node = session['nodes'][parent_node_id]
        parent_depth = parent_node['depth']
        
        # Check max depth
        if parent_depth >= session['config']['max_depth']:
            raise ValueError(f"Maximum depth {session['config']['max_depth']} reached")
        
        # Check max branches
        if len(parent_node['children']) + len(thoughts) > session['config']['max_branches']:
            raise ValueError(f"Maximum branches {session['config']['max_branches']} would be exceeded")
        
        added_nodes = []
        for thought in thoughts:
            node_id = self._generate_node_id()
            new_node = TreeOfThoughtsNode(node_id, thought, parent_node_id, parent_depth + 1)
            
            session['nodes'][node_id] = new_node.__dict__
            parent_node['children'].append(node_id)
            session['total_nodes'] += 1
            
            added_nodes.append(new_node.__dict__)
            
            session['execution_log'].append({
                'action': 'add_thought',
                'node_id': node_id,
                'parent_id': parent_node_id,
                'timestamp': datetime.now().isoformat()
            })
        
        session['last_updated'] = datetime.now().isoformat()
        return added_nodes
    
    def _add_evaluation(self, session_id: str, node_id: str, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Add evaluation to node"""
        if session_id not in tot_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = tot_sessions[session_id]
        
        if node_id not in session['nodes']:
            raise ValueError(f"Node {node_id} not found")
        
        eval_obj = TreeOfThoughtsEvaluation(
            node_id,
            evaluation['value'],
            evaluation['confidence'],
            evaluation['viability'],
            evaluation['reasoning']
        )
        
        session['evaluations'][node_id] = eval_obj.__dict__
        session['total_evaluations'] += 1
        
        session['execution_log'].append({
            'action': 'add_evaluation',
            'node_id': node_id,
            'value': evaluation['value'],
            'viability': evaluation['viability'],
            'timestamp': datetime.now().isoformat()
        })
        
        session['last_updated'] = datetime.now().isoformat()
        return eval_obj.__dict__
    
    def _search_next(self, session_id: str, strategy: Optional[str] = None) -> Dict[str, Any]:
        """Find next node to explore"""
        if session_id not in tot_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = tot_sessions[session_id]
        
        if not strategy:
            strategy = session['config']['search_strategy']
        
        # 평가되지 않은 노드 중에서 선택
        unevaluated_nodes = [
            node_id for node_id in session['nodes'].keys()
            if node_id not in session['evaluations'] and node_id != session['root_node_id']
        ]
        
        if not unevaluated_nodes:
            return {
                'next_node': None,
                'action': 'no_unevaluated_nodes',
                'message': 'All nodes have been evaluated'
            }
        
        # BFS: 깊이가 얕은 노드부터
        if strategy == 'bfs':
            unevaluated_nodes.sort(key=lambda nid: session['nodes'][nid]['depth'])
        # DFS: 깊이가 깊은 노드부터
        else:
            unevaluated_nodes.sort(key=lambda nid: session['nodes'][nid]['depth'], reverse=True)
        
        next_node_id = unevaluated_nodes[0]
        next_node = session['nodes'][next_node_id]
        
        session['execution_log'].append({
            'action': 'search_next',
            'node_id': next_node_id,
            'strategy': strategy,
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'next_node': next_node,
            'action': 'node_found',
            'strategy': strategy
        }
    
    def _backtrack(self, session_id: str, dead_end_node_id: str, strategy: str = 'parent') -> Dict[str, Any]:
        """Backtrack from dead end"""
        if session_id not in tot_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = tot_sessions[session_id]
        
        if dead_end_node_id not in session['nodes']:
            raise ValueError(f"Node {dead_end_node_id} not found")
        
        dead_end_node = session['nodes'][dead_end_node_id]
        
        backtrack_node = None
        
        if strategy == 'parent':
            # 부모 노드로 돌아가기
            if dead_end_node['parent_id']:
                backtrack_node = session['nodes'][dead_end_node['parent_id']]
        
        elif strategy == 'best_alternative':
            # 같은 부모의 자식들 중 가장 좋은 평가를 받은 노드로
            if dead_end_node['parent_id']:
                parent = session['nodes'][dead_end_node['parent_id']]
                siblings = [
                    sid for sid in parent['children']
                    if sid != dead_end_node_id and sid in session['evaluations']
                ]
                
                if siblings:
                    # 평가 점수가 가장 높은 형제 노드 선택
                    best_sibling = max(
                        siblings,
                        key=lambda sid: session['evaluations'][sid]['value']
                    )
                    backtrack_node = session['nodes'][best_sibling]
        
        elif strategy == 'root':
            # 루트로 돌아가기
            backtrack_node = session['nodes'][session['root_node_id']]
        
        if backtrack_node:
            session['execution_log'].append({
                'action': 'backtrack',
                'from_node': dead_end_node_id,
                'to_node': backtrack_node['id'],
                'strategy': strategy,
                'timestamp': datetime.now().isoformat()
            })
        
        return {
            'backtrack_node': backtrack_node,
            'action': 'backtracked' if backtrack_node else 'backtrack_failed',
            'strategy': strategy
        }
    
    def _set_solution(self, session_id: str, solution: str) -> Dict[str, Any]:
        """Set final solution"""
        if session_id not in tot_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = tot_sessions[session_id]
        session['final_solution'] = solution
        session['solution_found'] = True
        session['status'] = 'completed'
        session['last_updated'] = datetime.now().isoformat()
        
        session['execution_log'].append({
            'action': 'set_solution',
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'session_id': session_id,
            'solution': solution,
            'status': 'completed',
            'total_nodes': session['total_nodes'],
            'total_evaluations': session['total_evaluations']
        }
    
    def _get_session(self, session_id: str) -> Dict[str, Any]:
        """Get session information"""
        if session_id not in tot_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        return tot_sessions[session_id]
    
    def _list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions"""
        return [
            {
                'id': session['id'],
                'problem_statement': session['problem_statement'],
                'status': session['status'],
                'solution_found': session['solution_found'],
                'total_nodes': session['total_nodes'],
                'total_evaluations': session['total_evaluations'],
                'created_at': session['created_at'],
                'last_updated': session['last_updated']
            }
            for session in tot_sessions.values()
        ]
    
    def _display_results(self, session_id: str) -> Dict[str, Any]:
        """Display session results"""
        if session_id not in tot_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = tot_sessions[session_id]
        
        # 평가된 노드들을 점수순으로 정렬
        evaluated_nodes = []
        for node_id, evaluation in session['evaluations'].items():
            node = session['nodes'][node_id]
            
            # 노드 경로 구성
            path = self._get_node_path(node_id, session)
            
            evaluated_nodes.append({
                'node_id': node_id,
                'thought': node['thought'],
                'score': evaluation['value'],
                'confidence': evaluation['confidence'],
                'viability': evaluation['viability'],
                'reasoning': evaluation['reasoning'],
                'depth': node['depth'],
                'path': path
            })
        
        evaluated_nodes.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'session_id': session_id,
            'problem_statement': session['problem_statement'],
            'total_nodes': session['total_nodes'],
            'total_evaluations': session['total_evaluations'],
            'status': session['status'],
            'final_solution': session.get('final_solution'),
            'available_solutions': [
                {
                    'rank': idx + 1,
                    'node_id': node['node_id'],
                    'thought': node['thought'],
                    'score': node['score'],
                    'confidence': node['confidence'],
                    'viability': node['viability'],
                    'reasoning': node['reasoning'],
                    'depth': node['depth'],
                    'path_description': ' → '.join(node['path'])
                }
                for idx, node in enumerate(evaluated_nodes)
            ]
        }
    
    def _get_node_path(self, node_id: str, session: Dict[str, Any]) -> List[str]:
        """Build path to node"""
        path = []
        current_id = node_id
        
        while current_id:
            node = session['nodes'][current_id]
            path.insert(0, node['thought'][:50] + '...' if len(node['thought']) > 50 else node['thought'])
            current_id = node.get('parent_id')
        
        return path
    
    async def execute(
        self,
        action: str,
        session_id: Optional[str] = None,
        problem_statement: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        parent_node_id: Optional[str] = None,
        thoughts: Optional[List[str]] = None,
        node_id: Optional[str] = None,
        evaluation: Optional[Dict[str, Any]] = None,
        search_strategy: Optional[str] = None,
        dead_end_node_id: Optional[str] = None,
        backtrack_strategy: Optional[str] = None,
        solution: Optional[str] = None,
        ctx: Optional[Context] = None
    ) -> str:
        """Execute Tree of Thoughts action"""
        
        try:
            result = None
            
            if action == 'create_session':
                if not problem_statement:
                    raise ValueError("problem_statement is required for create_session")
                
                session = self._create_session(problem_statement, config)
                result = {
                    'action': 'create_session',
                    'session_id': session['id'],
                    'problem_statement': session['problem_statement'],
                    'config': session['config'],
                    'root_node_id': session['root_node_id'],
                    'status': session['status']
                }
            
            elif action == 'add_thoughts':
                if not session_id or not thoughts:
                    raise ValueError("session_id and thoughts are required for add_thoughts")
                
                added_nodes = self._add_thoughts(session_id, parent_node_id, thoughts)
                session = tot_sessions[session_id]
                result = {
                    'action': 'add_thoughts',
                    'session_id': session_id,
                    'added_thoughts': added_nodes,
                    'total_nodes': session['total_nodes']
                }
            
            elif action == 'add_evaluation':
                if not session_id or not node_id or not evaluation:
                    raise ValueError("session_id, node_id, and evaluation are required for add_evaluation")
                
                eval_result = self._add_evaluation(session_id, node_id, evaluation)
                session = tot_sessions[session_id]
                result = {
                    'action': 'add_evaluation',
                    'session_id': session_id,
                    'node_id': node_id,
                    'evaluation': eval_result,
                    'total_evaluations': session['total_evaluations']
                }
            
            elif action == 'search_next':
                if not session_id:
                    raise ValueError("session_id is required for search_next")
                
                search_result = self._search_next(session_id, search_strategy)
                result = {
                    'action': 'search_next',
                    'session_id': session_id,
                    **search_result
                }
            
            elif action == 'backtrack':
                if not session_id or not dead_end_node_id:
                    raise ValueError("session_id and dead_end_node_id are required for backtrack")
                
                backtrack_result = self._backtrack(session_id, dead_end_node_id, backtrack_strategy or 'parent')
                result = {
                    'action': 'backtrack',
                    'session_id': session_id,
                    'dead_end_node_id': dead_end_node_id,
                    **backtrack_result
                }
            
            elif action == 'set_solution':
                if not session_id or not solution:
                    raise ValueError("session_id and solution are required for set_solution")
                
                result = self._set_solution(session_id, solution)
            
            elif action == 'get_session':
                if not session_id:
                    raise ValueError("session_id is required for get_session")
                
                session = self._get_session(session_id)
                result = {
                    'action': 'get_session',
                    'session': session
                }
            
            elif action == 'list_sessions':
                sessions = self._list_sessions()
                result = {
                    'action': 'list_sessions',
                    'total_sessions': len(sessions),
                    'sessions': sessions
                }
            
            elif action == 'display_results':
                if not session_id:
                    raise ValueError("session_id is required for display_results")
                
                result = self._display_results(session_id)
            
            else:
                raise ValueError(f"Unknown action: {action}")
            
            # 로그 기록
            await self.log_execution(ctx, f"Tree of Thoughts - {action}")
            
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        except Exception as e:
            error_result = {
                'error': str(e),
                'action': action,
                'status': 'failed'
            }
            return json.dumps(error_result, indent=2, ensure_ascii=False)
