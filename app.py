import streamlit as st
import google.generativeai as genai
import resend

# 1. PAGE SETUP & PERSONALITY
st.set_page_config(page_title="MAX | Limon Media", page_icon="🤖")

# Define who MAX is
SYSTEM_PROMPT = """
You are MAX, an expert Growth Operations AI consultant for Limon Media. 
Your goal is to help business owners automate bottlenecks and scale ROI.
Be professional, insightful, and proactive.
"""

# Initialize API Keys from Secrets
if "GOOGLE_API_KEY" in st.secrets and "RESEND_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    resend.api_key = st.secrets["RESEND_API_KEY"]
else:
    st.error("Missing API Keys in Streamlit Secrets. Please check your dashboard.")
    st.stop()

# 2. SIDEBAR: LEAD CAPTURE
with st.sidebar:
    st.title("📬 Lead Intake")
    st.write("Send conversation details to Edward.")
    with st.form("lead_form", clear_on_submit=True):
        biz_name = st.text_input("Business Name")
        lead_email = st.text_input("Lead Email Address")
        submit_btn = st.form_submit_button("Send Lead to Edward")

# 3. EMAIL DELIVERY FUNCTION
def send_lead_email(biz, email, history):
    try:
        # Default to your email if CLIENT_EMAIL isn't set
        target_email = st.secrets.get("CLIENT_EMAIL", "Edward@Limon.Media")
        
        resend.Emails.send({
            "from": "MAX Intake <onboarding@resend.dev>",
            "to": [target_email],
            "subject": f"🚀 New Growth Lead: {biz}",
            "html": f"""
                <h3>New Lead Details</h3>
                <p><strong>Business:</strong> {biz}</p>
                <p><strong>Email:</strong> {email}</p>
                <hr>
                <h4>Chat Transcript:</h4>
                <pre style="white-space: pre-wrap; background: #f9f9f9; padding: 10px;">{history}</pre>
            """
        })
        return True
    except Exception as e:
        st.error(f"Email Error: {e}")
        return False

# 4. CHAT INTERFACE LOGIC
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm MAX from Limon Media. What business are we growing today?"}
    ]

# Display current chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input & Gemini Response
if prompt := st.chat_input("Tell MAX about your business..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Using the latest 2026 model ID to avoid 404 errors
            model = genai.GenerativeModel(
                model_name="gemini-3.1-flash-lite-preview",
                system_instruction=SYSTEM_PROMPT
            )
            
            # Format history for Gemini
            chat = model.start_chat(history=[])
            response = chat.send_message(prompt)
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"MAX is having trouble connecting: {e}")

# 5. FORM SUBMISSION HANDLING
if submit_btn:
    if biz_name and lead_email:
        # Build the transcript string
        transcript = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
        if send_lead_email(biz_name, lead_email, transcript):
            st.sidebar.success("✅ Lead sent successfully!")
    else:
        st.sidebar.warning("Please fill out both fields.")
