import streamlit as st
import google.generativeai as genai

# 1. Page Configuration & UI Clean-up
st.set_page_config(page_title="MAX | Limon Media Intake", layout="centered")

# Custom CSS to hide Streamlit branding for a cleaner "app" feel
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stChatMessage { border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Meet MAX")
st.caption("Limon Media's AI Intake Specialist")

# 2. Access Gemini API Key from Streamlit Secrets
# Make sure GEMINI_API_KEY is set in your Streamlit Cloud Secrets dashboard
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("API Key configuration failed. Check your Streamlit Secrets.")
    st.stop()

# 3. Initialize the Model with System Instructions
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=(
        "You are MAX, the AI Intake Specialist for Limon Media (https://www.limon.media/). "
        "Your goal is to help business owners bridge the gap between their goals and marketing solutions. "
        "Business owners often say 'I want more calls' or 'more orders'—translate this into SEO, Google Ads, or Web Design. "
        "Always be professional, encouraging, and Coachella Valley local-friendly. "
        "MANDATORY: You must eventually collect the Business Name and Email Address so Edward Limon can follow up."
    )
)

# 4. Chat History Management
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "Hi! I'm MAX from Limon Media. Tell me a bit about your business and what you're hoping to achieve—is it more phone calls, more walk-ins, or just more growth in general?"
        }
    ]

# Display existing chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Chat Logic
if prompt := st.chat_input("How can Limon Media help your business?"):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and display AI response
    with st.chat_message("assistant"):
        # Format history for the Gemini API
        history = [
            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
            for m in st.session_state.messages[:-1]
        ]
        
        chat_session = model.start_chat(history=history)
        response = chat_session.send_message(prompt)
        
        full_response = response.text
        st.markdown(full_response)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})
