import os
from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import Tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.text_splitter import CharacterTextSplitter
from RAG_agent import construct_rag_agent
# from langchain.chains import create_history_aware_retriever, create_retrieval_chain
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain_community.vectorstores import FAISS
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_community.document_loaders import WebBaseLoader


load_dotenv()
os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
google_api_key = os.getenv('GOOGLE_API_KEY')

custom_splitter = CharacterTextSplitter(
    chunk_size=1000, chunk_overlap=100)

custom_embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001", google_api_key=google_api_key)


llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", temperature=0, api_key=google_api_key
)


rag_chain = construct_rag_agent(DB_NAME='test2',
                                llm=llm,
                                google_api_key=google_api_key,
                                custom_splitter=custom_splitter,
                                custom_embeddings=custom_embeddings,
                                mode='scrape',
                                urls="https://www.medicalnewstoday.com/",
                                search_type='similarity',
                                k=5)


# Load ReAct Prompt
react_docstore_prompt = hub.pull("hwchase17/react")

tools = [
    Tool(
        name="Answer Question",
        func=lambda input, **kwargs: rag_chain.invoke(
            {"input": input, "chat_history": kwargs.get("chat_history", [])}
        ),
        # description="Useful for answering questions based on retrieved context",
        description="Useful for answering questions about health and medical news based on retrieved context"
    )
]

# Create ReAct Agent
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=react_docstore_prompt,
)

agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent, tools=tools, handle_parsing_errors=True, verbose=True
)

# Chat Loop
chat_history = []
while True:
    query = input("You: ")
    if query.lower() == "exit":
        break
    response = agent_executor.invoke(
        {"input": query, "chat_history": chat_history}
    )
    print(f"AI: {response['output']}")

    # Update history
    chat_history.append(HumanMessage(content=query))
    chat_history.append(AIMessage(content=response["output"]))
