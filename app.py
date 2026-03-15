import streamlit as st
import google.generativeai as genai

# 1. Page Configuration
st.set_page_config(page_title="MAX | Limon Media Intake", layout="centered")

# Hide Streamlit UI elements
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Meet MAX")
st.caption("Limon Media's AI Intake Specialist")

# 2. Key Setup
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Please add your GEMINI_API_KEY to Streamlit Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 3. Model Initialization 
# We use the direct string here to ensure compatibility
try:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction="You are MAX, the professional AI Intake Specialist for Limon Media. Your goal is to turn business goals into marketing leads. Ask for their business name and email address naturally."
    )
except Exception as e:
    st.error(f"Model failed to initialize: {e}")

# 4. Chat Session
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.chat_session = model.start_chat(history=[])

# Display history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Welcome Message
if not st.session_state.messages:
    welcome = "Hi! I'm MAX from Limon Media. Tell me about your business objectives—are you looking for more calls, more leads, or something else?"
    st.session_state.messages.append({"role": "assistant", "content": welcome})
    with st.chat_message("assistant"):
        st.markdown(welcome)

# 5. Interaction
if prompt := st.chat_input("Tell MAX about your business goals..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Generate response
        response = st.session_state.chat_session.send_message(prompt)
        
        # Add assistant message
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        
    except Exception as e:
        st.error(f"MAX hit a snag: {e}")
        st.info("Check if your API Key is active at https://aistudio.google.com/")
