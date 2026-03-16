import streamlit as st
import google.generativeai as genai
from google.api_core import client_options
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="MAX | Limon Media", page_icon="🤖", layout="centered")

# Professional Branding: Hiding all Streamlit elements for a clean Wix integration
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        div[data-testid="stToolbar"] {display: none;}
        div[data-testid="stDecoration"] {display: none;}
        div[data-testid="stStatusWidget"] {display: none;}
        .stChatFloatingInputContainer {padding-bottom: 20px;}
        /* Make background white to blend with your Wix container */
        .stApp {background-color: white;}
    </style>
""", unsafe_allow_html=True)

# 2. API & Sheets Configuration
if "GEMINI_API_KEY" not in st.secrets or "gsheets_url" not in st.secrets:
    st.error("Configuration missing in Streamlit Secrets.")
    st.stop()

# Configure Gemini
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
            "You are MAX, the professional, highly intelligent AI Intake Specialist for Limon Media. "
            "Your tone is warm, strategic, and deeply insightful. "
            "CRITICAL RULE: You have already introduced yourself in the first message. "
            "DO NOT repeat your name or the phrase 'Intake Specialist' again. "
            "BILINGUAL LOGIC: If context suggests a Hispanic-owned business, offer to continue in Spanish. "
            "MANDATORY: You must collect Business Name and Email Address for Edward Limon."
        )
    )

model = load_model()

# 4. Chat Session & Memory
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.lead_captured = False

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Initial Greeting (Run once)
if not st.session_state.messages:
    welcome = "Hi! I'm MAX from Limon Media. I help Coachella Valley businesses turn big goals into digital reality. What's the main objective for your business right now?"
    st.session_state.
