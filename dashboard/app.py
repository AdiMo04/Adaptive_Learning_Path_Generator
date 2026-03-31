import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Adaptive Learning Path Generator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API URL (change if running on different host/port)
API_URL = "https://adaptive-learning-api.onrender.com"

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .skill-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .progress-text {
        font-size: 0.9rem;
        color: #666;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'user_id' not in st.session_state:
    st.session_state.user_id = "default_user"
if 'selected_goal' not in st.session_state:
    st.session_state.selected_goal = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

# Sidebar navigation
st.sidebar.markdown("## 🎯 Navigation")
pages = ["Dashboard", "Learning Path", "Skills", "Progress", "About"]
selected_page = st.sidebar.radio("Go to", pages, index=0)

st.session_state.current_page = selected_page

# User management in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("## 👤 User")
user_id = st.sidebar.text_input("User ID", value=st.session_state.user_id)

if user_id != st.session_state.user_id:
    st.session_state.user_id = user_id
    # Switch user in backend
    try:
        response = requests.post(f"{API_URL}/switch-user", json={"user_id": user_id})
        if response.status_code == 200:
            st.sidebar.success(f"Switched to user: {user_id}")
        else:
            st.sidebar.error("Failed to switch user")
    except:
        st.sidebar.error("API not reachable. Make sure the server is running.")

# Reset user button
if st.sidebar.button("🔄 Reset Progress"):
    try:
        response = requests.post(f"{API_URL}/reset-user")
        if response.status_code == 200:
            st.sidebar.success("Progress reset successfully!")
            st.rerun()
    except:
        st.sidebar.error("Failed to reset progress")

# Check API connection
try:
    health = requests.get(f"{API_URL}/health", timeout=2)
    api_connected = health.status_code == 200
except:
    api_connected = False

if not api_connected:
    st.error("⚠️ Cannot connect to the API. Please make sure the server is running with: `python api/main.py`")
    st.stop()

st.markdown('<div class="main-header">🎯 Adaptive Learning Path Generator</div>', unsafe_allow_html=True)
st.markdown("### Your Personal AI-Powered Learning Assistant")

# ============ DASHBOARD PAGE ============
if st.session_state.current_page == "Dashboard":
    # Fetch progress data
    progress_response = requests.get(f"{API_URL}/progress")
    goals_response = requests.get(f"{API_URL}/goals")
    
    if progress_response.status_code == 200:
        progress_data = progress_response.json()
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Overall Progress",
                f"{progress_data['overall_progress']:.1f}%",
                delta=None
            )
        
        with col2:
            st.metric(
                "Total Goals",
                len(progress_data.get('goals', [])),
                delta=None
            )
        
        with col3:
            completed_goals = sum(1 for g in progress_data.get('goals', []) if g['progress'] == 100)
            st.metric("Completed Goals", completed_goals, delta=None)
        
        with col4:
            st.metric("Skills Mastered", progress_data.get('total_skills_learned', 0), delta=None)
        
        # Goals progress chart
        st.markdown("## 📊 Goals Progress")
        
        if progress_data.get('goals'):
            goals_df = pd.DataFrame(progress_data['goals'])
            fig = px.bar(
                goals_df,
                x='goal_name',
                y='progress',
                title='Progress Across Goals',
                labels={'progress': 'Progress (%)', 'goal_name': 'Goal'},
                color='progress',
                color_continuous_scale='Viridis',
                text='progress'
            )
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent activity placeholder
        st.markdown("## 📈 Learning Activity")
        st.info("Complete quizzes and skill modules to see your progress grow!")
    
    # Get user confidence
    confidence_response = requests.get(f"{API_URL}/user-confidence")
    if confidence_response.status_code == 200:
        confidence_data = confidence_response.json()
        
        st.markdown("## 📚 Your Skills Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ✅ Known Skills (≥70%)")
            known_skills = confidence_data.get('known_skills', [])
            if known_skills:
                for skill in known_skills[:10]:
                    st.markdown(f"<div class='skill-card'>✓ {skill}</div>", unsafe_allow_html=True)
            else:
                st.info("No skills mastered yet. Start by taking quizzes!")
        
        with col2:
            st.markdown("### ⚠️ Skills to Improve (<50%)")
            weak_skills = confidence_data.get('weak_skills', [])
            if weak_skills:
                for skill in weak_skills[:10]:
                    conf = confidence_data['confidences'].get(skill, 0)
                    st.markdown(f"<div class='skill-card' style='border-left-color: #ff6b6b;'>⚠️ {skill} ({conf:.0%})</div>", unsafe_allow_html=True)
            else:
                st.success("Great job! No weak skills to report.")

