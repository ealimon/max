import streamlit as st
import google.generativeai as genai

# 1. Page Configuration & UI Clean-up
st.set_page_config(page_title="MAX | Limon Media Intake", layout="centered")

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Meet MAX")
st.caption("Limon Media's AI Intake Specialist")

# 2. Access Gemini API Key from Streamlit Secrets
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("API Key missing or incorrect in Streamlit Secrets.")
    st.stop()

# 3. Initialize the Model
# Switched to 'gemini-1.5-flash' which is the most compatible string
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", 
    system_instruction=(
        "You are MAX, the AI Intake Specialist for Limon Media (https://www.limon.media/). "
        "Your goal is to help business owners understand how marketing can solve their growth problems. "
        "If they want 'more calls', suggest SEO or Google Ads. "
        "Always be professional, tech-savvy, and Coachella Valley friendly. "
        "MANDATORY: You must collect their Business Name and Email Address before the chat ends."
    )
)

# 4. Chat History Management
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Initial Greeting
if not st.session_state.messages:
    initial_msg = "Hi! I'm MAX from Limon Media. Tell me a bit about your business—are you looking for more phone calls, more leads, or just more growth in general?"
    st.session_state.messages.append({"role": "assistant", "content": initial_msg})
    with st.chat_message("assistant"):
        st.markdown(initial_msg)

# 5. Chat Logic
if prompt := st.chat_input("How can Limon Media help?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Re-build the chat session with the current history
        history_for_api = []
        for m in st.session_state.messages[:-1]:
            role = "user" if m["role"] == "user" else "model"
            history_for_api.append({"role": role, "parts": [m["content"]]})
        
        chat_session = model.start_chat(history=history_for_api)
        response = chat_session.send_message(prompt)
        
        full_response = response.text
        with st.chat_message("assistant"):
            st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
    except Exception as e:
        # Improved error message for debugging
        st.error(f"MAX is having a momentary glitch: {e}")
        st.info("Tip: Double-check that your Gemini API key is active in Google AI Studio.")
