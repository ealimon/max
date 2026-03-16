import streamlit as st
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. UI Branding
st.set_page_config(page_title="MAX | Limon Media", page_icon="🤖", layout="centered")
st.markdown("<style>#MainMenu, footer, header {visibility: hidden;} div[data-testid='stToolbar'] {display: none;} .stApp {background-color: white;}</style>", unsafe_allow_html=True)

# 2. Connection
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Secrets Error: {e}")
    st.stop()

# 3. Model
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-3.1-flash-lite-preview", system_instruction="You are MAX from Limon Media. Collect Business Name and Email.")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.lead_captured = False

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if not st.session_state.messages:
    welcome = "Hi! I'm MAX from Limon Media. What business goals are we tackling today?"
    st.session_state.messages.append({"role": "assistant", "content": welcome})
    with st.chat_message("assistant"): st.markdown(welcome)

# 4. Reliable Sync
if prompt := st.chat_input("Message MAX..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    try:
        response = st.session_state.chat_session.send_message(prompt)
        with st.chat_message("assistant"): st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

        # TRIGGER
        history = " ".join([m["content"] for m in st.session_state.messages])
        if "@" in history and not st.session_state.lead_captured:
            extract = model.generate_content(f"Extract as pipes: Name | Email | Goal from: {history}").text
            if "|" in extract:
                try:
                    p = extract.split("|")
                    new_row = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Business": p[0].strip(),
                        "Email": p[1].strip(),
                        "Notes": p[2].strip() if len(p) > 2 else "Lead"
                    }])
                    
                    # We specify 'Sheet1' directly to be safe
                    conn.create(data=new_row, worksheet="Sheet1")
                    
                    st.session_state.lead_captured = True
                    st.toast("✅ Synced to Google Sheets!")
                except Exception as sheet_err:
                    # This will now show the actual error message from Google
                    st.error(f"Google Sheet Sync Error: {str(sheet_err)}")
    except Exception as e:
        st.error(f"AI Error: {e}")
