import streamlit as st
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="MAX | Limon Media", page_icon="🤖", layout="centered")

# Professional UI for Wix
st.markdown("<style>#MainMenu, footer, header {visibility: hidden;} div[data-testid='stToolbar'] {display: none;} .stApp {background-color: white;}</style>", unsafe_allow_html=True)

# 2. Connection
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Secret Setup Error: {e}")
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

# 4. Input & Direct Sync
if prompt := st.chat_input("Message MAX..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    try:
        response = st.session_state.chat_session.send_message(prompt)
        ai_msg = response.text
        with st.chat_message("assistant"): st.markdown(ai_msg)
        st.session_state.messages.append({"role": "assistant", "content": ai_msg})

        # TRIGGER: Second an email is typed, we sync.
        history_text = " ".join([m["content"] for m in st.session_state.messages])
        if "@" in history_text and not st.session_state.lead_captured:
            # We bypass the AI extraction for a moment to see if a hardcoded test works
            try:
                # We'll let the AI find the data
                extract = model.generate_content(f"Extract 'Name | Email | Goal' from: {history_text}").text
                parts = extract.split("|")
                
                # We build the row specifically to match your Sheet headers
                new_row = pd.DataFrame([{
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Business Name": parts[0].strip() if len(parts) > 0 else "Unknown",
                    "Email": parts[1].strip() if len(parts) > 1 else "No email",
                    "Goals/Notes": parts[2].strip() if len(parts) > 2 else "Check chat"
                }])

                # Using 'create' which is the most reliable for Service Accounts
                conn.create(data=new_row)
                
                st.session_state.lead_captured = True
                st.toast("✅ Lead synced to Google Sheets!")
            except Exception as sheet_error:
                st.error(f"Google Sheet Sync Error: {sheet_error}")

    except Exception as e:
        st.error(f"Error: {e}")
