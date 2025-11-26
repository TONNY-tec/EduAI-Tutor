import streamlit as st
from google import genai
from google.genai import types
import requests
import logging


# --- Defining variables and parameters  ---
REGION = "global"
PROJECT_ID = "eduai-478610" # TO DO: Insert Project ID
GEMINI_MODEL_NAME = "gemini-2.5-flash"

# Set the title and icon for your Streamlit app.
# This should be the first Streamlit command in your script.
st.set_page_config(
    page_title="EduAI Tutor",
    page_icon="📚", 
    layout="centered",
)

# 🎨 Custom CSS for Blue Background and Personalized Icons
# Injecting custom CSS to change the page color and icon styles
st.markdown("""
<style>
/* Change the main background color of the entire page to a light blue */
.stApp {
    background-color: #E6F0FF; /* A light, academic blue */
}

/* --- ICON STYLES (NEW ICONS) --- */

/* Target the assistant (AI tutor) messages */
.stChatMessage:nth-child(odd) .st-emotion-cache-1c7icp5.e1gr2sg30 > div:first-child {
    content: "💡"; /* Tutor icon: Light Bulb (illumination/guidance) */
    font-size: 24px;
    background-color: #0047AB !important; /* Cobalt blue for tutor */
    color: white !important; /* Ensure the emoji is visible */
}

/* Target the user (student) messages */
.stChatMessage:nth-child(even) .st-emotion-cache-1c7icp5.e1gr2sg30 > div:first-child {
    content: "💭"; /* Student icon: Thought Bubble (question/idea) */
    font-size: 24px;
    background-color: #6495ED !important; /* Cornflower blue for student */
    color: white !important; /* Ensure the emoji is visible */
}

/* Style the chat input box to match the theme */
.st-emotion-cache-1c7icp5.e1gr2sg30 {
    border-radius: 15px;
}

</style>
""", unsafe_allow_html=True)


# --- AI and API Configuration ---
    
# This system prompt defines the AI's persona and rules.
# It's crucial for guiding the AI to act as a Socratic tutor.
system_instructions = """
You are 'EduAI Tutor,' a personalized, Socratic AI learning companion specializing in high school level Science and Math. Your primary goal is to foster deep understanding, critical thinking, and problem-solving skills.

CORE METHODOLOGY: "GUIDE, DON'T JUST GIVE."
 
STRICT RULES:
1.  **Socratic Dialogue:** Respond by asking simplified, guiding questions. Your response must *never* contain the final answer initially.
2.  **Adaptive Simplification:** If the student's question is complex, break it into smaller, foundational components before asking your question.
3.  **Feedback Check & Dynamic Adjustment:** You must analyze the student's current message for specific feedback:
    * **If the student uses a keyword like "I get it" or "understood" OR gives a correct answer:** Provide positive reinforcement, summarize the learned concept concisely, and suggest a logical, curated follow-up question to guide them along a learning path.
    * **If the student uses a keyword like "A bit confusing" or "not sure" OR gives a partially correct answer:** Gently rephrase the previous question, offer a hint, or provide a simple analogy to address the specific point of confusion.
    * **If the student explicitly uses a keyword like "I'm lost," "stuck," or "need the answer," OR if they upload an image of a problem:** ONLY THEN provide a detailed, step-by-step explanation. Ensure this detailed answer is grounded in a relatable, real-world context to make the abstract concrete.
4.  **Resource Guidance:** In your guiding response, always encourage the student to consult external resources (e.g., "Think about what happens to pressure when volume changes," or "You might want to quickly search for the definition of the Pythagorean theorem.") before asking your next guiding question.
5.  **Tone:** Maintain a patient, encouraging, and supportive tone at all times.
6.  **Multimodal Input:** If the input includes an image, acknowledge the visual and treat it as a problem statement requiring Socratic guidance first (Rule 1).
"""

