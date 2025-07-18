import json
import faiss
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2

app = FastAPI()
load_dotenv()

class Query(BaseModel):
    question: str

def connect_database():
    return psycopg2.connect(os.getenv('string'))

def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

def fetch_projects():
    conn = connect_database()
    cur = conn.cursor()
    cur.execute('SELECT * FROM "Projects"')
    rows = cur.fetchall()
    conn.close()

    projects = []
    for row in rows:
        projects.append({
            "title": row[1],
            "description": row[2],
            "category": row[6],
            "text": f"{row[1]} {row[2]}"
        })
    return projects

def create_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index

@app.post("/ask")
def ask_question(query: Query):
    projects = fetch_projects()
    texts = [p["text"] for p in projects]

    model = load_model()
    embeddings = model.encode(texts, show_progress_bar=False)

    index = create_index(embeddings)
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
        model="openrouter/cypher-alpha:free",
        messages=[{"role": "user", "content": prompt}]
    )

    return {"response": response.choices[0].message.content}

@app.get("/refresh")
def refresh_data():
    # Uproszczona wersja: tylko zapisuje dane do pliku
    projects = fetch_projects()
    with open('projects.json', 'w') as f:
        json.dump(projects, f, indent=2)
    return {"status": "Dane zapisane do projects.json"}
