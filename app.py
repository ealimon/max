import streamlit as st
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. UI Branding & Wix Optimization
st.set_page_config(page_title="MAX | Limon Media", page_icon="🤖", layout="centered")
st.markdown("<style>#MainMenu, footer, header {visibility: hidden;} div[data-testid='stToolbar'] {display: none;} .stApp {background-color: white;}</style>", unsafe_allow_html=True)

# 2. Connection
try:
    # ttl=0 ensures we are always getting fresh data from Google
    conn = st.connection("gsheets", type=GSheetsConnection, ttl=0)
except Exception as e:
    st.error(f"Secrets Error: {e}")
    st.stop()

# 3. Gemini Config
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel(
    model_name="gemini-3.1-flash-lite-preview", 
    system_instruction="You are MAX from Limon Media. Strategic and professional AI assistant. You MUST collect a Business Name and Email."
)

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.lead_captured = False

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if not st.session_state.messages:
    welcome = "Hi! I'm MAX from Limon Media. I help Coachella Valley businesses scale. What is your main business goal right now?"
    st.session_state.messages.append({"role": "assistant", "content": welcome})
    with st.chat_message("assistant"): st.markdown(welcome)

# 4. Reliable Sync Logic
if prompt := st.chat_input("Message MAX..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    try:
        response = st.session_state.chat_session.send_message(prompt)
        with st.chat_message("assistant"): st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

        # TRIGGER: Sync when email is found
        history = " ".join([m["content"] for m in st.session_state.messages])
        if "@" in history and not st.session_state.lead_captured:
            extract = model.generate_content(f"Extract as pipes: Name | Email | Goal from: {history}").text
            if "|" in extract:
                try:
                    p = extract.split("|")
                    # Ensure Row 1 of Sheet1 is: Date, Business, Email, Notes
                    new_row = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Business": p[0].strip(),
                        "Email": p[1].strip(),
                        "Notes": p[2].strip() if len(p) > 2 else "Lead"
                    }])
                    
                    # --- THE FINAL FIX ---
                    # Instead of 'create', we Read then Update
                    existing_data = conn.read(worksheet="Sheet1")
                    updated_data = pd.concat([existing_data, new_row], ignore_index=True)
                    conn.update(worksheet="Sheet1", data=updated_data)
                    
                    st.session_state.lead_captured = True
                    st.toast("✅ Strategy synced to Edward!")
                except Exception as sheet_err:
                    st.error(f"Sync Failure: {sheet_err}")
    except Exception as e:
        st.error(f"AI Error: {e}")
