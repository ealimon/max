import streamlit as st
import google.generativeai as genai
import resend

# 1. THE BRAIN: REFINED SCOPE & AI SERVICES
st.set_page_config(page_title="MAX | Limon Media", page_icon="🤖")

SYSTEM_PROMPT = """
ROLE: You are MAX, the AI Intake Specialist for Limon Media. 
PERSONALITY: Intelligent, social, and professional. 

CORE SERVICES (IN-SCOPE):
You only answer questions about Limon Media's services, which include:
1. Digital Marketing: Web Design (Wix), Google Ads management, SEO, and Social Media.
2. AI Solutions: Custom AI Intake Specialists, AI Business Assistants, and AI Paralegals.

GUARDRAILS (OUT-OF-SCOPE):
1. You are NOT a lawyer, doctor, or technical repairman. 
2. If a user asks for professional advice outside of marketing or AI automation, politely decline.
   - Say: "I'm a specialist in growth and AI automation, so I'm not qualified to provide advice on that. I'd recommend speaking with a professional in that field!"
3. PIVOT: Always guide the conversation back to how Limon Media can help their business scale through marketing or AI.
4. Respond in the same language the user uses (English/Spanish).
"""

# API Initialization
if "GOOGLE_API_KEY" in st.secrets and "RESEND_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    resend.api_key = st.secrets["RESEND_API_KEY"]
else:
    st.error("Missing API Keys in Streamlit Secrets.")
    st.stop()

# 2. SIDEBAR: LEAD CAPTURE
with st.sidebar:
    st.title("📬 Ready to scale?")
    st.write("Drop your details and I'll send this transcript over to Edward.")
    with st.form("lead_form", clear_on_submit=True):
        biz_name = st.text_input("Business Name")
        lead_email = st.text_input("Best email to reach you?")
        submit_btn = st.form_submit_button("Send to Edward")

# 3. EMAIL FUNCTION
def send_lead_email(biz, email, transcript):
    try:
        target = st.secrets.get("CLIENT_EMAIL", "Edward@Limon.Media")
        resend.Emails.send({
            "from": "MAX Intake <onboarding@resend.dev>",
            "to": [target],
            "subject": f"🚀 New Growth Lead: {biz}",
            "html": f"""
                <div style="font-family: sans-serif; color: #333;">
                    <h2>New Lead from MAX</h2>
                    <p><strong>Business:</strong> {biz}</p>
                    <p><strong>Email:</strong> {email}</p>
                    <hr>
                    <div style="background: #f9f9f9; padding: 15px; border-left: 4px solid #007bff;">
                        {transcript.replace(chr(10), '<br>')}
                    </div>
                </div>
            """
        })
        return True
    except Exception as e:
        st.error(f"Email failed: {e}")
        return False

# 4. CHAT INTERFACE
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi, I'm MAX. How can I help you grow your business today?"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Chat with MAX..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash-latest",
                system_instruction=SYSTEM_PROMPT
            )
            
            history = [
                {"role": m["role"] if m["role"] == "user" else "model", "parts": [m["content"]]} 
                for m in st.session_state.messages[:-1]
            ]
            
            chat = model.start_chat(history=history)
            response = chat.send_message(prompt)
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error("MAX is taking a quick coffee break. Try again in a second!")

# 5. FORM SUBMISSION
if submit_btn:
    if biz_name and lead_email:
        full_transcript = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
        if send_lead_email(biz_name, lead_email, full_transcript):
            st.sidebar.success("Got it! Edward will reach out soon.")
    else:
        st.sidebar.warning("Please fill out both fields.")
