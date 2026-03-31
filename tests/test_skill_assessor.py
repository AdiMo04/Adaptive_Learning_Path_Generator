import sys
sys.path.append('.')

from src.skill_assessor import SkillAssessor

# Create a new assessor for a user
assessor = SkillAssessor(user_id="test_user_001")
print("✅ Skill Assessor created")

# Test 1: Initial confidence (should be 0.3 or 30%)
print(f"\n📊 Initial confidence for 'python_basics': {assessor.get_confidence('python_basics'):.0%}")

# Test 2: Update from quiz (score 85/100)
new_conf = assessor.update_from_quiz('python_basics', score=85, max_score=100)
print(f"\n📝 After quiz (85%): {new_conf:.0%}")

# Test 3: Update from another quiz (score 95/100)
new_conf = assessor.update_from_quiz('python_basics', score=95, max_score=100)
print(f"📝 After second quiz (95%): {new_conf:.0%}")

# Test 4: Update from completion
assessor.update_from_completion('functions', time_spent_hours=6, estimated_hours=5)
print(f"\n✅ After completing 'functions': {assessor.get_confidence('functions'):.0%}")

# Test 5: Update from self-assessment
assessor.update_from_self_assessment('async_python', self_rating=3, max_rating=10)
print(f"📝 Self-assessment for 'async_python' (3/10): {assessor.get_confidence('async_python'):.0%}")

# Test 6: Get known skills
known = assessor.get_known_skills(threshold=0.7)
print(f"\n🎯 Known skills (≥70%): {known}")

# Test 7: Get weak skills
weak = assessor.get_weak_skills(threshold=0.5)
print(f"⚠️ Weak skills (<50%): {weak}")

# Test 8: Skill gaps for a goal
required_skills = ['python_basics', 'functions', 'async_python', 'fastapi_basics']
gaps = assessor.get_skill_gaps(required_skills, threshold=0.7)
print(f"\n📋 Skill gaps for {required_skills}:")
for gap in gaps:
    print(f"   - {gap['skill']}: {gap['current_confidence']:.0%} (need {gap['required_confidence']:.0%})")

# Test 9: Get next recommended skill
learning_path = ['python_basics', 'functions', 'async_python', 'fastapi_basics']
next_skill = assessor.get_recommended_next_skill(learning_path, threshold=0.7)
print(f"\n🎯 Next recommended skill: {next_skill}")

# Test 10: Print full summary
assessor.print_summary()

# Test 11: Save and load state
assessor.save_state("data/test_user_state.json")

# Create a new assessor and load the state
new_assessor = SkillAssessor(user_id="test_user_002")
new_assessor.load_state("data/test_user_state.json")
print(f"\n✅ Loaded state for {new_assessor.user_id}")
print(f"   Confidence for 'python_basics': {new_assessor.get_confidence('python_basics'):.0%}")

print("\n✅ All Skill Assessor tests passed!")