# ============ LEARNING PATH PAGE ============
elif st.session_state.current_page == "Learning Path":
    # Fetch available goals
    goals_response = requests.get(f"{API_URL}/goals")
    
    if goals_response.status_code == 200:
        goals_data = goals_response.json()
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("## 🎯 Select Your Goal")
            goal_options = [g['goal_name'] for g in goals_data['goals']]
            goal_mapping = {g['goal_name']: g['goal_id'] for g in goals_data['goals']}
            
            selected_goal_name = st.selectbox("Choose a learning goal:", goal_options)
            selected_goal_id = goal_mapping[selected_goal_name]
            
            threshold = st.slider("Confidence Threshold", 0.5, 0.9, 0.7, 0.05)
            
            if st.button("Generate Learning Path", type="primary"):
                st.session_state.selected_goal = selected_goal_id
        
        with col2:
            if st.session_state.selected_goal:
                path_response = requests.get(f"{API_URL}/learning-path/{st.session_state.selected_goal}?confidence_threshold={threshold}")
                
                if path_response.status_code == 200:
                    path_data = path_response.json()
                    
                    st.markdown(f"## 📖 Learning Path: {path_data['goal_name']}")
                    st.markdown(f"**Progress:** {path_data['progress_percentage']:.1f}%")
                    st.markdown(f"**Estimated hours remaining:** {path_data['total_estimated_hours']}")
                    
                    st.markdown("### 📋 Recommended Learning Order")
                    
                    for i, skill in enumerate(path_data['learning_path'], 1):
                        col_a, col_b = st.columns([3, 1])
                        
                        with col_a:
                            if skill['confidence'] >= threshold:
                                status = "✅"
                            elif skill['confidence'] >= 0.3:
                                status = "🔄"
                            else:
                                status = "📅"
                            
                            st.markdown(f"**{i}. {skill['name']}** {status}")
                            st.caption(f"📖 {skill['skill_id']} • {skill['estimated_hours']} hours • Difficulty: {'⭐' * skill['difficulty']}")
                        
                        with col_b:
                            st.markdown(f"Confidence: {skill['confidence']:.0%}")
                    
                    st.markdown("---")
                    st.info("Take quizzes and complete modules to increase your confidence in each skill!")
                else:
                    st.error("Failed to load learning path")

