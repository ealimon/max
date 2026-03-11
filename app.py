import streamlit as st
import google.generativeai as genai
import resend
import time

# 1. SETUP: High-Priority Config
st.set_page_config(page_title="MAX | Limon Media", page_icon="🤖", layout="centered")

SYSTEM_PROMPT = """
ROLE: You are MAX, the AI Intake Specialist for Limon Media. 
PERSONALITY: Intelligent, social, and professional. 

CORE SERVICES:
- Digital Marketing: Web Design (Wix), Google Ads (PPC), SEO, Social Media.
- AI Solutions: Custom Intake Specialists, AI Assistants, and AI Paralegals.

OFFICIAL CONTACT INFO:
- Scheduling: https://www.limon.media/contact
- Email: edward@limon.media
- Phone/Text: 442-268-0928
"""

# API Key Validation
if "GOOGLE_API_KEY" in st.secrets and "RESEND_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    resend.api_key = st.secrets["RESEND_API_KEY"]
else:
    st.error("Missing API Keys in Secrets.")
    st.stop()

# 2. SIDEBAR: Lead Capture
with st.sidebar:
    st.title("🚀 Growth Intake")
    with st.form("lead_form", clear_on_submit=True):
        biz_name = st.text_input("Business Name")
        lead_email = st.text_input("Contact Email")
        submit_btn = st.form_submit_button("Send to Edward")

# 3. CHAT INTERFACE
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi, I'm MAX. How can I help you grow your business today?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Chat with MAX..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # MODEL: Using the rock-solid 1.5-flash for initial Tier 1 stability
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash", 
            system_instruction=SYSTEM_PROMPT
        )
        
        # Fixed Retry Logic
        for attempt in range(3):
            try:
                history = [{"role": m["role"] if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                chat = model.start_chat(history=history)
                response = chat.send_message(prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                break
            except Exception as e:
                if attempt < 2:
                    time.sleep(2)
                    continue
                else:
                    st.error("MAX is finalizing his new upgraded engine. Try one more time in 30 seconds!")
                    print(f"DEBUG: {e}")

# 4. FORM LOGIC
if submit_btn and biz_name and lead_email:
    st.sidebar.success(f"Perfect! Edward will reach out to {biz_name} soon.")
