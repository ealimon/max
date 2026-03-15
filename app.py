import streamlit as st
import google.generativeai as genai

# 1. Setup Page & Styling
st.set_page_config(page_title="MAX | Limon Media Intake", layout="centered")
st.title("🤖 Meet MAX")
st.caption("Limon Media's AI Intake Specialist")

# 2. Access Gemini API Key from Streamlit Secrets
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except KeyError:
    st.error("API Key not found. Please set GEMINI_API_KEY in Streamlit Secrets.")

# 3. Initialize the "Brain"
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=(
        "You are MAX, the AI Intake Specialist for Limon Media (https://www.limon.media/). "
        "Business owners often don't know the technical terms; they just want 'more calls' or 'more orders.' "
        "Your job is to listen to their business goals and bridge the gap. "
        "Helpful Tip: If they want calls, mention Google Ads or Local SEO. "
        "Mandatory: Be professional, friendly, and eventually ask for their Business Name and Email Address."
    )
)

# 4. Chat History Management
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm MAX. Tell me a bit about your business and what you're hoping to achieve—is it more phone calls, more walk-ins, or something else?"}
    ]

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Chat Logic
if prompt := st.chat_input("How can Limon Media help your business?"):
    # User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI response
    with st.chat_message("assistant"):
        # We pass the history to Gemini to maintain context
        history = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages]
        chat = model.start_chat(history=history[:-1]) # Exclude the current prompt
        
        response = chat.send_message(prompt)
        full_response = response.text
        st.markdown(full_response)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})
