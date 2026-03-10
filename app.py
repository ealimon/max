import streamlit as st
import google.generativeai as genai

# 1. Page Configuration
st.set_page_config(page_title="MAX | Limon Media Intake", page_icon="🤖", layout="centered")

# Branding Styles
st.markdown("""
    <style>
    .stApp { max-width: 800px; margin: 0 auto; }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. API Security
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing API Key. Please add GOOGLE_API_KEY to your Streamlit Secrets.")
    st.stop()

# 3. System Instruction
SYSTEM_PROMPT = (
    "You are MAX, the AI Intake Specialist for Limon Media. "
    "Qualify leads for Edward Limon by asking for their business name, "
    "marketing bottleneck, and budget range ($1k-5k, $5k-10k, etc.). "
    "Be professional and concise."
)

# 4. Initialize History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm MAX from Limon Media. What business are we looking to grow today?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Chat Logic
if prompt := st.chat_input("How can Limon Media help you?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Using the stable model matching your GEO app
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=SYSTEM_PROMPT
            )
            
            # Start chat with history
            chat = model.start_chat(history=[
                {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                for m in st.session_state.messages[:-1]
            ])
            
            response = chat.send_message(prompt, stream=True)
            full_response = ""
            placeholder = st.empty()
            
            for chunk in response:
                full_response += chunk.text
                placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
