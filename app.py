import streamlit as st
from google import genai
from google.genai import types
import time

# --- 1. PROFESSIONAL PAGE CONFIG ---
st.set_page_config(
    page_title="MAX | Limon Media",
    page_icon="🤖",
    layout="centered"
)

# Custom CSS to hide Streamlit branding for a professional look
st.markdown("""
    <style>
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. INITIALIZATION ---
SYSTEM_PROMPT = """
ROLE: You are MAX, the professional AI Intake Specialist for Limon Media.
SERVICES: Web Design (Wix/WordPress), PPC (Google Ads), SEO, and AI Automation.
TONE: Professional, friendly, and efficient.
CONTACT: edward@limon.media | 442-268-0928
"""

# API Setup
if "GOOGLE_API_KEY" in st.secrets:
    client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("API Key missing. Please add GOOGLE_API_KEY to Streamlit Secrets.")
    st.stop()

# Session State for Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello. I'm Max. How can I help today?"}
    ]

# Sidebar Reset Button
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = [{"role": "assistant", "content": "Hello. I'm Max. How can I help today?"}]
    st.rerun()

# --- 3. CHAT INTERFACE ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 4. RESPONSE LOGIC ---
if prompt := st.chat_input("Message MAX..."):
    # User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        # Prepare history for the 2026 SDK
        # We exclude the very last user message because it's sent in 'send_message'
        history = []
        for m in st.session_state.messages[:-1]:
            history.append(types.Content(
                role="model" if m["role"] == "assistant" else "user",
                parts=[types.Part.from_text(text=m["content"])]
            ))

        # FORCED HANDSHAKE (RETRY LOGIC)
        full_response = ""
        success = False
        
        for attempt in range(5):
            try:
                # Configuration for the model
                config = types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.7
                )
                
                # Start chat and get response
                chat = client.chats.create(model="gemini-1.5-flash", config=config, history=history)
                response = chat.send_message(prompt)
                
                full_response = response.text
                response_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                success = True
                break
                
            except Exception as e:
                # If we hit a 429 (Rate Limit/Sync Issue), wait and retry
                if "429" in str(e):
                    wait_time = 2 ** attempt  # Wait 2, 4, 8, 16 seconds
                    response_placeholder.warning(f"Syncing with Google Tier 1... (Attempt {attempt+1}/5)")
                    time.sleep(wait_time)
                    continue
                else:
                    response_placeholder.error(f"Technical glitch: {str(e)}")
                    break
        
        if not success:
            response_placeholder.error("MAX is still finalizing his upgrade with Google. This sync can take a bit longer for new Tier 1 accounts. Please try again in 30 minutes.")
