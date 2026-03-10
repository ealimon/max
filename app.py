# 4. Main Chat Interface (MAX)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm MAX from Limon Media. What business are we looking to grow today?"}
    ]

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input logic - This only runs when the user types something
if prompt := st.chat_input("How can we help your business?"):
    # 1. Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate Assistant Response
    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # Combine history into a single string so Gemini has context
            history_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
            
            # Only generate if there is actual content
            response = model.generate_content(history_context)
            
            if response and response.text:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            else:
                st.error("MAX is thinking too hard. Please try again.")
        except Exception as e:
            st.error(f"Gemini Error: {e}")
