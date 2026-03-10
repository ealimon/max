import streamlit as st
import google.generativeai as genai
import resend

# 1. SETUP & CONFIGURATION (Must come first)
st.set_page_config(page_title="MAX | Limon Media Intake", page_icon="🤖")

# Initialize API Keys from Secrets
if "GOOGLE_API_KEY" in st.secrets and "RESEND_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    resend.api_key = st.secrets["RESEND_API_KEY"]
else:
    st.error("Missing API Keys in Secrets. Check your Streamlit Dashboard.")
    st.stop()

# 2. SIDEBAR: LEAD CAPTURE FORM
with st.sidebar:
    st.title("📬 Lead Capture")
    with st.form("lead_form", clear_on_submit=True):
        biz_name = st.text_input("Business Name")
        lead_email = st.text_input("Lead's Email Address")
        submit_button = st.form_submit_button("Send Lead to Edward")

# 3. EMAIL FUNCTION
def send_lead_email(biz, email, transcript):
    try:
        # We use Edward's email from Secrets
        recipient = st.secrets.get("CLIENT_EMAIL", "Edward@Limon.Media")
        
        params = {
            "from": "MAX Intake <onboarding@resend.dev>",
            "to": [recipient],
            "subject": f"🚀 New Lead: {biz}",
            "html": f"""
                <div style="font-family: sans-serif;">
                    <h2>New Lead Captured</h2>
                    <p><strong>Business:</strong> {biz}</p>
                    <p><strong>Email:</strong> {email}</p>
                    <hr>
                    <pre style="background: #f4f4f4; padding: 10px;">{transcript}</pre>
                </div>
            """
        }
        resend.Emails.send(params)
        return True
    except Exception as e:
        st.error(f"Email failed: {e}")
        return False

# 4. CHAT INTERFACE LOGIC
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm MAX from Limon Media. What business are we growing today?"}
    ]

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
if prompt := st.chat_input("How can we help your business?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            # Provide full context to Gemini
            history_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
            response = model.generate_content(history_context)
            
            if response.text:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Gemini Error: {e}")

# 5. FORM SUBMISSION
if submit_button:
    if biz_name and lead_email:
        chat_history = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
        if send_lead_email(biz_name, lead_email, chat_history):
            st.sidebar.success("✅ Lead sent successfully!")
    else:
        st.sidebar.warning("Please enter both Name and Email.")
