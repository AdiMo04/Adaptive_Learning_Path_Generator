from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict
import json

class SkillAssessor:
    """
    Tracks user's skill proficiency using Bayesian updating.
    
    Each skill has a confidence score (0-1) that updates as:
    - User takes quizzes
    - User spends time on material
    - User marks skills as complete
    
    Bayesian formula: posterior = (prior * prior_weight + evidence * evidence_weight) / (prior_weight + evidence_weight)
    """
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        # Confidence for each skill (0-1)
        self.confidence: Dict[str, float] = defaultdict(lambda: 0.3)  # Start at 30% confidence
        # History of updates
        self.history: Dict[str, List[Dict]] = defaultdict(list)
    
    def update_from_quiz(self, skill_id: str, score: float, max_score: float = 100) -> float:
        """
        Update skill confidence based on quiz performance.
        
        Args:
            skill_id: The skill being tested
            score: Points earned (e.g., 85)
            max_score: Maximum possible score (e.g., 100)
        
        Returns:
            New confidence score
        """
        normalized_score = score / max_score  # Convert to 0-1
        
        # Bayesian update
        prior = self.confidence[skill_id]
        
        # Weight: quizzes are strong evidence
        evidence_weight = 0.4
        prior_weight = 0.6
        
        new_confidence = (prior * prior_weight + normalized_score * evidence_weight) / (prior_weight + evidence_weight)
        
        # Record history
        self.history[skill_id].append({
            'type': 'quiz',
            'score': normalized_score,
            'raw_score': score,
            'max_score': max_score,
            'prior': prior,
            'new': new_confidence,
            'timestamp': datetime.now().isoformat()
        })
        
        self.confidence[skill_id] = new_confidence
        return new_confidence
    
    def update_from_completion(self, skill_id: str, time_spent_hours: float, estimated_hours: float) -> float:
        """
        Update skill confidence when user completes a module.
        
        Args:
            skill_id: The skill completed
            time_spent_hours: Actual time spent learning
            estimated_hours: Estimated time from knowledge graph
        """
        prior = self.confidence[skill_id]
        
        # Calculate progress ratio
        if estimated_hours > 0:
            progress = min(time_spent_hours / estimated_hours, 1.5)
        else:
            progress = 0.8
        
        # Completion is strong evidence, but less than quiz
        evidence_weight = 0.25
        prior_weight = 0.75
        
        # Progress maps to confidence: 0.5-1.0 range
        evidence = 0.5 + (progress * 0.5)
        
        new_confidence = (prior * prior_weight + evidence * evidence_weight) / (prior_weight + evidence_weight)
        
        self.history[skill_id].append({
            'type': 'completion',
            'time_spent': time_spent_hours,
            'estimated_hours': estimated_hours,
            'progress': progress,
            'prior': prior,
            'new': new_confidence,
            'timestamp': datetime.now().isoformat()
        })
        
        self.confidence[skill_id] = new_confidence
        return new_confidence
    
    def update_from_self_assessment(self, skill_id: str, self_rating: int, max_rating: int = 10) -> float:
        """
        Update based on user's self-assessment (less reliable).
        
        Args:
            skill_id: The skill being assessed
            self_rating: User's rating (e.g., 7)
            max_rating: Maximum rating (e.g., 10)
        """
        normalized = self_rating / max_rating
        
        prior = self.confidence[skill_id]
        
        # Self-assessment is weaker evidence
        evidence_weight = 0.15
        prior_weight = 0.85
        
        new_confidence = (prior * prior_weight + normalized * evidence_weight) / (prior_weight + evidence_weight)
        
        self.history[skill_id].append({
            'type': 'self_assessment',
            'rating': self_rating,
            'max_rating': max_rating,
            'normalized': normalized,
            'prior': prior,
            'new': new_confidence,
            'timestamp': datetime.now().isoformat()
        })
        
        self.confidence[skill_id] = new_confidence
        return new_confidence
    
    def get_confidence(self, skill_id: str) -> float:
        """Get current confidence for a skill"""
        return self.confidence[skill_id]
    
    def get_all_confidences(self) -> Dict[str, float]:
        """Get confidence for all skills"""
        return dict(self.confidence)
    
    def get_known_skills(self, threshold: float = 0.7) -> List[str]:
        """
        Get skills where confidence is above threshold.
        
        Args:
            threshold: Minimum confidence to consider skill "known" (0-1)
        
        Returns:
            List of skill IDs the user knows
        """
        return [skill for skill, conf in self.confidence.items() if conf >= threshold]
    
    def get_weak_skills(self, threshold: float = 0.5) -> List[str]:
        """
        Get skills where confidence is below threshold (needs improvement).
        
        Args:
            threshold: Maximum confidence to consider skill "weak" (0-1)
        
        Returns:
            List of skill IDs that need improvement
        """
        return [skill for skill, conf in self.confidence.items() if conf < threshold]
    
    def get_skill_gaps(self, required_skills: List[str], threshold: float = 0.7) -> List[Dict]:
        """
        Identify which required skills are below threshold.
        
        Args:
            required_skills: List of skills needed for a goal
            threshold: Confidence threshold for "known"
        
        Returns:
            List of skills with their current confidence and gap
        """
        gaps = []
        for skill in required_skills:
            conf = self.get_confidence(skill)
            if conf < threshold:
                gaps.append({
                    'skill': skill,
                    'current_confidence': conf,
                    'required_confidence': threshold,
                    'gap': threshold - conf
                })
        
        return sorted(gaps, key=lambda x: x['gap'], reverse=True)
    
    def get_history(self, skill_id: Optional[str] = None) -> Dict:
        """
        Get update history for a skill or all skills.
        
        Args:
            skill_id: Optional skill ID. If None, returns all history.
        """
        if skill_id:
            return {skill_id: self.history.get(skill_id, [])}
        return dict(self.history)
    
    def save_state(self, filepath: str = "data/user_state.json"):
        """Save user confidence state to file"""
        state = {
            'user_id': self.user_id,
            'confidence': dict(self.confidence),
            'history': dict(self.history),
            'saved_at': datetime.now().isoformat()
        }
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        print(f"✅ State saved to {filepath}")
    
    def load_state(self, filepath: str = "data/user_state.json"):
        """Load user confidence state from file"""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            self.user_id = state['user_id']
            self.confidence = defaultdict(lambda: 0.3, state['confidence'])
            self.history = defaultdict(list, state['history'])
            print(f"✅ State loaded from {filepath}")
        except FileNotFoundError:
            print(f"⚠️ No saved state found at {filepath}")
    
    def get_recommended_next_skill(self, learning_path: List[str], threshold: float = 0.7) -> Optional[str]:
        """
        Get the next skill to learn based on current confidence.
        
        Args:
            learning_path: Ordered list of skills to learn
            threshold: Confidence threshold to consider skill "mastered"
        
        Returns:
            The next skill that needs attention, or None if all are mastered
        """
        for skill in learning_path:
            if self.get_confidence(skill) < threshold:
                return skill
        return None
    
    def print_summary(self):
        """Print a summary of user's skill confidence"""
        print(f"\n📊 Skill Confidence Summary for User: {self.user_id}")
        print("-" * 40)
        
        known = self.get_known_skills()
        weak = self.get_weak_skills()
        
        print(f"Known skills (≥70%): {len(known)}")
        for skill in known[:5]:  # Show first 5
            print(f"  ✅ {skill}: {self.get_confidence(skill):.0%}")
        
        print(f"\nSkills needing improvement (<50%): {len(weak)}")
        for skill in weak[:5]:  # Show first 5
            print(f"  ⚠️ {skill}: {self.get_confidence(skill):.0%}")