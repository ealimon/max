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

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    st.error(f"Configuration Error: {e}")
    st.stop()

# 3. Chat Session Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Start the conversation with the model
    st.session_state.chat = model.start_chat(history=[])

# Display existing messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Initial Greeting
if not st.session_state.messages:
    welcome = "Hi! I'm MAX. I help business owners in the Coachella Valley grow. What is your biggest goal for your business right now?"
    st.session_state.messages.append({"role": "assistant", "content": welcome})
    with st.chat_message("assistant"):
        st.markdown(welcome)

# 4. Interaction Logic
if prompt := st.chat_input("Tell MAX about your business..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Prompt context to keep MAX on brand
        context = (
            "You are MAX, the AI Intake Specialist for Limon Media. "
            "Help the user understand how digital marketing can solve their growth goals. "
            "Always ask for their Business Name and Email Address politely."
        )
        response = st.session_state.chat.send_message(f"{context}\n\nUser: {prompt}")
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
    except Exception as e:
        st.error(f"Connection status: Almost there! Error detail: {e}")
