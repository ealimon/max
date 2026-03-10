import streamlit as st
import google.generativeai as genai
import resend

# 1. Setup
st.set_page_config(page_title="MAX | Limon Media Intake", page_icon="🤖")

# Initialize API Keys
if "GOOGLE_API_KEY" in st.secrets and "RESEND_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    resend.api_key = st.secrets["RESEND_API_KEY"]
else:
    st.error("Missing API Keys in Secrets.")
    st.stop()

# 2. Sidebar Form
with st.sidebar:
    st.title("📬 Lead Capture")
    with st.form("lead_form", clear_on_submit=True):
        biz_name = st.text_input("Business Name")
        lead_email = st.text_input("Lead's Email")
        submit_button = st.form_submit_button("Send to Edward")

# 3. Email Function (Wix-Friendly Version)
def send_lead_email(biz, email, transcript):
    try:
        # We use onboarding@resend.dev to bypass the Wix DNS issue
        params = {
            "from": "MAX Intake <onboarding@resend.dev>",
            "to": ["Edward@Limon.Media"],
            "subject": f"🚀 New Lead: {biz}",
            "html": f"""
                <h3>New Lead Captured</h3>
                <p><strong>Business:</strong> {biz}</p>
                <p><strong>Email:</strong> {email}</p>
                <hr>
                <h4>Conversation:</h4>
                <pre style="white-space: pre-wrap;">{transcript}</pre>
            """
        }
        resend.Emails.send(params)
        return True
    except Exception as e:
        st.error(f"Email failed: {e}")
        return False

# 4. Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I'm MAX. What business are we growing today?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Chat with MAX..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

# 5. Form Handling
if submit_button:
    if biz_name and lead_email:
        transcript = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
        if send_lead_email(biz_name, lead_email, transcript):
            st.sidebar.success("✅ Lead sent to Edward!")
    else:
        st.sidebar.warning("Please fill out both fields.")
