import os
import streamlit as st
from google import genai
from google.genai import types
import logging

# --- Configuration ---
# Set logging level (optional, but good for debugging)
logging.basicConfig(level=logging.INFO)

# --- Defining variables and parameters ---
REGION = "global"
# TO DO: Insert your actual Project ID here
PROJECT_ID = "eduai-478610" 
GEMINI_MODEL_NAME = "gemini-2.5-flash"

# Set the title and icon for your Streamlit app.
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

/* --- ICON STYLES --- */

/* Target the assistant (AI tutor) messages */
/* Note: Streamlit uses emojis/text as role icons by default. We adjust the color here. */
.stChatMessage:nth-child(odd) .st-emotion-cache-1c7icp5.e1gr2sg30 > div:first-child {
    background-color: #0047AB !important; /* Cobalt blue for tutor */
    color: white !important;
}

/* Target the user (student) messages */
.stChatMessage:nth-child(even) .st-emotion-cache-1c7icp5.e1gr2sg30 > div:first-child {
    background-color: #6495ED !important; /* Cornflower blue for student */
    color: white !important;
}

/* Style the chat input box to match the theme */
.st-emotion-cache-1c7icp5.e1gr2sg30 {
    border-radius: 15px;
}

/* Ensures the markdown links rendered as HTML are styled nicely */
a:link, a:visited {
    color: #0047AB; /* Dark blue for links */
    text-decoration: underline;
}

/* Custom button styling for the feedback options */
.feedback-button {
    background-color: #ffffff;
    color: #0047AB;
    border: 1px solid #0047AB;
    border-radius: 8px;
    padding: 8px 15px;
    margin: 5px 5px 5px 0;
    cursor: pointer;
    transition: background-color 0.2s;
    font-size: 14px;
    font-weight: 600;
}

.feedback-button:hover {
    background-color: #0047AB;
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)


# --- AI and API Configuration: System Instructions ---
system_instructions = """
You are 'EduAI Tutor,' a personalized, Socratic AI learning companion specializing in high school level Science and Math. Your primary goal is to foster deep understanding, critical thinking, and problem-solving skills.

CORE METHODOLOGY: "GUIDE, DON'T JUST GIVE."
 
STRICT RULES:
1.  **Socratic Dialogue:** Respond by asking simplified, guiding questions. Your response must *never* contain the final answer initially.
2.  **Adaptive Simplification:** If the student's question is complex, break it into smaller, foundational components before asking your question.
3.  **Feedback Check & Dynamic Adjustment:** Use the keywords provided by the student to adjust your response.
    * **If the student uses a keyword like "I get it" or "understood" OR gives a correct answer:** Provide positive reinforcement, summarize the learned concept concisely, and suggest a logical, curated follow-up question.
    * **If the student uses a keyword like "A bit confusing" or "not sure" OR gives a partially correct answer:** Gently rephrase the previous question, offer a hint, or provide a simple analogy.
    * **If the student explicitly uses a keyword like "I'm lost," "stuck," or "need the answer," OR if they upload an image of a problem:** ONLY THEN provide a detailed, step-by-step explanation.
4.  **Resource Guidance & Grounding:** **ALWAYS** find 5 relevant external resources for the topic being discussed. You must use the grounding tool for this.
5.  **Tone:** Maintain a patient, encouraging, and supportive tone at all times.

RESPONSE STRUCTURE: Every response MUST conclude with two sections.
1.  **"📚 Related Resources for Deeper Learning:"** followed by a bulleted list of 5 topics and their generated links. **Crucially, format these as standard Markdown links: `[Topic Name](URL)`**.
2.  **The final line of your response MUST be the exact sentence: "How are you feeling about this topic?"** DO NOT include the predefined student response options (e.g., "I get it!", "A bit confusing.", etc.) in your text, as the UI handles the buttons.
"""


# --- Initialize the Vertex AI Client ---
try:
    # Initialize the Gemini client using Vertex AI configuration
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=REGION,
    )
except Exception as e:
    st.error(f"Error initializing VertexAI client. Please check your PROJECT_ID: {e}")
    st.stop()


# --- Call the Model (With Grounding) ---
def call_model(messages: list, model_name: str) -> str:
    """
    Interacts with the LLM using the full chat history for context and enables Google Search grounding
    to fetch real-time links.

    Args:
        messages (list): The list of messages in the chat history.
        model_name (str): The name of the language model to use.
    Returns:
        str: The response text from the model.
    """
    try:
        # Convert Streamlit messages history to GenAI contents format
        contents = []
        for msg in messages:
            # Skip messages without content (shouldn't happen, but good practice)
            if not msg.get("content"):
                continue

            # GenAI uses 'model' for the AI's role.
            role = "model" if msg["role"] == "assistant" else "user"
            
            # Skip the initial welcome message from the assistant for the API call 
            if msg["role"] == "assistant" and msg["content"].startswith("Hello! I am EduAI Tutor"):
                continue

            # Ensure we pass a proper Content object with the role and text part
            parts = [types.Part.from_text(text=msg["content"])]
            contents.append(types.Content(role=role, parts=parts))

        # Configuration for the call, including system instructions and the grounding tool
        generate_content_config = types.GenerateContentConfig(
            system_instruction=[
                types.Part.from_text(text=system_instructions)
            ],
            # This enables the model to use Google Search to find real-time links and topics.
            tools=[{"google_search": {}}], 
            temperature=0.9
        )

        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=generate_content_config,
        )

        # The model is instructed to output Markdown links [Topic](URL), 
        # which Streamlit will render as clickable links because of unsafe_allow_html=True.
        return response.text
    
    except Exception as e:
        logging.error(f"Gemini API Error: {e}")
        return f"🚨 **Error:** Failed to communicate with the AI Tutor. Details: {e}"


