import streamlit as st
import google.generativeai as genai
from google.api_core import client_options

# 1. Page Configuration
st.set_page_config(page_title="MAX | Limon Media Intake", page_icon="🤖")
st.markdown("<style>#MainMenu, footer, header {visibility: hidden;}</style>", unsafe_allow_html=True)

st.title("🤖 Meet MAX")
st.caption("Strategic Intake Specialist for Limon Media")

# 2. Key Setup
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing API Key in Streamlit Secrets.")
    st.stop()

# Force the connection to the stable endpoint
options = client_options.ClientOptions(api_endpoint="generativelanguage.googleapis.com")
genai.configure(api_key=st.secrets["GEMINI_API_KEY"], client_options=options)

# 3. Model Initialization 
# Using the specific Gemini 3.1 model found in your authorized list
@st.cache_resource
def load_model():
    return genai.GenerativeModel("gemini-3.1-flash-lite-preview")

model = load_model()

# 4. Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display existing messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Initial Greeting
if not st.session_state.messages:
    welcome = "Hi! I'm MAX from Limon Media. I help Coachella Valley businesses scale with AI. What's your biggest marketing goal right now?"
    st.session_state.messages.append({"role": "assistant", "content": welcome})
    with st.chat_message("assistant"):
        st.markdown(welcome)

# 5. The Interaction
if prompt := st.chat_input("Tell MAX about your business..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Prompt context
        context = (
            "You are MAX, the AI Intake Specialist for Limon Media. "
            "Explain how digital marketing solves the user's problem. "
            "Always ask for their Business Name and Email Address politely."
        )
        
        response = model.generate_content(f"{context}\n\nUser Goal: {prompt}")
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
    except Exception as e:
        st.error(f"MAX is having a connection glitch: {e}")
