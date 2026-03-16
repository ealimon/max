import streamlit as st
import google.generativeai as genai
from google.api_core import client_options

# 1. Page Configuration
st.set_page_config(page_title="MAX | Limon Media Intake", page_icon="🤖")

# Custom CSS to hide Streamlit UI for a professional look
st.markdown("<style>#MainMenu, footer, header {visibility: hidden;}</style>", unsafe_allow_html=True)

st.title("🤖 Meet MAX")
st.caption("Strategic Intake Specialist for Limon Media")

# 2. Key & API Setup
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing API Key in Streamlit Secrets.")
    st.stop()

# Force the stable endpoint for your upgraded account
options = client_options.ClientOptions(api_endpoint="generativelanguage.googleapis.com")
genai.configure(api_key=st.secrets["GEMINI_API_KEY"], client_options=options)

# 3. Model Initialization
@st.cache_resource
def load_model():
    return genai.GenerativeModel(
        model_name="gemini-3.1-flash-lite-preview",
        system_instruction=(
            "You are MAX, the professional and highly intelligent AI Intake Specialist for Limon Media. "
            "Your tone is warm, encouraging, and deeply insightful—act as a strategic partner, not just a bot. "
            "Help business owners understand how SEO, Ads, or Web Design can solve their specific growth goals. "
            "BILINGUAL LOGIC: If a business name or context suggests a Hispanic-owned business or Spanish-speaking "
            "clientele, politely offer to continue in Spanish. "
            "MANDATORY: Collect their Business Name and Email Address. "
            "Do not repeat your name or introduction after the initial greeting."
        )
    )

model = load_model()

# 4. Chat Memory Management
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.chat_session = model.start_chat(history=[])

# Display existing messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Initial Greeting
if not st.session_state.messages:
    welcome = "Hi! I'm MAX from Limon Media. I help Coachella Valley businesses turn big goals into digital reality. What's the main objective for your business right now?"
    st.session_state.messages.append({"role": "assistant", "content": welcome})
    with st.chat_message("assistant"):
        st.markdown(welcome)

# 5. The Interaction Logic
if prompt := st.chat_input("Tell MAX about your business goals..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = st.session_state.chat_session.send_message(prompt)
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
    except Exception as e:
        st.error(f"MAX is having a momentary glitch: {e}")
