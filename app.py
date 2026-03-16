import streamlit as st
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Configuration & UI
st.set_page_config(page_title="MAX | Limon Media", page_icon="🤖", layout="centered")

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        div[data-testid="stToolbar"] {display: none;}
        .stApp {background-color: white;}
    </style>
""", unsafe_allow_html=True)

# 2. Connection Setup
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Configuration Error: {e}")
    st.stop()

# 3. Gemini Config
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing GEMINI_API_KEY in Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

@st.cache_resource
def load_model():
    return genai.GenerativeModel(
        model_name="gemini-3.1-flash-lite-preview",
        system_instruction="You are MAX from Limon Media. Strategic and professional. You MUST collect a Business Name and Email Address."
    )

model = load_model()

# 4. Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.lead_captured = False

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if not st.session_state.messages:
    welcome = "Hi! I'm MAX from Limon Media. I help Coachella Valley businesses scale. What is your main business goal right now?"
    st.session_state.messages.append({"role": "assistant", "content": welcome})
    with st.chat_message("assistant"):
        st.markdown(welcome)

# 5. Input & Sync
if prompt := st.chat_input("Message MAX..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = st.session_state.chat_session.send_message(prompt)
        ai_response = response.text
        
        with st.chat_message("assistant"):
            st.markdown(ai_response)
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

        # --- REFINED TRIGGER LOGIC ---
        history_text = " ".join([m["content"] for m in st.session_state.messages])
        
        if "@" in history_text and not st.session_state.lead_captured:
            extract_prompt = f"Extract 'Name | Email | Goal' from this chat. Use pipes. Chat: {history_text}"
            extraction = model.generate_content(extract_prompt).text
            
            if "|" in extraction:
                try:
                    parts = extraction.split("|")
                    new_row = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Business Name": parts[0].strip(),
                        "Email": parts[1].strip(),
                        "Goals/Notes": parts[2].strip() if len(parts) > 2 else "Check history"
                    }])

                    # Use the most basic 'create' method which works best for appending rows
                    conn.create(data=new_row)
                    
                    st.session_state.lead_captured = True
                    st.toast("🚀 Lead captured! Check your Google Sheet.")
                except Exception as sheet_error:
                    st.error(f"Google Sheet sync failed: {sheet_error}")

    except Exception as e:
        st.error(f"Something went wrong: {e}")