# --- Button Callback Function ---
def handle_feedback_click(feedback_text):
    """
    Handles the click event from the feedback buttons.
    1. Sends the feedback text as a new user message.
    2. Runs the model to generate the next response.
    3. Triggers a rerun of the app to display the new chat.
    """
    # 1. Add the selected feedback as a user message
    st.session_state.messages.append({"role": "user", "content": feedback_text})
    
    # 2. Set a flag to process the new message immediately
    st.session_state.process_feedback = True

# --- Presentation Tier (Streamlit) ---
# Set the title of the Streamlit application
st.title("📚 EduAI Tutor")

# Initialize session state variables if they don't exist
if "messages" not in st.session_state:
    # Initialize the chat history with a welcome message
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hello! I am EduAI Tutor. Ask me a complex topic of your interest and I will guide you on how to find the answer yourself."}
    ]

# Initialize feedback options flag
if "show_feedback_buttons" not in st.session_state:
    st.session_state.show_feedback_buttons = False

# Initialize the state to handle immediate feedback processing
if "process_feedback" not in st.session_state:
    st.session_state.process_feedback = False


# Display the chat history
for msg_index, msg in enumerate(st.session_state.messages): 
    display_content = msg["content"]
    
    # Check if this is the last message and it's from the assistant
    is_last_assistant_message = (msg_index == len(st.session_state.messages) - 1 and msg["role"] == "assistant")
    
    # Trigger condition
    trigger_phrase = "How are you feeling about this topic?"
    
    # We check if the last message contains the trigger phrase
    if is_last_assistant_message and trigger_phrase in display_content:
        st.session_state.show_feedback_buttons = True
        
        # 1. Clean the content for display by removing the trigger phrase (this prevents the unclickable text)
        display_content = display_content.replace(trigger_phrase, "").strip()
        
        # 2. Display the cleaned message content in the chat bubble
        st.chat_message(msg["role"]).write(display_content, unsafe_allow_html=True)
        
        # --- Button Rendering Logic ---
        # Show the buttons immediately below the message
        if st.session_state.show_feedback_buttons:
            st.markdown("---")
            st.markdown("**What would you like to do next?**")
            feedback_options = ["I get it!", "A bit confusing.", "I'm lost.", "Explain it to me"]
            cols = st.columns(len(feedback_options))
            
            # Use the column layout to place buttons side-by-side
            for i, option in enumerate(feedback_options):
                with cols[i]:
                    # Added icons for visual appeal
                    icon = ""
                    if option == "I get it!": icon = "👍"
                    elif option == "A bit confusing.": icon = "❓"
                    elif option == "I'm lost.": icon = "👎"
                    elif option == "Explain it to me": icon = "💬"

                    st.button(
                        f"{icon} {option}", 
                        key=f"feedback_{i}", 
                        on_click=handle_feedback_click, 
                        args=[option],
                        help=f"Click here if you feel: {option}",
                        use_container_width=True
                    )
    else:
        # Display all other messages normally
        st.chat_message(msg["role"]).write(display_content, unsafe_allow_html=True)
        
# --- Main Chat Input & Logic ---

# Handle the case where a user clicked a button
if st.session_state.process_feedback:
    # Reset the flag and clear the buttons state
    st.session_state.process_feedback = False
    st.session_state.show_feedback_buttons = False
    
    # The last message is the user feedback (e.g., "I get it!")
    last_prompt = st.session_state.messages[-1]["content"]
    
    # Display the simulated user message (the button click)
    st.chat_message("user").write(last_prompt)

    # Rerun the model call with the new message
    with st.spinner(f"EduAI Tutor is analyzing: {last_prompt}..."):
        model_response = call_model(st.session_state.messages, GEMINI_MODEL_NAME)
        
        # Add the model's new response to the chat history
        st.session_state.messages.append(
            {"role": "assistant", "content": model_response}
        )
    
    # Trigger a script rerun to update the chat UI cleanly
    st.rerun()

# Handle the case where the user types a new prompt
# MODIFICATION: Removed 'disabled' attribute so the user can always type.
if prompt := st.chat_input("Ask me about any topic of your interest am here to guide you understand that topic better..."):
    # If the user types a new message, we assume they're moving past the previous feedback options
    st.session_state.show_feedback_buttons = False
    
    # 1. Add the user's message to the chat history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # 2. Show a spinner while waiting for the model's response
    with st.spinner(" EduAI Tutor is Thinking..."):
        # Get the model's response using the call_model function
        model_response = call_model(st.session_state.messages, GEMINI_MODEL_NAME)
        
        # 3. Add the model's response to the chat history
        st.session_state.messages.append(
            {"role": "assistant", "content": model_response}
        )
        
    # Trigger a script rerun to update the chat UI cleanly
    st.rerun()