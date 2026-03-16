import streamlit as st
import google.generativeai as genai
from google.api_core import client_options
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Configuration & Professional Branding
st.set_page_config(page_title="MAX | Limon Media Intake", page_icon="🤖", layout="centered")

# Custom CSS to hide standard Streamlit UI for a clean "agency" feel
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

# 2. Configuration & API Setup
# Ensure both your Gemini Key and GSheets URL are in Streamlit Secrets
if "GEMINI_API_KEY" not in st.secrets or "gsheets_url" not in st.secrets:
    st.error("Missing configuration. Please check Streamlit Secrets for 'GEMINI_API_KEY' and 'gsheets_url'.")
    st.stop()

# Configure Gemini with the stable endpoint
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
            "You are MAX, the professional, intelligent, and friendly AI Intake Specialist for Limon Media. "
            "Your goal is to help business owners understand how SEO, Google Ads, and Web Design can grow their revenue. "
            "You are based in the Coachella Valley and have a local, strategic vibe. "
            "BILINGUAL LOGIC: If the user mentions a business name or context suggesting a Hispanic-owned business "
            "or Spanish-speaking clientele (e.g., a Taqueria or Panaderia), politely offer to continue in Spanish. "
            "MANDATORY: You must collect their Business Name and Email Address. "
            "Do not repeat your name or introduction after the initial greeting."
        )
    )

model = load_model()

# 4. Chat Memory Management
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Initialize the continuous chat session
    st.session_state.chat_session = model.start_chat(history=[])
    # Track if we have already saved this lead to avoid duplicates
    st.session_state.lead_captured = False

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Initial Greeting (Triggers only once)
if not st.session_state.messages:
    welcome = "Hi! I'm MAX from Limon Media. I help Coachella Valley businesses turn big goals into digital reality. What's the main objective for your business right now?"
    st.session_state.messages.append({"role": "assistant", "content": welcome})
    with st.chat_message("assistant"):
        st.markdown(welcome)

# 5. Interaction & Lead Capture Logic
if prompt := st.chat_input("Tell MAX about your business goals..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        # Send message through the session to maintain memory
        response = st.session_state.chat_session.send_message(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

        # --- LEAD LOGGING LOGIC ---
        if not st.session_state.lead_captured:
            # Quick internal check to see if we have the data needed
            check_prompt = "Has the user provided a Business Name and an Email address yet? Answer only 'YES' or 'NO'."
            check = model.generate_content(f"History: {st.session_state.messages}\n\n{check_prompt}")
            
            if "YES" in check.text.upper():
                # Extract the data cleanly
                extract_prompt = "Extract from the chat: Business Name | Email | Primary Goal. Format exactly with pipes."
                extraction = model.generate_content(f"History: {st.session_state.messages}\n\n{extract_prompt}").text
                
                try:
                    parts = extraction.split("|")
                    
                    # Read current sheet to prepare for append
                    existing_df = conn.read(spreadsheet=st.secrets["gsheets_url"])
                    
                    # Create new row
                    new_row = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Business Name": parts[0].strip(),
                        "Email": parts[1].strip(),
                        "Goals/Notes": parts[2].strip()
                    }])
                    
                    # Combine and update
                    updated_df = pd.concat([existing_df, new_row], ignore_index=True)
                    conn.update(spreadsheet=st.secrets["gsheets_url"], data=updated_df)
                    
                    st.session_state.lead_captured = True
                    st.toast("Success! Lead info sent to Edward's dashboard.")
                except Exception as sync_error:
                    # Silent fail for the user, but we can log it for you
                    pass

    except Exception as e:
        st.error(f"MAX is having a momentary glitch: {e}")
