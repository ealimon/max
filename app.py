import streamlit as st
import google.generativeai as genai
import resend

# 1. Setup
st.set_page_config(page_title="MAX | Limon Media", page_icon="🤖")
resend.api_key = st.secrets["RESEND_API_KEY"]

# 2. Sidebar Lead Form
with st.sidebar:
    st.title("📬 Capture Lead")
    with st.form("lead_form", clear_on_submit=True):
        biz_name = st.text_input("Business Name")
        lead_email = st.text_input("Lead's Email")
        submit_button = st.form_submit_button("Send Transcript")

# 3. Professional Email Function
def send_pro_email(biz, email, transcript):
    try:
        # This sends from YOUR domain (e.g., max@limonmedia.ai) 
        # to Edward and the Client
        params = {
            "from": "MAX Intake <onboarding@resend.dev>", # You can verify your own domain later
            "to": ["Edward@Limon.Media", st.secrets["CLIENT_EMAIL"]],
            "subject": f"🚀 New Lead for {biz}",
            "html": f"""
                <h3>New Lead Captured by MAX</h3>
                <p><strong>Business:</strong> {biz}</p>
                <p><strong>Lead Email:</strong> {email}</p>
                <hr>
                <h4>Chat Transcript:</h4>
                <pre style="background-color: #f4f4f4; padding: 10px; border-radius: 5px;">{transcript}</pre>
            """,
        }
        resend.Emails.send(params)
        return True
    except Exception as e:
        st.error(f"Email Error: {e}")
        return False

# 4. Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I'm MAX. Let's talk about your business growth."}]

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

# 5. Handle Submit
if submit_button:
    if biz_name and lead_email:
        transcript = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
        if send_pro_email(biz_name, lead_email, transcript):
            st.sidebar.success("✅ Sent! Check your inbox.")
