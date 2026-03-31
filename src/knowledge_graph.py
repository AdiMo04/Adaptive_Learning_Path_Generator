import json
from typing import List, Dict, Set, Optional
from collections import deque

class KnowledgeGraph:
    """
    Manages the skill knowledge graph.
    
    Responsibilities:
    - Load/validate skill data from JSON
    - Find prerequisites for a skill
    - Get all skills needed for a goal
    - Topological sort for correct learning order
    """
    
    def __init__(self, json_path: str = "data/knowledge_graph.json"):
        with open(json_path, 'r') as f:
            self.data = json.load(f)
        
        self.skills = self.data['skills']
        self.goals = self.data['goals']
        
        # Build adjacency list for quick lookups
        self.prereq_map = {}
        for skill_id, skill in self.skills.items():
            self.prereq_map[skill_id] = skill.get('prerequisites', [])
        
        # Validate graph has no cycles
        self._validate_no_cycles()
    
    def get_skill_info(self, skill_id: str) -> dict:
        """Get all information about a skill"""
        return self.skills.get(skill_id, {})
    
    def get_prerequisites(self, skill_id: str) -> List[str]:
        """Get direct prerequisites for a skill"""
        return self.prereq_map.get(skill_id, [])
    
    def get_all_prerequisites(self, skill_id: str, visited: Set[str] = None) -> List[str]:
        """
        Recursively get ALL prerequisites for a skill.
        
        Example: If skill requires B, and B requires A,
        returns [A, B] in correct dependency order.
        """
        if visited is None:
            visited = set()
        
        if skill_id in visited:
            return []
        
        visited.add(skill_id)
        all_prereqs = []
        
        for prereq in self.get_prerequisites(skill_id):
            all_prereqs.append(prereq)
            all_prereqs.extend(self.get_all_prerequisites(prereq, visited))
        
        return all_prereqs
    
    def get_skills_for_goal(self, goal_id: str) -> List[str]:
        """Get all skills required to achieve a goal"""
        return self.goals.get(goal_id, [])
    
    def get_all_skills_in_path(self, target_skills: List[str]) -> Set[str]:
        """
        Get all skills needed including all prerequisites.
        
        Example: target_skills = ['fastapi_advanced']
        Returns: {'python_basics', 'functions', 'http_basics', 
                  'async_python', 'fastapi_basics', 'fastapi_advanced'}
        """
        all_skills = set(target_skills)
        
        for skill in target_skills:
            prereqs = self.get_all_prerequisites(skill)
            all_skills.update(prereqs)
        
        return all_skills
    
    def topological_sort(self, skills: List[str]) -> List[str]:
        """
        Order skills so prerequisites come before dependents.
        
        Uses Kahn's algorithm for topological sorting.
        """
        # Build graph for these skills only
        graph = {skill: [] for skill in skills}
        in_degree = {skill: 0 for skill in skills}
        
        for skill in skills:
            for prereq in self.get_prerequisites(skill):
                if prereq in graph:
                    graph[prereq].append(skill)
                    in_degree[skill] += 1
        
        # Kahn's algorithm
        queue = deque([skill for skill in skills if in_degree[skill] == 0])
        sorted_skills = []
        
        while queue:
            current = queue.popleft()
            sorted_skills.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # If we couldn't sort all, there's a cycle
        if len(sorted_skills) != len(skills):
            raise ValueError("Cycle detected in skill dependencies")
        
        return sorted_skills
    
    def _validate_no_cycles(self):
        """Check if there are any circular dependencies in the graph"""
        all_skills = list(self.skills.keys())
        
        try:
            self.topological_sort(all_skills)
        except ValueError:
            print("⚠️ Warning: Circular dependency detected in knowledge graph")
            raise
    
    def get_learning_path(self, known_skills: List[str], goal_id: str) -> Dict:
        """
        Generate personalized learning path.
        
        Args:
            known_skills: Skills the user already knows
            goal_id: The goal they want to achieve
        
        Returns:
            Dict with path, missing skills, etc.
        """
        # Get skills required for goal
        target_skills = self.get_skills_for_goal(goal_id)
        
        if not target_skills:
            return {"error": f"Goal '{goal_id}' not found"}
        
        # Get all skills needed (including prerequisites)
        all_needed = self.get_all_skills_in_path(target_skills)
        
        # Find which skills are missing
        known_set = set(known_skills)
        missing_skills = all_needed - known_set
        
        # Sort missing skills in correct order
        if missing_skills:
            sorted_missing = self.topological_sort(list(missing_skills))
        else:
            sorted_missing = []
        
        # Calculate estimated time
        total_hours = sum(
            self.skills.get(skill, {}).get('estimated_hours', 0)
            for skill in sorted_missing
        )
        
        return {
            'goal': goal_id,
            'known_skills': known_skills,
            'missing_skills': list(missing_skills),
            'learning_path': sorted_missing,
            'total_estimated_hours': total_hours,
            'skills_required': list(all_needed)
        }
    
    def get_all_goals(self) -> List[str]:
        """Get list of all available goals"""
        return list(self.goals.keys())
    
    def get_all_skills(self) -> List[str]:
        """Get list of all skill IDs"""
        return list(self.skills.keys())