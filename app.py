import streamlit as st
import google.generativeai as genai
import resend

# 1. App Configuration
st.set_page_config(page_title="MAX | Limon Media Intake", page_icon="🤖")

# Initialize API Keys from Secrets
if "GOOGLE_API_KEY" in st.secrets and "RESEND_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    resend.api_key = st.secrets["RESEND_API_KEY"]
else:
    st.error("Missing API Keys in Secrets (Google or Resend).")
    st.stop()

# 2. Sidebar: Secure Lead Capture Form
with st.sidebar:
    st.title("📬 Lead Capture")
    st.write("Submit the lead details and the chat history will be sent to Edward and the business owner.")
    
    with st.form("lead_form", clear_on_submit=True):
        biz_name = st.text_input("Business Name")
        lead_email = st.text_input("Lead's Email Address")
        submit_button = st.form_submit_button("Send Lead to Inbox")

# 3. Email Delivery Function (Using Resend API)
def send_lead_via_resend(biz, email, transcript):
    try:
        # recipients = [Edward's email, the client/owner's email]
        recipients = ["Edward@Limon.Media", st.secrets["CLIENT_EMAIL"]]
        
        params = {
            "from": "MAX Intake <onboarding@resend.dev>", 
            "to": recipients,
            "subject": f"🚀 New Lead Captured: {biz}",
            "html": f"""
                <div style="font-family: sans-serif; border: 1px solid #ddd; padding: 20px; border-radius: 8px;">
                    <h2 style="color: #1D4ED8;">New Lead for Limon Media</h2>
                    <p><strong>Business Name:</strong> {biz}</p>
                    <p><strong>Lead Email:</strong> <a href="mailto:{email}">{email}</a></p>
                    <hr>
                    <h4>Full Chat Conversation:</h4>
                    <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; white-space: pre-wrap;">{transcript}</div>
                    <br>
                    <a href="mailto:{email}" style="background-color: #1D4ED8; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reply to Lead</a>
                </div>
            """
        }
        resend.Emails.send(params)
        return True
    except Exception as e:
        st.error(f"Email delivery failed: {e}")
        return False

# 4. Main Chat Interface (MAX)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm MAX from Limon Media. What business are we looking to grow today?"}
    ]

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input logic
if prompt := st.chat_input("How can we help your business?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # We use the fast Gemini 1.5 Flash model for 2026 responsiveness
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

# 5. Handle Form Submission Logic
if submit_button:
    if biz_name and lead_email:
        # Create a clean transcript of the entire session
        full_transcript = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
        
        if send_lead_via_resend(biz_name, lead_email, full_transcript):
            st.sidebar.success(f"✅ Lead for {biz_name} sent successfully!")
    else:
        st.sidebar.warning("Please fill out both fields before submitting.")
