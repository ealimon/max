import streamlit as st
import google.generativeai as genai
from google.api_core import client_options
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="MAX | Limon Media Intake", page_icon="🤖", layout="centered")

# Professional Agency Styling
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stChatFloatingInputContainer {padding-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Meet MAX")
st.caption("Strategic Intake Specialist for Limon Media")

# 2. API & Sheets Configuration
if "GEMINI_API_KEY" not in st.secrets or "gsheets_url" not in st.secrets:
    st.error("Configuration missing in Streamlit Secrets.")
    st.stop()

# Force stable endpoint connection
options = client_options.ClientOptions(api_endpoint="generativelanguage.googleapis.com")
genai.configure(api_key=st.secrets["GEMINI_API_KEY"], client_options=options)

# Establish Google Sheets Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Model Initialization (The "Brain")
@st.cache_resource
def load_model():
    return genai.GenerativeModel(
        model_name="gemini-3.1-flash-lite-preview",
        system_instruction=(
            "You are MAX, the professional, highly intelligent AI Intake Specialist for Limon Media. "
            "Your tone is warm, strategic, and deeply insightful. "
            "CRITICAL RULE: You have already introduced yourself in the first message. "
            "DO NOT repeat your name or the phrase 'Intake Specialist' again in this conversation. "
            "Dive straight into the user's business goals. "
            "BILINGUAL LOGIC: If the user mentions a business name or context suggesting a Hispanic-owned business, "
            "politely offer to continue in Spanish. "
            "MANDATORY: You must collect their Business Name and Email Address to pass to Edward Limon."
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
    st.session_state.messages.append({"role": "assistant", "content": welcome})
    with st.chat_message("assistant"):
        st.markdown(welcome)

# 5. Interaction & Data Logging
if prompt := st.chat_input("Tell MAX about your business goals..."):
    # Show user input
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Get AI response via session memory
        response = st.session_state.chat_session.send_message(prompt)
        
        # Display AI response
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

        # --- AUTOMATED LEAD CAPTURE ---
        if not st.session_state.lead_captured:
            # Silent background check for data
            check_prompt = "Has the user shared both a Business Name and an Email address? Answer ONLY 'YES' or 'NO'."
            check = model.generate_content(f"History: {st.session_state.messages}\n\n{check_prompt}")
            
            if "YES" in check.text.upper():
                # Extract clean data for the spreadsheet
                extract_prompt = "Extract exactly: Name | Email | Primary Goal. Use pipes as separators."
                ext = model.generate_content(f"History: {st.session_state.messages}\n\n{extract_prompt}").text
                
                try:
                    parts = ext.split("|")
                    
                    # Read current sheet
                    df = conn.read(spreadsheet=st.secrets["gsheets_url"])
                    
                    # Create new lead entry
                    new_entry = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Business Name": parts[0].strip(),
                        "Email": parts[1].strip(),
                        "Goals/Notes": parts[2].strip()
                    }])
                    
                    # Append and Sync
                    updated_df = pd.concat([df, new_entry], ignore_index=True)
                    conn.update(spreadsheet=st.secrets["gsheets_url"], data=updated_df)
                    
                    st.session_state.lead_captured = True
                    st.toast("Success! Lead data synced to your Google Sheet, Edward.")
                except:
                    pass # Silent fail to keep user experience smooth

    except Exception as e:
        st.error(f"MAX is refreshing... Technical detail: {e}")
