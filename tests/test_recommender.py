import sys
sys.path.append('.')

from src.knowledge_graph import KnowledgeGraph
from src.skill_assessor import SkillAssessor
from src.recommender import RecommenderEngine

print("=" * 50)
print("RECOMMENDER ENGINE TEST")
print("=" * 50)

# Initialize components
kg = KnowledgeGraph('data/knowledge_graph.json')
assessor = SkillAssessor(user_id="student_001")
recommender = RecommenderEngine(kg, assessor)

print("\n✅ All components initialized")

# Test 1: Show all available goals
print("\n" + "=" * 50)
print("TEST 1: Available Goals")
print("=" * 50)
goals = kg.get_all_goals()
for goal in goals:
    print(f"  - {goal}")

# Test 2: Generate learning path for a goal
print("\n" + "=" * 50)
print("TEST 2: Generate Learning Path")
print("=" * 50)

# First, simulate some learning
print("\n📚 Simulating initial learning...")
assessor.update_from_quiz('python_basics', 85, 100)
assessor.update_from_completion('functions', 6, 5)

path = recommender.generate_learning_path('become_fastapi_developer')
print(f"\nGoal: {path['goal_name']}")
print(f"Overall Progress: {path['progress_percentage']:.1f}%")
print(f"Total Estimated Hours Remaining: {path['total_estimated_hours']}")
print(f"\nLearning Path:")
for skill in path['learning_path'][:5]:  # Show first 5
    print(f"  {skill['skill_id']}: {skill['confidence']:.0%} confidence ({skill['estimated_hours']} hours)")

# Test 3: Get next recommendation
print("\n" + "=" * 50)
print("TEST 3: Next Recommendation")
print("=" * 50)

next_skill = recommender.get_next_recommendation('become_fastapi_developer')
print(f"\nNext skill to learn: {next_skill['skill_name']}")
print(f"Current confidence: {next_skill['current_confidence']:.0%}")
print(f"Estimated hours: {next_skill['estimated_hours']}")
print(f"Prerequisites: {next_skill['prerequisites']}")
if next_skill['missing_prerequisites']:
    print(f"⚠️ Missing prerequisites: {next_skill['missing_prerequisites']}")

# Test 4: Get skill details
print("\n" + "=" * 50)
print("TEST 4: Skill Details")
print("=" * 50)

skill_details = recommender.get_skill_details('fastapi_advanced')
print(f"\nSkill: {skill_details['name']}")
print(f"Description: {skill_details['description']}")
print(f"Difficulty: {skill_details['difficulty']}/5")
print(f"Prerequisites: {skill_details['prerequisites']}")
print(f"Your confidence: {skill_details['user_confidence']:.0%}")
print(f"Prerequisites met: {skill_details['prerequisites_met']}")

# Test 5: Record quiz result
print("\n" + "=" * 50)
print("TEST 5: Record Quiz Result")
print("=" * 50)

result = recommender.record_quiz_result('http_basics', 90, 100)
print(f"\n{result['message']}")

# Test 6: Get updated learning path after quiz
print("\n" + "=" * 50)
print("TEST 6: Updated Learning Path After Quiz")
print("=" * 50)

updated_path = recommender.generate_learning_path('become_fastapi_developer')
print(f"\nUpdated Progress: {updated_path['progress_percentage']:.1f}%")

# Show updated confidences
for skill in updated_path['learning_path'][:5]:
    print(f"  {skill['skill_id']}: {skill['confidence']:.0%} confidence")

# Test 7: Estimate time to goal
print("\n" + "=" * 50)
print("TEST 7: Time to Goal Estimate")
print("=" * 50)

time_estimate = recommender.estimate_time_to_goal('become_fastapi_developer', hours_per_week=10)
print(f"\nRemaining hours: {time_estimate['remaining_hours']}")
print(f"At 10 hours/week: {time_estimate['weeks_estimated']} weeks ({time_estimate['days_estimated']} days)")

# Test 8: Get all goals with progress
print("\n" + "=" * 50)
print("TEST 8: All Goals Progress")
print("=" * 50)

all_goals = recommender.get_all_goals_with_progress()
for goal in all_goals:
    print(f"\n{goal['goal_name']}: {goal['progress']:.1f}% complete")
    print(f"  {goal['skills_mastered']}/{goal['skills_required']} skills mastered")

# Test 9: Get comprehensive learning summary
print("\n" + "=" * 50)
print("TEST 9: Learning Summary")
print("=" * 50)

summary = recommender.get_learning_summary('become_fastapi_developer')
print(f"\n📊 Learning Summary for {summary['goal_name']}")
print(f"Overall Progress: {summary['overall_progress']:.1f}%")
print(f"\nSkills Status:")
print(f"  ✅ Mastered: {summary['skills_summary']['mastered']}")
print(f"  🔄 In Progress: {summary['skills_summary']['in_progress']}")
print(f"  📅 Not Started: {summary['skills_summary']['not_started']}")

if summary['next_recommendation'] and 'skill_name' in summary['next_recommendation']:
    print(f"\n🎯 Next: {summary['next_recommendation']['skill_name']}")

# Test 10: Record completion of a skill
print("\n" + "=" * 50)
print("TEST 10: Record Skill Completion")
print("=" * 50)

completion_result = recommender.record_completion('http_basics', 4.5)
print(f"\n{completion_result['message']}")

# Final progress check
final_path = recommender.generate_learning_path('become_fastapi_developer')
print(f"\n🎯 Final Progress: {final_path['progress_percentage']:.1f}%")

print("\n" + "=" * 50)
print("✅ ALL RECOMMENDER ENGINE TESTS PASSED!")
print("=" * 50)