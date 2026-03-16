import streamlit as st
import google.generativeai as genai
from google.api_core import client_options
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="MAX | Limon Media Intake", page_icon="🤖")
st.markdown("<style>#MainMenu, footer, header {visibility: hidden;}</style>", unsafe_allow_html=True)

st.title("🤖 Meet MAX")
st.caption("Strategic Intake Specialist for Limon Media")

# 2. API & Sheets Setup
if "GEMINI_API_KEY" not in st.secrets or "gsheets_url" not in st.secrets:
    st.error("Missing configuration in Streamlit Secrets (API Key or GSheets URL).")
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
            "You are MAX, the professional AI Intake Specialist for Limon Media. "
            "Help businesses understand SEO, Ads, and Web Design. Be friendly and Coachella Valley local. "
            "MANDATORY: You must collect Business Name and Email. "
            "Once they provide both, let them know Edward Limon will reach out shortly."
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
    welcome = "Hi! I'm MAX from Limon Media. What's your biggest marketing goal right now?"
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

        # LEAD DETECTION
        if not st.session_state.lead_captured:
            check_prompt = "Has the user provided a Business Name and an Email? Answer ONLY 'YES' or 'NO'."
            check = model.generate_content(f"Chat: {st.session_state.messages}\n\n{check_prompt}")
            
            if "YES" in check.text.upper():
                # Extract details
                ext_prompt = "Extract: Name | Email | Main Goal. Format exactly like that."
                ext = model.generate_content(f"Chat: {st.session_state.messages}\n\n{ext_prompt}").text
                
                try:
                    parts = ext.split("|")
                    new_data = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Business Name": parts[0].strip(),
                        "Email": parts[1].strip(),
                        "Goals/Notes": parts[2].strip()
                    }])
                    
                    # Update the Google Sheet
                    conn.create(spreadsheet=st.secrets["gsheets_url"], data=new_data)
                    st.session_state.lead_captured = True
                    st.toast("Lead captured! Check your spreadsheet, Edward.")
                except:
                    pass

    except Exception as e:
        st.error(f"Something went wrong: {e}")
