from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.knowledge_graph import KnowledgeGraph
from src.skill_assessor import SkillAssessor
from src.recommender import RecommenderEngine

# Initialize FastAPI app
app = FastAPI(
    title="Adaptive Learning Path Generator",
    description="AI-powered personalized learning recommendation system",
    version="1.0.0"
)

# Add CORS middleware (allows frontend to call the API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances (will be initialized at startup)
kg = None
assessor = None
recommender = None
current_user_id = "default_user"

# ============ Request/Response Models ============

class QuizResult(BaseModel):
    skill_id: str
    score: float
    max_score: float = 100

class CompletionRecord(BaseModel):
    skill_id: str
    time_spent_hours: float

class GoalRequest(BaseModel):
    goal_id: str
    confidence_threshold: Optional[float] = 0.7

class SelfAssessment(BaseModel):
    skill_id: str
    rating: int
    max_rating: int = 10

class UserState(BaseModel):
    user_id: str

# ============ Startup Event ============

@app.on_event("startup")
async def startup_event():
    """Initialize all components when the API starts"""
    global kg, assessor, recommender
    
    print("🚀 Starting Adaptive Learning Path Generator API...")
    
    # Load knowledge graph
    kg = KnowledgeGraph("data/knowledge_graph.json")
    print("✅ Knowledge Graph loaded")
    
    # Create skill assessor for default user
    assessor = SkillAssessor(user_id=current_user_id)
    print("✅ Skill Assessor initialized")
    
    # Create recommender engine
    recommender = RecommenderEngine(kg, assessor)
    print("✅ Recommender Engine initialized")
    
    print("🎯 API is ready to serve requests!")

# ============ Health Check ============

@app.get("/")
async def root():
    return {
        "service": "Adaptive Learning Path Generator",
        "status": "running",
        "version": "1.0.0",
        "endpoints": [
            "/goals",
            "/learning-path/{goal_id}",
            "/next-recommendation/{goal_id}",
            "/skill/{skill_id}",
            "/quiz",
            "/completion",
            "/self-assessment",
            "/time-estimate/{goal_id}",
            "/progress",
            "/reset-user"
        ]
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "user_id": current_user_id}

# ============ Goal Endpoints ============

@app.get("/goals")
async def get_all_goals():
    """Get all available learning goals with progress"""
    if recommender is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    goals = recommender.get_all_goals_with_progress()
    return {
        "goals": goals,
        "total_goals": len(goals)
    }

@app.get("/learning-path/{goal_id}")
async def get_learning_path(
    goal_id: str,
    confidence_threshold: float = Query(0.7, ge=0, le=1)
):
    """Get personalized learning path for a goal"""
    if recommender is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    path = recommender.generate_learning_path(goal_id, confidence_threshold)
    
    if "error" in path:
        raise HTTPException(status_code=404, detail=path["error"])
    
    return path

@app.get("/next-recommendation/{goal_id}")
async def get_next_recommendation(
    goal_id: str,
    confidence_threshold: float = Query(0.7, ge=0, le=1)
):
    """Get the next skill recommendation for a goal"""
    if recommender is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    recommendation = recommender.get_next_recommendation(goal_id, confidence_threshold)
    
    if recommendation is None:
        raise HTTPException(status_code=404, detail=f"Goal '{goal_id}' not found")
    
    return recommendation

@app.get("/skill/{skill_id}")
async def get_skill_details(skill_id: str):
    """Get detailed information about a skill"""
    if recommender is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    details = recommender.get_skill_details(skill_id)
    
    if "error" in details:
        raise HTTPException(status_code=404, detail=details["error"])
    
    return details

@app.get("/time-estimate/{goal_id}")
async def get_time_estimate(
    goal_id: str,
    hours_per_week: float = Query(10, ge=1, le=40)
):
    """Estimate time to complete a goal"""
    if recommender is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    estimate = recommender.estimate_time_to_goal(goal_id, hours_per_week)
    
    if "error" in estimate:
        raise HTTPException(status_code=404, detail=estimate["error"])
    
    return estimate

@app.get("/progress")
async def get_progress():
    """Get overall progress across all goals"""
    if recommender is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    goals = recommender.get_all_goals_with_progress()
    
    total_progress = sum(g["progress"] for g in goals) / len(goals) if goals else 0
    
    return {
        "user_id": current_user_id,
        "overall_progress": round(total_progress, 1),
        "goals": goals,
        "total_skills_learned": len(assessor.get_known_skills()) if assessor else 0
    }

# ============ Learning Interaction Endpoints ============

@app.post("/quiz")
async def record_quiz_result(quiz: QuizResult):
    """Record a quiz result and update skill confidence"""
    if recommender is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    result = recommender.record_quiz_result(quiz.skill_id, quiz.score, quiz.max_score)
    return result

@app.post("/completion")
async def record_completion(completion: CompletionRecord):
    """Record completion of a skill module"""
    if recommender is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    result = recommender.record_completion(completion.skill_id, completion.time_spent_hours)
    return result

@app.post("/self-assessment")
async def record_self_assessment(assessment: SelfAssessment):
    """Record a user self-assessment for a skill"""
    if assessor is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    new_confidence = assessor.update_from_self_assessment(
        assessment.skill_id, 
        assessment.rating, 
        assessment.max_rating
    )
    
    return {
        "skill_id": assessment.skill_id,
        "self_rating": f"{assessment.rating}/{assessment.max_rating}",
        "new_confidence": new_confidence,
        "message": f"Self-assessment recorded. Confidence updated to {new_confidence:.0%}"
    }

@app.get("/user-confidence")
async def get_user_confidence():
    """Get all skill confidences for the current user"""
    if assessor is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    return {
        "user_id": current_user_id,
        "confidences": assessor.get_all_confidences(),
        "known_skills": assessor.get_known_skills(),
        "weak_skills": assessor.get_weak_skills()
    }

# ============ User Management ============

@app.post("/reset-user")
async def reset_user():
    """Reset the current user's learning progress"""
    global assessor, recommender
    
    assessor = SkillAssessor(user_id=current_user_id)
    recommender = RecommenderEngine(kg, assessor)
    
    return {"message": "User progress reset successfully", "user_id": current_user_id}

@app.post("/switch-user")
async def switch_user(user_state: UserState):
    """Switch to a different user"""
    global assessor, recommender, current_user_id
    
    current_user_id = user_state.user_id
    assessor = SkillAssessor(user_id=current_user_id)
    recommender = RecommenderEngine(kg, assessor)
    
    return {"message": f"Switched to user: {current_user_id}", "user_id": current_user_id}

@app.post("/save-user-state")
async def save_user_state():
    """Save current user state to disk"""
    if assessor is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    assessor.save_state(f"data/user_{current_user_id}_state.json")
    return {"message": f"User state saved for {current_user_id}"}

@app.post("/load-user-state")
async def load_user_state():
    """Load user state from disk"""
    global assessor, recommender
    
    if assessor is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    assessor.load_state(f"data/user_{current_user_id}_state.json")
    recommender = RecommenderEngine(kg, assessor)
    
    return {"message": f"User state loaded for {current_user_id}"}

# ============ Learning Summary ============

@app.get("/learning-summary/{goal_id}")
async def get_learning_summary(goal_id: str):
    """Get comprehensive learning summary for a goal"""
    if recommender is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    summary = recommender.get_learning_summary(goal_id)
    
    if "error" in summary:
        raise HTTPException(status_code=404, detail=summary["error"])
    
    return summary

# ============ Run the Server ============

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )