from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import streamlit as st

from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain_community.callbacks.streamlit import (
    StreamlitCallbackHandler,
)

load_dotenv()
CHROMA_PATH = "C:/ProgramData/UserDataFolders/S-1-5-21-1271617331-789234398-1144656980-1030/Documents/chroma_compliance"
# Variables
model_types = {'gpt3.5': 'gpt-3.5-turbo', 'gpt4': 'gpt-4',
               'claude-sonnet': 'claude-3-sonnet-20240229', 'claude-opus': 'claude-3-opus-20240229',
               'claude-haiku': 'claude-3-haiku-20240307'}

st.set_page_config(page_title='Streamlit Chatbot')
st.title("Chatbot")

def get_response(user_query, chat_history, model_type, st_callback):
    template = """
    Answer the question based only on the following context:

    {context}

    ---

    Answer this question based on the above context: {user_question}
    """

    # Prepare the DB.
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_relevance_scores(user_query, k=3)
    if len(results) == 0 or results[0][1] < 0.7:
        print(f"Unable to find matching results.")
        return

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])

    prompt = ChatPromptTemplate.from_template(template)
    # Select model
    if model_type.startswith('gpt'):
        model = ChatOpenAI(model=model_type)
    elif model_type.startswith('claude'):
        model = ChatAnthropic(model=model_type)
    else:
        print("Not a valid model or logic hasn't been implemented yet")
    chain = prompt | model | StrOutputParser()

    sources = [doc.metadata.get("source", None) for doc, _score in results]
    return chain.stream({
        # "chat_history": chat_history,
        "user_question": user_query,
        "context": context_text
    }, {"callbacks": [st_callback]}), sources

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello, I am a bot for compliance policies! How can I help you?")
    ]

for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)

user_query = st.chat_input("Type your message here...")
if user_query is not None and user_query != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    with st.chat_message("Human"):
        st.markdown(user_query)
    with st.chat_message("AI"):
        st_callback = StreamlitCallbackHandler(st.container())
        response, source = st.write_stream(get_response(user_query, st.session_state.chat_history, model_types["claude-opus"], st_callback))
    
    st.session_state.chat_history.append(AIMessage(content=response))