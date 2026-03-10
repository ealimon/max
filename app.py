import streamlit as st
import google.generativeai as genai

# 1. Page Configuration
st.set_page_config(page_title="MAX | Limon Media Intake", page_icon="🤖", layout="centered")

# Custom CSS for a clean agency look
st.markdown("""
    <style>
    .stApp { max-width: 800px; margin: 0 auto; }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. API Security & Setup
# This looks for the "GOOGLE_API_KEY" you added to Streamlit Advanced Settings > Secrets
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing API Key. Please add GOOGLE_API_KEY to your Streamlit Secrets.")
    st.stop()

# 3. System Instruction (MAX's Persona)
SYSTEM_PROMPT = (
    "You are MAX, the AI Intake Specialist for Limon Media, a growth operations and automation consultancy. "
    "Your goal is to qualify potential clients for Edward Limon. "
    "\n\nTONE: Professional, tech-savvy, energetic, and concise."
    "\n\nGUIDELINES:"
    "\n- Greet the user and ask for their business name."
    "\n- Identify their primary marketing or automation bottleneck (SEO, PPC, Growth Ops)."
    "\n- Ask for their monthly budget range (e.g., $1k-5k, $5k-10k, $10k+)."
    "\n- If the user is qualified, tell them Edward Limon will follow up shortly."
    "\n- Keep responses brief—avoid long paragraphs."
)

# 4. Initialize Chat Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Initial Greeting
    st.session_state.messages.append({"role": "assistant", "content": "Hello! I'm MAX from Limon Media. What business are we looking to grow today?"})

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Chat Logic
if prompt := st.chat_input("How can Limon Media help you?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Assistant Response
    with st.chat_message("assistant"):
        try:
            # Using 1.5-flash for consistency with GEO Auditor PRO
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=SYSTEM_PROMPT
            )
            
            # Start a chat session with history
            chat = model.start_chat(history=[
                {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                for m in st.session_state.messages[:-1]
            ])
            
            # Streaming the response for a high-end feel
            response = chat.send_message(prompt, stream=True)
            
            full_response = ""
            placeholder = st
