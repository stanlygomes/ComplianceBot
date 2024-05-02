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
import json
import os
import pycountry


load_dotenv()
CHROMA_PATH = "C:/ProgramData/UserDataFolders/S-1-5-21-1271617331-789234398-1144656980-1030/Documents/chroma_compliance"
# Variables
model_types = {'gpt3.5': 'gpt-3.5-turbo', 'gpt4': 'gpt-4',
               'claude-sonnet': 'claude-3-sonnet-20240229', 'claude-opus': 'claude-3-opus-20240229',
               'claude-haiku': 'claude-3-haiku-20240307'}
country = 'Mexico'
# Get OPEN_AI_KEY
openai_keys = json.load(open('c:/shared/content/config/api-keys/hackathon_openai_keys.json'))
claude_keys = json.load(open('c:/shared/content/config/api-keys/hackathon_claude_keys.json'))
os.environ["OPENAI_API_KEY"] = openai_keys['team_13']
os.environ["ANTHROPIC_API_KEY"] = claude_keys['team_5']
# app config
st.set_page_config(page_title='Wolfie Chatbot', page_icon="🤖")
st.title('Ask Wolfie')

def get_countries():
    countries = list(pycountry.countries)
    country_names = [country.name for country in countries]
    return country_names

def contains_country(string):
    for country in get_countries():
        if country.lower() in string.lower():
            return True, country
    return False, None

# Prepare the DB.
embedding_function = OpenAIEmbeddings()
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

def get_response(user_query, chat_history, country, model_type):

    template = """
    Answer the question based only on the following context:

    {context}

    ---

    Answer this question based on the above context: {user_question}

    Include policy data that is specific to {location}.
    Mention that user is based in {location}.
    """
    # Search the DB.
    question_has_country, country_found = contains_country(user_query) 
    if question_has_country:
        sel_country = country_found
        relevance_prompt = f'{user_query} Include non region-specific policies as well'
    else:
        sel_country = country
        relevance_prompt = f'{user_query} Include not region-specific policies and policies specific to {country}'
    results = db.similarity_search_with_relevance_scores(user_query, k=3)
    if len(results) == 0 or results[0][1] < 0.7:
        print(f"Unable to find matching results.")
        return
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    source_files = [doc.metadata.get("source", None) for doc, _score in results]
    prompt = ChatPromptTemplate.from_template(template)
    
    if model_type.startswith('gpt'):
        model = ChatOpenAI(model=model_type)
    elif model_type.startswith('claude'):
        model = ChatAnthropic(model=model_type)
    else:
        print("Not a valid model or logic hasn't been implemented yet")
        
    chain = prompt | model | StrOutputParser()
    
    return chain.stream({
        # "chat_history": chat_history,
        "user_question": user_query,
        "context": context_text,
        "location": sel_country
    }), source_files

def fbcb(feedback):
    message_id = len(st.session_state.chat_history) - 1
    if message_id >= 0:
        st.session_state.chat_history.append(feedback)

# session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello, I am a chatbot for Wolfgang's corporate policies! How can I help you?"),
    ]

    
# conversation
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)

# user input
user_query = st.chat_input("Type your message here...")
if user_query is not None and user_query != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    with st.chat_message("Human"):
        st.markdown(user_query)

    with st.chat_message("AI"):
        response_temp, response2 = get_response(user_query, st.session_state.chat_history, country, model_types['gpt3.5'])
        response = st.write_stream(response_temp)
        # response, response2 = st.write_stream(get_response(user_query, st.session_state.chat_history, country, model_types['gpt3.5']))
        st.write('Sources:')
        for source in response2:
            st.write(source)
        cols = st.columns([0.1, 1, 1, 6])
        with cols[1]:
            st.button(':thumbsup:', on_click=fbcb, args=('Positive',), key='thumbsup')
        with cols[2]:
            st.button(':thumbsdown:', on_click=fbcb, args=('Negative',), key='thumbsdown')
    st.session_state.chat_history.append(AIMessage(content=f"{str(response)}\nSources:{str(response2)}"))