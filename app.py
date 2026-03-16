import streamlit as st
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. UI Setup
st.set_page_config(page_title="MAX | Limon Media", page_icon="🤖", layout="centered")
st.markdown("<style>#MainMenu, footer, header {visibility: hidden;} div[data-testid='stToolbar'] {display: none;} .stApp {background-color: white;}</style>", unsafe_allow_html=True)

# 2. Connection
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Check your Secrets formatting.")
    st.stop()

# 3. Model Logic
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

# 4. Brute Force Sync
if prompt := st.chat_input("Message MAX..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    try:
        response = st.session_state.chat_session.send_message(prompt)
        with st.chat_message("assistant"): st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

        # Trigger on email
        history = " ".join([m["content"] for m in st.session_state.messages])
        if "@" in history and not st.session_state.lead_captured:
            extract = model.generate_content(f"Extract 'Name | Email | Goal' from: {history}").text
            if "|" in extract:
                try:
                    p = extract.split("|")
                    new_row = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Business": p[0].strip(),
                        "Email": p[1].strip(),
                        "Notes": p[2].strip() if len(p) > 2 else "Lead"
                    }])
                    
                    # We use 'create' with a clear worksheet name to avoid ambiguity
                    conn.create(data=new_row, worksheet="Sheet1")
                    
                    st.session_state.lead_captured = True
                    st.toast("✅ Lead synced successfully!")
                except Exception as sheet_err:
                    # We are forcing the app to show the full error string
                    error_msg = str(sheet_err)
                    if "403" in error_msg or "permission" in error_msg.lower():
                        st.error("Error: The Service Account needs 'Editor' access and the Google Drive API must be enabled in Cloud Console.")
                    else:
                        st.error(f"Sync Failure: {error_msg}")

    except Exception as e:
        st.error(f"AI Error: {e}")
