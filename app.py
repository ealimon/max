import streamlit as st
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="MAX | Limon Media", page_icon="🤖", layout="centered")

# Professional Wix styling
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        div[data-testid="stToolbar"] {display: none;}
        .stApp {background-color: white;}
    </style>
""", unsafe_allow_html=True)

# 1. Establish Connection using Secrets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Connection Setup Error: {e}")
    st.stop()

# 2. Configure Gemini
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing GEMINI_API_KEY in Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

@st.cache_resource
def load_model():
    return genai.GenerativeModel(
        model_name="gemini-3.1-flash-lite-preview",
        system_instruction="You are MAX from Limon Media. Strategic, professional, and friendly. You MUST collect a Business Name and Email Address."
    )

model = load_model()

# 3. Chat Session
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

# 4. Chat Input & Sync Logic
if prompt := st.chat_input("Message MAX..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = st.session_state.chat_session.send_message(prompt)
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

        # Check for email in history to trigger sync
        history = " ".join([m["content"] for m in st.session_state.messages])
        if "@" in history and not st.session_state.lead_captured:
            extract = model.generate_content(f"Extract as pipes: Name | Email | Goal from: {history}").text
            if "|" in extract:
                try:
                    parts = extract.split("|")
                    new_row = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Business Name": parts[0].strip(),
                        "Email": parts[1].strip(),
                        "Goals/Notes": parts[2].strip() if len(parts) > 2 else "Check history"
                    }])
                    # APPEND DATA
                    conn.create(data=new_row)
                    st.session_state.lead_captured = True
                    st.toast("Success! Lead details synced.")
                except:
                    pass
    except Exception as e:
        st.error(f"Error: {e}")
