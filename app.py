import streamlit as st
import google.generativeai as genai

# 1. Setup - Pulls from Streamlit Secrets
# On your computer, this is in .streamlit/secrets.toml
# On Streamlit Cloud, it's in the 'Secrets' settings menu.
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Please add your GOOGLE_API_KEY to Streamlit Secrets.")
    st.stop()

# 2. Configure MAX's Persona
st.set_page_config(page_title="MAX | Limon Media Intake", page_icon="🤖")
st.title("🤖 Meet MAX")
st.caption("Professional Intake Specialist for Limon Media")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm MAX. I help Limon Media understand your marketing goals. What's your business name?"}
    ]

# Display existing messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Chat Logic
if prompt := st.chat_input("Type your message here..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response from Gemini
    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # This is where you inject the "Limon Media" instructions
            system_instruction = (
                "You are MAX, an intake specialist for Limon Media digital marketing. "
                "Be professional, encouraging, and brief. Ask about their marketing needs "
                "(SEO, Ads, Web) and their general budget. Once qualified, let them know "
                "Edward will be in touch."
            )
            
            # Combine history for context
            full_history = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages]
            
            # Generate the reply
            response = model.generate_content([system_instruction] + [m["content"] for m in st.session_state.messages])
            
            msg = response.text
            st.markdown(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg})
            
        except Exception as e:
            st.error(f"Something went wrong: {e}")
