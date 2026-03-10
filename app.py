import streamlit as st
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText

# 1. Setup
st.set_page_config(page_title="MAX | Limon Media Intake", page_icon="🤖")

# Credentials from your Secrets
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing GOOGLE_API_KEY in Secrets.")
    st.stop()

# 2. Email Function (The "Resellable" Part)
def send_email_notification(biz_name, email, bottleneck, budget):
    # These would be your Limon Media or Client's SMTP settings
    sender_email = st.secrets["SENDER_EMAIL"]
    receiver_email = st.secrets["RECEIVER_EMAIL"]
    password = st.secrets["EMAIL_PASSWORD"] 

    subject = f"🔥 New Lead: {biz_name}"
    body = f"MAX has captured a new lead:\n\nBusiness: {biz_name}\nEmail: {email}\nBottleneck: {bottleneck}\nBudget: {budget}"
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Email failed: {e}")
        return False

# 3. MAX Chat Logic (Simplified)
# ... [Keep your existing Chat Logic here] ...

# 4. Trigger the Email
# When MAX says "Edward will reach out soon," we fire the function
if "reach out soon" in response.text.lower():
    # You can use Gemini to extract these variables from the chat history
    send_email_notification("Business Name", "client@email.com", "Automation", "$2k/mo")
    st.success("Lead sent to Edward's inbox!")
