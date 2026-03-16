import streamlit as st
import google.generativeai as genai
from google.api_core import client_options
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="MAX | Limon Media", page_icon="🤖", layout="centered")

# Hide Streamlit UI elements for a professional Wix integration
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

# Force stable endpoint
options = client_options.ClientOptions(api_endpoint="generativelanguage.googleapis.com")
genai.configure(api_key=st.secrets["GEMINI_API_KEY"], client_options=options)

# Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Model Initialization
@st.cache_resource
def load_model():
    return genai.GenerativeModel(
        model_name="gemini-3.1-flash-lite-preview",
        system_instruction=(
            "You are MAX, the professional and highly intelligent AI Intake Specialist for Limon Media. "
            "Your tone is warm, strategic, and deeply insightful. "
            "CRITICAL RULE: You have already introduced yourself in the initial greeting. "
            "DO NOT repeat your name or the phrase 'Intake Specialist' again. "
            "BILINGUAL LOGIC: If a business suggests a Hispanic-owned business or Spanish-speaking audience, "
            "politely offer to continue in Spanish. "
            "MANDATORY: You must collect Business Name and Email Address for Edward Limon."
        )
    )

model = load_model()

# 4. Chat Memory Management
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.lead_captured = False

# Display existing messages
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

        # --- AUTOMATED LEAD LOGGING ---
        if not st.session_state.lead_captured:
            check_prompt = "Has the user shared a Business Name and Email? Answer ONLY 'YES' or 'NO'."
            check = model.generate_content(f"Chat: {st.session_state.messages}\n\n{check_prompt}")
            
            if "YES" in check.text.upper():
                extract_prompt = "Extract exactly: Name | Email | Goal. Use pipes."
                ext = model.generate_content(f"Chat: {st.session_state.messages}\n\n{extract_prompt}").text
                
                try:
                    parts = ext.split("|")
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
                    st.toast("Success! Strategy details synced.")
                except Exception as e:
                    # Logs error internally if needed
                    pass

    except Exception as e:
        st.error(f"MAX is refreshing... Technical detail: {e}")