# ============ SKILLS PAGE ============
elif st.session_state.current_page == "Skills":
    st.markdown("## 📚 All Skills")
    
    # Get all skills
    skills_response = requests.get(f"{API_URL}/user-confidence")
    
    if skills_response.status_code == 200:
        skills_data = skills_response.json()
        confidences = skills_data['confidences']
        
        # Convert to DataFrame for better visualization
        skills_df = pd.DataFrame([
            {"Skill": skill, "Confidence": conf, "Status": "Known" if conf >= 0.7 else "In Progress" if conf >= 0.3 else "Not Started"}
            for skill, conf in confidences.items()
        ]).sort_values("Confidence", ascending=False)
        
        # Confidence gauge chart
        fig = go.Figure()
        
        for skill in skills_df.head(10).iterrows():
            fig.add_trace(go.Bar(
                x=[skill[1]['Confidence']],
                y=[skill[1]['Skill']],
                orientation='h',
                text=[f"{skill[1]['Confidence']:.0%}"],
                textposition='outside',
                marker_color='#1f77b4'
            ))
        
        fig.update_layout(
            title="Top 10 Skills by Confidence",
            xaxis_title="Confidence Level",
            yaxis_title="Skill",
            xaxis=dict(range=[0, 1]),
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Quiz section
        st.markdown("## 📝 Take a Quiz")
        
        col1, col2 = st.columns(2)
        
        with col1:
            quiz_skill = st.selectbox("Select skill to test:", list(confidences.keys()))
        
        with col2:
            quiz_score = st.slider("Your score (0-100):", 0, 100, 70)
        
        if st.button("Submit Quiz Result", type="primary"):
            response = requests.post(f"{API_URL}/quiz", json={
                "skill_id": quiz_skill,
                "score": quiz_score,
                "max_score": 100
            })
            
            if response.status_code == 200:
                result = response.json()
                st.success(result.get('message', 'Quiz recorded!'))
                st.rerun()
            else:
                st.error("Failed to record quiz")
        
        # Self-assessment section
        st.markdown("## 📝 Self-Assessment")
        st.caption("Rate your confidence in a skill (1-10)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            assess_skill = st.selectbox("Select skill to assess:", list(confidences.keys()), key="assess")
        
        with col2:
            self_rating = st.slider("Your rating (1-10):", 1, 10, 5)
        
        if st.button("Submit Self-Assessment"):
            response = requests.post(f"{API_URL}/self-assessment", json={
                "skill_id": assess_skill,
                "rating": self_rating,
                "max_rating": 10
            })
            
            if response.status_code == 200:
                result = response.json()
                st.success(result.get('message', 'Assessment recorded!'))
                st.rerun()
            else:
                st.error("Failed to record assessment")

# ============ PROGRESS PAGE ============
elif st.session_state.current_page == "Progress":
    st.markdown("## 📈 Your Learning Journey")
    
    # Get progress data
    progress_response = requests.get(f"{API_URL}/progress")
    confidence_response = requests.get(f"{API_URL}/user-confidence")
    
    if progress_response.status_code == 200:
        progress_data = progress_response.json()
        
        # Overall progress gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=progress_data['overall_progress'],
            title={'text': "Overall Progress"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#1f77b4"},
                'steps': [
                    {'range': [0, 33], 'color': "#ffcccc"},
                    {'range': [33, 66], 'color': "#ffffcc"},
                    {'range': [66, 100], 'color': "#ccffcc"}
                ]
            }
        ))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Goals progress table
        if progress_data.get('goals'):
            st.markdown("## 🎯 Goals Progress")
            goals_df = pd.DataFrame(progress_data['goals'])
            st.dataframe(
                goals_df[['goal_name', 'progress', 'skills_mastered', 'skills_required']],
                use_container_width=True,
                column_config={
                    "progress": st.column_config.ProgressColumn("Progress", format="%.1f%%"),
                    "goal_name": "Goal",
                    "skills_mastered": "Skills Mastered",
                    "skills_required": "Skills Required"
                }
            )
    
    if confidence_response.status_code == 200:
        confidence_data = confidence_response.json()
        
        st.markdown("## 📊 Skills Distribution")
        
        # Skills pie chart
        confidences = confidence_data['confidences']
        mastered = sum(1 for c in confidences.values() if c >= 0.7)
        in_progress = sum(1 for c in confidences.values() if 0.3 <= c < 0.7)
        not_started = sum(1 for c in confidences.values() if c < 0.3)
        
        fig = px.pie(
            values=[mastered, in_progress, not_started],
            names=["Mastered (≥70%)", "In Progress (30-70%)", "Not Started (<30%)"],
            title="Skills Distribution",
            color_discrete_sequence=["#2ecc71", "#f39c12", "#e74c3c"]
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ============ ABOUT PAGE ============
else:
    st.markdown("## ℹ️ About This Project")
    
    st.markdown("""
    ### 🎯 Adaptive Learning Path Generator
    
    This system uses **AI and Bayesian inference** to create personalized learning paths based on your current skill level.
    
    ### 🧠 How It Works
    
    1. **Knowledge Graph**: Skills are connected with prerequisites
    2. **Skill Assessment**: Bayesian model tracks your confidence in each skill
    3. **Adaptive Recommendations**: The system recommends the next skill you should learn
    4. **Real-time Updates**: As you take quizzes and complete modules, your path adapts
    
    ### 📊 Key Features
    
    - **Personalized Learning Paths**: Based on what you already know
    - **Skill Confidence Tracking**: Bayesian updating with each quiz
    - **Time Estimates**: Realistic estimates based on your pace
    - **Progress Visualization**: Track your journey across multiple goals
    
    ### 🛠️ Tech Stack
    
    - **Backend**: FastAPI, Python
    - **Knowledge Graph**: Custom JSON-based graph with topological sorting
    - **AI/ML**: Bayesian inference for skill confidence
    - **Frontend**: Streamlit
    - **Visualization**: Plotly
    """)
    
    st.markdown("### 📁 Project Structure")
    st.code("""
learning-path-recommender/
├── src/
│   ├── knowledge_graph.py   # Skill relationships
│   ├── skill_assessor.py    # Bayesian confidence
│   └── recommender.py       # Path generation
├── api/
│   └── main.py              # REST API
├── dashboard/
│   └── app.py              # Streamlit UI
├── data/
│   └── knowledge_graph.json
└── tests/
    └── test_*.py
    """, language="text")
    
    st.markdown("""
    ### 🚀 Getting Started
    
    1. Make sure the API is running: `python api/main.py`
    2. Open this dashboard
    3. Select a goal and start learning!
    
    ### 👨‍💻 Built By
    
    Built as a portfolio project demonstrating AI/ML, API development, and full-stack skills.
    """)