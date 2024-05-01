import utils
import streamlit as st

def fbcb(feedback):
    message_id = len(st.session_state.chat_history) - 1
    if message_id >= 0:
        st.session_state.feedback_history.append(feedback)

# Variables
model_types = {'gpt3.5': 'gpt-3.5-turbo', 'gpt4': 'gpt-4',
               'claude-sonnet': 'claude-3-sonnet-20240229', 'claude-opus': 'claude-3-opus-20240229',
               'claude-haiku': 'claude-3-haiku-20240307'}

# Streamlit ChatBot UI Setup
st.title('Ask Wolfie')
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
    # response, sources = st.write_stream(utils.llm_rag_predict(prompt, st.session_state.messages, 'Mexico', model_types['claude-opus']))
    # st.chat_message('assistant').write_stream(response)
    response = utils.llm_rag_predict(prompt, st.session_state.messages, 'Mexico', model_types['claude-sonnet'])
    st.chat_message('assistant').markdown(response)
    cols = st.columns([0.1, 1, 1, 6])
    with cols[1]:
        st.button(':thumbsup:', on_click=None, args=('Positive',), key='thumbsup')
    with cols[2]:
        st.button(':thumbsdown:', on_click=None, args=('Negative',), key='thumbsdown')
    st.session_state.messages.append(
        {'role':'assistant', 'content':response.content}
    )