import streamlit as st
import google.generativeai as genai

# 1. Page Configuration for Limon Media
st.set_page_config(page_title="MAX | Limon Media Intake", page_icon="🤖", layout="centered")

# Custom UI styling
st.markdown("""
    <style>
    .stApp { max-width: 800px; margin: 0 auto; }
    .stChatMessage { border-radius: 15px; border: 1px solid #f0f0f0; }
    </style>
    """, unsafe_allow_html=True)

# 2. API Security & Setup
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing API Key. Add GOOGLE_API_KEY to Streamlit Secrets (Advanced Settings).")
    st.stop()

# 3. System Instruction (MAX's Persona)
SYSTEM_PROMPT = (
    "You are MAX, the lead qualification specialist for Limon Media. "
    "Your tone is professional, helpful, and energetic. "
    "1. Greet the user and ask for their business name. "
    "2. Ask about their marketing bottleneck (SEO, PPC, Automation). "
    "3. Ask for their monthly budget range (e.g., $1k-5k, $5k-10k). "
    "4. If they seem qualified, tell them Edward Limon will follow up in 24 hours. "
    "Be concise—no long paragraphs."
)

# 4. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm MAX. What business are we growing today?"}
    ]

# Display current chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Chat Interaction Logic
if prompt := st.chat_input("Tell me about your business..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Assistant Response
    with st.chat_message("assistant"):
        try:
            # Using Gemini 2.5 Flash (the 2026 stable workhorse)
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction=SYSTEM_PROMPT
            )
