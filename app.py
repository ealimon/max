import streamlit as st
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText

# 1. Page Config
st.set_page_config(page_title="MAX | Limon Media", page_icon="🤖")

# 2. Sidebar Lead Form
with st.sidebar:
    st.title("📬 Capture Lead")
    st.write("Ready to follow up? Enter the details below.")
    with st.form("lead_form", clear_on_submit=True):
        biz_name = st.text_input("Business Name")
        lead_email = st.text_input("Lead's Email Address")
        submit_button = st.form_submit_button("Submit to Edward & Owner")

# 3. Email Delivery Logic
def send_combined_email(biz, email, transcript):
    sender = st.secrets["SENDER_EMAIL"]
    password = st.secrets["EMAIL_PASSWORD"]
    # Sending to both Edward and the Owner
    recipients = ["Edward@Limon.Media", st.secrets["RECEIVER_EMAIL"]] 
    
    body = f"NEW LEAD CAPTURED\n\nBusiness: {biz}\nEmail: {email}\n\n--- FULL CONVERSATION ---\n{transcript}"
    
    msg = MIMEText(body)
    msg['Subject'] = f"🚀 New Lead: {biz}"
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, recipients, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Delivery failed: {e}")
        return False

# 4. Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I'm MAX. Tell me a bit about your business and your current bottlenecks."}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Chat with MAX..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

# 5. Handle Form Submission
if submit_button:
    if biz_name and lead_email:
        # Create the transcript from session state
        chat_transcript = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        if send_combined_email(biz_name, lead_email, chat_transcript):
            st.sidebar.success("✅ Lead and Transcript sent!")
    else:
        st.sidebar.warning("Please enter both a Business Name and Email.")
