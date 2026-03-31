from typing import List, Dict, Optional, Any
from src.knowledge_graph import KnowledgeGraph
from src.skill_assessor import SkillAssessor

class RecommenderEngine:
    """
    Combines Knowledge Graph and Skill Assessor to generate personalized recommendations.
    
    Features:
    - Generate learning paths based on known skills
    - Get next skill recommendation
    - Estimate time to goal
    - Track progress
    """
    
    def __init__(self, knowledge_graph: KnowledgeGraph, skill_assessor: SkillAssessor):
        """
        Initialize the recommender engine.
        
        Args:
            knowledge_graph: The skill knowledge graph
            skill_assessor: User's skill confidence tracker
        """
        self.kg = knowledge_graph
        self.assessor = skill_assessor
    
    def generate_learning_path(self, goal_id: str, confidence_threshold: float = 0.7) -> Dict:
        """
        Generate a personalized learning path for a goal.
        
        Args:
            goal_id: The goal to achieve (e.g., 'become_fastapi_developer')
            confidence_threshold: Confidence level to consider skill "known" (0-1)
        
        Returns:
            Dict with learning path, estimated time, and progress
        """
        # Get skills the user already knows based on confidence
        known_skills = self.assessor.get_known_skills(threshold=confidence_threshold)
        
        # Get learning path from knowledge graph
        path = self.kg.get_learning_path(known_skills, goal_id)
        
        if 'error' in path:
            return path
        
        # Add confidence scores to missing skills
        skills_with_confidence = []
        for skill in path['learning_path']:
            skills_with_confidence.append({
                'skill_id': skill,
                'name': self.kg.get_skill_info(skill).get('name', skill),
                'confidence': self.assessor.get_confidence(skill),
                'estimated_hours': self.kg.get_skill_info(skill).get('estimated_hours', 0),
                'difficulty': self.kg.get_skill_info(skill).get('difficulty', 1)
            })
        
        # Calculate progress (percentage of skills known)
        total_skills = len(path['skills_required'])
        known_count = len([s for s in path['skills_required'] if s in known_skills])
        progress = (known_count / total_skills) * 100 if total_skills > 0 else 0
        
        return {
            'goal': goal_id,
            'goal_name': goal_id.replace('_', ' ').title(),
            'known_skills': known_skills,
            'learning_path': skills_with_confidence,
            'total_estimated_hours': path['total_estimated_hours'],
            'skills_required': path['skills_required'],
            'progress_percentage': progress,
            'missing_skills_count': len(path['missing_skills'])
        }
    
    def get_next_recommendation(self, goal_id: str, confidence_threshold: float = 0.7) -> Optional[Dict]:
        """
        Get the next skill the user should learn.
        
        Args:
            goal_id: The goal to achieve
            confidence_threshold: Confidence level to consider skill "known"
        
        Returns:
            Dict with next skill information, or None if goal is complete
        """
        path = self.generate_learning_path(goal_id, confidence_threshold)
        
        if 'error' in path:
            return None
        
        # Find the first skill in learning path that needs attention
        for skill in path['learning_path']:
            if skill['confidence'] < confidence_threshold:
                # Get prerequisites for this skill
                prerequisites = self.kg.get_prerequisites(skill['skill_id'])
                
                # Check if prerequisites are met
                missing_prereqs = []
                for prereq in prerequisites:
                    if self.assessor.get_confidence(prereq) < confidence_threshold:
                        missing_prereqs.append(prereq)
                
                return {
                    'skill_id': skill['skill_id'],
                    'skill_name': skill['name'],
                    'current_confidence': skill['confidence'],
                    'target_confidence': confidence_threshold,
                    'estimated_hours': skill['estimated_hours'],
                    'difficulty': skill['difficulty'],
                    'prerequisites': prerequisites,
                    'missing_prerequisites': missing_prereqs,
                    'progress': path['progress_percentage'],
                    'remaining_skills': len([s for s in path['learning_path'] if s['confidence'] < confidence_threshold])
                }
        
        # All skills are mastered
        return {
            'message': '🎉 Congratulations! You have mastered all skills for this goal!',
            'progress': 100,
            'goal_complete': True
        }
    
    def get_skill_details(self, skill_id: str) -> Dict:
        """
        Get detailed information about a skill.
        
        Args:
            skill_id: The skill ID
        
        Returns:
            Dict with skill details and user's progress
        """
        skill_info = self.kg.get_skill_info(skill_id)
        
        if not skill_info:
            return {'error': f'Skill {skill_id} not found'}
        
        return {
            'skill_id': skill_id,
            'name': skill_info.get('name', skill_id),
            'description': skill_info.get('description', ''),
            'prerequisites': self.kg.get_prerequisites(skill_id),
            'all_prerequisites': self.kg.get_all_prerequisites(skill_id),
            'estimated_hours': skill_info.get('estimated_hours', 0),
            'difficulty': skill_info.get('difficulty', 1),
            'user_confidence': self.assessor.get_confidence(skill_id),
            'is_known': self.assessor.get_confidence(skill_id) >= 0.7,
            'prerequisites_met': all(
                self.assessor.get_confidence(prereq) >= 0.7 
                for prereq in self.kg.get_prerequisites(skill_id)
            )
        }
    
    def estimate_time_to_goal(self, goal_id: str, hours_per_week: float = 10) -> Dict:
        """
        Estimate time to complete a goal based on user's pace.
        
        Args:
            goal_id: The goal to achieve
            hours_per_week: Hours user can dedicate per week
        
        Returns:
            Dict with time estimates
        """
        path = self.generate_learning_path(goal_id)
        
        if 'error' in path:
            return path
        
        remaining_hours = sum(
            skill['estimated_hours'] 
            for skill in path['learning_path'] 
            if skill['confidence'] < 0.7
        )
        
        weeks_needed = remaining_hours / hours_per_week if hours_per_week > 0 else 0
        
        return {
            'goal': goal_id,
            'remaining_hours': remaining_hours,
            'hours_per_week': hours_per_week,
            'weeks_estimated': round(weeks_needed, 1),
            'days_estimated': round(weeks_needed * 7, 1),
            'confidence_threshold': 0.7
        }
    
    def get_all_goals_with_progress(self) -> List[Dict]:
        """
        Get progress for all available goals.
        
        Returns:
            List of goals with progress percentages
        """
        goals = self.kg.get_all_goals()
        results = []
        
        for goal in goals:
            path = self.generate_learning_path(goal)
            if 'error' not in path:
                results.append({
                    'goal_id': goal,
                    'goal_name': goal.replace('_', ' ').title(),
                    'progress': path['progress_percentage'],
                    'remaining_hours': path['total_estimated_hours'],
                    'skills_required': len(path['skills_required']),
                    'skills_mastered': len([s for s in path['skills_required'] if s in path['known_skills']])
                })
        
        # Sort by progress (descending)
        results.sort(key=lambda x: x['progress'], reverse=True)
        return results
    
    def get_learning_summary(self, goal_id: str) -> Dict:
        """
        Get a comprehensive learning summary for a goal.
        
        Args:
            goal_id: The goal to analyze
        
        Returns:
            Dict with complete learning summary
        """
        path = self.generate_learning_path(goal_id)
        
        if 'error' in path:
            return path
        
        next_recommendation = self.get_next_recommendation(goal_id)
        time_estimate = self.estimate_time_to_goal(goal_id)
        
        # Categorize skills by status
        mastered = []
        in_progress = []
        not_started = []
        
        for skill in path['learning_path']:
            if skill['confidence'] >= 0.7:
                mastered.append(skill)
            elif skill['confidence'] >= 0.3:
                in_progress.append(skill)
            else:
                not_started.append(skill)
        
        return {
            'goal_id': goal_id,
            'goal_name': goal_id.replace('_', ' ').title(),
            'overall_progress': path['progress_percentage'],
            'skills_summary': {
                'total': len(path['learning_path']),
                'mastered': len(mastered),
                'in_progress': len(in_progress),
                'not_started': len(not_started)
            },
            'time_estimate': time_estimate,
            'next_recommendation': next_recommendation,
            'mastered_skills': [{'skill_id': s['skill_id'], 'name': s['name']} for s in mastered],
            'in_progress_skills': [{'skill_id': s['skill_id'], 'name': s['name'], 'confidence': s['confidence']} for s in in_progress],
            'not_started_skills': [{'skill_id': s['skill_id'], 'name': s['name']} for s in not_started]
        }
    
    def record_quiz_result(self, skill_id: str, score: float, max_score: float = 100) -> Dict:
        """
        Record a quiz result and update the skill assessor.
        
        Args:
            skill_id: The skill being tested
            score: Points earned
            max_score: Maximum possible score
        
        Returns:
            Dict with updated confidence and next recommendation
        """
        new_confidence = self.assessor.update_from_quiz(skill_id, score, max_score)
        
        return {
            'skill_id': skill_id,
            'skill_name': self.kg.get_skill_info(skill_id).get('name', skill_id),
            'quiz_score': f"{score}/{max_score}",
            'new_confidence': new_confidence,
            'message': f"Confidence for {skill_id} updated to {new_confidence:.0%}"
        }
    
    def record_completion(self, skill_id: str, time_spent_hours: float) -> Dict:
        """
        Record completion of a skill module.
        
        Args:
            skill_id: The skill completed
            time_spent_hours: Actual time spent learning
        
        Returns:
            Dict with updated confidence
        """
        skill_info = self.kg.get_skill_info(skill_id)
        estimated_hours = skill_info.get('estimated_hours', 5)
        
        new_confidence = self.assessor.update_from_completion(skill_id, time_spent_hours, estimated_hours)
        
        return {
            'skill_id': skill_id,
            'skill_name': skill_info.get('name', skill_id),
            'time_spent': time_spent_hours,
            'estimated_hours': estimated_hours,
            'new_confidence': new_confidence,
            'message': f"Completion recorded for {skill_id}. Confidence: {new_confidence:.0%}"
        }