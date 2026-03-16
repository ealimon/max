import streamlit as st
import google.generativeai as genai
from google.api_core import client_options
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="MAX | Limon Media", page_icon="🤖", layout="centered")

# Professional UI: Hiding Streamlit elements for Wix integration
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        div[data-testid="stToolbar"] {display: none;}
        div[data-testid="stDecoration"] {display: none;}
        div[data-testid="stStatusWidget"] {display: none;}
        .stChatFloatingInputContainer {padding-bottom: 20px;}
        .stApp {background-color: white;}
    </style>
""", unsafe_allow_html=True)

# 2. Configuration & API Setup
if "GEMINI_API_KEY" not in st.secrets or "gsheets_url" not in st.secrets:
    st.error("Missing configuration in Streamlit Secrets.")
    st.stop()

options = client_options.ClientOptions(api_endpoint="generativelanguage.googleapis.com")
genai.configure(api_key=st.secrets["GEMINI_API_KEY"], client_options=options)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Model Initialization
@st.cache_resource
def load_model():
    return genai.GenerativeModel(
        model_name="gemini-3.1-flash-lite-preview",
        system_instruction=(
            "You are MAX, the professional and highly intelligent AI Intake Specialist for Limon Media. "
            "Your tone is warm, strategic, and insightful. "
            "CRITICAL RULES: "
            "1. You have already introduced yourself. DO NOT repeat your name or title. "
            "2. LANGUAGE: You are English-only by default. NEVER offer Spanish proactively. "
            "ONLY switch to Spanish if the user explicitly asks for it or starts typing in Spanish. "
            "3. MANDATORY: You must collect the Business Name and Email Address for Edward Limon."
        )
    )

model = load_model()

# 4. Chat Memory
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.lead_captured = False

# Display Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Initial Greeting
if not st.session_state.messages:
    welcome = "Hi! I'm MAX from Limon Media. I help Coachella Valley businesses turn big goals into digital reality. What's the main objective for your business right now?"
    st.session_state.messages.append({"role": "assistant", "content": welcome})
    with st.chat_message("assistant"):
        st.markdown(welcome)

# 5. Interaction & Data Logging
if prompt := st.chat_input("Tell MAX about your business goals..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = st.session_state.chat_session.send_message(prompt)
        
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

        # --- REFINED LEAD CAPTURE ---
        if not st.session_state.lead_captured:
            # We use the model to check the history for Name and Email
            history_text = str(st.session_state.messages)
            check = model.generate_content(f"Does this conversation contain a business name and an email address? Answer only YES or NO. History: {history_text}")
            
            if "YES" in check.text.upper():
                extract = model.generate_content(f"Extract these 3 things: Business Name | Email | Primary Goal. Format with pipes. History: {history_text}").text
                
                try:
                    parts = extract.split("|")
                    existing_df = conn.read(spreadsheet=st.secrets["gsheets_url"], ttl=0)
                    new_row = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Business Name": parts[0].strip(),
                        "Email": parts[1].strip(),
                        "Goals/Notes": parts[2].strip()
                    }])
                    updated_df = pd.concat([existing_df, new_row], ignore_index=True)
                    conn.update(spreadsheet=st.secrets["gsheets_url"], data=updated_df)
                    st.session_state.lead_captured = True
                    st.toast("Strategy synced!")
                except:
                    pass

    except Exception as e:
        st.error(f"MAX is refreshing. Just a moment...")
