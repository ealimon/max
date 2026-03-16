import streamlit as st
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Configuration & UI Cleanup
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
# This automatically looks for [connections.gsheets] in your secrets
conn = st.connection("gsheets", type=GSheetsConnection)

if "GEMINI_API_KEY" not in st.secrets:
    st.error("Please set GEMINI_API_KEY in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# 3. Model Setup
@st.cache_resource
def load_model():
    return genai.GenerativeModel(
        model_name="gemini-3.1-flash-lite-preview",
        system_instruction=(
            "You are MAX, the strategic AI Specialist for Limon Media. "
            "Help businesses in the Coachella Valley grow. "
            "Stay in English unless asked for Spanish. "
            "Goal: Collect Business Name and Email Address."
        )
    )

model = load_model()

# 4. Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.lead_captured = False

# Display Chat
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Initial Greeting
if not st.session_state.messages:
    welcome = "Hi! I'm MAX from Limon Media. I help businesses turn digital goals into reality. What's the main objective for your business right now?"
    st.session_state.messages.append({"role": "assistant", "content": welcome})
    with st.chat_message("assistant"):
        st.markdown(welcome)

# 5. Interaction Logic
if prompt := st.chat_input("Tell MAX about your goals..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = st.session_state.chat_session.send_message(prompt)
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

        # --- LEAD CAPTURE ---
        history = " ".join([m["content"] for m in st.session_state.messages])
        
        # Check if we have an email and haven't saved this session yet
        if "@" in history and not st.session_state.lead_captured:
            extract = model.generate_content(f"Extract: Name | Email | Goal from: {history}. Use pipes.").text
            
            if "|" in extract:
                try:
                    parts = extract.split("|")
                    new_row = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Business Name": parts[0].strip(),
                        "Email": parts[1].strip(),
                        "Goals/Notes": parts[2].strip() if len(parts) > 2 else "Check history"
                    }])
                    
                    # Pro-level: Append the row to your Google Sheet
                    conn.create(data=new_row)
                    st.session_state.lead_captured = True
                    st.toast("Success! Lead synced to Google Sheets.")
                except Exception as e:
                    pass 

    except Exception as e:
        st.error("MAX is momentarily resetting. Please try your message again.")
