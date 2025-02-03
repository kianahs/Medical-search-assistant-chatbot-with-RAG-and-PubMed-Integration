from langchain_community.vectorstores import FAISS
import os
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv


def create_vector_store_and_retriever(faiss_index_path, mode=None, urls=None, embeddings=None, text_splitter=None, search_type='similarity', k=3):
    if mode == 'scrape':
        loader = WebBaseLoader(urls)
        documents = loader.load()

    # Chunking
    if text_splitter is None:
        text_splitter = CharacterTextSplitter(
            chunk_size=1000, chunk_overlap=100)

    docs = text_splitter.split_documents(documents)

    # Embedding
    if embeddings is None:
        google_api_key = os.getenv('GOOGLE_API_KEY')
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001", google_api_key=google_api_key)

    # Create FAISS vector store
    print("\n--- Creating FAISS vector store ---")
    db = FAISS.from_documents(docs, embeddings)

    # Save FAISS index
    db.save_local(faiss_index_path)

    print(f"--- FAISS vector store saved at {faiss_index_path} ---")

    # Create  retriever
    retriever = db.as_retriever(
        search_type=search_type,
        search_kwargs={"k": k},
    )

    return retriever


def construct_rag_agent(DB_NAME, llm, google_api_key, custom_splitter, custom_embeddings, mode, urls, search_type, k):

    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(current_dir, "db")
    os.makedirs(db_dir, exist_ok=True)
    faiss_index_path = os.path.join(db_dir, DB_NAME)

    if not os.path.exists(faiss_index_path):

        retriever = create_vector_store_and_retriever(
            faiss_index_path=faiss_index_path,
            mode=mode,
            urls=urls,
            embeddings=custom_embeddings,
            text_splitter=custom_splitter,
            search_type=search_type,
            k=k
        )

    else:

        print(f"--- Loading FAISS vector store from {faiss_index_path} ---")
        db = FAISS.load_local(faiss_index_path, custom_embeddings,
                              allow_dangerous_deserialization=True)
        retriever = db.as_retriever(
            search_type=search_type,
            k=k,
        )

    # Contextualizing question prompt
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question, "
        "which might reference context in the chat history, "
        "formulate a standalone question that can be understood "
        "without the chat history. Do NOT answer the question, just "
        "reformulate it if needed, otherwise return it as is."
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    # Create history-aware retriever
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    # QA Prompt
    qa_system_prompt = (
        "You are an assistant for question-answering tasks. Use "
        "the following retrieved context to answer the question. "
        "If you don't know the answer, just say that you don't know. "
        "Use three sentences maximum and keep it concise."
        "\n\n"
        "{context}"
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    # Question-answering chain
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    # Retrieval-Augmented Generation (RAG) Chain
    rag_chain = create_retrieval_chain(
        history_aware_retriever, question_answer_chain)

    return rag_chain
