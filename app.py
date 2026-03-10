import streamlit as st
import google.generativeai as genai
import resend

# 1. THE BRAIN: PERSONALITY & LOGIC
st.set_page_config(page_title="MAX | Limon Media", page_icon="🤖")

SYSTEM_PROMPT = """
You are MAX, a savvy and approachable Growth Ops specialist at Limon Media.
- TONE: Intelligent, social, and helpful. You sound like a partner, not a vendor.
- STYLE: Avoid corporate jargon like 'friction points' or 'ROI scaling' unless the user says it first. 
- LOCAL TOUCH: You're based in the Coachella Valley. You know the local business landscape.
- HANDLING OFF-TOPIC: If asked 'off the wall' or personal questions, answer with wit and a smile, then gracefully pivot back to how you can help their business grow.
- GOAL: Be concise. Ask one thoughtful question at a time to keep the conversation flowing.
"""

# API Initialization
if "GOOGLE_API_KEY" in st.secrets and "RESEND_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    resend.api_key = st.secrets["RESEND_API_KEY"]
else:
    st.error("Missing API Keys in Streamlit Secrets.")
    st.stop()

# 2. SIDEBAR: THE CONVERSION BOX
with st.sidebar:
    st.title("📬 Ready to scale?")
    st.write("Drop your details below and I'll send this transcript over to Edward.")
    with st.form("lead_form", clear_on_submit=True):
        biz_name = st.text_input("What's your business name?")
        lead_email = st.text_input("Best email to reach you?")
        submit_btn = st.form_submit_button("Send to Edward")

# 3. EMAIL DELIVERY
def send_lead_email(biz, email, transcript):
    try:
        target = st.secrets.get("CLIENT_EMAIL", "Edward@Limon.Media")
        resend.Emails.send({
            "from": "MAX Intake <onboarding@resend.dev>",
            "to": [target],
            "subject": f"🚀 New Growth Conversation: {biz}",
            "html": f"""
                <div style="font-family: sans-serif; color: #333;">
                    <h2>New Lead from MAX</h2>
                    <p><strong>Business:</strong> {biz}</p>
                    <p><strong>Email:</strong> {email}</p>
                    <hr>
                    <div style="background: #fdfdfd; padding: 15px; border-left: 4px solid #007bff;">
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
        {"role": "assistant", "content": "Hey! I'm MAX. I was just looking over some local growth trends... curious, what's the one part of your business right now that feels like it should be automated, but just isn't yet?"}
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
            # Using the latest stable March 2026 model
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash-latest",
                system_instruction=SYSTEM_PROMPT
            )
            
            # Use start_chat to manage the history properly
            chat = model.start_chat(history=[
                {"role": m["role"] if m["role"] == "user" else "model", "parts": [m["content"]]} 
                for m in st.session_state.messages[:-1]
            ])
            
            response = chat.send_message(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error("MAX is taking a quick coffee break. Try again in a second!")
            print(f"Error: {e}")

# 5. FORM SUBMISSION
if submit_btn:
    if biz_name and lead_email:
        full_transcript = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
        if send_lead_email(biz_name, lead_email, full_transcript):
            st.sidebar.success("Got it! Edward will reach out soon.")
    else:
        st.sidebar.warning("Mind filling those out so I know who to tell Edward about?")
