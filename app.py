import streamlit as st
import google.generativeai as genai

# 1. Page Configuration
st.set_page_config(page_title="MAX | Limon Media Intake", page_icon="🤖")
st.markdown("<style>#MainMenu, footer, header {visibility: hidden;}</style>", unsafe_allow_html=True)

st.title("🤖 Meet MAX")
st.caption("Strategic Intake Specialist for Limon Media")

# 2. Key Setup
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing API Key in Streamlit Secrets.")
    st.stop()

# Configure the API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 3. Model Initialization
# We are switching to the Pro model alias to bypass the Flash 404 issue
@st.cache_resource
def load_model():
    return genai.GenerativeModel("gemini-1.5-pro")

try:
    model = load_model()
except Exception as e:
    st.error(f"Model Load Error: {e}")

# 4. Chat History Management
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Start a clean chat session
    st.session_state.chat = model.start_chat(history=[])

# Display existing messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Initial Greeting
if not st.session_state.messages:
    welcome = "Hi! I'm MAX from Limon Media. I help Coachella Valley businesses scale. What's your biggest marketing goal right now?"
    st.session_state.messages.append({"role": "assistant", "content": welcome})
    with st.chat_message("assistant"):
        st.markdown(welcome)

# 5. The Brain Logic
if prompt := st.chat_input("Tell MAX about your business..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Direct generation to bypass potential chat history formatting issues
        persona = (
            "You are MAX, the AI Intake Specialist for Limon Media. "
            "Explain how digital marketing solves the user's problem. "
            "Always ask for their Business Name and Email Address."
        )
        
        # Using the model directly for the response
        response = model.generate_content(f"{persona}\n\nUser Goal: {prompt}")
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
    except Exception as e:
        st.error("MAX is almost live! We are refining the model connection.")
        st.info(f"Technical Detail: {e}")
