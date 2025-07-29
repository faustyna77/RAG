import os
import json
import faiss
import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from openai import OpenAI

load_dotenv()
app = FastAPI()

class Query(BaseModel):
    question: str

projects = []
model = None
index = None

def connect_database():
    return psycopg2.connect(os.getenv("DB_STRING"))

def fetch_projects():
    conn = connect_database()
    cur = conn.cursor()
    cur.execute('SELECT * FROM "Projects"')
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "title": row[1],
            "description": row[2],
            "category": row[6],
            "text": f"{row[1]} {row[2]}"
        }
        for row in rows
    ]

def create_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index

@app.on_event("startup")
def load_resources():
    global projects, model, index
    projects = fetch_projects()
    texts = [p["text"] for p in projects]
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(texts, show_progress_bar=False)
    index = create_index(embeddings)

@app.get("/")
def root():
    return {"message": "Hello from FastAPI + FAISS on Render!"}

@app.post("/ask")
def ask_question(query: Query):
    question_embedding = model.encode([query.question])
    _, I = index.search(question_embedding, k=1)
    project = projects[I[0][0]]

    prompt = f"""Odpowiedz na pytanie na podstawie poniższych informacji o projekcie.
Nie zgaduj, jeśli nie masz wystarczającej informacji – powiedz, że nie wiesz. 
Pamiętaj, że wszystkie projekty na tej stronie są własnością Faustyny Misiura.

Tytuł: {project['title']}
Opis: {project['description']}
Kategoria: {project['category']}

Pytanie: {query.question}
"""

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("API_KEY")
    )

    response = client.chat.completions.create(
        model="mistralai/mistral-small-3.2-24b-instruct",
        messages=[{"role": "user", "content": prompt}]
    )

    return {"response": response.choices[0].message.content}
