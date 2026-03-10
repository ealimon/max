import streamlit as st
import google.generativeai as genai

# 1. Page Configuration for Limon Media
st.set_page_config(page_title="MAX | Limon Media Intake", page_icon="🤖", layout="centered")

# Custom UI styling for an agency feel
st.markdown("""
    <style>
    .stApp { max-width: 800px; margin: 0 auto; }
    .stChatMessage { border-radius: 15px; border: 1px solid #f0f0f0; }
    </style>
    """, unsafe_allow_html=True)

# 2. API Security & Setup
# Make sure "GOOGLE_API_KEY" is added in Streamlit Advanced Settings > Secrets
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Missing API Key. Please add GOOGLE_API_KEY to your Streamlit Secrets.")
    st.stop()

# 3. System Instruction (MAX's Persona)
SYSTEM_PROMPT = (
    "You are MAX, the AI Intake Specialist for Limon Media. "
    "Your goal is to qualify potential leads for Edward Limon. "
    "1. Be professional, tech-savvy, and helpful. "
    "2. Greet the user and ask for their business name. "
    "3. Identify their primary bottleneck (Growth Ops, SEO, or Automation). "
    "4. Ask for their monthly budget range (e.g., $1k-5k, $5k-10k, $10k+). "
    "5. If they seem like a good fit, tell them Edward will reach out within 24 hours. "
    "Be concise."
)

# 4. Initialize Chat Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm MAX from Limon Media. What business are we growing today?"}
    ]

# Display chat history
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
            # Using Gemini 2.5 Flash for its speed and reliability in 2026
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction=SYSTEM_PROMPT
            )
            
            # Start chat session with previous messages for context
            chat = model.start_chat(history=[
                {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                for m in st.session_state.messages[:-1]
            ])
            
            # Streaming the response for a "Pro" feel
            response = chat.send_message(prompt, stream=True)
            
            full_response = ""
            placeholder = st.empty()
            
            for chunk in response:
                full_response += chunk.text
                placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            
            # Final save to history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            # This 'except' block fixes the SyntaxError from previous versions
            st.error(f"MAX is having a moment. Details: {str(e)}")
