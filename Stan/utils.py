from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic
import argparse
from dataclasses import dataclass
import os
import shutil
import json

# Get OPEN_AI_KEY
openai_keys = json.load(open('c:/shared/content/config/api-keys/hackathon_openai_keys.json'))
claude_keys = json.load(open('c:/shared/content/config/api-keys/hackathon_claude_keys.json'))
os.environ["OPENAI_API_KEY"] = openai_keys['team_13']
os.environ["ANTHROPIC_API_KEY"] = claude_keys['team_5']

CHROMA_PATH = "C:/ProgramData/UserDataFolders/S-1-5-21-1271617331-789234398-1144656980-1030/Documents/chroma_compliance"
DATA_PATH = "data/compliance"

def generate_data_store():
    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)


def load_documents():
    loader = DirectoryLoader(DATA_PATH, glob="*.md")
    documents = loader.load()
    return documents


def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    document = chunks[10]
    print(document.page_content)
    print(document.metadata)

    return chunks


def save_to_chroma(chunks: list[Document]):
    # Clear out the database first.
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Create a new DB from the documents.
    db = Chroma.from_documents(
        chunks, OpenAIEmbeddings(), persist_directory=CHROMA_PATH
    )
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

def query_data(question, model_type):
    # # Create CLI.
    # parser = argparse.ArgumentParser()
    # parser.add_argument("query_text", type=str, help="The query text.")
    # args = parser.parse_args()
    # query_text = args.query_text
    query_text = question

    # Prepare the DB.
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    if len(results) == 0 or results[0][1] < 0.7:
        print(f"Unable to find matching results.")
        return

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    print(prompt)

    # Select model
    if model_type.startswith('gpt'):
        model = ChatOpenAI(model=model_type)
    elif model_type.startswith('claude'):
        model = ChatAnthropic(model=model_type)
    else:
        print("Not a valid model or logic hasn't been implemented yet")
    response_text = model.invoke(prompt)

    sources = [doc.metadata.get("source", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
    return response_text

def llm_rag_predict(question, model_type):
    # # Create CLI.
    # parser = argparse.ArgumentParser()
    # parser.add_argument("query_text", type=str, help="The query text.")
    # args = parser.parse_args()
    # query_text = args.query_text
    query_text = question

    # Prepare the DB.
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    if len(results) == 0 or results[0][1] < 0.7:
        print(f"Unable to find matching results.")
        return

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    print(prompt)

    # Select model
    if model_type.startswith('gpt'):
        model = ChatOpenAI(model=model_type)
    elif model_type.startswith('claude'):
        model = ChatAnthropic(model=model_type)
    else:
        print("Not a valid model or logic hasn't been implemented yet")
    response_text = model.invoke(prompt)

    sources = [doc.metadata.get("source", None) for doc, _score in results]
    # formatted_response = f"{response_text.content}\nGenerated using: {response_text.response_metadata['model_name']}\nSources: {sources}"
    formatted_response = f"{response_text.content}\nSources: {sources}"
    print(formatted_response)
    return formatted_response