from fastapi import FastAPI
from pydantic import BaseModel

app2 = FastAPI()

class Query(BaseModel):
    question: str

@app2.post("/ask")
def ask_question(data: Query):
    print(data.question)
    return {"message": "OK"}
