import streamlit as st
import google.generativeai as genai
import time

# 1. PROFESSIONAL SETUP
st.set_page_config(page_title="MAX | Limon Media", page_icon="🤖")

SYSTEM_PROMPT = """
ROLE: You are MAX, the professional AI Intake Specialist for Limon Media. 
CONTACT: edward@limon.media | 442-268-0928
"""

# Configure API
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Check your Streamlit Secrets for the API Key.")
    st.stop()

# 2. SESSION MANAGEMENT
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello. I'm Max. How can I help today?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 3. INTERACTION LOGIC
if prompt := st.chat_input("Message MAX..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash", # Best stability for Tier 1
            system_instruction=SYSTEM_PROMPT
        )
        
        # PRO-SYNC RETRY LOGIC
        for attempt in range(3):
            try:
                # Format history for Gemini's specific 'model' vs 'user' roles
                history = [{"role": "model" if m["role"] == "assistant" else "user", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)
                response = chat.send_message(prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                break
            except Exception as e:
                if attempt < 2:
                    time.sleep(3) # Wait for Tier 1 handshake
                    continue
                else:
                    st.error("MAX is finalizing his engine. This can take 1-4 hours after a billing update.")
                    print(f"DEBUG: {e}")