# Add new instructions for response structure
system_instructions += """

RESPONSE STRUCTURE: Every response MUST conclude with two sections. The topic links MUST be a valid URL:
1.  **"Here are some topics and resources to help you find the answer:"** followed by a bulleted list of 3-5 relevant topics for further reading. Each topic should be presented as "Topic Name - Read more".
2.  **"How are you feeling about this topic?"** followed by a list of predefined student response options, each on a new line: "I get it!", "A bit confusing.", "I'm lost.", "Explain it to me".
"""

# TODO: Define the weather tool function declaration

# TODO: Define the get_current_temperature function


# --- Initialize the Vertex AI Client ---
try:
      # TODO: Initialize the Vertex AI client
      client = genai.Client(
          vertexai=True,
          project=PROJECT_ID,
          location=REGION,
      )
    
except Exception as e:
    st.error(f"Error initializing VertexAI client: {e}")
    st.stop()


# TODO: Add the get_chat function here in Task 15.

# --- Call the Model ---

# --- Call the Model (Updated for Context & Multimodal) ---
def call_model(messages: list, model_name: str) -> str:
    """
    Interacts with the LLM using the full chat history for context and handles optional image uploads.

    Args:
        messages (list): The list of messages in the chat history.
        model_name (str): The name of the language model to use.
    Returns:
        str: The response text from the model.
    """
    try:
        # Convert Streamlit messages history to GenAI contents format (list of Content objects)
        contents = []
        for msg in messages:
            # Streamlit uses 'assistant' and 'user'. GenAI uses 'model' for the AI's role.
            role = "model" if msg["role"] == "assistant" else "user"
            
            # Skip the initial welcome message from the assistant for the API call 
            if msg["role"] == "assistant" and msg["content"].startswith("Hello! I am EduAI Tutor"):
                continue

            parts = [{"text": msg["content"]}]
            contents.append(types.Content(role=role, parts=parts))

        generate_content_config = types.GenerateContentConfig(
            system_instruction=[
                types.Part.from_text(text=system_instructions)
            ],
        )

        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=generate_content_config,
        )

        # Custom links for each topic
        topic_links = {
            "Pythagorean Theorem": "<a href='https://en.wikipedia.org/wiki/Pythagorean_theorem' target='_blank'>Pythagorean Theorem</a>",
            "Kinetic Energy": "<a href='https://en.wikipedia.org/wiki/Kinetic_energy' target='_blank'>Kinetic Energy</a>",
            "Cell Structure": "<a href='https://en.wikipedia.org/wiki/Cell_(biology)' target='_blank'>Cell Structure</a>",
            "Photosynthesis": "<a href='https://en.wikipedia.org/wiki/Photosynthesis' target='_blank'>Photosynthesis</a>",
            "Algebraic Equations": "<a href='https://en.wikipedia.org/wiki/Algebraic_equation' target='_blank'>Algebraic Equations</a>",
        }

        # Replace topic names with links
        response_text = response.text
        for topic, link in topic_links.items():
            response_text = response_text.replace(f"{topic} - Read more", f"{link} - Read more")

        return response_text
    except Exception as e:
        return f"Error: {e}"


# --- Presentation Tier (Streamlit) ---
# Set the title of the Streamlit application
st.title("📚 EduAI Tutor")

# Initialize session state variables if they don't exist
if "messages" not in st.session_state:
    # Initialize the chat history with a welcome message
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hello! I am EduAI Tutor. Ask me a complex question, and I will guide you on how to find the answer yourself.?"}
    ]

# Display the chat history
for msg in st.session_state.messages: 
    st.chat_message(msg["role"]).write(msg["content"], unsafe_allow_html=True)

# Get user input
if prompt := st.chat_input():
    # Add the user's message to the chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display the user's message
    st.chat_message("user").write(prompt)

    # Show a spinner while waiting for the model's response
    with st.spinner(" EduAI Tutor is Thinking..."):
        # Get the model's response using the call_model function
        model_response = call_model(st.session_state.messages, GEMINI_MODEL_NAME)
        # Add the model's response to the chat history
        st.session_state.messages.append(
            {"role": "assistant", "content": model_response}
        )
        # Display the model's response
        st.chat_message("assistant").write(model_response, unsafe_allow_html=True)