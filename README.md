🎓 EduAI Tutor: Personalized Socratic Learning Companion

EduAI Tutor is a cutting-edge educational solution designed to address the challenge of AI dependency by emphasizing critical thinking and deep understanding. It utilizes a Socratic guidance methodology where the AI asks guiding questions instead of giving instant answers. This approach fosters independent problem-solving skills, ensures deeper comprehension, and delivers a truly adaptive and effective personalized learning experience.

Brief Project Description:
EduAI Tutor tackles AI's critical thinking challenge via a Socratic learning system. It avoids instant answers, guiding students step-by-step and adapting based on their feedback. This fosters independent thinking, deep comprehension, and personalized learning.

💡 Core Philosophy: Guide, Don't Give

The system is built around Socratic dialogue, ensuring students actively participate in finding solutions. It simplifies complex  problems and dynamically adapts its approach based on explicit student feedback ("I get it!", "A bit confusing.", "Explain it to me").

🚀 Get Started

To see the system in action and understand the technical details, check out the resources below.

🎥 Live Demo Video

Watch a quick run-through of the EduAI Tutor's core features, user interface, and the personalized Socratic interaction model.

[EduAi live demo](https://drive.google.com/file/d/1ukgNhs4VSfv7L3WVIU1Jokj_xoY6Vw1K/view?usp=sharing)

📊 Presentation & Technical Overview

Review the official presentation slides, which cover the project's architecture, technology stack, problem statement, and future roadmap.

[View the Complete Presentation Slides](https://docs.google.com/presentation/d/1IcP_kq7xGRsg6w40srHSR2vDo883kU59/edit?usp=sharing&ouid=108632074655327542041&rtpof=true&sd=true)

🛠️ Technology Stack

Frontend / Core Logic: Python (Streamlit)

AI / LLM: Google Gemini API (gemini-2.5-flash model, running on Vertex AI)

Grounding: Google Search Grounding Tool (for real-time resource links)

Deployment: Single-file Streamlit application (using app.py)

📋 Installation

This project is a single-file Python/Streamlit application.

Prerequisites

Python 3.8+

A Google Cloud Project with the Vertex AI API enabled.

gcloud authentication setup for Application Default Credentials (ADC).

Setup and Run

# 1. Clone the repository
git clone [https://github.com/TONNY-tec/EduAI-Tutor.git]

# 2. Navigate to the project directory
cd eduai-tutor

# 3. Install required Python packages
pip install streamlit google-genai

# 4. Set up authentication for Google Cloud
# This command ensures your application can access Vertex AI
gcloud auth application-default login

# 5. Run the Streamlit application
streamlit run app.py
