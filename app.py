import streamlit as st
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Setup
st.set_page_config(page_title="MAX | Limon Media Intake", page_icon="🤖")

# 2. Connections & Credentials
# This pulls from the Secrets you just fixed!
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing GOOGLE_API_KEY in Secrets.")
    st.stop()

# Connect to your Limon_Media_Leads sheet
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. System Instructions for MAX
SYSTEM_PROMPT = (
    "You are MAX, the AI Intake Specialist for Limon Media. "
    "Your goal is to qualify leads for Edward Limon. "
    "1. Ask for their Business Name. "
    "2. Identify their bottleneck (Growth Ops, SEO, or Automation). "
    "3. Ask for their monthly budget. "
    "4. Ask for an Email address to follow up. "
    "Once you have all 4 pieces of info, tell them Edward will reach out soon."
)

# 4. Helper Function: Save Lead to Google Sheets
def save_lead(biz, bottleneck, budget, email):
    try:
        new_row = pd.DataFrame([{
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Business Name": biz,
            "Bottleneck": bottleneck,
            "Budget": budget,
            "Email/Contact": email
        }])
        # Append the data to your Google Sheet
        conn.create(data=new_row)
        return True
    except Exception as e:
        st.error(f"Error saving to sheet: {e}")
        return False

# 5. Chat Interface Logic
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm MAX from Limon Media. What business are we looking to grow today?"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("How can Limon Media help you?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Using the latest Gemini 2.5 Flash for 2026 reliability
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction=SYSTEM_PROMPT
            )
            
            chat = model.start_chat(history=[
                {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                for m in st.session_state.messages[:-1]
            ])
            
            response = chat.send_message(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

            # 6. Automation Logic: Check for a 'Lead' state
            # We can use a button or simple keyword detection to trigger the save
            if "@" in prompt and any(term in prompt.lower() for term in ["$", "budget", "bottleneck"]):
                st.info("Saving your details to Edward's dashboard...")
                # In a real scenario, you'd extract these precisely using the AI
                # For now, we'll trigger the save function
                save_lead("New Lead", "Inquiry", "Check Chat History", prompt)

        except Exception as e:
            # Fixes the 'except or finally' SyntaxError from earlier screenshots
            st.error(f"An error occurred: {e}")
