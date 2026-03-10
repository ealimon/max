import streamlit as st
import google.generativeai as genai
import resend

# 1. INITIAL SETUP
st.set_page_config(page_title="MAX | Limon Media", page_icon="🤖")

# Initialize Keys from your Secrets
if "GOOGLE_API_KEY" in st.secrets and "RESEND_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    resend.api_key = st.secrets["RESEND_API_KEY"]
else:
    st.error("Missing API Keys in Streamlit Secrets.")
    st.stop()

# 2. SIDEBAR LEAD FORM
with st.sidebar:
    st.header("📬 Capture Lead")
    with st.form("lead_form", clear_on_submit=True):
        biz_name = st.text_input("Business Name")
        lead_email = st.text_input("Contact Email")
        submit_btn = st.form_submit_button("Send to Edward")

# 3. CHAT HISTORY SETUP
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi, I'm MAX. Ready to scale your growth operations?"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. GEMINI LOGIC (Updated for March 2026)
if prompt := st.chat_input("Ask MAX anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Using the latest March 2026 model ID
            model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")
            
            # Feed the whole conversation history so MAX has context
            full_chat = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
            response = model.generate_content(full_chat)
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Connection Error: {e}")

# 5. EMAIL DELIVERY
if submit_btn:
    if biz_name and lead_email:
        try:
            transcript = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
            resend.Emails.send({
                "from": "MAX Intake <onboarding@resend.dev>",
                "to": [st.secrets.get("CLIENT_EMAIL", "Edward@Limon.Media")],
                "subject": f"🔥 New Growth Lead: {biz_name}",
                "html": f"<p><strong>Lead Email:</strong> {lead_email}</p><hr><pre>{transcript}</pre>"
            })
            st.sidebar.success("Sent! Check your inbox.")
        except Exception as e:
            st.sidebar.error(f"Email failed: {e}")
