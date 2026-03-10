import streamlit as st
import google.generativeai as genai
import resend

# 1. SETUP & PERSONALITY
st.set_page_config(page_title="MAX | Limon Media", page_icon="🤖")

# Define MAX's Personality
SYSTEM_PROMPT = """
You are MAX, a high-level Growth Operations AI consultant for Limon Media. 
Your goal is to help business owners in the Coachella Valley (and beyond) 
automate their bottlenecks. Be professional, insightful, and slightly witty. 
Focus on lead generation, AI automation, and ROI.
"""

# Initialize Keys
if "GOOGLE_API_KEY" in st.secrets and "RESEND_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    resend.api_key = st.secrets["RESEND_API_KEY"]
else:
    st.error("Missing API Keys in Streamlit Secrets.")
    st.stop()

# 2. SIDEBAR FORM
with st.sidebar:
    st.title("📬 Capture Lead")
    with st.form("lead_form", clear_on_submit=True):
        biz_name = st.text_input("Business Name")
        lead_email = st.text_input("Contact Email")
        submit_btn = st.form_submit_button("Send to Edward")

# 3. CHAT INTERFACE
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm MAX from Limon Media. Ready to automate your growth?"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. GEMINI LOGIC (The 404 Fix)
if prompt := st.chat_input("Tell MAX about your bottleneck..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # FIXED: Using the 'latest' alias to avoid 404 errors
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash-latest",
                system_instruction=SYSTEM_PROMPT
            )
            
            # Create context from history
            history = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages]
            
            # Generate response
            response = model.generate_content(prompt)
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"MAX Connection Error: {e}")

# 5. SEND LEAD
if submit_btn:
    if biz_name and lead_email:
        transcript = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
        resend.Emails.send({
            "from": "MAX Intake <onboarding@resend.dev>",
            "to": [st.secrets.get("CLIENT_EMAIL", "Edward@Limon.Media")],
            "subject": f"🚀 New Growth Lead: {biz_name}",
            "html": f"<h3>Lead: {lead_email}</h3><hr><pre>{transcript}</pre>"
        })
        st.sidebar.success("Success! Edward will be in touch.")
