import streamlit as st
import google.generativeai as genai
import time

# 1. SETUP
st.set_page_config(page_title="MAX | Limon Media", page_icon="🤖")

SYSTEM_PROMPT = """
ROLE: You are MAX, the AI Intake Specialist for Limon Media. 
OFFICIAL CONTACT: edward@limon.media | 442-268-0928
"""

# Configure API
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing GOOGLE_API_KEY in Streamlit Secrets.")
    st.stop()

# 2. CHAT SESSION MANAGEMENT
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Ready to grow. How can I help today?"}]

# Sidebar Reset
if st.sidebar.button("Reset MAX"):
    st.session_state.messages = [{"role": "assistant", "content": "Ready to grow. How can I help today?"}]
    st.rerun()

# Display Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 3. INTERACTION LOGIC
if prompt := st.chat_input("Ask MAX..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash", # Best for Tier 1 stability
            system_instruction=SYSTEM_PROMPT
        )
        
        # Tier 1 Handshake Logic
        for attempt in range(3):
            try:
                chat = model.start_chat(history=[])
                response = chat.send_message(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                break
            except Exception as e:
                if "429" in str(e) or "404" in str(e):
                    time.sleep(2) # Wait for Tier 1 sync
                    continue
                st.error("MAX is warming up his new engine. Please try once more!")
