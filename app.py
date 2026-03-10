import streamlit as st
import google.generativeai as genai
import smtplib
import json
from email.mime.text import MIMEText

# 1. Configuration
st.set_page_config(page_title="MAX | Limon Media", page_icon="🤖")

if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing GOOGLE_API_KEY in Secrets.")
    st.stop()

# 2. Lead Extraction Logic
def extract_lead_data(chat_history):
    """Hidden call to Gemini to parse the conversation into a clean dictionary."""
    model = genai.GenerativeModel("gemini-1.5-flash") # Use Flash for speed/cost
    extraction_prompt = (
        f"Review this chat history and extract the following: Business Name, Email, Bottleneck, and Budget. "
        f"Return the result ONLY as a JSON object. If a field is missing, use 'Unknown'.\n\n"
        f"History: {chat_history}"
    )
    response = model.generate_content(extraction_prompt)
    try:
        # Clean the response text in case of markdown backticks
        json_str = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(json_str)
    except:
        return None

# 3. Email Delivery Function
def send_lead_email(data):
    try:
        sender = st.secrets["SENDER_EMAIL"]
        receiver = st.secrets["RECEIVER_EMAIL"]
        password = st.secrets["EMAIL_PASSWORD"]

        body = (
            f"Business: {data.get('Business Name')}\n"
            f"Email: {data.get('Email')}\n"
            f"Bottleneck: {data.get('Bottleneck')}\n"
            f"Budget: {data.get('Budget')}\n"
        )
        
        msg = MIMEText(body)
        msg['Subject'] = f"🚀 New Limon Media Lead: {data.get('Business Name')}"
        msg['From'] = sender
        msg['To'] = receiver

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

# 4. Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I'm MAX. What's the name of your business?"}]
    st.session_state.email_sent = False

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Message MAX..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        model = genai.GenerativeModel("gemini-1.5-flash")
        # Standard intake prompt
        full_history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        response = model.generate_content(f"You are MAX, the intake AI for Limon Media. Collect: Biz Name, Email, Bottleneck, Budget. History:\n{full_history}")
        
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

        # Trigger extraction and email if MAX is wrapping up
        if "reach out" in response.text.lower() and not st.session_state.email_sent:
            lead_data = extract_lead_data(full_history)
            if lead_data:
                if send_lead_email(lead_data):
                    st.toast("Lead delivered to Edward!", icon="📧")
                    st.session_state.email_sent = True
