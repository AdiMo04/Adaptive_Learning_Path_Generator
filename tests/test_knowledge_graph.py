import sys
sys.path.append('.')

from src.knowledge_graph import KnowledgeGraph

# Initialize
kg = KnowledgeGraph('data/knowledge_graph.json')
print("✅ Knowledge Graph loaded")

# Test 1: Get all goals
print(f"\n📚 Available goals: {kg.get_all_goals()}")

# Test 2: Get prerequisites
prereqs = kg.get_prerequisites('fastapi_advanced')
print(f"\n📖 Direct prerequisites for FastAPI Advanced: {prereqs}")

# Test 3: Get all prerequisites (recursive)
all_prereqs = kg.get_all_prerequisites('fastapi_advanced')
print(f"\n🔗 All prerequisites for FastAPI Advanced: {all_prereqs}")

# Test 4: Generate learning path
path = kg.get_learning_path(
    known_skills=['python_basics', 'functions'],
    goal_id='become_fastapi_developer'
)

print("\n🎯 Learning Path for 'become_fastapi_developer':")
print(f"   User already knows: {path['known_skills']}")
print(f"   Missing skills: {path['missing_skills']}")
print(f"   Recommended order: {path['learning_path']}")
print(f"   Total estimated hours: {path['total_estimated_hours']}")

# Test 5: Topological sort
skills = ['fastapi_advanced', 'async_python', 'fastapi_basics', 'functions']
sorted_skills = kg.topological_sort(skills)
print(f"\n🔄 Topological sort of {skills}: {sorted_skills}")

# Test 6: Get all skills needed for a path
all_needed = kg.get_all_skills_in_path(['fastapi_advanced'])
print(f"\n📋 All skills needed for FastAPI Advanced: {all_needed}")

print("\n✅ All tests passed!")