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

# 3. Model Initialization (Using the 3.1 model authorized for your account)
@st.cache_resource
def load_model():
    return genai.GenerativeModel(
        model_name="gemini-3.1-flash-lite-preview",
        system_instruction=(
            "You are MAX, the professional AI Intake Specialist for Limon Media. "
            "Your goal is to help business owners understand how digital marketing (SEO, Ads, Web Design) "
            "can solve their problems. Be friendly and Coachella Valley local-focused. "
            "BILINGUAL LOGIC: If the user mentions a business name or context that suggests a Hispanic-owned "
            "business or a Spanish-speaking clientele (e.g., a Taqueria or Restaurant), politely ask if "
            "they would prefer to continue the conversation in Spanish. "
            "MANDATORY: You must collect their Business Name and Email Address. "
            "Do not repeat your name or introduction after the first message."
        )
    )

model = load_model()

# 4. Chat Memory Management
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Initialize the continuous chat session
    st.session_state.chat_session = model.start_chat(history=[])

# Display existing messages from the conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Initial Greeting (Only triggered once per session)
if not st.session_state.messages:
    welcome = "Hi! I'm MAX from Limon Media. I help local businesses scale with AI. What's your biggest marketing goal right now?"
    st.session_state.messages.append({"role": "assistant", "content": welcome})
    with st.chat_message("assistant"):
        st.markdown(welcome)

# 5. The Interaction Logic
if prompt := st.chat_input("Tell MAX about your business goals..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Send message through the session to maintain context/memory
        response = st.session_state.chat_session.send_message(prompt)
        
        # Show assistant response
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
    except Exception as e:
        st.error(f"MAX is having a momentary glitch: {e}")
