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
    st.session_state.messages = [{"role": "assistant", "content": "How can I help today?"}]

# Sidebar Reset
if st.sidebar.button("Reset MAX"):
    st.session_state.messages = [{"role": "assistant", "content": "How can I help today?"}]
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
            model_name="gemini-1.5-flash", 
            system_instruction=SYSTEM_PROMPT
        )
        
        # Proper History Formatting for Gemini
        formatted_history = []
        for m in st.session_state.messages[:-1]:
            role = "model" if m["role"] == "assistant" else "user"
            formatted_history.append({"role": role, "parts": [m["content"]]})

        # Tier 1 Handshake Logic
        success = False
        for attempt in range(3):
            try:
                chat = model.start_chat(history=formatted_history)
                response = chat.send_message(prompt)
                
                placeholder = st.empty()
                placeholder.markdown(response.text)
                
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                success = True
                break
            except Exception as e:
                if attempt < 2:
                    time.sleep(2)
                    continue
                else:
                    st.error("MAX is still syncing with the new billing tier. Try one more time!")
                    # Log the error to the Streamlit console for you to see
                    print(f"Error: {e}")
