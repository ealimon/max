import streamlit as st
import google.generativeai as genai
import time

# 1. PRODUCTION CONFIG
st.set_page_config(page_title="MAX | Limon Media", page_icon="🤖", layout="centered")

# Hide Streamlit "Made with Streamlit" for a cleaner look
hide_style = """<style>footer {visibility: hidden;} #MainMenu {visibility: hidden;}</style>"""
st.markdown(hide_style, unsafe_allow_html=True)

SYSTEM_PROMPT = """
ROLE: You are MAX, the professional AI Intake Specialist for Limon Media. 
TONE: Helpful, social, and direct.
SERVICES: Web Design, PPC, SEO, and AI Automation.
CONTACT: edward@limon.media | 442-268-0928
"""

# Configure API
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing API Key. Please check Streamlit Secrets.")
    st.stop()

# 2. SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm Max. How may I you help today?"}]

# Sidebar Reset
if st.sidebar.button("Reset Conversation"):
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm Max. How may I you help today?"}]
    st.rerun()

# 3. CHAT DISPLAY
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. RESPONSE LOGIC
if prompt := st.chat_input("Ask MAX..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # We use a placeholder to give a 'typing' feel
        response_placeholder = st.empty()
        
        # Format history correctly for Gemini's 'ChatSession'
        history = []
        for m in st.session_state.messages[:-1]:
            history.append({
                "role": "model" if m["role"] == "assistant" else "user",
                "parts": [m["content"]]
            })

        # AUTO-RETRY & SYNC LOGIC
        model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)
        
        success = False
        for attempt in range(3):
            try:
                chat = model.start_chat(history=history)
                response = chat.send_message(prompt)
                
                full_response = response.text
                response_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                success = True
                break
            except Exception as e:
                if attempt < 2:
                    time.sleep(3) # Give the API 3 seconds to breathe
                    continue
                else:
                    response_placeholder.error("MAX is finalizing his upgraded engine. This usually takes a few hours after a billing update. Please try again shortly!")
                    print(f"DEBUG: {e}")
