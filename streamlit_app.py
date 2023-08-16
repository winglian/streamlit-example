import streamlit as st
import openai

st.set_page_config(page_title="💬 OpenAccess AI Collective Chat")

with st.sidebar:
    openai_api_base = st.text_input("OpenAI API Base URL", key="chatbot_api_base", type="password")
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    openai_api_model = st.text_input("Model NAme", key="chatbot_api_model")

st.title("💬 OpenAccess AI Collective Chat")


# Function for generating LLM response
def generate_response():
    response = openai.ChatCompletion.create(model=openai_api_model, messages=st.session_state.messages)
    return response.choices[0].message


# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I help you?"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User-provided prompt
if prompt := st.chat_input(disabled=not (openai_api_key and openai_api_base)):
    if not openai_api_key or not openai_api_base:
        st.info("Please add your OpenAI API credentials to continue.")
        st.stop()

    openai.api_key = openai_api_key
    openai.api_base = openai_api_base

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_response()
            st.write(response)
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)


# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_response()
            st.write(response)

            message = {"role": "assistant", "content": response}
            st.session_state.messages.append(message)
