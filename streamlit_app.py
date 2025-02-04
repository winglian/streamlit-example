import re
import logging
import streamlit as st
import openai

st.set_page_config(page_title="💬 OpenAccess AI Collective Chat")

with st.sidebar:
    openai_api_base = st.text_input("OpenAI API Base URL", key="chatbot_api_base")
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    openai_api_model = st.text_input("Model NAme", key="chatbot_api_model")
    system_prompt = st.text_area("System Prompt", key="system_prompt")
    prompt_style = st.selectbox("Prompt Style", ("chatml", "vicuna", "openchat"))

    st.session_state['temperature'] = st.slider('Temperature:', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
    st.session_state['top_p'] = st.slider('Top P:', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    st.session_state['top_k'] = st.slider('Top k:', min_value=0, max_value=100, value=40, step=1)
    st.session_state['max_seq_len'] = st.slider('Max Sequence Length:', min_value=64, max_value=4096, value=512, step=8)
    st.session_state['repetition_penalty'] = st.slider('Repetition Penalty:', min_value=0.0, max_value=2.0, value=1.1, step=0.1)

st.title("💬 OpenAccess AI Collective Chat")


# Function for generating LLM response
def generate_response():
    client = openai.OpenAI(
        base_url=openai_api_base,
        api_key=openai_api_key,
    )

    # response = openai.ChatCompletion.create(model=openai_api_model, messages=st.session_state.messages)
    prompt = ""
    prompt += system_prompt + "\n"
    for message in st.session_state.messages:
        if prompt_style == "chatml":
            for message in st.session_state.messages:
                prompt += f"<|im_start|>{message['role']}\n{message['content']}<|im_end|>\n"
            prompt += "<|im_start|>assistant"
        elif prompt_style == "vicuna":
            if message['role'] == "user":
                prompt += f"USER: {message['content']}\n"
            else:
                prompt += f"ASSISTANT: {message['content']}</s>\n"
            prompt += "ASSISTANT:"
        elif prompt_style == "openchat":
            if message['role'] == "user":
                prompt += f"GPT4 User: {message['content']}<|end_of_turn|>\n"
            else:
                prompt += f"GPT4 Assistant: {message['content']}<|end_of_turn|>\n"
            prompt += "GPT4 Assistant: "
    response = client.chat.completions.create(
        messages=st.session_state.messages,
        model=openai_api_model,
        stream=True,
        temperature=st.session_state['temperature'],
        max_tokens=st.session_state['max_seq_len'],
        top_p=st.session_state['top_p'],
    )
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content


# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = []
#     st.session_state.messages = [{"role": "assistant", "content": "How may I help you?"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User-provided prompt
if prompt := st.chat_input(disabled=not openai_api_base):
    if not openai_api_base:
        st.info("Please add your OpenAI API credentials to continue.")
        st.stop()

    openai.api_key = openai_api_key
    openai.api_base = openai_api_base

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if len(st.session_state.messages) and st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        response = ""
        with st.spinner("Thinking..."):
            response_stream = generate_response()
            for tokens in response_stream:
                tokens = re.findall(r'(.*?)(\s|$)', tokens)
                for subtoken in tokens:
                    subtoken = "".join(subtoken)
                    response += subtoken
                    message_placeholder.markdown(response + "▌")
        message_placeholder.markdown(response)
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)


# Generate a new response if last message is not from assistant
if len(st.session_state.messages) and st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_response()
            st.write(response)

            message = {"role": "assistant", "content": response}
            st.session_state.messages.append(message)
