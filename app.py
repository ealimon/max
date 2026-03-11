import streamlit as st
import google.generativeai as genai
import resend

# 1. BRAIN: HARD-CODED CONTACTS & STABLE MODEL
st.set_page_config(page_title="MAX | Limon Media", page_icon="🤖")

SYSTEM_PROMPT = """
ROLE: You are MAX, the AI Intake Specialist for Limon Media. 
PERSONALITY: Intelligent, social, and professional. 

CORE SERVICES (IN-SCOPE):
- Digital Marketing: Web Design (Wix), Google Ads, SEO, Social Media.
- AI Solutions: Custom Intake Specialists, AI Assistants, and AI Paralegals.

OFFICIAL CONTACT INFO (USE ONLY THESE):
- Scheduling: https://www.limon.media/contact
- Email: edward@limon.media
- Phone/Text: 442-268-0928
- NEVER guess URLs. If you don't know, provide the phone number.

GUARDRAILS:
- You only answer marketing/AI automation questions. 
- For everything else, pivot: "I'm a growth specialist, so I can't provide advice on that, but I can help you scale your business!"
- Respond in the user's language (English/Spanish).
"""

# API Setup
if "GOOGLE_API_KEY" in st.secrets and "RESEND_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    resend.api_key = st.secrets["RESEND_API_KEY"]
else:
    st.error("Missing API Keys in Streamlit Secrets.")
    st.stop()

# 2. SIDEBAR
with st.sidebar:
    st.title("📬 Ready to scale?")
    with st.form("lead_form", clear_on_submit=True):
        biz_name = st.text_input("Business Name")
        lead_email = st.text_input("Best email?")
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
        try:
            # FIX: Using the most stable 2026 production model ID
            model = genai.GenerativeModel(
                model_name="gemini-3.1-flash-lite", 
                system_instruction=SYSTEM_PROMPT
            )
            
            history = [{"role": m["role"] if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
            chat = model.start_chat(history=history)
            response = chat.send_message(prompt)
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error("MAX is taking a quick coffee break. Try again in a second!")
            print(f"CRITICAL ERROR: {e}") # This shows in your Streamlit dashboard logs
