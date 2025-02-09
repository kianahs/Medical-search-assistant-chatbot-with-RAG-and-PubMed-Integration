from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from AI_agent import create_agent


load_dotenv()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent_executor = create_agent()


class QueryRequest(BaseModel):
    query: str


@app.post("/chat")
async def chat(request: QueryRequest):
    try:
        response = agent_executor.invoke(
            {"input": request.query, "chat_history": []})
        return {"response": response['output']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run : uvicorn main:app --reload
