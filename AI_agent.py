import os
from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import Tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.text_splitter import CharacterTextSplitter
from RAG_agent import construct_rag_agent


load_dotenv()
os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
google_api_key = os.getenv('GOOGLE_API_KEY')

os.environ["HTTP_PROXY"] = "http://127.0.0.1:10809"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:10809"


custom_splitter = CharacterTextSplitter(
    chunk_size=1000, chunk_overlap=100)

custom_embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001", google_api_key=google_api_key)


llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", temperature=0, api_key=google_api_key
)

news_urls = [
    "https://www.medicalnewstoday.com/",
    "https://www.who.int/news-room/headlines",
    "https://www.cdc.gov/media/releases/index.html",
    "https://www.news-medical.net/",
    "https://www.medscape.com/index/list_13470_0",
    "https://pubmed.ncbi.nlm.nih.gov/trending/",
    "https://www.thelancet.com/latest-research"]

# trending_articles_urls = [

# ]

exisiting_docs_path = None

news_rag_chain = construct_rag_agent(DB_NAME='news',
                                     llm=llm,
                                     google_api_key=google_api_key,
                                     custom_splitter=custom_splitter,
                                     custom_embeddings=custom_embeddings,
                                     mode='scrape',
                                     urls=news_urls,
                                     search_type='similarity',
                                     k=5,
                                     dir_path=None)

api_rag_chain = construct_rag_agent(DB_NAME='PubMed_articles',
                                    llm=llm,
                                    google_api_key=google_api_key,
                                    custom_splitter=custom_splitter,
                                    custom_embeddings=custom_embeddings,
                                    mode='scrape pubmed',
                                    urls=None,
                                    search_type='similarity',
                                    k=5,
                                    dir_path=None)

docs_rag_chain = construct_rag_agent(DB_NAME='existing_articles',
                                     llm=llm,
                                     google_api_key=google_api_key,
                                     custom_splitter=custom_splitter,
                                     custom_embeddings=custom_embeddings,
                                     mode='docs',
                                     urls=None,
                                     search_type='similarity',
                                     k=5,
                                     dir_path='pdfs')


# Load ReAct Prompt
react_docstore_prompt = hub.pull("hwchase17/react")

tools = [
    Tool(
        name="Answer Question for Health and Medical News",
        func=lambda input, **kwargs: news_rag_chain.invoke(
            {"input": input, "chat_history": kwargs.get("chat_history", [])}
        ),
        description="Useful for answering questions about health, medical news based on retrieved context."
    ),

    Tool(
        name="Answer Question for Health and Medical PubMed researches, publications, and articles",
        func=lambda input, **kwargs: api_rag_chain.invoke(
            {"input": input, "chat_history": kwargs.get("chat_history", [])}
        ),
        description="Useful for answering questions about Health and Medical PubMed researches, publications, and articles based on your retrieved data. Add abstract to your answers as well"
    ),
    Tool(
        name="Answer Question for IBS disease",
        func=lambda input, **kwargs: docs_rag_chain.invoke(
            {"input": input, "chat_history": kwargs.get("chat_history", [])}
        ),
        description="Useful for answering questions about IBS disease based on your retrieved data. Mention the title of the article in your answer"
    )


]

agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=react_docstore_prompt,
)

agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent, tools=tools, handle_parsing_errors=True, verbose=True
)


chat_history = []
while True:
    query = input("You: ")
    if query.lower() == "exit":
        break
    response = agent_executor.invoke(
        {"input": query, "chat_history": chat_history}
    )
    print(f"AI: {response['output']}")

    chat_history.append(HumanMessage(content=query))
    chat_history.append(AIMessage(content=response["output"]))
