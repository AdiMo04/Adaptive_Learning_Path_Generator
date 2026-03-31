# 🎯 Adaptive Learning Path Generator

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> An AI-powered personalized learning recommendation system that generates adaptive skill paths using Bayesian confidence tracking and knowledge graphs.

## 🚀 Live Demo

- **API Documentation:** http://localhost:8000/docs (after running locally)
- **Dashboard:** http://localhost:8501 (after running locally)

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **Bayesian Skill Assessment** | Tracks confidence in each skill (0-1) using quiz results, completions, and self-assessments with configurable evidence weights |
| 📊 **Knowledge Graph** | 12+ skills with prerequisite relationships using directed graph structure and topological sorting |
| 🎯 **Personalized Learning Paths** | Generates optimal learning order ensuring prerequisites are mastered before advanced topics |
| ⏱️ **Time Estimation** | Predicts remaining hours based on user's pace and skill difficulty |
| 🚀 **REST API** | 15+ endpoints with automatic Swagger/OpenAPI documentation |
| 📱 **Interactive Dashboard** | Streamlit UI with real-time progress visualization, skill charts, and quiz interface |
| 💾 **User State Persistence** | Save/load user progress across sessions |


## 📚 Skills Knowledge Graph

The system currently supports 12+ technical skills with prerequisite relationships:

| Skill ID | Skill Name | Prerequisites | Est. Hours | Difficulty |
|----------|------------|---------------|------------|------------|
| `python_basics` | Python Basics | None | 10 | ⭐ |
| `functions` | Python Functions | python_basics | 5 | ⭐⭐ |
| `data_structures` | Python Data Structures | python_basics | 8 | ⭐⭐ |
| `error_handling` | Error Handling | functions | 3 | ⭐⭐ |
| `oop` | Object Oriented Programming | functions, data_structures | 12 | ⭐⭐⭐ |
| `http_basics` | HTTP Basics | None | 4 | ⭐⭐ |
| `async_python` | Async Python | functions | 8 | ⭐⭐⭐⭐ |
| `fastapi_basics` | FastAPI Basics | functions, http_basics | 8 | ⭐⭐⭐ |
| `pydantic` | Pydantic | fastapi_basics | 4 | ⭐⭐⭐ |
| `dependency_injection` | FastAPI Dependencies | fastapi_basics | 4 | ⭐⭐⭐ |
| `fastapi_advanced` | FastAPI Advanced | fastapi_basics, async_python | 10 | ⭐⭐⭐⭐ |

### Available Goals

| Goal ID | Goal Name | Required Skills |
|---------|-----------|-----------------|
| `become_python_developer` | Become Python Developer | oop, error_handling, file_io |
| `become_fastapi_developer` | Become FastAPI Developer | fastapi_advanced, pydantic, dependency_injection |
| `become_backend_engineer` | Become Backend Engineer | fastapi_advanced, async_python, http_basics |


**Example:**
- Initial confidence: 30%
- Quiz score: 85% (evidence weight = 0.4)
- New confidence = (0.3 × 0.6 + 0.85 × 0.4) / (0.6 + 0.4) = **52%**
