import utils
import streamlit as st

# Variables
model_types = {'gpt3.5': 'gpt-3.5-turbo', 'gpt4': 'gpt-4',
               'claude-sonnet': 'claude-3-sonnet-20240229', 'claude-opus': 'claude-3-opus-20240229',
               'claude-haiku': 'claude-3-haiku-20240307'}

# Streamlit ChatBot UI Setup
st.title('Ask ComplyBot')
prompt = st.chat_input('Provide your prompt here')
# Setup message history variable to hold old messages during session
if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    st.chat_message(message['role']).markdown(message['content'])

if prompt:
    st.chat_message('user').markdown(prompt)
    # Store provided prompt to message history variable
    st.session_state.messages.append({'role':'user', 'content':prompt})
    # Send prompt to LLM
    response = utils.llm_rag_predict(prompt, model_types['claude-opus'])
    st.chat_message('assistant').markdown(response)
    st.session_state.messages.append(
        {'role':'assistant', 'content':response}
    )